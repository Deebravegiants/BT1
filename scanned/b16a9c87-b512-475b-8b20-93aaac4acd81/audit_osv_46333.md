# [C] CVE-1999-0199

## Summary
Severity: Critical
Advisory: CVE-1999-0199
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/CVE-1999-0199
Type: osv

## Details
manual/search.texi in the GNU C Library (aka glibc) before 2.2 lacks a statement about the unspecified tdelete return value upon deletion of a tree's root, which might allow attackers to access a dangling pointer in an application whose developer was unaware of a documentation update from 1999.

## References
- https://ftp.gnu.org/gnu/glibc/glibc-2.2.tar.gz
- https://github.com/bminor/glibc/commit/2864e767053317538feafa815046fff89e5a16be#diff-94e8c502f255fdfc346df0e29fd4ef40
- https://www.cee.studio/tdelete.html
- https://www.cee.studio/tdelete.html
- https://github.com/bminor/glibc/commit/2864e767053317538feafa815046fff89e5a16be#diff-94e8c502f255fdfc346df0e29fd4ef40
- https://ftp.gnu.org/gnu/glibc/glibc-2.2.tar.gz
