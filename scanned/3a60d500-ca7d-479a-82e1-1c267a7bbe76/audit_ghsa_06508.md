# [M] OpenClaw: Embedded runner policy could be confused by provider aliases

## Summary
Severity: Medium
Advisory: GHSA-p39j-x9h5-q66m
CVE: CVE-2026-53809
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-p39j-x9h5-q66m
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.25

## Details
### Summary

Embedded runner policy could be confused by provider aliases. In affected versions, a request using provider aliases could compare policy against an alias instead of the canonical provider identity.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could select bundled tool access outside the intended provider policy. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.25`.

### Mitigations

Avoid provider alias routing for embedded runner tool policy until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-p39j-x9h5-q66m
- https://nvd.nist.gov/vuln/detail/CVE-2026-53809
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-provider-alias-confusion-in-embedded-runner-policy
