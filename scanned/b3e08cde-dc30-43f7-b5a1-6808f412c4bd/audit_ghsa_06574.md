# [M] OpenClaw: Bundle MCP loopback could miss its exec denylist on session spawn

## Summary
Severity: Medium
Advisory: GHSA-qh2f-99mv-mrcf
CWE: CWE-284, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-qh2f-99mv-mrcf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

Bundle MCP loopback could miss its exec denylist on session spawn. In affected versions, a caller that can reach the affected bundled MCP session-spawn path could bypass the denylist that was intended for that loopback MCP entry point.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could start a session with broader command reach than that MCP path should provide. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

restrict bundled MCP loopback access to trusted operators until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qh2f-99mv-mrcf
- https://github.com/openclaw/openclaw
