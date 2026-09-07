# [M] Svelte: XSS via HTML Comment Injection in SSR Error Boundary Hydration Markers

## Summary
Severity: Medium
Advisory: GHSA-qgvg-pr8v-6rr3
CVE: CVE-2026-27902
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:L/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-qgvg-pr8v-6rr3
Type: github-advisory

## Affected
- npm: `svelte` — affected >=5.53.0 <5.53.5

## Details
Errors from `transformError` were not correctly escaped prior to being embedded in the HTML output, causing potential HTML injection and XSS if attacker-controlled content is returned from `transformError`.

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-qgvg-pr8v-6rr3
- https://nvd.nist.gov/vuln/detail/CVE-2026-27902
- https://github.com/sveltejs/svelte/commit/0298e979371bb583855c9810db79a70a551d22b9
- https://github.com/sveltejs/svelte
- https://github.com/sveltejs/svelte/releases/tag/svelte@5.53.5
