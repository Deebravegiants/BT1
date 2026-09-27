# [M] AppFlowy-Cloud 0.7.2 through 0.9.64 Missing Workspace Authorization on Bulk Publish Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-88898
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88898
Type: osv

## Details
AppFlowy-Cloud versions 0.7.2 through 0.9.64 fail to authorize callers against the workspace in the bulk publish endpoint path, allowing authenticated users to publish content into other tenants' namespaces. Attackers can write published views with attacker-controlled title, body and metadata into victim workspaces to deface public pages or host phishing content on trusted URLs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88898.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-88898
- https://www.vulncheck.com/advisories/appflowy-cloud-0.7.2-through-0.9.64-missing-workspace-authorization-on-bulk-publish-endpoint
- https://github.com/AppFlowy-IO/AppFlowy-Cloud
- https://github.com/AppFlowy-IO/AppFlowy-Cloud/blob/0.9.64/src/api/workspace.rs
- https://github.com/AppFlowy-IO/AppFlowy-Cloud/blob/0.9.64/src/biz/workspace/publish.rs
- https://gist.github.com/mtholmquist/ab550712a4628c7c7c4705bceccd93b3
