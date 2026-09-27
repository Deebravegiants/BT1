# [H] Chartbrew: Incorrect Access Control in dataset and dataRequest routes via team-scoped permission checks

## Summary
Severity: High
Advisory: CVE-2026-40904
Aliases: GHSA-jq95-gqww-vhm3
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-40904
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. In version 4.9.0, Chartbrew exposes multiple dataset and dataRequest endpoints that authorize low-privileged project members at the team level instead of binding the requested dataset_id, dataRequest id, and connection_id to the caller's allowed projects. An authenticated attacker who only has access to one project inside a team can read, execute, create, update, and delete datasets and data requests that belong to other projects in the same team. The issue is exploitable remotely with ordinary project-level credentials and leads to cross-project data disclosure and unauthorized use of victim-side database or API connections. This issue has been patched in version 5.0.0.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40904.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-jq95-gqww-vhm3
- https://nvd.nist.gov/vuln/detail/CVE-2026-40904
