# [M] OpenClaw: Gateway `operator.write` can reach admin-only persisted `verboseLevel` via `chat.send` `/verbose`

## Summary
Severity: Medium
Advisory: GHSA-5h2w-qmfp-ggp6
CVE: CVE-2026-41344
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-5h2w-qmfp-ggp6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

The `chat.send` path let authorized write-scoped callers persist `/verbose` session overrides even though the same stored session mutation is admin-only through `sessions.patch`.

## Impact

A write-scoped gateway caller could persist verbose output for later runs and expose more reasoning or tool output than the operator intended.

## Affected Component

`src/auto-reply/reply/directive-handling.impl.ts, src/gateway/sessions-patch.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `c603123528` (`fix(gateway): require admin for persisted verbose defaults`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5h2w-qmfp-ggp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-41344
- https://github.com/openclaw/openclaw/commit/c6031235288a8d3bdf2243bd974340d8c8045bc2
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-privilege-escalation-via-chat-send-verbose-parameter
