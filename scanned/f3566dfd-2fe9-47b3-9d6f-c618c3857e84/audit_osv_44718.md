# [M] Trigger.dev before 4.5.2 Unauthorized Environment Access via Run Replay

## Summary
Severity: Medium
Advisory: CVE-2026-85651
Aliases: GHSA-qxpp-qjg8-x4jv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:H/SA:L)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85651
Type: osv

## Details
Trigger.dev versions before 4.5.2 fail to validate environment membership during run replay operations, allowing authenticated attackers to inject task runs into arbitrary environments. Attackers can replay their own runs into other organizations' or projects' environments to consume victim resources and pollute run history.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85651.json
- https://github.com/triggerdotdev/trigger.dev/releases/tag/v4.5.2
- https://github.com/triggerdotdev/trigger.dev/security/advisories/GHSA-qxpp-qjg8-x4jv
- https://nvd.nist.gov/vuln/detail/CVE-2026-85651
- https://www.vulncheck.com/advisories/trigger-dev-before-4.5.2-unauthorized-environment-access-via-run-replay
- https://github.com/triggerdotdev/trigger.dev/issues/4173
- https://github.com/triggerdotdev/trigger.dev/commit/34b1a181c2a1d33a53ebab88f84b05f81fea4254
- https://github.com/triggerdotdev/trigger.dev
