# [H] gix and gitoxide: unvalidated submodule name traverses out of .git/modules and redirects state() / open() to another repository

## Summary
Severity: High
Advisory: GHSA-fr8x-3vfx-f45h
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-fr8x-3vfx-f45h
Type: github-advisory

## Affected
- crates.io: `gitoxide` — affected >=0 <0.52.1
- crates.io: `gix` — affected >=0 <0.83.0

## Details
## **Summary**
attachments:
[pocs.zip](https://github.com/user-attachments/files/26431422/pocs.zip)

Submodule names coming from `.gitmodules` are exposed as unvalidated names and are later reused to derive the submodule git directory as:

```
<superproject common_dir>/modules/<submodule name>
```

Because the submodule name is joined directly as a filesystem path component, a name such as `../../../escaped-target.git` escapes `.git/modules` after normalization. The current implementation then uses that escaped path in both `state()` and `open()`.

The updated PoC demonstrates the real sink, not just string construction:

- `state()` reports `repository_exists=true` for the traversed path;
- `open()` returns a repository whose normalized `common_dir()` matches the attacker-chosen repository outside `.git/modules`.

## **Root cause analysis**

The relevant flow is:

1. [`gix-submodule/src/access.rs`](https://github.com/GitoxideLabs/gitoxide/blob/v0.52.0/gix-submodule/src/access.rs) exposes unvalidated submodule names from configuration.
2. [`gix/src/submodule/mod.rs`](https://github.com/GitoxideLabs/gitoxide/blob/v0.52.0/gix/src/submodule/mod.rs) derives the git directory by doing `common_dir().join("modules").join(name)` with no confinement check.
3. [`gix/src/submodule/mod.rs`](https://github.com/GitoxideLabs/gitoxide/blob/v0.52.0/gix/src/submodule/mod.rs) uses that derived path during state resolution and repository opening.

There is no normalization-and-confinement step between “submodule name from configuration” and “filesystem path used for repository existence checks / open.” As a result, traversal segments in the submodule name directly influence which repository path is inspected and opened.

## **Reproduce steps**

Use the attached PoC zip that contains the `pocs/` workspace.

1. Unzip the PoC archive.
2. Enter `pocs/F002`.
3. Run:
    
    ```
    cargo run --quiet
    ```
    
4. Compare the output with `pocs/F002/result.txt`.

Key outputs are:

- `submodule_name=../../../escaped-target.git`
- `derived_git_dir_raw=.../.git/modules/../../../escaped-target.git`
- `derived_git_dir_normalized=.../artifacts/escaped-target.git`
- `escaped_target=.../artifacts/escaped-target.git`
- `repository_exists=true`
- `submodule_opened=true`
- `opened_common_dir_normalized=.../artifacts/escaped-target.git`
- `normalized_git_dir_matches_target=true`
- `opened_common_dir_matches_target=true`
- `target_outside_modules_root=true`

These outputs show that gitoxide is not only constructing a traversable path string. It is actually using the escaped path for repository existence checks and for opening a repository object.

## **Impact**

Confirmed impact:

- a malicious submodule name can redirect submodule state inspection away from `.git/modules/<name>` to an attacker-chosen repository path outside `.git/modules`;
- `Submodule::state()` can report repository existence for the wrong repository;
- `Submodule::open()` can return a repository object backed by that attacker-chosen path.

This is best described as a path-traversal / repository-confusion issue in submodule repository resolution.

This report does **not** claim command execution from this behavior alone. The demonstrated impact is repository redirection: callers that enumerate, inspect, or operate on submodules can be steered into using the wrong repository.

## **Recommended fix**

Two complementary fixes are advisable:

1. do not reuse raw submodule names as filesystem path fragments;
    - either use a validated/sanitized name for filesystem derivation,
    - or derive the storage path from a safe identifier instead of the user-controlled name;
2. add an explicit confinement check after path derivation;
    - normalize or canonicalize the candidate path,
    - verify that the result stays under `<common_dir>/modules`,
    - reject names that contain traversal segments, path separators, or any representation that can escape the modules root.

In short, submodule names may remain opaque configuration identifiers, but they should not be treated as trusted filesystem subpaths.

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-fr8x-3vfx-f45h
- https://github.com/GitoxideLabs/gitoxide
