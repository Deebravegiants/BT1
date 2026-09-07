# [M] OpenClaw: Sandboxed session spawn could expose the real workspace path to child prompts

## Summary
Severity: Medium
Advisory: GHSA-6c4r-g249-wv3c
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-6c4r-g249-wv3c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.26

## Details
### Summary

Sandboxed session spawn could expose the real workspace path to child prompts. In affected versions, a child session spawned from a sandboxed parent could forward the host workspace path into the child session prompt.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could reveal host workspace location or related memory context to the child model. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.26`.

### Mitigations

avoid spawning child sessions from sensitive sandboxed workspaces until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6c4r-g249-wv3c
- https://github.com/openclaw/openclaw
