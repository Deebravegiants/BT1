# [M] @sveltejs/kit vulnerable to Cross-site Scripting via tracked search_params

## Summary
Severity: Medium
Advisory: GHSA-6q87-84jw-cjhp
CVE: CVE-2025-32388
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-14
Source: https://github.com/advisories/GHSA-6q87-84jw-cjhp
Type: github-advisory

## Affected
- npm: `@sveltejs/kit` — affected >=2.0.0 <2.20.6

## Details
### Summary

Unsanitized search param names cause XSS vulnerability. You are affected if you iterate over all entries of `event.url.searchParams` inside a server `load` function. Attackers can exploit it by crafting a malicious URL and getting a user to click a link with said URL.

### Details

SvelteKit tracks which parameters in `event.url.searchParams` are read inside server `load` functions. If the application iterates over the these parameters, the `uses.search_params` array included in the boot script (embedded in the server-rendered HTML) will have any search param name included in unsanitized form.

`packages/kit/src/runtime/server/utils.js:150` has the `stringify_uses(node)` function which prints these out.

### Reproduction

In a `+page.server.js` or `+layout.server.js`:

```js
/** @type {import('@sveltejs/kit').Load} */
export function load(event) {
  const values = {};

  for (const key of event.url.searchParams.keys()) {
    values[key] = event.url.searchParams.get(key);
  }
}
```

If a user visits the page in question via a link containing `?</script/><script>window.pwned%3D1</script/>`, the `</script>` will be included verbatim in the payload, causing the embedded script to be executed.

It is not necessary to return the parameter value from `load` or render it in the page, only to read it (which causes it to be tracked as a dependency) while `load` is running.

### Impact

Any application that iterates over all values in `event.url.searchParams` in a `load` function in `+page.server.js` or `+layout.server.js` (directly or indirectly) is vulnerable to XSS.

## References
- https://github.com/sveltejs/kit/security/advisories/GHSA-6q87-84jw-cjhp
- https://nvd.nist.gov/vuln/detail/CVE-2025-32388
- https://github.com/sveltejs/kit/commit/d3300c6a67908590266c363dba7b0835d9a194cf
- https://github.com/sveltejs/kit
- https://github.com/sveltejs/kit/releases/tag/%40sveltejs%2Fkit%402.20.6
