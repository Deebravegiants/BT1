# [C] OpenClaw has a CWD `.env` environment variable injection which bypasses host-env policy and allows config takeover

## Summary
Severity: Critical
Advisory: GHSA-8rh7-6779-cjqq
CVE: CVE-2026-41294
CWE: CWE-426
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-8rh7-6779-cjqq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

OpenClaw loaded the current working directory `.env` before trusted state-dir configuration, allowing untrusted workspace state to inject host environment values.

## Impact

A repository or workspace containing a malicious `.env` file could override runtime configuration and security-sensitive environment settings when OpenClaw started there.

## Affected Component

`src/infra/dotenv.ts, src/cli/dotenv.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `6a79324802` (`Filter untrusted CWD .env entries before OpenClaw startup`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8rh7-6779-cjqq
- https://github.com/openclaw/openclaw/commit/6a793248024dca7685f63bcceb64a0096fd1586d
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.28
