# [M] OpenClaw: Mattermost slash token revocation could lag until monitor refresh

## Summary
Severity: Medium
Advisory: GHSA-4m3v-q747-pc6h
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-4m3v-q747-pc6h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.24

## Details
### Summary

Mattermost slash token revocation could lag until monitor refresh. In affected versions, a caller with an old Mattermost slash token during the refresh window could continue accepting the old token until the monitor refreshed.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could invoke slash command behavior briefly after token revocation. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.24`.

### Mitigations

restart or refresh the Mattermost monitor after token rotation until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4m3v-q747-pc6h
- https://github.com/openclaw/openclaw
