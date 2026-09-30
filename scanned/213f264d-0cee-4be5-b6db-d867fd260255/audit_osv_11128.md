# [H] CVE-2017-6308

## Summary
Severity: High
Advisory: CVE-2017-6308
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2017-6308
Type: osv

## Details
An issue was discovered in tnef before 1.4.13. Several Integer Overflows, which can lead to Heap Overflows, have been identified in the functions that wrap memory allocation.

## References
- http://www.debian.org/security/2017/dsa-3798
- http://www.securityfocus.com/bid/96427
- https://security.gentoo.org/glsa/201708-02
- https://github.com/verdammelt/tnef/blob/master/ChangeLog
- https://github.com/verdammelt/tnef/commit/c5044689e50039635e7700fe2472fd632ac77176
- https://www.x41-dsec.de/lab/advisories/x41-2017-004-tnef/
