# [M] OpenClaw: Internal/webchat command auth could inherit ownerAllowFrom wildcard state

## Summary
Severity: Medium
Advisory: GHSA-4hpg-mp64-x7xq
CVE: CVE-2026-53854
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-4hpg-mp64-x7xq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.25

## Details
### Summary

Internal/webchat command auth could inherit ownerAllowFrom wildcard state. In affected versions, a sender on an affected internal or webchat path could inherit wildcard ownerAllowFrom state across channel boundaries.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could run owner-style command behavior that should have stayed channel-scoped. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.25`.

### Mitigations

keep owner command allowlists explicit per channel until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-4hpg-mp64-x7xq
- https://nvd.nist.gov/vuln/detail/CVE-2026-53854
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-ownerallowfrom-wildcard-inheritance-in-internal-webchat-commands
