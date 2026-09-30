# [C] OpenClaw < 2026.5.7 - Privilege Escalation via Mutable Display Names in Matrix allowFrom

## Summary
Severity: Critical
Advisory: CVE-2026-53811
Aliases: GHSA-7hxm-f538-3xp6
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-53811
Type: osv

## Details
OpenClaw before 2026.5.7 contains a privilege escalation vulnerability in the Matrix allowFrom feature that allows authenticated accounts to match policy entries through mutable display name metadata. Attackers with the ability to change display names can receive agent access intended for another Matrix identity, potentially gaining unauthorized permissions depending on operator configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53811.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7hxm-f538-3xp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-53811
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-mutable-display-names-in-matrix-allowfrom
- https://github.com/openclaw/openclaw
