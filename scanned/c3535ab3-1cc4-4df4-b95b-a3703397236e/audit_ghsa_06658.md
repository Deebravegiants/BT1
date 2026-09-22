# [M] n8n: Improper Authorization Allows Authenticated Users to Assign Workflows to Folders in Other Projects

## Summary
Severity: Medium
Advisory: GHSA-2xgm-wc4g-5jvg
CVE: CVE-2026-59253
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-2xgm-wc4g-5jvg
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.28.0

## Details
## Impact
An authenticated user with permission to create workflows in one project could bypass project/folder authorization boundaries during workflow creation. By supplying a crafted request payload, the user could associate a newly created workflow with a folder belonging to a different project they do not have access to.

The workflow itself remains in the attacker's project and is not visible to the target project's members. The target project's folder ownership is not changed, and no data from the target project is exposed. The impact is limited to a logical integrity violation of the target project's folder structure at the database level.

This issue affects instances with multi-project and folder support enabled.

## Patches
The issue has been fixed in n8n version 2.28.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict project membership and workflow creation permissions to fully trusted users only.

This workaround does not fully remediate the risk and should only be used as a short-term mitigation measure.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-2xgm-wc4g-5jvg
- https://nvd.nist.gov/vuln/detail/CVE-2026-59253
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.28.0
- https://www.vulncheck.com/advisories/n8n-improper-authorization-in-workflow-assignment-to-folders
