# [M] Svelte Vulnerable to XSS via DOM Clobbering of Internal Framework State

## Summary
Severity: Medium
Advisory: GHSA-rcqx-6q8c-2c42
CVE: CVE-2026-42573
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:L/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-rcqx-6q8c-2c42
Type: github-advisory

## Affected
- npm: `svelte` — affected >=0 <5.55.7

## Details
Svelte was vulnerable to DOM clobbering of its internal framework state on elements, potentially leading to XSS attacks.

You are vulnerable if all of the following is true:
- you are using attribute spreading on a form element
- you are using attribute spreading or allow a dynamic value for the `name` attribute on an input or button element within that form
- both of these are simultaneously user-controllable

```svelte
<form {...spread1}>
  <input {...spread2}>
</form>
```

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-rcqx-6q8c-2c42
- https://nvd.nist.gov/vuln/detail/CVE-2026-42573
- https://github.com/sveltejs/svelte
- https://github.com/sveltejs/svelte/releases/tag/svelte%405.55.7
