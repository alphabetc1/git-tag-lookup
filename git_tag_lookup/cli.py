"""Command-line interface for git-tag-lookup."""

import argparse
import sys
from typing import Optional
from .core import find_earliest_tag_for_commit, search_commits_by_keyword, GitTagLookupError
from .utils import format_json_output


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Lookup git tags and search commits',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find earliest tag containing a commit
  git-tag-lookup --repo https://github.com/sgl-project/sglang --commit 123xxx
  
  # Search commits by keyword
  git-tag-lookup --repo /path/to/repo --key "fix bug"
  
  # Search commits with limit
  git-tag-lookup --repo /path/to/repo --key "fix bug" -n 10
        """
    )
    
    parser.add_argument(
        '--repo',
        required=True,
        help='Git repository URL or local directory path'
    )
    
    # Mutually exclusive group for commit and keyword
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--commit',
        help='Commit hash to find the earliest tag containing it'
    )
    group.add_argument(
        '--key',
        dest='keyword',
        help='Keyword to search in commit messages'
    )
    
    parser.add_argument(
        '-n',
        '--limit',
        type=int,
        default=None,
        help='Limit the number of results when searching commits (only for --key)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.commit:
            # Function 1: Find earliest tag for commit
            result = find_earliest_tag_for_commit(args.repo, args.commit)
            print(format_json_output(result))
            
        elif args.keyword:
            # Function 2: Search commits by keyword
            result = search_commits_by_keyword(args.repo, args.keyword, args.limit)
            print(format_json_output(result))
            
    except GitTagLookupError as e:
        error_result = {
            "error": str(e)
        }
        print(format_json_output(error_result), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_result = {
            "error": f"Unexpected error: {str(e)}"
        }
        print(format_json_output(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

