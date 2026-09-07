# [H] OpenClaw: PowerShell encoded-command aliases could miss exec allowlist checks

## Summary
Severity: High
Advisory: GHSA-j472-gf56-x589
CVE: CVE-2026-53836
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-j472-gf56-x589
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

PowerShell encoded-command aliases could miss exec allowlist checks. In affected versions, a command request using abbreviated encoded-command flags could use an alias form not recognized by the allowlist parser.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run encoded PowerShell content without the intended allowlist decision. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

Avoid allowlisting PowerShell wrapper forms and require approval for encoded commands until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j472-gf56-x589
- https://nvd.nist.gov/vuln/detail/CVE-2026-53836
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-allowlist-bypass-via-powershell-encoded-command-aliases
