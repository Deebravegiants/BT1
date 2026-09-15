# [H] CVE-2019-13464

## Summary
Severity: High
Advisory: CVE-2019-13464
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-07-09
Source: https://osv.dev/vulnerability/CVE-2019-13464
Type: osv

## Details
An issue was discovered in OWASP ModSecurity Core Rule Set (CRS) 3.0.2. Use of X.Filename instead of X_Filename can bypass some PHP Script Uploads rules, because PHP automatically transforms dots into underscores in certain contexts where dots are invalid.

## References
- https://github.com/SpiderLabs/owasp-modsecurity-crs/pull/1391
- https://github.com/SpiderLabs/owasp-modsecurity-crs/issues/1386
