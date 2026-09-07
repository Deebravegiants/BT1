# [M] Joomla Framework Database Package Vulnerable to SQL Injection

## Summary
Severity: Medium
Advisory: GHSA-44v2-prcf-pc3m
CVE: CVE-2025-25226
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-44v2-prcf-pc3m
Type: github-advisory

## Affected
- Packagist: `joomla/database` — affected >=3.0.0 <3.4.0
- Packagist: `joomla/database` — affected >=1.0.0 <2.2.0

## Details
Improper handling of identifiers lead to a SQL injection vulnerability in the quoteNameStr method of the database package. Please note: the affected method is a protected method. It has no usages in the original packages in neither the 2.x nor 3.x branch and therefore the vulnerability in question can not be exploited when using the original database class. However, classes extending the affected class might be affected, if the vulnerable method is used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25226
- https://developer.joomla.org/security-centre/963-20250401-framework-sql-injection-vulnerability-in-quotenamestr-method-of-database-package.html
- https://github.com/joomla-framework/database
