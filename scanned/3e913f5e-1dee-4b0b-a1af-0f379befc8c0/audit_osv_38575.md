# [M] Chartbrew: Incorrect Access Control in /api/project/dashboard/:brewName via same-team override

## Summary
Severity: Medium
Advisory: CVE-2026-40603
Aliases: GHSA-6qr3-g75h-xm3f
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-40603
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. In version 4.9.0, Chartbrew exposes a legacy dashboard route that returns a project's report data to any authenticated member of the same team, even when that user does not have access to the specific project. The route bypasses project-level authorization and returns the raw project object. As a result, a low-privileged same-team user can read another project's dashboard data and recover the project's stored report password from the response. This issue has been patched in version 5.0.0.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v5.0.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40603.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-6qr3-g75h-xm3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-40603
