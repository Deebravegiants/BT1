# [H] CVE-2018-16384

## Summary
Severity: High
Advisory: CVE-2018-16384
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-09-03
Source: https://osv.dev/vulnerability/CVE-2018-16384
Type: osv

## Details
A SQL injection bypass (aka PL1 bypass) exists in OWASP ModSecurity Core Rule Set (owasp-modsecurity-crs) through v3.1.0-rc3 via {`a`b} where a is a special function name (such as "if") and b is the SQL statement to be executed.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00033.html
- https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/1167
