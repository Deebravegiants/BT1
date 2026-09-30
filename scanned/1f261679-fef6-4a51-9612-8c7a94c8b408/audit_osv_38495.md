# [C] Masa CMS SQL injection via sortDirection parameter in beanFeed

## Summary
Severity: Critical
Advisory: CVE-2026-40330
Aliases: GHSA-56cc-gxfr-hqp8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-40330
Type: osv

## Details
Masa CMS is an open source content management system. In versions 7.2.0 through 7.2.9, 7.3.0 through 7.3.14, 7.4.0 through 7.4.9, and 7.5.0 through 7.5.2, a SQL injection vulnerability exists in the beanFeed.cfc component within the getQuery function's handling of the sortDirection parameter. The parameter value is concatenated directly into SQL queries without sanitization or parameterization. An unauthenticated remote attacker can exploit this to extract sensitive information, modify or delete database records, or potentially achieve remote code execution on the underlying database server.

This issue has been fixed in versions 7.2.10, 7.3.15, 7.4.10, and 7.5.3. As a workaround, use a WAF to block or restrict access to the beanFeed.cfc component, or deploy rules to detect SQL injection patterns targeting the sortDirection parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40330.json
- https://github.com/MasaCMS/MasaCMS/security/advisories/GHSA-56cc-gxfr-hqp8
- https://nvd.nist.gov/vuln/detail/CVE-2026-40330
