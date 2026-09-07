# [M] OpenClaw: Hostname checks could treat trailing-dot hosts inconsistently

## Summary
Severity: Medium
Advisory: GHSA-gxg4-2rrr-jhc7
CVE: CVE-2026-53859
CWE: CWE-20, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-gxg4-2rrr-jhc7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.26

## Details
### Summary

Hostname checks could treat trailing-dot hosts inconsistently. In affected versions, a request path that accepts model- or workspace-derived URLs could present the same hostname with a trailing dot and avoid a blocklist comparison.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could reach a destination that the operator expected the hostname policy to block. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.26`.

### Mitigations

keep private-network and metadata destinations blocked at the proxy or network layer until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-gxg4-2rrr-jhc7
- https://nvd.nist.gov/vuln/detail/CVE-2026-53859
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-hostname-validation-bypass-via-trailing-dot-inconsistency
