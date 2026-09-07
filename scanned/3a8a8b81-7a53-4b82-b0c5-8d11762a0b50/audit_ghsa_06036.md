# [M] DOMPurify: IN_PLACE hook removal leaves a detached subtree executable, causing XSS

## Summary
Severity: Medium
Advisory: GHSA-55q2-fjhq-7xh7
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-55q2-fjhq-7xh7
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.4.13

## Details
### Summary

During `IN_PLACE` sanitization, a hook that removes an element can leave that element's detached descendants executable. A descendant image can retain its attacker-provided `onload` handler and fire after `sanitize()` returns, even though the returned root is clean and the image remains disconnected from the document.

### Details

In DOMPurify 3.4.12, `_sanitizeElements()` in `src/purify.ts:1862-1904` runs the `beforeSanitizeElements` or `uponSanitizeElement` hook and returns immediately when the hook detached the current node. The return does not call `_neutralizeSubtree(currentNode)`.

The detached subtree is not added to `DOMPurify.removed`, so the post-walk `IN_PLACE` neutralization cannot reach it. If the browser queued a resource event while the application constructed the detached dirty root, a descendant can therefore retain its handler and execute after sanitization.

The hook only rejects the containing element and does not add or approve the event handler. DOMPurify's ordinary removal path de-arms the same queued event; only the hook-detachment early return skips the existing subtree neutralization.

### PoC

Load the published `dompurify@3.4.12` `dist/purify.js` before this script in Chromium:

```html
<div id="result">not fired</div>
<script>
const root = document.createElement('div');
root.innerHTML = `
  <footer>
    <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
         onload="result.textContent = 'XSS after sanitize'">
  </footer>
  <div>safe</div>`;

DOMPurify.setConfig({
  ALLOWED_TAGS: ['div', '#text', 'footer'],
  IN_PLACE: true
});
DOMPurify.addHook('uponSanitizeElement', node => {
  if (node.tagName === 'FOOTER') node.remove();
});

DOMPurify.sanitize(root);
document.body.append(root);
</script>
```

`sanitize()` returns with no handler execution and the returned root contains only the safe `div`. After the event loop advances, the original image remains disconnected but its retained `onload` changes the page to `XSS after sanitize`.

As the claim-matched control, use the same detached input with `ALLOWED_TAGS: ['div', '#text']` and no hook. DOMPurify's ordinary removal path removes the original image's handler, the returned root is still `<div>safe</div>`, and the marker does not fire.

### Impact

In an application that uses `IN_PLACE` with the documented element-removal hook pattern, an attacker who can supply HTML can execute JavaScript in the integrating application's origin after the application sanitizes and renders that content.

The required non-default configuration is `IN_PLACE` plus a hook that removes a containing element. The hook does not add or approve the event handler, and the dirty root never needs to be connected before sanitization.

### Suggested fix

Reuse the existing `_neutralizeSubtree(currentNode)` helper before returning from both hook-detachment branches in `_sanitizeElements()`. Add regressions for `beforeSanitizeElements` and `uponSanitizeElement` that retain a reference to a descendant resource element and verify that its event handler is removed after the hook detaches its ancestor.

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-55q2-fjhq-7xh7
- https://github.com/cure53/DOMPurify/pull/1557
- https://github.com/cure53/DOMPurify/commit/3067f7746769
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/releases/tag/3.4.13
