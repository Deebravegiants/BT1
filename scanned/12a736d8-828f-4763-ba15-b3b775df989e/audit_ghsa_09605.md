# [C] OpenClaw: Gateway HTTP endpoints re-resolve bearer auth after SecretRef rotation

## Summary
Severity: Critical
Advisory: GHSA-xmxx-7p24-h892
CVE: CVE-2026-43585
CWE: CWE-324, CWE-672
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-xmxx-7p24-h892
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.15

## Details
## Summary

Gateway HTTP and WebSocket handlers captured the resolved bearer-auth configuration when the server started. After a SecretRef rotation, the already-running gateway could continue accepting the old bearer token until restart.

## Impact

A bearer token that should have been revoked by SecretRef rotation could remain valid on the gateway HTTP and upgrade surfaces for the lifetime of the process. Severity remains high because the old token could continue to authorize gateway requests after operators believed it was rotated out.

## Affected versions

- Affected: `< 2026.4.15`
- Patched: `2026.4.15`

## Fix

OpenClaw `2026.4.15` resolves active gateway auth from the runtime secret snapshot per request and per upgrade instead of using a stale startup-time value.

Verified in `v2026.4.15`:

- `src/gateway/server.impl.ts` exposes `getResolvedAuth()` backed by the current runtime secret snapshot.
- `src/gateway/server-http.ts` calls `getResolvedAuth()` for each HTTP request and WebSocket upgrade before running auth checks.
- `src/gateway/server-http.probe.test.ts` verifies `/ready` re-resolves bearer auth after rotation and rejects the old token.

Fix commit included in `v2026.4.15` and absent from `v2026.4.14`:

- `acd4e0a32f12e1ad85f3130f63b42443ce90f094` via PR #66651

Thanks to @zsxsoft, Keen Security Lab, and @qclawer for reporting this issue.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-xmxx-7p24-h892
- https://nvd.nist.gov/vuln/detail/CVE-2026-43585
- https://github.com/openclaw/openclaw/pull/66651
- https://github.com/openclaw/openclaw/commit/acd4e0a32f12e1ad85f3130f63b42443ce90f094
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-bearer-token-validation-bypass-via-stale-secretref-resolution
