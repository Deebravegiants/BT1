# [H] OpenClaw: Voice-call Plivo V3 webhook replay key uses unsorted URL, allowing replay via query-parameter reordering

## Summary
Severity: High
Advisory: GHSA-8689-gm9g-jgr6
CVE: CVE-2026-41395
CWE: CWE-294
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-8689-gm9g-jgr6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Plivo V3 signature verification canonicalized query ordering, but replay detection hashed the raw verification URL. Reordering query parameters preserved a valid signature while producing a fresh replay-cache key.

## Impact

An attacker who captured one valid signed Plivo V3 webhook could replay the same event by permuting query parameters and trigger duplicate voice-call processing.

## Affected Component

`extensions/voice-call/src/webhook-security.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `85777e726c` (`Voice Call: canonicalize Plivo V3 replay key`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8689-gm9g-jgr6
- https://github.com/openclaw/openclaw/commit/85777e726cb02c01a911b3ff832ddf4d664d5c94
- https://github.com/openclaw/openclaw
