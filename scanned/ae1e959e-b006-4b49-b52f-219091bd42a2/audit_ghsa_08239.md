# [H] gix-fs: Symlink prefix-reuse allows worktree escape during checkout

## Summary
Severity: High
Advisory: GHSA-f89h-2fjh-2r9q
CVE: CVE-2026-44471
CWE: CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-f89h-2fjh-2r9q
Type: github-advisory

## Affected
- crates.io: `gix-fs` — affected >=0 <0.21.1

## Details
### Summary

A malicious tree can be constructed that will, when checked out with gitoxide, permit writing an attacker-controlled symlink into any existing directory the user has write access to.

### Details

During checkout, all symlink index entries are deferred and created after regular files using a single shared `gix_worktree::Stack`. Internally, this uses a `gix_fs::Stack`.

`gix_fs::Stack::make_relative_path_current()` caches validated path prefixes: when the previously-processed leaf component exactly matches the leading component(s) of the next path, the leaf-to-directory transition at `gix-fs/src/stack.rs:195-197` invokes only `delegate.push_directory()`, never `delegate.push()`.

In `gix_worktree::stack::delegate::StackDelegate`, when the state member is `State::CreateDirectoryAndAttributesStack`, `Attributes::push_directory()` only loads attributes (from the ODB, in the clone case), and does not perform any other checks. The on-disk `symlink_metadata()` check and unlink-on-collision live in `StackDelegate::push()`'s invocation of `create_leading_directory()`, which is therefore bypassed for the cached prefix. The final symlink is created with plain `std::os::unix::fs::symlink`, which follows symlinks in parent directories.

Therefore, it's possible to provide a tree with duplicate symlink and directory entries that exploits this. If a tree is constructed with:

1. A `120000` (symlink) entry `a` that points to `.git/hooks`.
2. A `040000` (directory) entry `a` with a subtree that contains a symlink from `post-checkout` to `../../payload`.
3. A `100755` (executable file) entry `payload`.

This is converted by `gix_index::State::from_tree()` into index entries `["a" (SYMLINK), "a/post-checkout" (SYMLINK)]`.

Then, during the delayed symlink phase:

1. `a` is created as a symlink to e.g. `.git/hooks`.
2. When processing `a/post-checkout`, the `a` prefix is reused from the just-processed leaf entry without re-running the intermediate-directory check, after which…
3. `symlink(target, "<wt>/a/post-checkout")` resolves through the just-created symlink to write `.git/hooks/post-checkout`.

Although this example uses `.git/hooks` for simplicity, there's no actual requirement to write within the repo checkout. This can be fairly easily chained into code execution by writing to something that is known to be executed — for example, by writing to `.git/hooks/post-checkout` if the attacker knows that a hook-aware Git implementation will be used later, or by writing to something like `~/.local/bin`.

### PoC

Attached is [build-bad-repo.sh](https://github.com/user-attachments/files/27223800/build-bad-repo.sh), which builds a repo with the aforementioned tree structure. Cloning it with `gix` will set up the malicious `.git/hooks/post-checkout`, at which point anything that normally invokes the `post-checkout` hook will result in its execution, such as `git checkout -b new-branch`.

### Impact

Arbitrary symlink creation into any existing directory the user can write to.

### Disclosure

This vulnerability was found by AI (specifically, Claude Mythos) as part of [Project Glasswing](https://www.anthropic.com/glasswing). This advisory was written and verified by a human.

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-f89h-2fjh-2r9q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44471
- https://github.com/GitoxideLabs/gitoxide
