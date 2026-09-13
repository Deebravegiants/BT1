# [M] CVE-2019-11387

## Summary
Severity: Medium
Advisory: CVE-2019-11387
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2019-04-21
Source: https://osv.dev/vulnerability/CVE-2019-11387
Type: osv

## Details
An issue was discovered in OWASP ModSecurity Core Rule Set (CRS) through 3.1.0. /rules/REQUEST-942-APPLICATION-ATTACK-SQLI.conf allows remote attackers to cause a denial of service (ReDOS) by entering a specially crafted string with nested repetition operators.

## References
- https://coreruleset.org/20190627/announcement-owasp-modsecurity-core-rule-set-version-3-1-1/
- https://github.com/SpiderLabs/owasp-modsecurity-crs/blob/v3.1/dev/CHANGES
- https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/1359
