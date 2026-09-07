# [C] OpenClaw: QQBot admin commands could skip DM-only and allowFrom policy

## Summary
Severity: Critical
Advisory: GHSA-w4v6-g3wm-w36c
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-w4v6-g3wm-w36c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.29

## Details
### Summary

QQBot admin commands could skip DM-only and allowFrom policy. In affected versions, a QQBot sender able to trigger the exported command could route admin commands without the QQBot-specific DM-only and allowFrom checks.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run QQBot admin behavior from a sender or context that policy should have blocked. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.29`.

### Mitigations

disable exported QQBot admin commands or restrict QQBot access until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w4v6-g3wm-w36c
- https://github.com/openclaw/openclaw
