# [C] n8n Has an XML Node Prototype Pollution Patch Bypass

## Summary
Severity: Critical
Advisory: GHSA-wrwr-h859-xh2r
CVE: CVE-2026-44791
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-wrwr-h859-xh2r
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.43
- npm: `n8n` — affected >=2.21.0 <2.22.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.20.7

## Details
## Impact
An authenticated user with permission to create or modify workflows could bypass the patch for GHSA-hqr4-h3xv-9m3r in the XML node. When combined with other nodes, this could lead to RCE on the n8n host.

## Patches
The issue has been fixed in n8n versions 1.123.43, 2.20.7, and 2.22.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the XML node by adding `n8n-nodes-base.xml` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backwards compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-wrwr-h859-xh2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44791
- https://github.com/advisories/GHSA-hqr4-h3xv-9m3r
- https://github.com/n8n-io/n8n
