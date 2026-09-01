# [?] fix[ux]: fix relpath compiler panic on windows (#4228)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2024-10-04
Source: https://github.com/vyperlang/vyper/commit/c7669bd2ebe2c405aa5572b58311b51517568143
Type: security-commit

## Details
fix[ux]: fix relpath compiler panic on windows (#4228)

fix a bug where `os.path.relpath()` raises an exception on window
- when the source path and the destination path are on different
drives. this commit introduces the helper function `safe_relpath()`,
which tries hard to construct a relpath (using `os.path.relpath()`),
but falls back to the original path (which might be an absolute path)
instead of raising an exception.

references:
- https://docs.python.org/3/library/os.path.html#os.path.relpath
