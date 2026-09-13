# [H] OpenClaw: Workspace-derived service PATH could influence trash command selection

## Summary
Severity: High
Advisory: GHSA-rx78-29qr-5hq8
CVE: CVE-2026-53865
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-rx78-29qr-5hq8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.2

## Details
### Summary

Workspace-derived service PATH could influence trash command selection. In affected versions, a workspace-derived environment path could select an unintended `trash` executable during maintenance.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run a local executable from a path the operator did not intend for maintenance tasks. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.2`.

### Mitigations

keep maintenance flows on trusted workspaces and fixed service paths until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rx78-29qr-5hq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-53865
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-command-execution-via-workspace-derived-service-path
