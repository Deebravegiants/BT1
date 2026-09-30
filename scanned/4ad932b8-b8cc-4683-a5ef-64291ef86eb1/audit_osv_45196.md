# [M] libgit2 is a cross-platform, linkable library implementation of Git

## Summary
Severity: Medium
Advisory: JLSEC-2025-184
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-10-21
Source: https://osv.dev/vulnerability/JLSEC-2025-184
Type: osv

## Affected
- Julia: `LibGit2_jll` — affected >=0 <1.6.1+0

## Details
libgit2 is a cross-platform, linkable library implementation of Git. When using an SSH remote with the optional libssh2 backend, libgit2 does not perform certificate checking by default. Prior versions of libgit2 require the caller to set the `certificate_check` field of libgit2's `git_remote_callbacks` structure - if a certificate check callback is not set, libgit2 does not perform any certificate checking. This means that by default - without configuring a certificate check callback, clients will not perform validation on the server SSH keys and may be subject to a man-in-the-middle attack. Users are encouraged to upgrade to v1.4.5 or v1.5.1. Users unable to upgrade should ensure that all relevant certificates are manually checked.

## References
- http://www.openwall.com/lists/oss-security/2023/11/06/5
- https://github.com/libgit2/libgit2/commit/42e5db98b963ae503229c63e44e06e439df50e56
- https://github.com/libgit2/libgit2/commit/cd6f679af401eda1f172402006ef8265f8bd58ea
- https://github.com/libgit2/libgit2/releases/tag/v1.4.5
- https://github.com/libgit2/libgit2/releases/tag/v1.5.1
- https://github.com/libgit2/libgit2/security/advisories/GHSA-8643-3wh5-rmjq
- https://www.libssh2.org
