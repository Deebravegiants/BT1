# [H] OpenClaw: Shell wrapper argv could change between approval and execution

## Summary
Severity: High
Advisory: GHSA-2j8v-hwgc-x698
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-2j8v-hwgc-x698
Type: github-advisory

## Affected
- npm: `Openclaw` — affected >=0 <2026.5.18

## Details
### Summary

Shell wrapper argv could change between approval and execution. In affected versions, a command request using a shell wrapper form could approve one resolved argv shape and rebuild another for execution.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run a command shape that was not checked against the allowlist. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

require explicit approval for shell wrappers and avoid durable allowlists for wrapper-heavy commands until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2j8v-hwgc-x698
- https://github.com/openclaw/openclaw
