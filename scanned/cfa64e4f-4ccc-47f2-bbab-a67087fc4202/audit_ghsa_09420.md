# [H] gix and gitoxide's symlinked .gitmodules are followed and parsed from outside of the repository

## Summary
Severity: High
Advisory: GHSA-pg4w-g64p-qwhj
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-pg4w-g64p-qwhj
Type: github-advisory

## Affected
- crates.io: `gitoxide` — affected >=0 <0.52.1
- crates.io: `gix` — affected >=0 <0.83.0

## Details
## Summary
attachments:
[pocs.zip](https://github.com/user-attachments/files/26431422/pocs.zip)


When `Repository::submodules()` loads submodule metadata, it prefers the worktree `.gitmodules` file if that path exists. In the current implementation, the path is read with `std::fs::read()`, which follows symlinks. As a result, a repository can present a symlinked `.gitmodules` that points outside the repository, and gitoxide will parse the out-of-repository bytes as submodule configuration.

This is a repository-boundary violation. A caller using the high-level submodule API can believe it is reading repository-local submodule metadata, while the bytes are actually coming from an arbitrary file outside the repository tree.

## Root cause analysis

The relevant flow is:

1. [`gix/src/repository/location.rs`](https://github.com/GitoxideLabs/gitoxide/blob/v0.52.0/gix/src/repository/location.rs) derives the worktree `.gitmodules` path as `workdir/.gitmodules`.
2. [`gix/src/repository/submodule.rs`](https://github.com/GitoxideLabs/gitoxide/blob/v0.52.0/gix/src/repository/submodule.rs) reads that path with `std::fs::read(&path)` and immediately parses the bytes as a submodule configuration file.
3. `Repository::submodules()` exposes the parsed entries through the high-level API.

The issue is not in the parser. The issue is that the worktree path is treated as an ordinary file without checking whether it is a symlink, and without checking whether the canonicalized target remains inside the repository worktree.

Because `std::fs::read()` follows symlinks, a malicious repository can cause gitoxide to ingest bytes from an attacker-chosen location outside the repository. The resulting `Submodule` objects then expose `name`, `path`, and `url` values derived from that external file.

## Reproduction steps

Use the attached PoC zip that contains the `pocs/` workspace.

1. Unzip the PoC archive.
2. Enter `pocs/F001`.
3. Run:
    
    ```bash
    cargo run --quiet
    ```
    
4. Compare the output with `pocs/F001/result.txt`.

Important outputs include:

- `gitmodules_symlink=.../victim-repo/.gitmodules`
- `symlink_target=.../outside/modules.conf`
- `parsed_name=symlinked`
- `parsed_path=deps/symlinked`
- `parsed_url=https://attacker.example/symlinked.git`

These outputs show that gitoxide parsed the submodule configuration from the symlink target outside the repository, not from repository-local bytes.

## Impact

Confirmed impact:

- out-of-repository bytes can be injected into the result of `Repository::submodules()`;
- callers can be misled about submodule metadata such as `name`, `path`, and `url`;
- any downstream workflow that uses those values to decide clone, fetch, update, or policy behavior is operating on attacker-controlled data that did not actually originate from the repository tree.

This report does **not** claim direct command execution from this code path by itself. The demonstrated impact is metadata injection across the repository boundary.

## Recommended fix

A safe fix is to stop silently following symlinks for the worktree `.gitmodules` path in this loading path.

Reasonable options include:

1. use `symlink_metadata()` / `lstat`style checks and reject symlinked `.gitmodules` when loading from the worktree;
2. canonicalize the target and verify that it still resides under the repository worktree before reading it;
3. for security-sensitive callers, prefer loading `.gitmodules` from the index or `HEAD` tree rather than following the worktree path.

At minimum, the worktree path should not silently follow symlinks to arbitrary external files.

## References
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-pg4w-g64p-qwhj
- https://github.com/GitoxideLabs/gitoxide
