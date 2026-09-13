# [M] n8n Vulnerable to Hijacking of Unauthenticated Chat Execution 

## Summary
Severity: Medium
Advisory: GHSA-f77h-j2v7-g6mw
CVE: CVE-2026-42228
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-29
Source: https://github.com/advisories/GHSA-f77h-j2v7-g6mw
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.123.32
- npm: `n8n` — affected >=2.18.0 <2.18.1
- npm: `n8n` — affected >=2.0.0 <2.17.4

## Details
## Impact
The `/chat` WebSocket endpoint used by the Chat Trigger node's Hosted Chat feature did not verify that an incoming connection was authorized to interact with the target execution. An unauthenticated remote attacker who could identify a valid execution ID for a workflow in a waiting state could attach to that execution, receive the pending prompt intended for the legitimate user, and submit arbitrary input to resume or influence downstream workflow behavior.

Exploitation requires the following conditions:
- The instance exposes a public Hosted Chat workflow with authentication set to `None`.
- A target execution is in a waiting state at the time of the attack.
- The attacker can obtain or discover the execution ID of that waiting execution.

## Patches
The issue has been fixed in n8n versions 1.123.32, 2.17.4, and 2.18.1. Users should upgrade to one of these versions or later to remediate the vulnerability.

## Workarounds
If upgrading is not immediately possible, administrators should consider the following temporary mitigations:
- Enable authentication on all Chat Trigger nodes by setting the Authentication field to `n8n User Auth` rather than `None`.

These workarounds do not fully remediate the risk and should only be used as short-term mitigation measures.

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backwards compatibility.

CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-f77h-j2v7-g6mw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42228
- https://github.com/n8n-io/n8n
