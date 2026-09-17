# [M] OpenClaw's allow-always wrapper persistence could bypass future approvals and enable command execution

## Summary
Severity: Medium
Advisory: GHSA-6j27-pc5c-m8w8
CVE: CVE-2026-29607
CWE: CWE-78, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-6j27-pc5c-m8w8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
### Summary
In `openclaw` npm releases up to and including `2026.2.21-2`, approving wrapped `system.run` commands with `allow-always` in `security=allowlist` mode could persist wrapper-level allowlist entries and enable later approval-bypass execution of different inner payloads.

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.21-2`
- Planned patched version: `2026.2.22`

### Details
`allow-always` persistence was based on wrapper-level resolution instead of stable inner executable intent. A benign approved wrapper invocation could therefore broaden future trust boundaries.

Affected paths included gateway and node-host execution approval persistence flows. The fix now persists inner executable paths for known dispatch-wrapper chains (`env`, `nice`, `nohup`, `stdbuf`, `timeout`) and fails closed when safe unwrapping cannot be derived.

### Impact
Authorization boundary bypass in allowlist mode, potentially leading to approval-free command execution (RCE class) on subsequent wrapped invocations.

### Mitigation
Upgrade to `2026.2.22` (planned next release) or run with stricter exec policy (`ask=always` / `security=deny`) until upgraded.

### Fix Commit(s)
- `24c954d972400f508814532dea0e4dcb38418bb0`

### Release Process Note
`patched_versions` is pre-set to `2026.2.22` so this advisory is publish-ready; publish after the npm release is live.

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6j27-pc5c-m8w8
- https://nvd.nist.gov/vuln/detail/CVE-2026-29607
- https://github.com/openclaw/openclaw/commit/24c954d972400f508814532dea0e4dcb38418bb0
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-allow-always-wrapper-persistence
