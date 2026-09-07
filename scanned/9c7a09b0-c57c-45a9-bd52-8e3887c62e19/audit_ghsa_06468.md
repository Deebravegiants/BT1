# [M] n8n: External Secrets Accessible via Workflow Expressions Outside Credentials

## Summary
Severity: Medium
Advisory: GHSA-2434-3x6q-8r99
CVE: CVE-2026-59254
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-2434-3x6q-8r99
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.28.0 <2.28.1
- npm: `n8n` — affected >=0 <2.27.4

## Details
## Impact
External secrets were incorrectly resolved in workflow node expressions, where they are not intended to be available. An authenticated user with project editor access could read the plaintext value of external secrets by referencing them in a node expression, without needing explicit secrets access permissions.

This issue only affects instances with the external secrets feature configured.

## Patches
The issue has been fixed in n8n versions 2.27.4 and 2.28.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Restrict project membership to fully trusted users only.
- Avoid granting editor access to projects on instances where external secrets are configured.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-2434-3x6q-8r99
- https://nvd.nist.gov/vuln/detail/CVE-2026-59254
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.27.4
- https://github.com/n8n-io/n8n/releases/tag/n8n%402.28.1
- https://www.vulncheck.com/advisories/n8n-external-secrets-disclosure-via-workflow-node-expressions
