# [C] AppFlowy-Cloud 0.9.64 Cross-Workspace Collab Access via HTTP API

## Summary
Severity: Critical
Advisory: CVE-2026-85619
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85619
Type: osv

## Details
AppFlowy-Cloud 0.9.64 fails to verify that requested collab objects belong to the workspace in authorization checks, allowing attackers to access documents and database rows across workspaces. Attackers can supply a victim's object ID with their own workspace ID to bypass access controls and read, modify, or delete cross-workspace data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85619.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85619
- https://www.vulncheck.com/advisories/appflowy-cloud-0.9.64-cross-workspace-collab-access-via-http-api
- https://github.com/AppFlowy-IO/AppFlowy-Cloud/issues/1624
- https://github.com/AppFlowy-IO/AppFlowy-Cloud
- https://github.com/AppFlowy-IO/AppFlowy-Cloud/blob/0.9.64/libs/access-control/src/casbin/collab.rs
