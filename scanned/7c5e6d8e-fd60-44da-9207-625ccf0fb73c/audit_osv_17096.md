# [C] CVE-2020-12279

## Summary
Severity: Critical
Advisory: CVE-2020-12279
Aliases: GHSA-589j-mmg9-733v
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-27
Source: https://osv.dev/vulnerability/CVE-2020-12279
Type: osv

## Details
An issue was discovered in libgit2 before 0.28.4 and 0.9x before 0.99.0. checkout.c mishandles equivalent filenames that exist because of NTFS short names. This may allow remote code execution when cloning a repository. This issue is similar to CVE-2019-1353.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00034.html
- https://github.com/libgit2/libgit2/releases/tag/v0.28.4
- https://github.com/libgit2/libgit2/releases/tag/v0.99.0
- https://lists.debian.org/debian-lts-announce/2022/03/msg00031.html
- https://github.com/git/git/security/advisories/GHSA-589j-mmg9-733v
- https://github.com/libgit2/libgit2/commit/64c612cc3e25eff5fb02c59ef5a66ba7a14751e4
