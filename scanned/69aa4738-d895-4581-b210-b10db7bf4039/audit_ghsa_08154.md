# [C] n8n has Potential Remote Code Execution via Merge Node

## Summary
Severity: Critical
Advisory: GHSA-wxx7-mcgf-j869
CVE: CVE-2026-27497
CWE: CWE-89, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-wxx7-mcgf-j869
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.22
- npm: `n8n` — affected >=2.0.0 <2.9.3
- npm: `n8n` — affected >=2.10.0 <2.10.1

## Details
## Impact
An authenticated user with permission to create or modify workflows could leverage the Merge node's SQL query mode to execute arbitrary code and write arbitrary files on the n8n server.

## Patches
The issues have been fixed in n8n versions 2.10.1, 2.9.3, and 1.123.22. Users should upgrade to one of these versions or later to remediate all known vulnerabilities.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the Merge node by adding `n8n-nodes-base.merge` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-wxx7-mcgf-j869
- https://nvd.nist.gov/vuln/detail/CVE-2026-27497
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.22
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.10.1
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.9.3
