# [H] Focalboard doesn't sanitize category IDs before incorporating them into dynamic SQL statements

## Summary
Severity: High
Advisory: GHSA-p32q-v29x-wq9r
CVE: CVE-2026-25773
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-p32q-v29x-wq9r
Type: github-advisory

## Affected
- Go: `github.com/mattermost/focalboard` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** Focalboard version 8.0 fails to sanitize category IDs before incorporating them into dynamic SQL statements when reordering categories. An attacker can inject a malicious SQL payload into the category id field, which is stored in the database and later executed unsanitized when the category reorder API processes the stored value. This Second-Order SQL Injection (Time-Based Blind) allows an authenticated attacker to exfiltrate sensitive data including password hashes of other users. NOTE: Focalboard as a standalone product is not maintained and no fix will be issued.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25773
- https://github.com/mattermost-community/focalboard
