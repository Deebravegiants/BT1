# [H] CakePHP: FunctionsBuilder::jsonValue() vulerable to SQL injection with PostgresDriver

## Summary
Severity: High
Advisory: CVE-2026-77635
Aliases: GHSA-fxf7-vhh8-7vpq
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-77635
Type: osv

## Details
CakePHP is a rapid development framework for PHP. Prior to versions 5.1.10, 5.2.15, and 5.3.7 on their respective release lines, FunctionsBuilder::jsonValue() with PostgresDriver is vulnerable to SQL injection when user-controlled data is supplied to the jsonPath parameter. This issue is fixed in versions 5.1.10, 5.2.15, and 5.3.7.

## References
- https://github.com/cakephp/cakephp/releases/tag/5.1.10
- https://github.com/cakephp/cakephp/releases/tag/5.2.15
- https://github.com/cakephp/cakephp/releases/tag/5.3.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77635.json
- https://github.com/cakephp/cakephp/security/advisories/GHSA-fxf7-vhh8-7vpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-77635
- https://github.com/cakephp/cakephp/commit/138f2f61486532c29ee4d106da2a9848c1ff1ab3
- https://github.com/cakephp/cakephp/commit/489a40fb7c6e597af33fe0f7264047afccb90d55
- https://github.com/cakephp/cakephp/commit/9f1ad970a3b72293d4a37e694276645f804e819f
