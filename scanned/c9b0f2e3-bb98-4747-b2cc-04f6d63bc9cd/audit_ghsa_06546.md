# [M] OpenClaw's Slack plugin approvals used the exec approver gate for plugin actions

## Summary
Severity: Medium
Advisory: GHSA-wv26-j37q-2g7p
CWE: CWE-863
Ecosystem: npm
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-wv26-j37q-2g7p
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

Slack plugin approvals used the exec approver gate for plugin actions. In affected versions, a Slack user authorized only for exec approvals could resolve a plugin approval through the exec approver gate.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could approve a plugin action outside the operator's intended approval split. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

keep approval allowlists aligned and review Slack approval actions manually until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-wv26-j37q-2g7p
- https://github.com/openclaw/openclaw
