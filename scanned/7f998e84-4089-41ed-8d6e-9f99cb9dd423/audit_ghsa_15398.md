# [M] Qwik has a potential mXSS vulnerability due to improper HTML escaping

## Summary
Severity: Medium
Advisory: GHSA-2rwj-7xq8-4gx4
CVE: CVE-2024-41677
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-08-06
Source: https://github.com/advisories/GHSA-2rwj-7xq8-4gx4
Type: github-advisory

## Affected
- npm: `@builder.io/qwik` — affected >=0 <1.7.3

## Details
### Summary

A potential mXSS vulnerability exists in Qwik for versions up to 1.6.0.

### Details

Qwik improperly escapes HTML on server-side rendering. It converts strings according to the following rules:

https://github.com/QwikDev/qwik/blob/v1.5.5/packages/qwik/src/core/render/ssr/render-ssr.ts#L1182-L1208

- If the string is an attribute value:
    - `"` -> `&quot;`
    - `&` -> `&amp;`
    - Other characters -> No conversion
- Otherwise:
    - `<` -> `&lt;`
    - `>` -> `&gt;`
    - `&` -> `&amp;`
    - Other characters -> No conversion

It sometimes causes the situation that the final DOM tree rendered on browsers is different from what Qwik expects on server-side rendering. This may be leveraged to perform XSS attacks, and a type of the XSS is known as mXSS (mutation XSS).

## PoC

A vulnerable component:
```javascript
import { component$ } from "@builder.io/qwik";
import { useLocation } from "@builder.io/qwik-city";

export default component$(() => {
  
  // user input
  const { url } = useLocation();
  const href = url.searchParams.get("href") ?? "https://example.com";

  return (
    <div>
      <noscript>
        <a href={href}>test</a>
      </noscript>
    </div>
  );
});
```

If a user accesses the following URL,
```
http://localhost:4173/?href=</noscript><script>alert(123)</script>
```
then, `alert(123)` will be executed.

### Impact

XSS

## References
- https://github.com/QwikDev/qwik/security/advisories/GHSA-2rwj-7xq8-4gx4
- https://nvd.nist.gov/vuln/detail/CVE-2024-41677
- https://github.com/QwikDev/qwik/commit/7e742eb3a1001542d795776c0317d47df8b9d64e
- https://github.com/QwikDev/qwik
- https://github.com/QwikDev/qwik/blob/v1.5.5/packages/qwik/src/core/render/ssr/render-ssr.ts#L1182-L1208
