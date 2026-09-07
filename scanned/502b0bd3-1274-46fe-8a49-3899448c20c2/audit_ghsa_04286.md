# [H] OpenClaw: Shell positional parameters could weaken strict inline-eval checks

## Summary
Severity: High
Advisory: GHSA-5cj2-3jr2-5h77
CVE: CVE-2026-53855
CWE: CWE-269, CWE-284, CWE-78, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-5cj2-3jr2-5h77
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
### Summary

Shell positional parameters could weaken strict inline-eval checks. In affected versions, a command request that combines allowlisted tools with shell positional arguments could place inline-eval content in a shell carrier not covered by the strict check.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run shell-provided content outside the intended allowlist rule. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.2`.

### Mitigations

avoid allowlisting shell carrier patterns and require approval for shell wrappers until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5cj2-3jr2-5h77
- https://nvd.nist.gov/vuln/detail/CVE-2026-53855
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-shell-positional-parameters-bypass-in-inline-eval-checks
