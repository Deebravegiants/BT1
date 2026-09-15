# [M] OpenClaw < 2026.2.26 - Improper Authorization via DM Pairing Store Identity Inheritance in Group Allowlist

## Summary
Severity: Medium
Advisory: CVE-2026-32027
Aliases: GHSA-jv6r-27ww-4gw4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-32027
Type: osv

## Details
OpenClaw versions prior to 2026.2.26 contain an authorization bypass vulnerability where DM pairing-store identities are incorrectly eligible for group allowlist authorization checks. Attackers can exploit this cross-context authorization flaw by using a sender approved via DM pairing to satisfy group sender allowlist checks without explicit presence in groupAllowFrom, bypassing group message access controls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32027.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jv6r-27ww-4gw4
- https://nvd.nist.gov/vuln/detail/CVE-2026-32027
- https://www.vulncheck.com/advisories/openclaw-improper-authorization-via-dm-pairing-store-identity-inheritance-in-group-allowlist
- https://github.com/openclaw/openclaw/commit/051fdcc428129446e7c084260f837b7284279ce9
- https://github.com/openclaw/openclaw/commit/8bdda7a651c21e98faccdbbd73081e79cffe8be0
