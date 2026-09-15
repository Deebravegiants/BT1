# [M] OpenClaw: message.action forwarding could send Gateway credentials to model-supplied loopback URLs

## Summary
Severity: Medium
Advisory: GHSA-grc3-2j34-p6gm
CWE: CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-grc3-2j34-p6gm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.2

## Details
### Summary

message.action forwarding could send Gateway credentials to model-supplied loopback URLs. In affected versions, model-controlled action metadata that selects a loopback Gateway URL could forward the action payload with Gateway credentials to the supplied loopback URL.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could expose the token and action payload to a local listener chosen through the affected path. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.2`.

### Mitigations

restrict message action forwarding and avoid model-supplied loopback targets until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-grc3-2j34-p6gm
- https://github.com/openclaw/openclaw
