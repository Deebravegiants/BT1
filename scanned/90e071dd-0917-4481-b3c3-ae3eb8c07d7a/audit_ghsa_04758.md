# [M] OpenClaw: memory-wiki shared search could miss session visibility checks

## Summary
Severity: Medium
Advisory: GHSA-72fw-cqh5-f324
CVE: CVE-2026-53844
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-72fw-cqh5-f324
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.29

## Details
### Summary

memory-wiki shared search could miss session visibility checks. In affected versions, a caller able to search shared memory could skip the session visibility guard on the affected search path.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could return memory entries that should not have been visible to that session. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.29`.

### Mitigations

limit shared memory search to trusted operators until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-72fw-cqh5-f324
- https://nvd.nist.gov/vuln/detail/CVE-2026-53844
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-session-visibility-check-bypass-in-shared-memory-search
