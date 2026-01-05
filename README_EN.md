# git-tag-lookup

A Python tool to lookup git tags and search commits in git repositories.

[中文文档 / Chinese Documentation](README.md)

## Background

When working with git repositories, developers often need to:
- Find which release tag contains a specific commit to understand when a feature or bug fix was released
- Search for commits related to specific topics or keywords to track changes and understand project history

However, manually searching through tags and commit history can be time-consuming, especially in large repositories with many tags and commits. `git-tag-lookup` automates these tasks, providing a simple command-line interface to quickly find the earliest tag containing a commit (sorted by version number) and search commits by keywords in commit messages.

## Features

1. **Find earliest tag containing a commit**
   - Supports both git URLs and local directories
   - Automatically clones remote repositories when needed
   - Sorts tags by semantic version number to find the earliest release
   - Supports all tag formats:
     - Tags that can be parsed as version numbers (e.g., `v1.0.0`, `1.2.3`, `release-1.0.0`) are sorted by version number
     - Tags that cannot be parsed as version numbers are sorted alphabetically
     - The tool selects the tag with the smallest version number (or earliest alphabetically) from all tags containing the commit

2. **Search commits by keyword**
   - Fuzzy matching in commit messages (case-insensitive)
   - Returns detailed commit information: hash, message, author, and date
   - Supports limiting results with `-n` option
   - Works with local repositories (requires clone for remote repos)

## Installation

### Install from PyPI (when published)

```bash
pip install git-tag-lookup
```

### Install from source

```bash
# Clone the repository
git clone https://github.com/yourusername/git-tag-lookup.git
cd git-tag-lookup

# Install using pip
pip install .

# Or install in development mode
pip install -e .
```

### Run directly from source

After cloning, you can run the script directly:

```bash
./git-tag-lookup --help
```

## Usage

### Find earliest tag containing a commit

```bash
# Using git URL
git-tag-lookup --repo https://github.com/sgl-project/sglang --commit 123xxx

# Using local directory
git-tag-lookup --repo /path/to/repo --commit abc123def456
```

**Output example:**

```json
{
  "repo": "https://github.com/sgl-project/sglang",
  "commit": "123xxx",
  "earliest_tag": "v1.0.0"
}
```

### Search commits by keyword

```bash
# Search all matching commits
git-tag-lookup --repo /path/to/repo --key "fix bug"

# Limit results to 10
git-tag-lookup --repo /path/to/repo --key "fix bug" -n 10
```

**Output example:**

```json
{
  "repo": "/path/to/repo",
  "keyword": "fix bug",
  "limit": 10,
  "total": 15,
  "commits": [
    {
      "hash": "abc123def456...",
      "message": "Fix bug in authentication",
      "author": "John Doe",
      "date": "2024-01-01 12:00:00"
    },
    {
      "hash": "def456ghi789...",
      "message": "Fix critical bug",
      "author": "Jane Smith",
      "date": "2024-01-02 10:30:00"
    }
  ]
}
```

## Command Line Options

```
--repo REPO        Git repository URL or local directory path

--commit COMMIT    Commit hash to find the earliest tag containing it

--key KEYWORD      Keyword to search in commit messages

-n, --limit N      Limit the number of results when searching commits
                   (only for --key)
```

## Requirements

- Python 3.7+
- Git (must be installed and available in PATH)
- packaging (for version sorting)

## Notes

1. **Remote repository commit search**
   - Searching commits in remote repositories requires a local clone
   - Use the local directory path after cloning
   - The tool will automatically clone remote repos when finding tags

2. **Tag version sorting**
   - Tags are sorted by semantic version (e.g., v1.0.0, 1.2.3)
   - Tags that cannot be parsed as versions are sorted alphabetically
   - The "earliest" tag is determined by version number, not by creation time

3. **Keyword search**
   - Uses case-insensitive fuzzy matching
   - Searches in commit messages only
   - Returns all matching commits unless limited by `-n` option

## Error Handling

The tool returns JSON output with error information when something goes wrong:

```json
{
  "error": "Error message here"
}
```

Common errors:
- Invalid repository path or URL
- Commit not found
- No tags found
- Git command not found
- Network timeout when cloning remote repositories

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

