# [H] Nuxt: Unauthenticated CPU exhaustion parsing and hashing the Nuxt island endpoint body before hash validation

## Summary
Severity: High
Advisory: GHSA-9pgf-384g-p7mv
CVE: CVE-2026-71321
CWE: CWE-407, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-9pgf-384g-p7mv
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.0.0 <4.5.1
- npm: `nuxt` — affected >=3.1.0 <3.21.10

## Details
### Impact

The internal island renderer endpoint (`/__nuxt_island/...`) decodes and hashes attacker-controlled request input before it validates the URL-resident hash. An unauthenticated `POST /__nuxt_island/<name>_<anything>.json` with a large JSON body (for example ~4.6 MB / 150k keys) is fully read, `destr`-parsed, and run through `ohash` before the request is rejected with a 400. Because Nitro runs on a single event loop, this both wastes CPU on the doomed request and delays every concurrent request. A low request rate is enough to degrade or stall the server. No valid hash and no authentication are required.

### Patches

Fixed in `nuxt@4.5.1` and `nuxt@3.21.10`. The island handler now enforces a raw body-size cap (`413`) and a JSON nesting-depth cap (`400`) before parsing or hashing, so oversized or deeply nested input is rejected cheaply.

### Workarounds

Put a small request-body limit in front of `/__nuxt_island/` at your reverse proxy / edge (islands legitimately send only a compact props payload), or disable server components if unused.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-9pgf-384g-p7mv
- https://github.com/nuxt/nuxt/commit/4e35ae9babd94be53246e31200232d48438bb34e
- https://github.com/nuxt/nuxt/commit/668cdfdfda41849ed11c1ee5e2067a11fc103b22
- https://github.com/nuxt/nuxt
- https://github.com/nuxt/nuxt/releases/tag/v3.21.10
- https://github.com/nuxt/nuxt/releases/tag/v4.5.1
