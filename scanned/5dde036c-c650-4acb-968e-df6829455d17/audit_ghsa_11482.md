# [M] Cross-Site Scripting (XSS) via SVG Schema innerHTML Injection in @pdfme/schemas

## Summary
Severity: Medium
Advisory: GHSA-87v3-4cfp-cm76
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-87v3-4cfp-cm76
Type: github-advisory

## Affected
- npm: `@pdfme/schemas` — affected >=0 <5.5.9

## Details
## Summary

The SVG schema plugin in `@pdfme/schemas` renders user-supplied SVG content using `container.innerHTML = value` without any sanitization, enabling arbitrary JavaScript execution in the user's browser.

## Details

In `packages/schemas/src/graphics/svg.ts`, line 87, the SVG schema's `ui` renderer assigns raw SVG markup directly to `innerHTML` when in viewer mode or form mode with `readOnly: true`:

```typescript
// svg.ts, line 81-94 (non-editable rendering path)
} else {
  if (!value) return;
  if (!isValidSVG(value)) {
    rootElement.appendChild(createErrorElm());
    return;
  }
  container.innerHTML = value;  // <-- VULNERABLE: unsanitized SVG injected into DOM
  const svgElement = container.childNodes[0];
  if (svgElement instanceof SVGElement) {
    svgElement.setAttribute('width', '100%');
    svgElement.setAttribute('height', '100%');
    rootElement.appendChild(container);
  }
}
```

The `isValidSVG()` function (lines 11-37) only validates that the string contains `<svg` and `</svg>` tags and passes `DOMParser` well-formedness checks. It does NOT strip or block:
- `<script>` tags embedded in SVG
- Event handler attributes (`onload`, `onerror`, `onclick`, etc.)
- `<foreignObject>` elements containing HTML with event handlers
- `<animate>` / `<set>` elements with `onbegin` / `onend` handlers
- SVG `<use>` elements referencing malicious external resources

All of these are valid SVG and pass `isValidSVG()`, but execute JavaScript when inserted via `innerHTML`.

## Attack Vectors

### 1. Malicious Template (readOnly SVG schema)
An attacker crafts a template JSON with a readOnly SVG schema containing a malicious `content` value. When loaded into the pdfme Form or Viewer component, the SVG executes JavaScript.

### 2. Application-Supplied Inputs + Viewer
If an application uses the pdfme Viewer component and passes user-controlled data as inputs for a non-readOnly SVG schema, the attacker's SVG flows directly to `innerHTML`.

## Proof of Concept

Loading the following template into a pdfme Form or Viewer component triggers JavaScript execution:

```json
{
  "basePdf": { "width": 210, "height": 297, "padding": [20, 20, 20, 20] },
  "schemas": [[
    {
      "name": "malicious_svg",
      "type": "svg",
      "content": "<svg xmlns='http://www.w3.org/2000/svg' onload='alert(document.domain)'><rect width='100' height='100' fill='red'/></svg>",
      "readOnly": true,
      "position": { "x": 20, "y": 20 },
      "width": 80,
      "height": 40
    }
  ]]
}
```

Additional payloads that bypass `isValidSVG()` and execute JavaScript:

```svg
<!-- Via foreignObject -->
<svg xmlns="http://www.w3.org/2000/svg"><foreignObject width="200" height="60"><body xmlns="http://www.w3.org/1999/xhtml"><img src="x" onerror="alert(1)"/></body></foreignObject></svg>

<!-- Via animate onbegin -->
<svg xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100"><animate attributeName="x" values="0" dur="0.001s" onbegin="alert(1)"/></rect></svg>
```

## Impact

An attacker who can supply a malicious template (via file upload, shared template URL, multi-tenant template storage, or `updateTemplate()` API) can execute arbitrary JavaScript in the context of any user who views or fills the template. This enables:
- Session hijacking via cookie/token theft
- Keylogging of form inputs (including sensitive data being entered into PDF forms)
- Phishing attacks by modifying the rendered page
- Data exfiltration from the application

The attack is particularly concerning for multi-tenant SaaS applications using pdfme where templates may be user-supplied.

## Suggested Fix

Sanitize SVG content before DOM insertion using DOMPurify or a similar library:

```typescript
import DOMPurify from 'dompurify';

// Replace line 87:
container.innerHTML = DOMPurify.sanitize(value, { USE_PROFILES: { svg: true } });
```

Alternatively, parse the SVG via `DOMParser`, strip all script elements and event handler attributes, then append the sanitized DOM nodes.

## References
- https://github.com/pdfme/pdfme/security/advisories/GHSA-87v3-4cfp-cm76
- https://github.com/pdfme/pdfme
