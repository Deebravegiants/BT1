# [M] n8n: Prototype Pollution enables confused-deputy execution via public webhooks

## Summary
Severity: Medium
Advisory: GHSA-2vff-hj5x-8gq7
CVE: CVE-2026-54306
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-2vff-hj5x-8gq7
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=0 <2.25.7

## Details
## Impact
A prototype pollution vulnerability allowed a crafted public webhook payload to inject attacker-controlled fields into workflow data during internal object copying. These fields could be surfaced and consumed as normal values by downstream built-in nodes.

Where a workflow combines a public webhook with action nodes that consume the resulting fields, an attacker could cause the workflow to act as a confused deputy — targeting unintended records or issuing outbound requests using the workflow owner's configured credentials.

## Patches
The issue has been fixed in n8n versions 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Avoid exposing public (unauthenticated) webhook workflows that pass incoming data through transform nodes into action nodes with sensitive credentials or database operations.
- Limit workflow creation and editing permissions to fully trusted users only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-2vff-hj5x-8gq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-54306
- https://github.com/n8n-io/n8n
