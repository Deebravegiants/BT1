# [M] OpenClaw's hooks count non-POST requests toward auth lockout

## Summary
Severity: Medium
Advisory: GHSA-6rmx-gvvg-vh6j
CWE: CWE-307, CWE-799
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-6rmx-gvvg-vh6j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.7

## Details
OpenClaw's hooks HTTP handler counted hook authentication failures before rejecting unsupported HTTP methods. An unauthenticated client could send repeated non-`POST` requests (for example `GET`) with an invalid token to consume the hook auth failure budget and trigger the temporary lockout window for that client key.

The fix moves the hook method gate ahead of auth-failure accounting so unsupported methods return `405 Method Not Allowed` without incrementing the hook auth limiter.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.2`
- Patched version: `2026.3.7`
- Latest published npm version at patch time: `2026.3.2`

## Impact

An unauthenticated network client that could reach `/hooks/*` could temporarily lock out legitimate webhook delivery when requests collapsed to the same hook auth client key, such as shared proxy or NAT topologies. Impact is limited to temporary availability loss for hook-triggered wake or automation delivery.

## Fix Commit(s)

- `44820dceadac65ac7c0ce8fc0ffba8c2bd9fae89`

## Verification

- `pnpm check` passed
- `pnpm test:fast` passed
- focused hook regression tests passed
- `pnpm exec vitest run --config vitest.gateway.config.ts` still has unrelated current-`main` failures in `src/gateway/server-channels.test.ts` and `src/gateway/server-methods/agents-mutate.test.ts`

## Release Process Note

npm `2026.3.7` was published on March 8, 2026. This advisory is fixed in the released package.

Thanks @JNX03 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6rmx-gvvg-vh6j
- https://github.com/openclaw/openclaw/commit/44820dceadac65ac7c0ce8fc0ffba8c2bd9fae89
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.7
