# [H] n8n: SecurityScorecard Node Leaks API Token to User-Controlled Host

## Summary
Severity: High
Advisory: GHSA-rm2v-h48j-895m
CVE: CVE-2026-54304
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-rm2v-h48j-895m
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.55
- npm: `n8n` — affected >=2.26.0 <2.26.1
- npm: `n8n` — affected >=2.0.0-rc.0 <2.25.7

## Details
## Impact
An authenticated user with permission to create or modify workflows and access to a SecurityScorecard credential with limited allowed domains could configure the SecurityScorecard node's report download operation to target an attacker-controlled URL. The node attached the SecurityScorecard API token to the outbound request, causing the credential to be sent to the attacker-controlled host bypassing credential configured limitations and exfiltrating.

## Patches
The issue has been fixed in n8n versions 1.123.55, 2.25.7, and 2.26.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit workflow creation and editing permissions to fully trusted users only.
- Disable the SecurityScorecard node by adding `n8n-nodes-base.securityScorecard` to the `NODES_EXCLUDE` environment variable.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-rm2v-h48j-895m
- https://nvd.nist.gov/vuln/detail/CVE-2026-54304
- https://github.com/n8n-io/n8n
