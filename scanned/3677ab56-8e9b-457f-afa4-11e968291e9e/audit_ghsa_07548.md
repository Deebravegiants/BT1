# [M] n8n has a Guardrail Node Bypass

## Summary
Severity: Medium
Advisory: GHSA-fvfv-ppw4-7h2w
CWE: CWE-20, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-fvfv-ppw4-7h2w
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <2.10.0

## Details
## Impact
An end user interacting with a workflow that uses the Guardrail node could craft an input that bypasses the default guardrail instructions.

## Patches
The issue has been fixed in n8n version 2.10.0. Users should upgrade to this version or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Limit access to trusted users.
- Review asses the practical impact of guardrail bypasses in your usecase and adjust your workflow accordingly.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-fvfv-ppw4-7h2w
- https://github.com/n8n-io/n8n/commit/8d0251d1deef256fd3d9176f05dedab62afde918
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.10.0
