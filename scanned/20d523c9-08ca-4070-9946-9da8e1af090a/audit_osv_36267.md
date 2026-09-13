# [C] Windmill < 1.615.0 Operator Role Missing Authorization Checks RCE

## Summary
Severity: Critical
Advisory: CVE-2026-22683
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/CVE-2026-22683
Type: osv

## Details
Windmill versions 1.56.0 through 1.614.0 contain a missing authorization vulnerability that allows users with the Operator role to perform prohibited entity creation and modification actions via the backend API. Although Operators are documented and priced as unable to create or modify entities, the API does not enforce the Operator restriction on workspace endpoints, allowing an Operator to create and update scripts, flows, apps, and raw_apps. Since Operators can also execute scripts via the jobs API, this allows direct privilege escalation to remote code execution within the Windmill deployment. This vulnerability has existed since the introduction of the Operator role in version 1.56.0.

## References
- https://www.windmill.dev/
- https://apps.nextcloud.com/apps/flow/releases
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22683.json
- https://github.com/windmill-labs/windmill/releases/tag/v1.615.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-22683
- https://github.com/windmill-labs/windmill/commit/c621a74804f4f6e8318819c01e3a23a17698588b
- https://chocapikk.com/posts/2026/windfall-nextcloud-flow-windmill-rce/
- https://github.com/Chocapikk/Windfall
