# [M] Svelte affected by XSS in SSR `<option>` element

## Summary
Severity: Medium
Advisory: GHSA-h7h7-mm68-gmrc
CVE: CVE-2026-27119
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:L/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-h7h7-mm68-gmrc
Type: github-advisory

## Affected
- npm: `svelte` — affected >=5.39.3 <5.51.5

## Details
In certain circumstances, the server-side rendering output of an `<option>` element does not properly escape its content, potentially allowing HTML injection in the SSR output. Client-side rendering is not affected.

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-h7h7-mm68-gmrc
- https://nvd.nist.gov/vuln/detail/CVE-2026-27119
- https://github.com/sveltejs/svelte
