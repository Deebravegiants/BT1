# [M] Mythic < 3.4.0.60 - Broken Permission Filter in payload_build_step Table

## Summary
Severity: Medium
Advisory: CVE-2026-57951
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-57951
Type: osv

## Details
Mythic before 3.4.0.60 contains a broken hasura permission filter on the payload_build_step table with an always-satisfied _or condition that bypasses operation-scoped access controls. Authenticated operators and spectators can query payload_build_step to read step_stdout, step_stderr, step_name, and step_description across all operations on the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57951.json
- https://github.com/its-a-feature/Mythic/releases/tag/v3.4.0.60
- https://nvd.nist.gov/vuln/detail/CVE-2026-57951
- https://www.vulncheck.com/advisories/mythic-broken-permission-filter-in-payload-build-step-table
- https://github.com/its-a-feature/Mythic/issues/563
- https://github.com/its-a-feature/Mythic/commit/82648e8241b800a32e1882afc310e7316d98ebaa
- https://github.com/its-a-feature/Mythic
- ttps://github.com/its-a-feature/Mythic/issues/563
