# [M] Cross-Site Scripting (XSS) via Select Schema Option Value Injection in @pdfme/schemas

## Summary
Severity: Medium
Advisory: GHSA-qq9g-96v4-m3cj
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-qq9g-96v4-m3cj
Type: github-advisory

## Affected
- npm: `@pdfme/schemas` — affected >=0 <5.5.9

## Details
## Summary

The Select schema plugin in `@pdfme/schemas` constructs HTML from template-defined option values using unsanitized string interpolation and sets it via `innerHTML`, enabling arbitrary JavaScript execution.

## Details

In `packages/schemas/src/select/index.ts`, lines 159-164, the Select schema's `ui` renderer builds `<option>` elements by directly interpolating option values from the template into an HTML string:

```typescript
const options = Array.isArray(schema.options) ? schema.options : [];
selectElement.innerHTML = options
  .map(
    (option) =>
      `<option value="${option}" ${option === value ? 'selected' : ''}>${option}</option>`,
  )
  .join('');
```

The `option` values come from `schema.options`, which is an array of strings defined in the template JSON. These values are interpolated directly into the HTML string without any escaping of `<`, `>`, `"`, `&`, or other HTML-special characters. An option value containing `">` breaks out of the `value` attribute and allows injection of arbitrary HTML elements and event handlers.

## Proof of Concept

Loading the following template into a pdfme Form or Designer component triggers JavaScript execution:

```json
{
  "basePdf": { "width": 210, "height": 297, "padding": [20, 20, 20, 20] },
  "schemas": [[
    {
      "name": "malicious_select",
      "type": "select",
      "content": "Normal",
      "options": [
        "Normal",
        "\"></option><img src=x onerror=\"alert(document.domain)\">"
      ],
      "position": { "x": 20, "y": 20 },
      "width": 80,
      "height": 10
    }
  ]]
}
```

The injected `<img onerror>` element executes JavaScript because it is parsed as HTML when assigned to `selectElement.innerHTML`.

## Attack Vectors

The `options` array is defined in the template (not by form-filling end users). The attack requires a malicious template to be loaded, which can happen via:
1. File upload (e.g., "Load Template" functionality in applications)
2. Shared/imported templates in multi-tenant applications
3. Templates stored in databases without content sanitization
4. The `updateTemplate()` API being called with untrusted data

This vulnerability is triggered in Form mode (for non-readOnly select fields) and Designer mode when the select element is rendered.

## Impact

An attacker who can supply a malicious template can execute arbitrary JavaScript in the browser of any user who views or interacts with the template. This enables:
- Session hijacking via cookie/token theft
- Keylogging of form input data
- Phishing and page modification
- Data exfiltration

## Suggested Fix

Use DOM APIs to create option elements safely instead of string interpolation:

```typescript
options.forEach((option) => {
  const optionEl = document.createElement('option');
  optionEl.value = option;
  optionEl.textContent = option;
  if (option === value) optionEl.selected = true;
  selectElement.appendChild(optionEl);
});
```

Alternatively, HTML-encode option values before interpolation:
```typescript
const escape = (s) => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
```

## References
- https://github.com/pdfme/pdfme/security/advisories/GHSA-qq9g-96v4-m3cj
- https://github.com/pdfme/pdfme
