# [H] OpenClaw: Trusted retry endpoint checks could match hostname prefixes

## Summary
Severity: High
Advisory: GHSA-77q5-rr5v-x43q
CWE: CWE-1023, CWE-20, CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-77q5-rr5v-x43q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.7

## Details
### Summary

Trusted retry endpoint checks could match hostname prefixes. In affected versions, a retry endpoint URL chosen by lower-trust input could pass validation by using a hostname prefix that resembled a trusted host.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could send authentication material to an endpoint outside the intended trust target. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.7`.

### Mitigations

pin retry endpoints to exact trusted origins until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-77q5-rr5v-x43q
- https://github.com/openclaw/openclaw
