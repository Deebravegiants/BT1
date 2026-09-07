# [M] svelte vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-6738-r8g5-qwp3
CVE: CVE-2025-15265
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-6738-r8g5-qwp3
Type: github-advisory

## Affected
- npm: `svelte` — affected >=5.46.0 <5.46.4

## Details
## Summary

An XSS vulnerability exists in Svelte 5.46.0-2 resulting from improper escaping of `hydratable` keys. If these keys incorporate untrusted user input, arbitrary JavaScript can be injected into server-rendered HTML.

## Details

When using the [`hydratable`](https://svelte.dev/docs/svelte/hydratable) function, the first argument is used as a key to uniquely identify the data, such that the value is not regenerated in the browser.

This key is embedded into a `<script>` block in the server-rendered `<head>` without escaping unsafe characters. A malicious key can break out of the script context and inject arbitrary JavaScript into the HTML response.

## Impact

This is a cross-site scripting vulnerability affecting applications that have the `experimental.async` flag enabled and use `hydratable` with keys incorporating untrusted user input. 

- **Impact**: Arbitrary JS execution in the client’s browser.
- **Exploitability**: Remote, single-request if key is attacker-controlled.
- **Typical Outcomes**:
  - Session/token theft
  - DOM defacement
  - CSRF bypass via injected JS
  - Account takeover depending on cookie/session strategy

Affected applications should upgrade to a patched version immediately.

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-6738-r8g5-qwp3
- https://nvd.nist.gov/vuln/detail/CVE-2025-15265
- https://github.com/sveltejs/svelte/commit/ef81048e238844b729942441541d6dcfe6c8ccca
- https://fluidattacks.com/advisories/lydian
- https://github.com/sveltejs/svelte
- https://github.com/sveltejs/svelte/releases/tag/svelte%405.46.4
