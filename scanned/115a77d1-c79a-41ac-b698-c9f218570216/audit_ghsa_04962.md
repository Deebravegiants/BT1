# [M] OpenClaw: macOS Swift exec allowlist missed combined POSIX inline flags

## Summary
Severity: Medium
Advisory: GHSA-c226-q6fx-6j6c
CVE: CVE-2026-53861
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-c226-q6fx-6j6c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.6

## Details
### Summary

macOS Swift exec allowlist missed combined POSIX inline flags. In affected versions, a command request using combined POSIX inline-command flags could miss inline-command content expressed through combined flags.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run shell content outside the intended allowlist check. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.6`.

### Mitigations

require approval for combined shell flag forms on macOS until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-c226-q6fx-6j6c
- https://nvd.nist.gov/vuln/detail/CVE-2026-53861
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-via-combined-posix-inline-flags-on-macos
