# [M] CVE-2018-8099

## Summary
Severity: Medium
Advisory: CVE-2018-8099
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-14
Source: https://osv.dev/vulnerability/CVE-2018-8099
Type: osv

## Details
Incorrect returning of an error code in the index.c:read_entry() function leads to a double free in libgit2 before v0.26.2, which allows an attacker to cause a denial of service via a crafted repository index file.

## References
- https://lists.debian.org/debian-lts-announce/2022/03/msg00031.html
- https://github.com/libgit2/libgit2/commit/58a6fe94cb851f71214dbefac3f9bffee437d6fe
- https://libgit2.github.com/security/
