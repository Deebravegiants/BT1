# [H] locize Client SDK: Cross-origin DOM XSS & Handler Hijack Through Missing e.origin Validation in InContext Editor 

## Summary
Severity: High
Advisory: GHSA-w937-fg2h-xhq2
CVE: CVE-2026-41886
CWE: CWE-346, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-w937-fg2h-xhq2
Type: github-advisory

## Affected
- npm: `locize` — affected >=0 <4.0.21

## Details
### Summary

Versions of the `locize` client SDK (the browser module that wires up the locize InContext translation editor) prior to 4.0.21 register a `window.addEventListener("message", …)` handler that dispatches to registered internal handlers (`editKey`, `commitKey`, `commitKeys`, `isLocizeEnabled`, `requestInitialize`, …) **without validating `event.origin`**.

The pre-patch listener in `src/api/postMessage.js` gates dispatch on `event.data.sender === "i18next-editor-frame"` — that value sits inside the attacker-controlled message payload, not the browser-enforced origin. Any web page that could embed or be embedded by a locize-enabled host — an iframe on a third-party page, a `window.open`-ed victim, a parent frame reaching down — could send a crafted `postMessage` and trigger the internal handlers.

### Impact

Depending on which handler the attacker invokes, distinct consequences follow. All of them share the same root cause: the handlers implicitly assumed the payload came from the real editor iframe.

- **Cross-origin DOM XSS** via `editKey` / `commitKeys`: the pre-patch `handleEditKey` assigned attacker-controlled payload values to `item.node.innerHTML` and to `item.node.setAttribute(attr, value)`. That allowed planting `<script>`, `<img onerror>`, or `onclick`/`onload`/`onfocus` event handlers; and on attribute writes, `href="javascript:…"` / `src="data:text/html,<script>…"` / `style="…"` / etc.

- **`api.source` / `api.origin` hijack** via `isLocizeEnabled`: the handler set `api.source = e.source; api.origin = e.origin` — attacker-controlled values. All subsequent `sendMessage` calls (which post translations, callbacks, etc., back toward `api.source`) would go to the attacker window rather than the real editor, leaking translation content and any metadata the SDK forwards.

- **CSS-injection / layout-escape** via `requestPopupChanges`: `containerStyle.height` / `.width` were interpolated into `calc()` expressions and `popup.style.setProperty()` without validation, allowing attackers to inject additional CSS declarations (semicolons, `behavior:url()` on legacy IE, CSS-exfil patterns) into the popup inline style.

Exploitation requires the attacker-owned page to share a window reference with the locize-enabled host: typical vectors are an `iframe` on an attacker-controlled page, a `window.opener`/`window.open` relationship, or a parent frame that can `postMessage` into an embedded locize host. The SDK intended model is that only the editor iframe at `https://incontext.locize.app` (or the configured staging/development origin) can reach these handlers.

### Affected versions

All versions of `locize` prior to **4.0.21**.

### Patch

Fixed in **4.0.21**. Two layers:

1. **Primary** — validate `event.origin` at the top of `window.addEventListener("message", …)` in `src/api/postMessage.js`. The expected origin is the configured iframe origin (`getIframeUrl()`), so custom environments continue to work. Messages from any other origin are silently dropped before any handler runs.

2. **Defence-in-depth** — `handleEditKey` now rejects dangerous attribute-name writes (`on*`, `style`) and `javascript:` / `data:` / `vbscript:` / `file:` URLs on `href` / `src` / `action` / `formaction` / `xlink:href`; `innerHTML` assignments are sanitised through a throwaway DOMParser document (stripping `<script>`, `<iframe>`, `<object>`, `<embed>`, `<link>`, `<meta>`, `<base>`, `<style>` plus event handlers and dangerous URL schemes). Legitimate translation formatting (`<b>`, `<em>`, `<strong>`, `<a href="https://…">`, etc.) passes through.

3. **CSS-injection** — `handleRequestPopupChanges` now requires `containerStyle.height` / `.width` to match a strict CSS length pattern; malformed values are dropped silently.

### Workarounds

No workaround short of upgrading.

### Credits

Discovered via an internal security audit of the locize ecosystem.

## References
- https://github.com/locize/locize/security/advisories/GHSA-w937-fg2h-xhq2
- https://nvd.nist.gov/vuln/detail/CVE-2026-41886
- https://github.com/locize/locize/commit/d006b75fadb8e8ab77b023e462850fc6e9170735
- https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage#security_concerns
- https://github.com/locize/locize
- https://github.com/locize/locize/releases/tag/v4.0.21
