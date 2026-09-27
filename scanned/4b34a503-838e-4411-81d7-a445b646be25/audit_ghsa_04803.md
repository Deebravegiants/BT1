# [M] OpenClaw: Focus command could miss controlScope enforcement

## Summary
Severity: Medium
Advisory: GHSA-mpc8-jxjh-qpgh
CVE: CVE-2026-53850
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-mpc8-jxjh-qpgh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.25

## Details
### Summary

Focus command could miss controlScope enforcement. In affected versions, a caller able to trigger the focus command could run the command without enforcing the expected control scope.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could change focus state outside the intended caller authority. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.25`.

### Mitigations

restrict focus command access to trusted operators until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mpc8-jxjh-qpgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-53850
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-control-scope-enforcement-bypass-in-focus-command
