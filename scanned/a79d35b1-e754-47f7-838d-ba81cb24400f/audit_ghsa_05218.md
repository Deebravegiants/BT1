# [H] n8n: Microsoft SQL Node Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-x6p3-m6h9-fx7r
CVE: CVE-2026-54312
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-x6p3-m6h9-fx7r
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.24.0

## Details
## Impact
An authenticated user with permission to create or modify workflows could achieve global prototype pollution via the Microsoft SQL node by supplying a crafted value as the table parameter. This pollutes `Object.prototype` process-wide for the lifetime of the n8n server process, causing application-wide validation failures and rendering the n8n instance completely non-functional until restarted.

## Patches
The issue has been fixed in n8n version 2.24.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Microsoft SQL node by adding `n8n-nodes-base.microsoftSql` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-x6p3-m6h9-fx7r
- https://nvd.nist.gov/vuln/detail/CVE-2026-54312
- https://github.com/n8n-io/n8n
