# [H] OpenClaw: Paired nodes could forge exec lifecycle events without system.run provenance

## Summary
Severity: High
Advisory: GHSA-3c6j-hq33-3jv4
CVE: CVE-2026-53816
CWE: CWE-284, CWE-862, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-3c6j-hq33-3jv4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

OpenClaw nodes send lifecycle events back to the gateway. In affected releases, a paired node could send an exec lifecycle event that was accepted without enough provenance tying it to an authorized `system.run` request.

This issue affects the node event boundary. It does not allow an unauthenticated caller to reach the gateway; the attacker must already control a paired node connection.

### Affected configurations

This affects deployments with a paired node where that node can send crafted `node.event` messages to the gateway and the target agent/session can process exec lifecycle events.

### Impact

A malicious or compromised paired node could make the gateway treat attacker-supplied event data as an exec lifecycle result. In the vulnerable flow, that could steer the target session into an exec-event path that exposed capabilities the reduced node surface should not have provided.

The issue is a missing provenance check for node-originated lifecycle events.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

Upgrade to `openclaw@2026.5.18` or later. Pair nodes only from trusted environments, and remove/re-pair nodes that may have been compromised.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3c6j-hq33-3jv4
- https://nvd.nist.gov/vuln/detail/CVE-2026-53816
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-exec-lifecycle-event-forgery-via-paired-node
