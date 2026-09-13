# [M] OpenClaw: Active Memory write scope could mutate global config

## Summary
Severity: Medium
Advisory: GHSA-x629-46cc-7xgw
CVE: CVE-2026-53847
CWE: CWE-266
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-x629-46cc-7xgw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.5.6

## Details
### Summary

Active Memory write scope could mutate global config. In affected versions, a Gateway caller with `operator.write` access to the affected command could change global configuration without requiring `operator.admin`.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could apply configuration changes beyond the intended write scope. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.5.6`.

### Mitigations

limit Active Memory write access to trusted operators until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x629-46cc-7xgw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53847
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-active-memory-write-scope
