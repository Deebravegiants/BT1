# [H] OpenClaw: Native command authorization could skip owner-command enforcement

## Summary
Severity: High
Advisory: GHSA-p73f-w79w-jqr5
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-p73f-w79w-jqr5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.6

## Details
### Summary

Native command authorization could skip owner-command enforcement. In affected versions, a sender able to trigger native command handling could authorize a native command without enforcing the configured owner-only command policy.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run an owner-style command from a sender that should not have that command access. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.6`.

### Mitigations

keep native command surfaces limited to trusted senders until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p73f-w79w-jqr5
- https://github.com/openclaw/openclaw
