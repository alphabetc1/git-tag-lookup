"""Utility functions for git-tag-lookup."""

import json
import os
import re
from typing import List, Optional, Tuple

from packaging import version


def is_git_url(repo: str) -> bool:
    """Check if the given string is a git URL."""
    git_url_patterns = [
        r"^https?://",
        r"^git@",
        r"^git://",
        r"^ssh://",
    ]
    return any(re.match(pattern, repo) for pattern in git_url_patterns)


def is_local_directory(path: str) -> bool:
    """Check if the given path is a valid local git directory."""
    if not os.path.exists(path):
        return False
    git_dir = os.path.join(path, ".git")
    return os.path.exists(git_dir) and os.path.isdir(git_dir)


def normalize_tag_name(tag: str) -> str:
    """Normalize tag name by removing refs/tags/ prefix if present."""
    # Remove refs/tags/ prefix if present
    return tag.replace("refs/tags/", "")


def parse_version(tag: str) -> Optional[version.Version]:
    """Parse version from tag name, return None if not a valid version.

    This function tries multiple strategies to extract a version number:
    1. Try to parse the tag directly
    2. Try removing common prefixes (v, V, release-, etc.)
    3. Try extracting version pattern from anywhere in the tag
    """
    # Strategy 1: Try parsing the tag directly
    try:
        return version.parse(tag)
    except (version.InvalidVersion, AttributeError):
        pass

    # Strategy 2: Try removing common prefixes
    normalized = normalize_tag_name(tag)
    prefixes = ["v", "V", "release-", "Release-", "RELEASE-", "version-", "Version-", "VERSION-"]
    for prefix in prefixes:
        if normalized.startswith(prefix):
            try:
                return version.parse(normalized[len(prefix) :])
            except (version.InvalidVersion, AttributeError):
                continue

    # Strategy 3: Try to extract version pattern from anywhere in the tag
    # Match patterns like: 1.2.3, 1.2.3.4, 1.2.3-beta, etc.
    version_patterns = [
        r"(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)",  # Standard version: 1.2.3 or 1.2.3.4
        r"(\d+\.\d+(?:\.\d+)?(?:\.\d+)?[-_][a-zA-Z0-9]+)",  # With suffix: 1.2.3-beta
        r"(\d+\.\d+(?:\.\d+)?(?:\.\d+)?[a-zA-Z]\d*)",  # With letter: 1.2.3a1
    ]

    for pattern in version_patterns:
        match = re.search(pattern, normalized)
        if match:
            try:
                return version.parse(match.group(1))
            except (version.InvalidVersion, AttributeError):
                continue

    return None


def sort_tags_by_version(tags: List[str]) -> List[Tuple[str, version.Version]]:
    """Sort tags by version number, return list of (tag, version) tuples.

    Only returns tags that can be parsed as versions.
    """
    tag_versions = []
    for tag in tags:
        v = parse_version(tag)
        if v is not None:
            tag_versions.append((tag, v))

    # Sort by version
    tag_versions.sort(key=lambda x: x[1])
    return tag_versions


def find_earliest_tag(tags: List[str]) -> Optional[str]:
    """Find the earliest tag from a list of tags.

    This function:
    1. Tries to parse tags as version numbers and sorts them
    2. If any tags can be parsed as versions, returns the one with smallest version
    3. If no tags can be parsed as versions, returns the alphabetically first one
    4. If both version-parsable and non-parsable tags exist, prioritizes version-parsable ones
    """
    if not tags:
        return None

    # Separate tags into version-parsable and non-parsable
    version_tags = sort_tags_by_version(tags)
    non_version_tags = [tag for tag in tags if parse_version(tag) is None]

    # If we have version-parsable tags, return the earliest one
    if version_tags:
        return version_tags[0][0]

    # Otherwise, return the alphabetically first non-version tag
    if non_version_tags:
        non_version_tags.sort()
        return non_version_tags[0]

    return None


def format_json_output(data: dict) -> str:
    """Format data as JSON string with proper indentation."""
    return json.dumps(data, indent=2, ensure_ascii=False)


def escape_json_string(s: str) -> str:
    """Escape string for JSON output."""
    return json.dumps(s)
