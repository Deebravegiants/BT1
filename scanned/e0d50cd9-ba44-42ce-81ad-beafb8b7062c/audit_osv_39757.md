# [H] Kavita: Pre-Auth Account Takeover

## Summary
Severity: High
Advisory: CVE-2026-47202
Aliases: GHSA-m2v3-fcjh-hm22
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-47202
Type: osv

## Details
Kavita is a cross platform reading server. Prior to 0.9.0.2, an Improper Token validation flaw permits a remote and unauthenticated threat actor to request a JWT for any user including admins given knowledge of their username. This vulnerability is fixed in 0.9.0.2.

## References
- https://github.com/Kareadita/Kavita/releases/tag/v0.9.0.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/47xxx/CVE-2026-47202.json
- https://github.com/Kareadita/Kavita/security/advisories/GHSA-m2v3-fcjh-hm22
- https://nvd.nist.gov/vuln/detail/CVE-2026-47202
