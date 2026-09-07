# [H] OpenClaw: fetch-guard forwards custom authorization headers across cross-origin redirects

## Summary
Severity: High
Advisory: GHSA-6mgf-v5j7-45cr
CVE: CVE-2026-32913
CWE: CWE-116, CWE-184, CWE-522
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-6mgf-v5j7-45cr
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.7

## Details
OpenClaw's `fetchWithSsrFGuard(...)` followed cross-origin redirects while preserving arbitrary caller-supplied headers except for a narrow denylist (`Authorization`, `Proxy-Authorization`, `Cookie`, `Cookie2`). This allowed custom authorization headers such as `X-Api-Key`, `Private-Token`, and similar sensitive headers to be forwarded to a different origin after a redirect.

The fix switches cross-origin redirect handling from a narrow sensitive-header denylist to a safe-header allowlist, so only benign headers such as content negotiation and cache validators survive an origin change.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.3.2`
- Patched version: `2026.3.7`
- Latest published npm version at patch time: `2026.3.2`

## Impact

A remote service that could trigger a redirect across origins could receive custom authorization credentials attached by OpenClaw callers. This can expose API keys, bearer-style custom headers, or private token headers intended only for the original destination.

## Fix Commit(s)

- `46715371b0612a6f9114dffd1466941ac476cef5`

## Verification

- `pnpm check` passed
- `pnpm test:fast` passed
- Focused redirect regression tests passed
- `pnpm exec vitest run --config vitest.gateway.config.ts` still has unrelated current-`main` failures in `src/gateway/server-channels.test.ts` and `src/gateway/server-methods/agents-mutate.test.ts`

## Release Process Note

npm `2026.3.7` was published on March 8, 2026. This advisory is fixed in the released package.

Thanks @Rickidevs for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-6mgf-v5j7-45cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-32913
- https://github.com/openclaw/openclaw/commit/46715371b0612a6f9114dffd1466941ac476cef5
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.7
- https://vulncheck.com/advisories/openclaw-mar-custom-authorization-header-leakage-via-cross-origin-redirects
