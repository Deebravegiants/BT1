# [M] CVE-2019-11389

## Summary
Severity: Medium
Advisory: CVE-2019-11389
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-04-21
Source: https://osv.dev/vulnerability/CVE-2019-11389
Type: osv

## Details
An issue was discovered in OWASP ModSecurity Core Rule Set (CRS) through 3.1.0. /rules/REQUEST-933-APPLICATION-ATTACK-PHP.conf allows remote attackers to cause a denial of service (ReDOS) by entering a specially crafted string with next# at the beginning and nested repetition operators. NOTE: the software maintainer disputes that this is a vulnerability because the issue cannot be exploited via ModSecurity

## References
- https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/1356
- https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/1372
