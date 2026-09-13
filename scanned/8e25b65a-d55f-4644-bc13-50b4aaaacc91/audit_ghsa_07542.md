# [H] OpenClaw: Same-host trusted-proxy deployments could accept local forged identity headers

## Summary
Severity: High
Advisory: GHSA-rggc-m335-3wvj
CVE: CVE-2026-53832
CWE: CWE-269, CWE-284, CWE-287, CWE-290, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-rggc-m335-3wvj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.18

## Details
### Summary

Same-host trusted-proxy deployments could accept local forged identity headers. In affected versions, a local same-host caller that can reach the proxy-facing Gateway port could supply identity headers normally reserved for the trusted proxy.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could receive operator identity associated with the forged headers. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.18`.

### Mitigations

bind trusted-proxy ingress behind the actual proxy and firewall direct same-host access. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rggc-m335-3wvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-53832
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-identity-header-forgery-via-trusted-proxy-configuration
