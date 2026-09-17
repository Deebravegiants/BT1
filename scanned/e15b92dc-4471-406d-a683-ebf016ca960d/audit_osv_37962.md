# [H] Coolify: Cross-team IDOR in logs component (resource lookup not team-scoped)

## Summary
Severity: High
Advisory: CVE-2026-34044
Aliases: GHSA-565g-9j4m-wqmr
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34044
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.466, the Logs::mount() component looks up resources by UUID without scoping the lookup to the current team, allowing an authenticated user to access logs for applications owned by other teams by supplying a victim resource UUID. This issue is fixed in version 4.0.0-beta.466.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.466
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34044.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-565g-9j4m-wqmr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34044
- https://github.com/coollabsio/coolify/commit/6fbb5e626a82c576ae7a1a08b4e1d16aee2e82ed
