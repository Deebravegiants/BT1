# [M] LibreNMS is vulnerable to Reflected-XSS in `report_this` function

## Summary
Severity: Medium
Advisory: GHSA-86rg-8hc8-v82p
CVE: CVE-2025-62365
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N/E:P (CVSS_V4)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-86rg-8hc8-v82p
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <25.7.0

## Details
### Summary
Reflected-XSS in `report_this` function in `librenms/includes/functions.php`

### Details
Recently, it was discovered that  the `report_this` function had improper filtering (`htmlentities` function was incorrectly used in a href environment), which caused the `project_issues` parameter to trigger an XSS vulnerability.

The Vulnerable Sink:
https://github.com/librenms/librenms/blob/master/includes/functions.php#L444

### PoC
GET
`project_issues=javascript:alert(document.cookie)`

### Impact
XSS vulnerabilities allow attackers to execute malicious scripts in users' browsers, enabling unauthorized access to sensitive data, session hijacking, or malware distribution.

### Suggestion
It is recommended to filter dangerous protocols, e.g. `javascript:`/`file:`.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-86rg-8hc8-v82p
- https://nvd.nist.gov/vuln/detail/CVE-2025-62365
- https://github.com/librenms/librenms/commit/30d3dd7e5f5e22a8c23c9db3ad90a731c005b008
- https://github.com/librenms/librenms
