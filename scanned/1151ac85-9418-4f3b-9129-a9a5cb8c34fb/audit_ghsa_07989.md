# [M] Svelte SSR attribute spreading includes inherited properties from prototype chain

## Summary
Severity: Medium
Advisory: GHSA-crpf-4hrx-3jrp
CVE: CVE-2026-27125
CWE: CWE-915
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:L/VI:L/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-crpf-4hrx-3jrp
Type: github-advisory

## Affected
- npm: `svelte` — affected >=0 <5.51.5

## Details
In server-side rendering, attribute spreading on elements (e.g. `<div {...attrs}>`) enumerates inherited properties from the object's prototype chain rather than only own properties. In environments where `Object.prototype` has already been polluted — a precondition outside of Svelte's control — this can cause unexpected attributes to appear in SSR output or cause SSR to throw errors. Client-side rendering is not affected.

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-crpf-4hrx-3jrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-27125
- https://github.com/sveltejs/svelte/commit/73098bb26c6f06e7fd1b0746d817d2c5ee90755f
- https://github.com/sveltejs/svelte
- https://github.com/sveltejs/svelte/releases/tag/svelte@5.51.5
