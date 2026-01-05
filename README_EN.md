# git-tag-lookup

A Python tool to lookup git tags and search commits in git repositories.

[中文文档 / Chinese Documentation](README.md)

## Background

When working with git repositories, developers often need to:
- Find which release tag contains a specific commit to understand when a feature or bug fix was released
- Search for commits related to specific topics or keywords to track changes and understand project history

However, manually searching through tags and commit history can be time-consuming, especially in large repositories with many tags and commits. `git-tag-lookup` automates these tasks, providing a simple command-line interface to quickly find the earliest tag containing a commit (sorted by creation time) and search commits by keywords in commit messages.

## Features

1. **Find earliest tag containing a commit**
   - Supports both git URLs and local directories
   - Automatically clones remote repositories when needed
   - Sorts tags by creation time to find the earliest release (by tag creation time, not version number)
   - Supports all tag formats, regardless of tag name, sorted by time

2. **Search commits by keyword**
   - Fuzzy matching in commit messages (case-insensitive)
   - Returns detailed commit information: hash, message, author, and date
   - Supports limiting results with `-n` option (default: all)
   - Works with local repositories (requires clone for remote repos)

3. **Common options**
   - `-n` / `--limit` option works for both functions:
     - When finding tags: returns top n earliest tags (default n=1)
     - When searching commits: returns top n matching commits (default: all)

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
# Using git URL (default: returns 1 earliest tag)
git-tag-lookup --repo https://github.com/sgl-project/sglang --commit 123xxx

# Return top 5 earliest tags
git-tag-lookup --repo https://github.com/sgl-project/sglang --commit 123xxx -n 5

# Using local directory
git-tag-lookup --repo /path/to/repo --commit abc123def456
```

**Output example (single tag):**

```json
{
  "repo": "https://github.com/sgl-project/sglang",
  "commit": "123xxx",
  "earliest_tag": "v1.0.0",
  "tags": ["v1.0.0"]
}
```

**Output example (multiple tags):**

```json
{
  "repo": "https://github.com/sgl-project/sglang",
  "commit": "123xxx",
  "limit": 5,
  "tags": ["v1.0.0", "v1.0.1", "v1.1.0", "v1.2.0", "v2.0.0"]
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

-n, --limit N      Limit the number of results
                   - For --commit: number of earliest tags to return (default: 1)
                   - For --key: number of commits to return (default: all)
```

## Requirements

- Python 3.7+
- Git (must be installed and available in PATH)
- packaging (Python dependency)

## Notes

1. **Remote repository commit search**
   - Searching commits in remote repositories requires a local clone
   - Use the local directory path after cloning
   - The tool will automatically clone remote repos when finding tags

2. **Tag time sorting**
   - Tags are sorted by creation time to find the earliest release
   - The "earliest" tag is determined by creation time, not by version number

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

