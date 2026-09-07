# [M] October Rain has Environment Variable Exfiltration via INI Parser Interpolation

## Summary
Severity: Medium
Advisory: GHSA-g6v3-wv4j-x9hg
CVE: CVE-2026-25125
CWE: CWE-200, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-g6v3-wv4j-x9hg
Type: github-advisory

## Affected
- Packagist: `october/rain` — affected >=4.0.0 <4.1.10
- Packagist: `october/rain` — affected >=0 <3.7.14

## Details
A server-side information disclosure vulnerability was identified in the INI settings parser. PHP's `parse_ini_string()` function supports `${}` syntax for environment variable interpolation. Attackers with Editor access could inject `${APP_KEY}`, `${DB_PASSWORD}`, or similar patterns into CMS page settings fields, causing sensitive environment variables to be resolved and stored in the template. These values were then returned to the attacker when the page was reopened.

### Impact
- Exfiltration of sensitive environment variables (APP_KEY, DB credentials, AWS keys, etc.)
- Could enable further attacks: database access, cookie forgery, AWS resource access
- Requires authenticated backend access with Editor permissions
- Only relevant when `cms.safe_mode` is enabled (otherwise direct PHP injection is already possible)

### Patches
The vulnerability has been patched in v3.7.14 and v4.1.10. All users are encouraged to upgrade to the latest patched version.

### Workarounds
If upgrading immediately is not possible:
- Restrict Editor tool access to fully trusted administrators only
- Ensure database and cloud service credentials are not accessible from the web server's network

### References
- Reported by Pentest-Tools.com

## References
- https://github.com/octobercms/october/security/advisories/GHSA-g6v3-wv4j-x9hg
- https://nvd.nist.gov/vuln/detail/CVE-2026-25125
- https://github.com/octobercms/october
