# [H] OpenClaw safeBins jq `$ENV` filter bypass allows environment variable disclosure

## Summary
Severity: High
Advisory: GHSA-jccr-rrw2-vc8h
CWE: CWE-185, CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-jccr-rrw2-vc8h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

The jq safe-bin policy blocked explicit `env` usage but still allowed jq programs that accessed environment data through `$ENV`.

## Impact

An operator-approved safe-bin jq command could disclose environment variables that the safe-bin policy was supposed to keep out of scope.

## Affected Component

`src/infra/exec-safe-bin-semantics.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `78e2f3d66d` (`Exec: tighten jq safe-bin env checks`).

Thanks @nicky-cc  of Tencent zhuque Lab ([https://github.com/Tencent/AI-Infra-Guard](https://github.com/Tencent/AI-Infra-Guard)) for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jccr-rrw2-vc8h
- https://github.com/openclaw/openclaw/commit/78e2f3d66d74e5c7e6f45c54162e63986e39771b
- https://github.com/openclaw/openclaw
