# [M] mathlive's Lack of Escaping of HTML allows for XSS

## Summary
Severity: Medium
Advisory: GHSA-fm7p-gw32-828p
CVE: CVE-2026-54705
CWE: CWE-116
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-fm7p-gw32-828p
Type: github-advisory

## Affected
- npm: `mathlive` — affected >=0 <0.110.0

## Details
### Summary

Despite the 0.104.0 patch escaping attribute-bearing constructs (`\htmlData`, `\href`), text-content reflection was missed. The `\text{}`, `\mbox{}` commands accept arbitrary characters in their body and emit them raw and unescaped into both the HTML markup and the MathML output, leading to XSS.

### Details

`Box.toMarkup` at `src/core/box.ts:356` concatenates `this.value` into the rendered span without HTML-escaping. In text mode any literal character (`<`, `>`, `&`, `"`) is wrapped into a `TextAtom` whose `value` is the raw codepoint and lands in the markup unchanged. The MathML serializer at `src/formats/atom-to-math-ml.ts` is independently broken: `xmlEscape` deliberately omits the `&` rule, and `scanText`, `case 'text'`, and the `mode === 'text'` early return all emit `atom.value` raw.

Both outputs flow into `innerHTML` sinks via the public API. `<math-span>` / `<math-div>` (`src/public/math-static-elements.ts:331,407`) bypass `MathfieldElement.createHTML` entirely. The editor and SSR paths route through `createHTML`, but its default value is the identity function (`src/public/mathfield-element.ts:789`).

### PoC

1. Go to https://mathlive.io/mathfield/demo/
2. open DevTools console and paste:

```js
const s = document.createElement('math-span');
s.style.display = 'block';
s.textContent = '\\text{<img src=x onerror=alert(1)>}';
document.body.appendChild(s);
s.scrollIntoView();
```

Equivalent payloads: `\mbox{<img src=x onerror=alert(1)>}`

or

```js
import { convertLatexToMarkup } from 'mathlive';
document.body.innerHTML = convertLatexToMarkup('\\text{<img src=x onerror=alert(1)>}');
```

### Impact

MathLive users who render untrusted mathematical expressions can encounter malicious input that runs arbitrary JavaScript.

## References
- https://github.com/arnog/mathlive/security/advisories/GHSA-fm7p-gw32-828p
- https://github.com/arnog/mathlive/issues/3028
- https://github.com/arnog/mathlive/commit/5fe1c46153883f9ec0249a5c8c34e64aaae9cfb8
- https://github.com/arnog/mathlive
