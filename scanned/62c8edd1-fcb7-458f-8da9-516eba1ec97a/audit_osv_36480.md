# [M] Whisper Money has IDOR Vulnerability on sync/balances endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-23844
Aliases: GHSA-c4g3-wpxr-2m74
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23844
Type: osv

## Details
Whisper Money is a personal finance application. Versions prior to 0.1.5 have an insecure direct object reference vulnerability. A user can update/create account balances in other users' bank accounts. Version 0.1.5 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23844.json
- https://github.com/whisper-money/whisper-money/security/advisories/GHSA-c4g3-wpxr-2m74
- https://nvd.nist.gov/vuln/detail/CVE-2026-23844
- https://github.com/whisper-money/whisper-money/commit/80117c3edeaf5c5a5166f3815fc555a15b5ce686
- https://github.com/whisper-money/whisper-money/pull/60
