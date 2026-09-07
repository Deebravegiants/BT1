# [H] go-git: Worktree operations may follow symlinks

## Summary
Severity: High
Advisory: GHSA-hc8v-wwc9-vgxm
CVE: CVE-2026-71556
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-hc8v-wwc9-vgxm
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-git/v5` — affected >=0 <5.19.2
- Go: `github.com/go-git/go-git/v6` — affected >=0 <6.0.0-alpha.5

## Details
## Impact

A symlink traversal issue in `go-git` could allow worktree operations to modify files outside the intended worktree path.

The `worktreeFilesystem` wrapper rejected dangerous path strings, including paths containing `.git`, parent-directory components, or control characters. However, it did not prevent filesystem operations from following symbolic links that were already present in the worktree.

As a result, a path that is safe when evaluated as a string could still resolve into the repository's Git metadata directory. For example, if `s` is a symbolic link to `.git`, writing to `s/config` would modify `.git/config`.

A symbolic link at the final path component could also be followed. For example, if `s` points directly to `.git/config`, opening `s` for writing with truncation could overwrite the repository configuration.

Exploitation requires an attacker to be able to introduce or control a symbolic link in the worktree and cause the application to perform a write through that path.

Applications using `storage/memory` for their Storer, or `go-billy/memfs` for their `Worktree`, are not affected by this vulnerability.

## Patches

The issue has been addressed by making the worktree filesystem wrapper a symlink-safe boundary.

Worktree operations now reject paths where an existing symbolic link in any path component could cause the operation to escape the intended worktree location, including symbolic links at the final component.

Users of filesystem-backed worktrees should upgrade to a patched version.

### Credits

Thanks to @kodareef5 for reporting this issue and working with the go-git security team toward its resolution. :1st_place_medal: 
We would also like to thank @HughLewis20, who independently reported the same issue while a fix was already in progress.

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-hc8v-wwc9-vgxm
- https://github.com/go-git/go-git/commit/008a78f2dd86f52544ddff8b8e8ddeecdf3f7aab
- https://github.com/go-git/go-git/commit/661d1c7f101d34e002a3cfcf8dbea5b7421d07ac
- https://github.com/go-git/go-git
- https://github.com/go-git/go-git/releases/tag/v5.19.2
- https://github.com/go-git/go-git/releases/tag/v6.0.0-alpha.5
