# [M] Svelte affected by cross-site scripting via spread attributes in Svelte SSR

## Summary
Severity: Medium
Advisory: GHSA-f7gr-6p89-r883
CVE: CVE-2026-27121
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:N/VC:L/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-f7gr-6p89-r883
Type: github-advisory

## Affected
- npm: `svelte` — affected >=0 <5.51.5

## Details
Versions of svelte prior to 5.51.5 are vulnerable to cross-site scripting (XSS) during server-side rendering. When using spread syntax to render attributes from untrusted data, event handler properties are included in the rendered HTML output. If an application spreads user-controlled or external data as element attributes, an attacker can inject malicious event handlers that execute in victims' browsers.

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-f7gr-6p89-r883
- https://nvd.nist.gov/vuln/detail/CVE-2026-27121
- https://github.com/sveltejs/svelte
