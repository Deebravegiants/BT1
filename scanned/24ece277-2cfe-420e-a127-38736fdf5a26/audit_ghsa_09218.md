# [M] @sveltejs/kit: `query.batch` cross-talk

## Summary
Severity: Medium
Advisory: GHSA-hgv7-v322-mmgr
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-hgv7-v322-mmgr
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=2.38.0 <2.60.1

## Details
`query.batch()` could, under very rare and specific timings, cause concurrent requests from different users to merge and resolve under single request context, enabling cross-user data disclosure.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-hgv7-v322-mmgr
- https://github.com/sveltejs/kit/commit/dadaefc2e647a0a62f49f3ee8bc7aa46f5e27056
- https://github.com/sveltejs/kit
