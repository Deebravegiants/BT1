# [H] OpenClaw has an authentication bypass in sandbox browser bridge server

## Summary
Severity: High
Advisory: GHSA-h9g4-589h-68xv
CVE: CVE-2026-28468
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-h9g4-589h-68xv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.1.29-beta.1 <2026.2.14

## Details
## Summary

openclaw could start the sandbox browser bridge server without authentication.

When the sandboxed browser is enabled, openclaw runs a local (loopback) HTTP bridge that exposes browser control endpoints (for example `/profiles`, `/tabs`, `/tabs/open`, `/agent/*`). Due to missing auth wiring in the sandbox initialization path, that bridge server accepted requests without requiring gateway auth.

## Impact

A local attacker (any process on the same machine) could access the bridge server port and:

- enumerate open tabs and retrieve CDP WebSocket URLs
- open/close/navigate tabs
- execute JavaScript in page contexts via CDP
- exfiltrate cookies/session data and page contents from authenticated sessions

This is a localhost-only exposure (CVSS AV:L), but provides full browser-session compromise for sandboxed browser usage.

## Affected Versions

- Introduced in: `2026.1.29-beta.1` (first npm release that shipped the sandbox browser bridge)
- Affected range: `>=2026.1.29-beta.1 <2026.2.14`

## Patched Versions

- `2026.2.14`

## Mitigation

- Upgrade to `2026.2.14` (recommended).
- Or disable the sandboxed browser (`agents.defaults.sandbox.browser.enabled=false`).

## Fix Details

- The sandbox browser bridge server now always requires auth and enforces the same gateway browser control auth (token/password) that loopback browser clients already use.
- Additional hardening: bridge server refuses non-loopback binds; local helper servers are bound to loopback.
- Added regression tests (including unit coverage for per-port bridge auth fallback).

Fix commits:

- openclaw/openclaw@4711a943e30bc58016247152ba06472dab09d0b0
- openclaw/openclaw@6dd6bce997c48752134f2d6ed89b27de01ced7e3
- openclaw/openclaw@cd84885a4ac78eadb7bf321aae98db9519426d67
## Credits

Thanks to Adnan Jakati (@jackhax) of [Praetorian](https://www.praetorian.com/) for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h9g4-589h-68xv
- https://github.com/openclaw/openclaw/commit/4711a943e30bc58016247152ba06472dab09d0b0
- https://github.com/openclaw/openclaw/commit/6dd6bce997c48752134f2d6ed89b27de01ced7e3
- https://github.com/openclaw/openclaw/commit/cd84885a4ac78eadb7bf321aae98db9519426d67
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
