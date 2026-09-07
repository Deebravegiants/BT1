# [M] Svelte vulnerable to XSS when using objects during server-side rendering

## Summary
Severity: Medium
Advisory: GHSA-wv8q-r932-8hc7
CVE: CVE-2022-25875
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-13
Source: https://github.com/advisories/GHSA-wv8q-r932-8hc7
Type: github-advisory

## Affected
- npm: `svelte` — affected >=0 <3.49.0

## Details
The package svelte before 3.49.0 is vulnerable to Cross-site Scripting (XSS) due to improper input sanitization and to improper escape of attributes when using objects during SSR (Server-Side Rendering). Exploiting this vulnerability is possible via objects with a custom toString() function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25875
- https://github.com/sveltejs/svelte/pull/7530#23issuecomment-1158575990
- https://github.com/sveltejs/svelte/commit/f8605d6acbf66976da9b4547f76e90e163899907
- https://github.com/sveltejs/svelte
- https://snyk.io/vuln/SNYK-JS-SVELTE-2931080
