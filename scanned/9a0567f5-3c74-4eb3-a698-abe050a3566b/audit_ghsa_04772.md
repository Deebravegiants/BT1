# [H] OpenClaw: Shell inline-command parsing could miss an allowlist check

## Summary
Severity: High
Advisory: GHSA-f397-5vjw-v2c2
CVE: CVE-2026-53866
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-f397-5vjw-v2c2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

Shell inline-command parsing could miss an allowlist check. In affected versions, a command request using shell inline-command forms could route an inline command through a parser case that did not receive the expected allowlist decision.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run shell content without the intended approval or allowlist prompt. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

require approval for shell inline-command forms until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f397-5vjw-v2c2
- https://nvd.nist.gov/vuln/detail/CVE-2026-53866
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-in-shell-inline-command-parsing
