# [H] CVE-2017-6307

## Summary
Severity: High
Advisory: CVE-2017-6307
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2017-6307
Type: osv

## Details
An issue was discovered in tnef before 1.4.13. Two OOB Writes have been identified in src/mapi_attr.c:mapi_attr_read(). These might lead to invalid read and write operations, controlled by an attacker.

## References
- http://www.debian.org/security/2017/dsa-3798
- http://www.securityfocus.com/bid/96427
- https://security.gentoo.org/glsa/201708-02
- https://github.com/verdammelt/tnef/blob/master/ChangeLog
- https://github.com/verdammelt/tnef/commit/1a17af1ed0c791aec44dbdc9eab91218cc1e335a
- https://www.x41-dsec.de/lab/advisories/x41-2017-004-tnef/
