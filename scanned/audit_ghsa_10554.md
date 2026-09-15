# [M] Focalboard doesn't validate file ownership when serving uploaded files

## Summary
Severity: Medium
Advisory: GHSA-vph7-r229-qxpf
CVE: CVE-2026-28736
CWE: CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-vph7-r229-qxpf
Type: github-advisory

## Affected
- Go: `github.com/mattermost/focalboard` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** Focalboard version 8.0 fails to validate file ownership when serving uploaded files. This allows an authenticated attacker who knows a victim's fileID to read the content of the file. NOTE: Focalboard as a standalone product is not maintained and no fix will be issued.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-28736
- https://github.com/mattermost-community/focalboard
