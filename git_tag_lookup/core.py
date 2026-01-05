"""Core functionality for git-tag-lookup."""

import os
import shutil
import subprocess
import tempfile
from typing import Dict, List, Optional

from .utils import is_git_url, is_local_directory


class GitTagLookupError(Exception):
    """Base exception for git-tag-lookup errors."""

    pass


def get_tags_from_remote(repo_url: str) -> List[str]:
    """Get all tags from a remote git repository."""
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", repo_url],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        tags = []
        for line in result.stdout.strip().split("\n"):
            if line:
                # Format: <hash>    refs/tags/<tag_name>
                parts = line.split("\t")
                if len(parts) == 2 and parts[1].startswith("refs/tags/"):
                    tag = parts[1].replace("refs/tags/", "")
                    # Skip tags that are not actual tags (like refs/tags/v1.0.0^{})
                    if not tag.endswith("^{}"):
                        tags.append(tag)
        return tags
    except subprocess.TimeoutExpired:
        raise GitTagLookupError(f"Timeout while fetching tags from {repo_url}")
    except subprocess.CalledProcessError as e:
        raise GitTagLookupError(f"Failed to fetch tags from {repo_url}: {e.stderr}")
    except FileNotFoundError:
        raise GitTagLookupError("git command not found. Please install git.")


def get_tags_from_local(repo_path: str) -> List[str]:
    """Get all tags from a local git repository."""
    try:
        result = subprocess.run(
            ["git", "tag"], cwd=repo_path, capture_output=True, text=True, check=True, timeout=10
        )
        tags = [tag.strip() for tag in result.stdout.strip().split("\n") if tag.strip()]
        return tags
    except subprocess.TimeoutExpired:
        raise GitTagLookupError(f"Timeout while fetching tags from {repo_path}")
    except subprocess.CalledProcessError as e:
        raise GitTagLookupError(f"Failed to fetch tags from {repo_path}: {e.stderr}")
    except FileNotFoundError:
        raise GitTagLookupError("git command not found. Please install git.")


def check_commit_in_tag_local(repo_path: str, commit: str, tag: str) -> bool:
    """Check if a commit is contained in a tag (local repository)."""
    try:
        # Use git merge-base to check if commit is ancestor of tag
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", commit, tag],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError:
        # If merge-base fails, try alternative method
        try:
            result = subprocess.run(
                ["git", "tag", "--contains", commit],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            tags = [t.strip() for t in result.stdout.strip().split("\n") if t.strip()]
            return tag in tags
        except subprocess.CalledProcessError:
            return False
    except subprocess.TimeoutExpired:
        return False


def get_tag_timestamp(repo_path: str, tag: str) -> Optional[int]:
    """Get the timestamp of a tag (when it was created/committed).

    Returns the timestamp as an integer (Unix timestamp), or None if unable to get it.
    """
    try:
        # Try to get the commit date of the tag
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", tag],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        timestamp_str = result.stdout.strip()
        if timestamp_str:
            return int(timestamp_str)
    except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired):
        pass

    # Fallback: try using for-each-ref
    try:
        result = subprocess.run(
            ["git", "for-each-ref", "--format=%(creatordate:unix)", f"refs/tags/{tag}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        timestamp_str = result.stdout.strip()
        if timestamp_str:
            return int(timestamp_str)
    except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired):
        pass

    return None


def find_earliest_tags_by_time(repo_path: str, tags: List[str], limit: int = 1) -> List[str]:
    """Find the earliest tags by creation time from a list of tags.

    Returns a list of tags sorted by creation time (earliest first).
    If limit is specified, returns at most that many tags.
    """
    if not tags:
        return []

    # Get timestamps for all tags
    tag_timestamps = []
    tags_without_timestamp = []

    for tag in tags:
        timestamp = get_tag_timestamp(repo_path, tag)
        if timestamp is not None:
            tag_timestamps.append((tag, timestamp))
        else:
            tags_without_timestamp.append(tag)

    result: List[str] = []

    # Sort by timestamp (earliest first)
    tag_timestamps.sort(key=lambda x: x[1])

    # Add tags with timestamps first
    for tag, _ in tag_timestamps:
        if len(result) >= limit:
            break
        result.append(tag)

    # If we still need more tags and there are tags without timestamps, add them alphabetically
    if len(result) < limit and tags_without_timestamp:
        tags_without_timestamp.sort()
        for tag in tags_without_timestamp:
            if len(result) >= limit:
                break
            result.append(tag)

    return result


def find_earliest_tag_for_commit(repo: str, commit: str, limit: int = 1) -> Dict:
    """Find the earliest tags (by creation time) that contain the given commit.

    Args:
        repo: Git repository URL or local directory path
        commit: Commit hash to find tags containing it
        limit: Maximum number of tags to return (default: 1)

    Returns:
        Dictionary with repo, commit, and tags (or earliest_tag for backward compatibility)
    """
    temp_dir = None
    original_repo = repo

    try:
        # For remote repos, we need to clone first to check commits
        if is_git_url(repo):
            temp_dir = tempfile.mkdtemp()
            # Shallow clone to save time and space
            subprocess.run(
                ["git", "clone", "--depth", "100", "--tags", repo, temp_dir],
                capture_output=True,
                text=True,
                check=True,
                timeout=120,
            )
            repo = temp_dir
        elif not is_local_directory(repo):
            raise GitTagLookupError(
                f"Invalid repository: {repo}. Must be a git URL or local directory."
            )

        # Get all tags
        tags = get_tags_from_local(repo)

        if not tags:
            return {
                "repo": original_repo,
                "commit": commit,
                "earliest_tag": None,
                "tags": [],
                "error": "No tags found in repository",
            }

        # Filter tags that contain the commit
        containing_tags = [tag for tag in tags if check_commit_in_tag_local(repo, commit, tag)]

        if not containing_tags:
            return {
                "repo": original_repo,
                "commit": commit,
                "earliest_tag": None,
                "tags": [],
                "error": f"No tag contains commit {commit}",
            }

        # Find the earliest tags by creation time
        earliest_tags = find_earliest_tags_by_time(repo, containing_tags, limit)

        result = {"repo": original_repo, "commit": commit, "tags": earliest_tags}

        # For backward compatibility, also include earliest_tag when limit is 1
        if earliest_tags:
            result["earliest_tag"] = earliest_tags[0]
        else:
            result["earliest_tag"] = None

        return result
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def search_commits_by_keyword(repo: str, keyword: str, limit: Optional[int] = None) -> Dict:
    """Search commits by keyword in commit message."""
    if is_git_url(repo):
        # For remote repos, we need to inform user that local clone is required
        return {
            "repo": repo,
            "keyword": keyword,
            "error": "Searching commits in remote repositories requires a local clone. Please clone the repository first and use the local path.",
            "commits": [],
        }
    elif not is_local_directory(repo):
        raise GitTagLookupError(
            f"Invalid repository: {repo}. Must be a git URL or local directory."
        )

    # Build git log command
    cmd = ["git", "log", "--grep", keyword, "--format=%H|%s|%an|%ai"]

    if limit is not None:
        cmd.extend(["-n", str(limit)])

    try:
        result = subprocess.run(
            cmd, cwd=repo, capture_output=True, text=True, check=True, timeout=60
        )

        commits: List[Dict] = []
        all_lines: List[str] = [line for line in result.stdout.strip().split("\n") if line.strip()]
        total_count = len(all_lines)

        # Parse output (respect limit if specified)
        for line in all_lines:
            if limit is not None and len(commits) >= limit:
                break
            parts = line.split("|", 3)
            if len(parts) >= 4:
                commits.append(
                    {"hash": parts[0], "message": parts[1], "author": parts[2], "date": parts[3]}
                )

        output = {"repo": repo, "keyword": keyword, "total": total_count, "commits": commits}

        if limit is not None:
            output["limit"] = limit

        return output

    except subprocess.TimeoutExpired:
        raise GitTagLookupError(f"Timeout while searching commits in {repo}")
    except subprocess.CalledProcessError as e:
        # If no commits found, git log returns non-zero, but that's okay
        if "fatal" in e.stderr.lower() or "error" in e.stderr.lower():
            raise GitTagLookupError(f"Failed to search commits: {e.stderr}")
        # Otherwise, return empty result
        return {"repo": repo, "keyword": keyword, "total": 0, "commits": []}
    except FileNotFoundError:
        raise GitTagLookupError("git command not found. Please install git.")
