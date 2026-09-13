# [C] n8n has XML Node Prototype Pollution that to RCE

## Summary
Severity: Critical
Advisory: GHSA-hqr4-h3xv-9m3r
CVE: CVE-2026-42232
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-hqr4-h3xv-9m3r
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.17.0 <2.17.4
- npm: `n8n` — affected >=0 <1.123.32

## Details
## Impact
An authenticated user with permission to create or modify workflows could achieve global prototype pollution via the XML Node leading to RCE when combined with other nodes exploiting the prototype pollution.

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the XML node by adding `n8n-nodes-base.xml` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-hqr4-h3xv-9m3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-42232
- https://github.com/n8n-io/n8n
