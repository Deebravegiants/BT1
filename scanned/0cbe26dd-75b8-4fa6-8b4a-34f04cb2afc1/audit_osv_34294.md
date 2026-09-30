# [C] eslint-ban-moment exposed a sensitive Supabase URI in .env (Credential leak)

## Summary
Severity: Critical
Advisory: CVE-2025-57754
Aliases: GHSA-2486-4cjg-pw98
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-21
Source: https://osv.dev/vulnerability/CVE-2025-57754
Type: osv

## Details
eslint-ban-moment is an Eslint plugin for final assignment in VIHU. In 3.0.0 and earlier, a sensitive Supabase URI is exposed in .env. A valid Supabase URI with embedded username and password will allow an attacker complete unauthorized access and control over database and user data. This could lead to data exfiltration, modification or deletion.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57754.json
- https://github.com/kristoferfannar/eslint-ban-moment/security/advisories/GHSA-2486-4cjg-pw98
- https://nvd.nist.gov/vuln/detail/CVE-2025-57754
- https://github.com/kristoferfannar/eslint-ban-moment/commit/bc2d2f9d23e6ae961a23e0d769e0722870b11108
