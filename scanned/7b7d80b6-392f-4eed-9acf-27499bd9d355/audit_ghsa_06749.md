# [H] OpenClaw: Message read actions could skip channel allowlist checks

## Summary
Severity: High
Advisory: GHSA-q7q8-3mgw-q67r
CVE: CVE-2026-53815
CWE: CWE-200, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-q7q8-3mgw-q67r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.19

## Details
### Summary

Message read actions could skip channel allowlist checks. In affected versions, a lower-trust caller with access to the affected message read action could request messages without the same channel allowlist check used by normal delivery.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could expose messages from a channel that was not intended for that caller. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.19`.

### Mitigations

limit message read actions to trusted operators and keep channel allowlists narrow. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q7q8-3mgw-q67r
- https://nvd.nist.gov/vuln/detail/CVE-2026-53815
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-channel-allowlist-bypass-in-message-read-actions
