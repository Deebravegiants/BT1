# [M] OpenClaw: Browser debug/export routes could reuse already-open blocked tabs

## Summary
Severity: Medium
Advisory: GHSA-hcm3-8f6r-6xwg
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-hcm3-8f6r-6xwg
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.29

## Details
### Summary

Browser debug/export routes could reuse already-open blocked tabs. In affected versions, a caller that can reference an already-open browser tab could reuse blocked private-network tabs without reapplying the expected SSRF policy.

This advisory is scoped to the named feature and configuration. It does not change OpenClaw's trusted-operator model: authenticated Gateway operators, installed plugins, and intentional local execution surfaces remain trusted unless a separate policy, approval, allowlist, sandbox, or auth boundary is crossed.

### Impact

When the affected feature is enabled and reachable, this could export or inspect content from a tab that should have stayed behind the browser network policy. Practical impact depends on the operator's configuration and whether lower-trust input can reach that path.

### Patched Versions

The first stable patched version is `2026.4.29`.

### Mitigations

close blocked tabs before debug/export use and restrict browser debug routes until patched. As general hardening, keep channel and tool allowlists narrow, avoid sharing one Gateway between mutually untrusted users, and disable the affected feature when it is not needed.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-hcm3-8f6r-6xwg
- https://github.com/openclaw/openclaw
