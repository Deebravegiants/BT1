# [M] CVE-2016-10713

## Summary
Severity: Medium
Advisory: CVE-2016-10713
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-13
Source: https://osv.dev/vulnerability/CVE-2016-10713
Type: osv

## Details
An issue was discovered in GNU patch before 2.7.6. Out-of-bounds access within pch_write_line() in pch.c can possibly lead to DoS via a crafted input file.

## References
- https://usn.ubuntu.com/3624-1/
- https://usn.ubuntu.com/3624-2/
- http://www.securityfocus.com/bid/103063
- https://access.redhat.com/errata/RHSA-2019:2033
- https://git.savannah.gnu.org/cgit/patch.git/commit/src/pch.c?id=a0d7fe4589651c64bd16ddaaa634030bb0455866
