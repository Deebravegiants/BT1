# [H] OpenClaw: QQBot pre-dispatch slash commands could skip allowFrom checks

## Summary
Severity: High
Advisory: GHSA-77pv-3w4q-vrj5
CVE: CVE-2026-53834
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-77pv-3w4q-vrj5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.27

## Details
### Summary

QQBot pre-dispatch slash commands could skip allowFrom checks. In affected versions, a QQBot sender able to invoke slash commands could dispatch the command before applying the configured allowFrom policy.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could trigger command handling from a sender that policy should have blocked. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.27`.

### Mitigations

restrict QQBot slash command exposure until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-77pv-3w4q-vrj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53834
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-in-qqbot-pre-dispatch-slash-commands
