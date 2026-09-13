# [H] OpenClaw: Discord allowFrom could bind to mutable display names

## Summary
Severity: High
Advisory: GHSA-cw4q-gqg5-g38h
CVE: CVE-2026-53849
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-cw4q-gqg5-g38h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.7

## Details
### Summary

Discord allowFrom could bind to mutable display names. In affected versions, a Discord account able to change display or global name metadata could match a policy entry through mutable display metadata.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could receive agent access intended for another Discord identity. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.7`.

### Mitigations

use stable Discord user IDs in allowlists until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-cw4q-gqg5-g38h
- https://nvd.nist.gov/vuln/detail/CVE-2026-53849
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-mutable-discord-display-names-in-allowfrom
