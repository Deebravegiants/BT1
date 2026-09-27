# [M] skilo add follows symbolic links, allowing arbitrary local file disclosure from a malicious skill source

## Summary
Severity: Medium
Advisory: GHSA-6xx4-9wp6-65p7
CWE: CWE-59, CWE-61
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-6xx4-9wp6-65p7
Type: github-advisory

## Affected
- crates.io: `skilo` — affected >=0.5.0 <0.11.1

## Details
### Impact

`skilo add` installs a skill by recursively copying the skill directory into the
target skills directory. The copy routine (`copy_dir_all`) classified each entry
with `std::fs::DirEntry::file_type()` — which does **not** follow symlinks — and
then copied non-directory entries with `std::fs::copy()`, which **does**
dereference symlinks.

As a result, a skill containing a symbolic link such as
`reference.txt -> /home/<user>/.ssh/id_rsa` was copied as a regular file whose
contents are the link's **target**. A malicious skill source — for example a git
repository installed via `skilo add github.com/<attacker>/<skills>`, or a local
path — could read arbitrary files readable by the user running `skilo add` (SSH
keys, cloud credentials, `.env` files, etc.) and place their contents inside the
installed skill directory, where the user or their agent may later read, share,
or sync them.

This is arbitrary local file disclosure (CWE-59 / CWE-61, symlink following)
triggered by installing an untrusted skills source.

### Patches

Fixed in **0.11.1**. `copy_dir_all` now rejects symbolic-link entries at any
recursion depth (failing closed with a dedicated error) instead of dereferencing
them.

### Workarounds

- Only install skills from sources you trust.
- Inspect a skill source for symbolic links before running `skilo add`.

### Affected versions

Introduced together with the `skilo add` command in 0.5.0 and present through
0.11.0. Releases before 0.5.0 do not include the `add` command.

## References
- https://github.com/manuelmauro/skilo/security/advisories/GHSA-6xx4-9wp6-65p7
- https://github.com/manuelmauro/skilo/pull/11
- https://github.com/manuelmauro/skilo/commit/c14bdc2eddcf26633ab1dcc0b2d5c0ff42c72a3e
- https://github.com/manuelmauro/skilo
- https://github.com/manuelmauro/skilo/releases/tag/v0.11.1
