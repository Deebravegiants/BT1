# [M] n8n: GraphQL Node Bypasses "Allowed HTTP Request Domains" Restriction

## Summary
Severity: Medium
Advisory: GHSA-gq66-9cw5-j5jm
CVE: CVE-2026-65596
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:N/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-gq66-9cw5-j5jm
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.64
- npm: `n8n` — affected >=2.30.0 <2.30.1
- npm: `n8n` — affected >=2.0.0 <2.29.8

## Details
## Impact
The GraphQL node did not enforce the "Allowed HTTP Request Domains" restriction on HTTP-based credentials (such as Header Auth, Basic Auth, Query Auth, and OAuth), unlike the HTTP Request node. An authenticated user able to create or edit workflows could therefore point the node's endpoint at a server they control and exfiltrate restricted credentials.

Only instances where a credential has "Allowed HTTP Request Domains" configured and is usable by non-owner users are affected.

## Patches
The issue has been fixed in n8n versions 1.123.64, 2.29.8, and 2.30.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict workflow creation and editing permissions to fully trusted users only.
- Restrict credential sharing to fully trusted users only.
- Audit credentials with domain restrictions for unexpected sharing relationships.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-gq66-9cw5-j5jm
- https://nvd.nist.gov/vuln/detail/CVE-2026-65596
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.64
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.29.8
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.30.1
- https://www.vulncheck.com/advisories/n8n-before-credential-exfiltration-via-graphql-node
