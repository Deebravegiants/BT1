# [M] OpenClaw: Tool group policy callers could accept unvalidated group IDs

## Summary
Severity: Medium
Advisory: GHSA-985f-72mj-8gf7
CVE: CVE-2026-53863
CWE: CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-985f-72mj-8gf7
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.25

## Details
### Summary

Tool group policy callers could accept unvalidated group IDs. In affected versions, a caller that can supply a group id to the affected policy resolver could resolve policy for an unvalidated group id.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could apply the wrong group-policy decision for a tool invocation. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.25`.

### Mitigations

avoid exposing group-policy controlled tools to untrusted senders until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-985f-72mj-8gf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-53863
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unvalidated-group-id-acceptance-in-tool-group-policy
