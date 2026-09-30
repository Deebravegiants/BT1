# [H] OpenClaw: Telegram interactive callbacks could skip commands.allowFrom

## Summary
Severity: High
Advisory: GHSA-w5ww-7chg-mxcq
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-w5ww-7chg-mxcq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.6

## Details
### Summary

Telegram interactive callbacks could skip commands.allowFrom. In affected versions, a Telegram user able to invoke an affected callback could mark the callback as an authorized sender before applying `commands.allowFrom`.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could trigger command behavior outside the configured Telegram sender allowlist. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.6`.

### Mitigations

restrict Telegram command callbacks to trusted chats until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w5ww-7chg-mxcq
- https://github.com/openclaw/openclaw
