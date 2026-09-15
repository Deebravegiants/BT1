# [H] CVE-2017-6310

## Summary
Severity: High
Advisory: CVE-2017-6310
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2017-6310
Type: osv

## Details
An issue was discovered in tnef before 1.4.13. Four type confusions have been identified in the file_add_mapi_attrs() function. These might lead to invalid read and write operations, controlled by an attacker.

## References
- http://www.debian.org/security/2017/dsa-3798
- http://www.securityfocus.com/bid/96427
- https://security.gentoo.org/glsa/201708-02
- https://github.com/verdammelt/tnef/blob/master/ChangeLog
- https://github.com/verdammelt/tnef/commit/8dccf79857ceeb7a6d3e42c1e762e7b865d5344d
- https://www.x41-dsec.de/lab/advisories/x41-2017-004-tnef/
