# [C] OpenCATS PHP Code Injection via installer AJAX endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-27760
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-27760
Type: osv

## Details
OpenCATS prior to commit 3002a29 contains a PHP code injection vulnerability in the installer AJAX endpoint that allows unauthenticated attackers to execute arbitrary code by injecting PHP statements into the databaseConnectivity action parameter. Attackers can break out of the define() string context in config.php using a single quote and statement separator to inject malicious PHP code that persists and executes on every subsequent page load when the installation wizard remains incomplete.

## References
- https://github.com/opencats/OpenCATS/blob/46e4727/lib/CATSUtility.php#L142-L172
- https://github.com/opencats/OpenCATS/blob/46e4727/modules/install/ajax/ui.php#L130
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27760.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27760
- https://www.vulncheck.com/advisories/opencats-php-code-injection-via-installer-ajax-endpoint
- https://github.com/opencats/OpenCATS/pull/706
- https://github.com/opencats/OpenCATS/commit/3002a29f4c3cada1aa2c4f3d4ae4e189906606b6
- https://github.com/opencats/OpenCATS
- https://chocapikk.com/posts/2026/opencats-installer-rce/
