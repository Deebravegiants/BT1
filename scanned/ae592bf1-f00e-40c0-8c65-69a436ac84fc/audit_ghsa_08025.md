# [M] Svelte SSR does not validate dynamic element tag names in `<svelte:element>`

## Summary
Severity: Medium
Advisory: GHSA-m56q-vw4c-c2cp
CVE: CVE-2026-27122
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:L/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-m56q-vw4c-c2cp
Type: github-advisory

## Affected
- npm: `svelte` — affected >=0 <5.51.5

## Details
When using `<svelte:element this={tag}>` in server-side rendering, the provided tag name is not validated or sanitized before being emitted into the HTML output. If the tag string contains unexpected characters, it can result in HTML injection in the SSR output. Client-side rendering is not affected.

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-m56q-vw4c-c2cp
- https://nvd.nist.gov/vuln/detail/CVE-2026-27122
- https://github.com/sveltejs/svelte
