# [C] FOSSBilling vulnerable to arbitrary PHP code injection via unescaped config serialization

## Summary
Severity: Critical
Advisory: CVE-2026-43921
Aliases: GHSA-v4j9-w6pj-38w5
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-43921
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Versions 0.6.10 through 0.7.2 have a PHP code injection vulnerability in FOSSBilling's `Config::prettyPrintArrayToPHP()` method. When configuration values are updated, string values are written into `config.php` without escaping single quotes. Because `config.php` is loaded via a bare `include` on every HTTP request, an attacker with admin privileges can inject arbitrary PHP code that executes on every subsequent request. Version 0.8.0 contains a patch. Some workarounds are available. Restrict admin access to trusted personnel only; audit `config.php` for unexpected PHP code; and/ or at the reverse proxy/WAF level, restrict access to admin API endpoints that modify configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43921.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-v4j9-w6pj-38w5
- https://nvd.nist.gov/vuln/detail/CVE-2026-43921
