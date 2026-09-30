# [M] OpenClaw has hook auth rate limiter bypass via IPv4-mapped IPv6 client key variants

## Summary
Severity: Medium
Advisory: GHSA-5847-rm3g-23mw
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-5847-rm3g-23mw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.22

## Details
## Vulnerability

The hook authentication throttle keyed failed attempts by raw socket `remoteAddress` text.

IPv4 and IPv4-mapped IPv6 forms of the same client (for example `1.2.3.4` and `::ffff:1.2.3.4`) were treated as different clients, allowing separate rate-limit buckets.

## Impact

An attacker could split failed hook-auth attempts across both address forms and effectively double the brute-force budget from 20 to 40 attempts per 60-second window.

## Affected Components

- `src/gateway/server-http.ts`
- `src/gateway/auth-rate-limit.ts`

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Vulnerable versions: `<= 2026.2.21-2`
- Patched version (planned next release): `2026.2.22`

## Remediation

Centralize and reuse canonical client-IP normalization for auth rate-limiting, and use that canonical key for hook auth throttling.

## Fix Commit(s)

- `3284d2eb227e7b6536d543bcf5c3e320bc9d13c5`

## Release Process Note

`patched_versions` is pre-set to the planned next release (`2026.2.22`) so once npm release `2026.2.22` is published, this advisory can be published directly.

OpenClaw thanks @aether-ai-agent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-5847-rm3g-23mw
- https://github.com/openclaw/openclaw/commit/3284d2eb227e7b6536d543bcf5c3e320bc9d13c5
- https://github.com/openclaw/openclaw
