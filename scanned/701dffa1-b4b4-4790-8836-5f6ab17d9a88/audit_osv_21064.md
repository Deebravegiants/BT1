# [H] CVE-2021-40330

## Summary
Severity: High
Advisory: CVE-2021-40330
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-31
Source: https://osv.dev/vulnerability/CVE-2021-40330
Type: osv

## Details
git_connect_git in connect.c in Git before 2.30.1 allows a repository path to contain a newline character, which may result in unexpected cross-protocol requests, as demonstrated by the git://localhost:1234/%0d%0a%0d%0aGET%20/%20HTTP/1.1 substring.

## References
- https://lists.debian.org/debian-lts-announce/2022/10/msg00014.html
- https://github.com/git/git/commit/a02ea577174ab8ed18f847cf1693f213e0b9c473
- https://github.com/git/git/compare/v2.30.0...v2.30.1
