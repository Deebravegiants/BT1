# [M] solidtime: Time entry update endpoint allows cross-organization modification of a known time-entry UUID

## Summary
Severity: Medium
Advisory: CVE-2026-42279
Aliases: GHSA-pmf9-pxq9-ccwr
CVSS: 5.8 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:H/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42279
Type: osv

## Details
solidtime is an open-source time-tracking app. In version 0.12.0, the PUT /api/v1/organizations/{organization}/time-entries/{timeEntry} API accepts a route-bound timeEntry from another organization when the caller has time-entries:update:all in the URL organization, allowing a known foreign time-entry UUID to be modified and rebound to objects in the caller's organization. This issue has been patched in version 0.12.1.

## References
- https://github.com/solidtime-io/solidtime/releases/tag/v0.12.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42279.json
- https://github.com/solidtime-io/solidtime/security/advisories/GHSA-pmf9-pxq9-ccwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-42279
- https://github.com/solidtime-io/solidtime/commit/b73aa543fdf5b61c37447307ab7277451296832c
