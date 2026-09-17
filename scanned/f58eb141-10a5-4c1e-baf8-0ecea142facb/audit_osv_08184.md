# [M] CVE-2016-1284

## Summary
Severity: Medium
Advisory: CVE-2016-1284
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-02-04
Source: https://osv.dev/vulnerability/CVE-2016-1284
Type: osv

## Details
rdataset.c in ISC BIND 9 Supported Preview Edition 9.9.8-S before 9.9.8-S5, when nxdomain-redirect is enabled, allows remote attackers to cause a denial of service (REQUIRE assertion failure and daemon exit) via crafted flag values in a query.

## References
- http://www.securitytracker.com/id/1034935
- https://kb.isc.org/article/AA-01348
- https://kb.isc.org/article/AA-01438
