# [M] n8n: Missing Token Validation on Microsoft Agent 365 Trigger and Stripe Nodes

## Summary
Severity: Medium
Advisory: GHSA-jvc7-762p-3743
CVE: CVE-2026-54308
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-jvc7-762p-3743
Type: github-advisory

## Affected
- npm: `n8n` — affected >=2.26.0 <2.26.2
- npm: `n8n` — affected >=0 <2.25.7

## Details
## Impact
The `MicrosoftAgent365Trigger` and `StripeTrigger` node did not validate that inbound requests. As a result, an unauthenticated attacker who knows the webhook URL could submit a forged payload and cause the workflow to execute with attacker-controlled data.

## Patches
The issue has been fixed in n8n versions 2.25.7, and 2.26.2. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Deactivate any workflows using the Microsoft Agent 365 Trigger node or Stripe Trigger node until the instance can be upgraded.
- Restrict network access to the n8n webhook endpoint to trusted sources only.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-jvc7-762p-3743
- https://nvd.nist.gov/vuln/detail/CVE-2026-54308
- https://github.com/n8n-io/n8n
