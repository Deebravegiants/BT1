# [M] Mermaid: Improper sanitization of `classDefs` in diagrams leads to CSS injection

## Summary
Severity: Medium
Advisory: GHSA-xcj9-5m2h-648r
CVE: CVE-2026-41148
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-xcj9-5m2h-648r
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=11.0.0-alpha.1 <11.15.0
- npm: `mermaid` — affected >=0 <10.9.6

## Details
### Details

The state diagram and any other diagram type that routes user-controlled style strings through createCssStyles parser for Mermaid v11.14.0 and earlier captures `classDef` values with an unrestricted regex:

```jison
// packages/mermaid/src/diagrams/state/parser/stateDiagram.jison:83
<CLASSDEFID>[^\n]*   { this.popState(); return 'CLASSDEF_STYLEOPTS' }
```

The value passes unsanitized through `addStyleClass()` -> `createCssStyles()` -> `style.innerHTML` (mermaidAPI.ts:418). A `}` in the value closes the generated CSS selector, and everything after becomes a new CSS rule on the page.

### PoC

```
stateDiagram-v2 
      classDef x }*{ background-image: url("http://media.giphy.com/media/SggILpMXO7Xt6/giphy.gif")}
```

Live demo:
<https://mermaid.live/edit#pako:eNpFjzFvgzAQhf-KdVNbEcBgMHhtlkqtOnSJKi8ONsYKBmRMlRTx3-skanvTfbp7996t0IxSAYPZC6_2Rmgn7O4rQ00v5nmvWnRG29OKjqI5aTcug9wZK7RiaHH9A4fO-4kliVXSiFibqbvEzWjvnHxo_fI6vR3e6cGXyX2qTcvhcYMItDMSmHeLisAqZ8UVYeUDQhx8p6ziwEIrhTtx4MNVM4nhcxztrywE0h2wVvRzoGWS_z_8rahBKvcckntgmN5OAFvhDIzUNCZZQXCR5nVaZkUEF2BVFpOcEkoxxhUuyRbB980yjStapKHqoKFlhvPtB7BFZEU>

### Patches

This has been patched in:

- [v11.15.0](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.15.0) (see [e9b0f34d8d82a6260077764ee45e1d7d90957a0f](https://github.com/mermaid-js/mermaid/commit/e9b0f34d8d82a6260077764ee45e1d7d90957a0f))
- [v10.9.6](https://github.com/mermaid-js/mermaid/releases/tag/v10.9.6) (see [8fead23c59166b7bab6a39eac81acebee2859102](https://github.com/mermaid-js/mermaid/commit/8fead23c59166b7bab6a39eac81acebee2859102))

### Workarounds

Setting [`"securityLevel": "sandbox"`](https://mermaid.js.org/config/schema-docs/config.html#securitylevel)  will prevent this, by rendering the mermaid diagram in a sandboxed `<iframe>`.

### Impact

 Enables page defacement, user tracking via `url()` callbacks, and DOM attribute exfiltration via CSS `:has()` selectors.

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-xcj9-5m2h-648r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41148
- https://github.com/mermaid-js/mermaid/commit/8fead23c59166b7bab6a39eac81acebee2859102
- https://github.com/mermaid-js/mermaid/commit/e9b0f34d8d82a6260077764ee45e1d7d90957a0f
- https://github.com/mermaid-js/mermaid
- https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.15.0
- https://github.com/mermaid-js/mermaid/releases/tag/v10.9.6
- https://mermaid.js.org/config/schema-docs/config.html#securitylevel
