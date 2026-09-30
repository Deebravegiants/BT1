# [M] OpenClaw: node.pair.approve missing callerScopes validation allows low-privilege operator to approve malicious nodes

## Summary
Severity: Medium
Advisory: GHSA-2x4x-cc5g-qmmg
CVE: CVE-2026-33577
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-2x4x-cc5g-qmmg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

The node pairing approval path did not consistently enforce that the approving caller already held every scope requested by the node.

## Impact

A lower-privileged operator could approve a pending node request for broader scopes and extend privileges onto the paired node.

## Affected Component

`src/infra/node-pairing.ts, src/gateway/server-methods/nodes.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `4d7cc6bb4f` (`gateway: restrict node pairing approvals`).

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2x4x-cc5g-qmmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33577
- https://github.com/openclaw/openclaw/commit/4d7cc6bb4fac68b5a5fadd1c5a23168281221f34
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-insufficient-scope-validation-in-node-pair-approve
