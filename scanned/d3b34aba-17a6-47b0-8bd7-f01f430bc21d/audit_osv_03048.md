# [H] ALPINE-CVE-2024-32021

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-32021
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-05-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-32021
Type: osv

## Affected
- Alpine:v3.17: `git` — affected >=2.40.0 <2.39.5-r0
- Alpine:v3.18: `git` — affected >=2.40.0 <2.40.3-r0
- Alpine:v3.19: `git` — affected >=2.40.0 <2.43.4-r0
- Alpine:v3.20: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.21: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.22: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.23: `git` — affected >=2.40.0 <2.45.1-r0
- Alpine:v3.24: `git` — affected >=2.40.0 <2.45.1-r0

## Details
Git is a revision control system. Prior to versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4, when cloning a local source repository that contains symlinks via the filesystem, Git may create hardlinks to arbitrary user-readable files on the same filesystem as the target repository in the `objects/` directory. Cloning a local repository over the filesystem may creating hardlinks to arbitrary user-owned files on the same filesystem in the target Git repository's `objects/` directory. When cloning a repository over the filesystem (without explicitly specifying the `file://` protocol or `--no-local`), the optimizations for local cloning
will be used, which include attempting to hard link the object files instead of copying them. While the code includes checks against symbolic links in the source repository, which were added during the fix for CVE-2022-39253, these checks can still be raced because the hard link operation ultimately follows symlinks. If the object on the filesystem appears as a file during the check, and then a symlink during the operation, this will allow the adversary to bypass the check and create hardlinks in the destination objects directory to arbitrary, user-readable files. The problem has been patched in versions 2.45.1, 2.44.1, 2.43.4, 2.42.2, 2.41.1, 2.40.2, and 2.39.4.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-32021
