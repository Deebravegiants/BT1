# [M] OpenClaw MCP SSE redirects could forward Authorization headers

## Summary
Severity: Medium
Advisory: GHSA-9c3v-684m-579c
CWE: CWE-200, CWE-522, CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-9c3v-684m-579c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.6.5

## Details
### Summary

MCP SSE redirects could forward Authorization headers. In affected versions, a lower-trust caller or configured input path could execute or persist actions beyond the caller's intended authorization.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could execute or persist actions beyond the caller's intended authorization. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.6.5`.

### Mitigations

Upgrade to a patched OpenClaw release when one is listed. Before upgrading, restrict the affected feature to trusted operators or disable it when it is not needed. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9c3v-684m-579c
- https://github.com/openclaw/openclaw
