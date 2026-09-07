# [M] OpenClaw: CDP /json/version WebSocket URL could pivot to untrusted second-hop targets

## Summary
Severity: Medium
Advisory: GHSA-f7fh-qg34-x2xh
CVE: CVE-2026-43576
CWE: CWE-601, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-f7fh-qg34-x2xh
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.5

## Details
## Summary

CDP /json/version WebSocket URL could pivot to untrusted second-hop targets.

## Affected Packages / Versions

- Package: `openclaw`
- Ecosystem: npm
- Affected versions: `< 2026.4.5`
- Patched versions: `>= 2026.4.5`

## Impact

A browser profile could trust a CDP `/json/version` response whose `webSocketDebuggerUrl` pointed at a different host, enabling a second-hop SSRF-style pivot.

## Technical Details

The fix normalizes and re-validates direct CDP WebSocket targets before connecting.

## Fix

The issue was fixed in #60469. The first stable tag containing the fix is `v2026.4.5`, and `openclaw@2026.4.14` includes the fix.

## Fix Commit(s)

- `bc356cc8c2beaa747c71dd86cceab8f804699665`
- PR: #60469

## Release Process Note

Users should upgrade to `openclaw` 2026.4.5 or newer. The latest npm release, `2026.4.14`, already includes the fix.

## Credits

Thanks to @tdjackey for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-f7fh-qg34-x2xh
- https://nvd.nist.gov/vuln/detail/CVE-2026-43576
- https://github.com/openclaw/openclaw/pull/60469
- https://github.com/openclaw/openclaw/commit/bc356cc8c2beaa747c71dd86cceab8f804699665
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-second-hop-ssrf-via-cdp-json-version-websocket-url
