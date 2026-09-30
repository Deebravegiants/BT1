# [C] CVE-2020-12278

## Summary
Severity: Critical
Advisory: CVE-2020-12278
Aliases: GHSA-5wph-8frv-58vj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-27
Source: https://osv.dev/vulnerability/CVE-2020-12278
Type: osv

## Details
An issue was discovered in libgit2 before 0.28.4 and 0.9x before 0.99.0. path.c mishandles equivalent filenames that exist because of NTFS Alternate Data Streams. This may allow remote code execution when cloning a repository. This issue is similar to CVE-2019-1352.

## References
- https://lists.debian.org/debian-lts-announce/2023/02/msg00034.html
- https://github.com/git/git/security/advisories/GHSA-5wph-8frv-58vj
- https://github.com/libgit2/libgit2/releases/tag/v0.28.4
- https://github.com/libgit2/libgit2/releases/tag/v0.99.0
- https://lists.debian.org/debian-lts-announce/2022/03/msg00031.html
- https://github.com/libgit2/libgit2/commit/3f7851eadca36a99627ad78cbe56a40d3776ed01
- https://github.com/libgit2/libgit2/commit/e1832eb20a7089f6383cfce474f213157f5300cb
