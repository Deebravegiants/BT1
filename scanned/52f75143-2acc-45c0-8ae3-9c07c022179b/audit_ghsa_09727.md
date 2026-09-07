# [M] @sveltejs/kit: Unvalidated redirect in handle hook causes Denial-of-Service

## Summary
Severity: Medium
Advisory: GHSA-3f6h-2hrp-w5wx
CVE: CVE-2026-40074
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-3f6h-2hrp-w5wx
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=0 <2.57.1

## Details
`redirect`, when called from inside the `handle` server hook with a location parameter containing characters that are invalid in a HTTP header, will cause an unhandled `TypeError`. This could result in DoS on some platforms, especially if the location passed to `redirect` contains unsanitized user input.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-3f6h-2hrp-w5wx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40074
- https://github.com/sveltejs/kit/commit/10d7b44425c3d9da642eecce373d0c6ef83b4fcd
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/%40sveltejs%2Fkit%402.57.1
- https://github.com/sveltejs/kit/releases/tag/@sveltejs/kit@2.57.1
