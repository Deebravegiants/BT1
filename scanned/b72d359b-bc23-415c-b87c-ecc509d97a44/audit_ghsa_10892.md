# [H] OpenClaw: `session_status` sessionId resolution bypasses sandboxed session-tree visibility

## Summary
Severity: High
Advisory: GHSA-q2qc-744p-66r2
CWE: CWE-639, CWE-863
Ecosystem: npm
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-q2qc-744p-66r2
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=2026.3.11 <2026.3.28

## Details
## Summary

`session_status` sessionId resolution bypasses sandboxed session-tree visibility

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `>= 2026.3.11, <= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

`session_status` previously resolved a `sessionId` to a canonical session key after early visibility checks, letting sandboxed children reach parent or sibling sessions that were blocked by explicit `sessionKey`. Commit `d9810811b6c3c9266d7580f00574e5e02f7663de` enforces visibility after `sessionId` resolution so sandboxed callers cannot escape their session tree.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `d9810811b6c3c9266d7580f00574e5e02f7663de`.

## Fix Commit(s)

- `d9810811b6c3c9266d7580f00574e5e02f7663de`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q2qc-744p-66r2
- https://github.com/openclaw/openclaw/commit/d9810811b6c3c9266d7580f00574e5e02f7663de
- https://github.com/openclaw/openclaw
