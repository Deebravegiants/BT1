# [M] Mermaid allows CSS injection applying to sibling elements of the diagram

## Summary
Severity: Medium
Advisory: GHSA-6x64-9x62-f2gx
CVE: CVE-2026-50159
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-08-06
Source: https://github.com/advisories/GHSA-6x64-9x62-f2gx
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=11.0.0-alpha.1 <11.16.1
- npm: `mermaid` — affected >=0 <10.9.8

## Details
### Summary

Mermaid does not fully restrict CSS to the rendered SVG subtree. Although selectors are prefixed with `#mermaid-X`, sibling (`~` and `+`) combinators can still escape the Mermaid container and inject styles to DOM elements adjacent to the diagram `<svg>`.

**Most users of mermaid would not be affected by this**, as mermaid adds its `<svg>` as an only child of it's parent element. However, you may be affected if you manually insert the `<svg>` (or other elements) into the DOM yourself.

### Details

Mermaid namespaces CSS through with a middleware intended to scope all rules to the diagram's SVG element. CSS nesting expands `& ~ * { ... }` to `#svgId ~ *`, which selects all sibling elements following the SVG in the DOM, outside the diagram boundary.

### Impact

An attacker able to supply diagram source to a page (e.g., user-generated content rendered by Mermaid) could inject CSS rules affecting sibling elements to the diagram `<svg>` on the host page. This can be used for UI redressing, hiding content, conditional CSS-based probing, or phishing-style visual manipulation.

JavaScript execution is not possible via this vector.

### Patches

This has been patched in https://github.com/mermaid-js/mermaid/commit/12d472c9ed43f94814b110da8d7a9ae6dd5266ed and released in [Mermaid v11.16.1](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1).

A backport has been made for the v10 branch in 7e83f1533318b307764d961906a73377266f4c5e and was released in [Mermaid v10.9.8](https://github.com/mermaid-js/mermaid/releases/tag/v10.9.8)

### Workarounds

If you are inserting the `<svg>` into the DOM yourself, you can wrap it in an element with no other children, e.g. `<div><svg>...</svg></div>` or `element.innerHTML = svg`. Alternatively, you can use `mermaid.run()` or `mermaid.initialize()`  which will do this for you. 

Setting ["securityLevel": "sandbox"](https://mermaid.js.org/config/schema-docs/config.html#securitylevel) will also prevent this, or setting the [`secure`](https://mermaid.js.org/config/schema-docs/config.html#secure) config value in the mermaid config to avoid allowing diagrams to modify `fontFamily`, `themeCSS`, `altFontFamily`, and `themeVariables`.

To test, you can try using a `themeCSS` with `& + * { /* my CSS here */}` and see if it's applied outside of your mermaid `<svg>`.

```mermaid-example
---
config:
  themeCSS: |-
    & + * { background:red !important; width:100vw !important; height:100vh !important; position:fixed !important; inset:0 !important; }
---
info
```

### References

- GHSA-87f9-hvmw-gh4p/CVE-2026-41159 (related vulnerability)
- https://github.com/mermaid-js/mermaid/commit/12d472c9ed43f94814b110da8d7a9ae6dd5266ed
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.16.1
- https://github.com/mermaid-js/mermaid/commit/7e83f1533318b307764d961906a73377266f4c5e
- https://github.com/mermaid-js/mermaid/releases/tag/v10.9.8

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-6x64-9x62-f2gx
- https://github.com/mermaid-js/mermaid/pull/8022
- https://github.com/mermaid-js/mermaid/commit/12d472c9ed43f94814b110da8d7a9ae6dd5266ed
- https://github.com/mermaid-js/mermaid/commit/7e83f1533318b307764d961906a73377266f4c5e
- https://github.com/mermaid-js/mermaid
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid@11.16.1
- https://github.com/mermaid-js/mermaid/releases/tag/v10.9.8
