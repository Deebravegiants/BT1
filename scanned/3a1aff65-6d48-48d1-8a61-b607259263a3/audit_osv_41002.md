# [H] 9Router: Mass assignment in PATCH /api/settings allows authenticated authorization downgrade

## Summary
Severity: High
Advisory: CVE-2026-56679
Aliases: GHSA-vmjq-hvgq-2wv4
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-56679
Type: osv

## Details
9Router is an AI router & token saver. Prior to 0.5.4, the PATCH /api/settings endpoint writes the entire request body to persistent settings without a field whitelist, allowing an authenticated user to set security-critical fields such as requireLogin and disable authentication for the whole application, exposing protected routes such as /api/keys and /api/providers to unauthenticated access. This issue is reported as fixed in version 0.5.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56679.json
- https://github.com/decolua/9router/security/advisories/GHSA-vmjq-hvgq-2wv4
- https://nvd.nist.gov/vuln/detail/CVE-2026-56679
