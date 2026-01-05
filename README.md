# git-tag-lookup

一个更聪明地帮你「找版本、查提交」的 Git 小工具。

[English Documentation](README_EN.md)

---

## 为什么需要这个工具？

在日常开发中，你多半遇到过这些场景：

1. **想知道一个 commit 属于哪个版本**
   - 某个 bug 是从哪个版本开始出现的？
   - 某个功能最早在哪个版本里上线？
   - 回滚或写 release notes 时，需要知道「这个提交最早在哪个 tag 里？」

2. **想按关键词查一串相关提交**
   - 想看和「登录优化」相关的所有改动
   - 想找出与某个 bug 相关的所有提交
   - 想整理一段时间内的变更记录，写 changelog

`git-tag-lookup` 就是为这种场景准备的一个小工具，它提供简单直接的命令行接口，可以帮你：
- 快速找到「包含指定 commit 的**最早** tag」（按版本号排序）
- 按关键词在提交信息中搜索相关 commit（可设置数量上限）

支持远程仓库 URL 和本地路径；对远程仓库会在需要时自动克隆；版本号解析也自动处理，让这些本来繁琐的工作更顺手。

---

## 功能特性

### 1. 查找包含指定 commit 的最早 tag

- 支持 Git 仓库 URL 或本地目录路径
- 对远程仓库，在需要时自动克隆到本地
- 按 **语义版本号** 排序，从中找出「最早的发布版本」
- 支持所有 tag 格式：
  - 能解析为版本号的 tag（如 `v1.0.0`、`1.2.3`、`release-1.0.0` 等）会按版本号排序
  - 无法解析为版本号的 tag 会按字母顺序排序
  - 最终从所有包含该 commit 的 tag 中选出版本号最小的（或字母序最早的）

### 2. 根据关键词搜索提交

- 在提交信息中进行 **不区分大小写** 的模糊匹配
- 返回详细提交信息，包括：
  - 提交哈希
  - 提交信息
  - 作者
  - 日期
- 支持使用 `-n` 限制结果条数
- 目前在 **本地仓库** 中搜索（远程仓库需要先自行克隆）

---

## 安装方法

### 从 PyPI 安装（发布后）

```bash
pip install git-tag-lookup
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/git-tag-lookup.git
cd git-tag-lookup

# 使用 pip 安装
pip install .

# 或者以开发模式安装
pip install -e .
```

### 直接从源码运行

克隆后，可以直接运行脚本：

```bash
./git-tag-lookup --help
```

## 使用方法

### 查找包含 commit 的最早 tag

```bash
# 使用 git URL
git-tag-lookup --repo https://github.com/sgl-project/sglang --commit 123xxx

# 使用本地目录
git-tag-lookup --repo /path/to/repo --commit abc123def456
```

**输出示例：**

```json
{
  "repo": "https://github.com/sgl-project/sglang",
  "commit": "123xxx",
  "earliest_tag": "v1.0.0"
}
```

### 根据关键词搜索提交

```bash
# 搜索所有匹配的提交
git-tag-lookup --repo /path/to/repo --key "修复bug"

# 限制结果为 10 条
git-tag-lookup --repo /path/to/repo --key "修复bug" -n 10
```

**输出示例：**

```json
{
  "repo": "/path/to/repo",
  "keyword": "修复bug",
  "limit": 10,
  "total": 15,
  "commits": [
    {
      "hash": "abc123def456...",
      "message": "修复认证中的bug",
      "author": "张三",
      "date": "2024-01-01 12:00:00"
    },
    {
      "hash": "def456ghi789...",
      "message": "修复关键bug",
      "author": "李四",
      "date": "2024-01-02 10:30:00"
    }
  ]
}
```

## 命令行选项

```
--repo REPO        Git 仓库 URL 或本地目录路径

--commit COMMIT    要查找包含它的最早 tag 的提交哈希

--key KEYWORD      在提交信息中搜索的关键词

-n, --limit N      搜索提交时限制结果数量（仅用于 --key）
```

## 依赖要求

- Python 3.7+
- Git（必须安装并在 PATH 中可用）
- packaging（用于版本号排序）

## 注意事项

1. **远程仓库提交搜索**
   - 在远程仓库中搜索提交需要本地克隆
   - 克隆后使用本地目录路径
   - 查找标签时工具会自动克隆远程仓库

2. **标签版本排序**
   - 标签按语义版本排序（例如 v1.0.0、1.2.3）
   - 无法解析为版本的标签按字母顺序排序
   - "最早"的标签是按版本号确定的，而不是按创建时间

3. **关键词搜索**
   - 使用不区分大小写的模糊匹配
   - 仅在提交信息中搜索
   - 除非使用 `-n` 选项限制，否则返回所有匹配的提交

## 错误处理

工具在出错时会返回包含错误信息的 JSON 输出：

```json
{
  "error": "错误信息"
}
```

常见错误：
- 无效的仓库路径或 URL
- 未找到提交
- 未找到标签
- 未找到 git 命令
- 克隆远程仓库时网络超时

## 许可证

MIT License

## 贡献

欢迎贡献代码！请随时提交 Pull Request。
