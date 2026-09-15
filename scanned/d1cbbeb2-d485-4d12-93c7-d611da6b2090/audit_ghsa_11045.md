# [M] OpenClaw plugin runtime command execution is part of trusted plugin boundary

## Summary
Severity: Medium
Advisory: GHSA-ff98-w8hj-qrxf
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-ff98-w8hj-qrxf
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
### Summary
OpenClaw plugins/extensions run in-process and are treated as trusted code. This advisory tracks trust-boundary clarification around plugin runtime command execution (`runtime.system.runCommandWithTimeout`).

### Impact
Plugins already execute with the same OS privileges as the OpenClaw process. Exposing runtime command helpers does not cross an additional sandbox boundary.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published version reviewed: `2026.2.17`
- Affected range for this advisory record: `<= 2026.2.17`
- Planned patched version metadata: `2026.2.19` (next release line)

### Fix Commit(s)
- `2e421f32dfc589c02706265fd3c3137ffc06c4b1`

### Remediation
- Install only trusted plugins.
- Use `plugins.allow` to pin explicit trusted plugin IDs.
- SECURITY.md now explicitly documents that plugin runtime helpers are convenience APIs, not a sandbox boundary.

OpenClaw thanks @markmusson for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-ff98-w8hj-qrxf
- https://github.com/openclaw/openclaw/commit/2e421f32dfc589c02706265fd3c3137ffc06c4b1
- https://github.com/openclaw/openclaw
