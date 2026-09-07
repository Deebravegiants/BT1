# [H] OpenClaw: Combined POSIX shell options could confuse exec revalidation

## Summary
Severity: High
Advisory: GHSA-vxx3-6hc9-7cc3
CVE: CVE-2026-53806
CWE: CWE-367
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-vxx3-6hc9-7cc3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.12

## Details
### Summary

Combined POSIX shell options could confuse exec revalidation. In affected versions, a command request using combined shell flags could parse approval-time and execution-time shell options differently.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run inline shell content without the intended allowlist decision. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.12`.

### Mitigations

avoid combined shell option forms in allowlisted commands until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vxx3-6hc9-7cc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-53806
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-shell-option-parsing-bypass-in-exec-revalidation
