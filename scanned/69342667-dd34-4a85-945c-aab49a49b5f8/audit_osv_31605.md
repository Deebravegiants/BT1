# [C] CVE-2025-15586

## Summary
Severity: Critical
Advisory: CVE-2025-15586
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-02-19
Source: https://osv.dev/vulnerability/CVE-2025-15586
Type: osv

## Details
OGP-Website installs prior git commit 52f865a4fba763594453068acf8fa9e3fc38d663 are affected by a type juggling flaw which if exploited can result in authentication bypass without knowledge of the victim account's password.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15586.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15586
- https://github.com/OpenGamePanel/OGP-Website/commit/52f865a4fba763594453068acf8fa9e3fc38d663
- https://github.com/OpenGamePanel/OGP-Website/pull/644
- https://github.com/OpenGamePanel/OGP-Website
- https://projectblack.io/blog/vibe-hacking-open-game-panel-rce/#vul-01-type-juggling-authentication-bypass
