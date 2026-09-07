# [M] Svelte vulnerable to XSS during SSR with contenteditable `bind:innerText` and `bind:textContent`

## Summary
Severity: Medium
Advisory: GHSA-phwv-c562-gvmh
CVE: CVE-2026-27901
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:L/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-phwv-c562-gvmh
Type: github-advisory

## Affected
- npm: `svelte` — affected >=0 <5.53.5

## Details
The contents of `bind:innerText` and `bind:textContent` on `contenteditable` elements were not properly escaped. This could enable HTML injection and Cross-site Scripting (XSS) if rendering untrusted data as the binding's initial value on the server.

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-phwv-c562-gvmh
- https://nvd.nist.gov/vuln/detail/CVE-2026-27901
- https://github.com/sveltejs/svelte/commit/0df5abcae223058ceb95491470372065fb87951d
- https://github.com/sveltejs/svelte
- https://github.com/sveltejs/svelte/releases/tag/svelte@5.53.5
