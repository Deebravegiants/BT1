# [C] ntfy.sh allows a remote attacker to execute arbitrary code via the parseActions function

## Summary
Severity: Critical
Advisory: GHSA-pqhx-w72w-m393
CVE: CVE-2026-39087
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-pqhx-w72w-m393
Type: github-advisory

## Affected
- Go: `heckel.io/ntfy/v2` — affected >=0 <2.22.0

## Details
An issue in Ntfy ntfy.sh before v.2.22.0 allows a remote attacker to execute arbitrary code via the parseActions function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39087
- https://gist.github.com/MightyNawaf/5d41d6e8ead16e217f86b016002ecae5
- https://github.com/binwiederhier/ntfy
- https://github.com/binwiederhier/ntfy/releases/tag/v2.22.0
- http://ntfy.com
- http://ntfysh.com
