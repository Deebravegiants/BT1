# [M] Valibot: record() issue paths can make flatten() throw for inherited Object property names

## Summary
Severity: Medium
Advisory: GHSA-5qjj-4xww-7phc
CVE: CVE-2026-59952
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-5qjj-4xww-7phc
Type: github-advisory

## Affected
- npm: `valibot` — affected >=0 <1.4.2

## Details
## Summary

`valibot` 1.4.1 can throw a `TypeError` inside its `flatten()` helper when validation issues contain attacker-controlled object keys such as `toString`, `valueOf`, or `hasOwnProperty`.

The issue is reachable through normal `record()` validation. `record()` intentionally filters `__proto__`, `prototype`, and `constructor`, but it still accepts other own keys that collide with inherited `Object.prototype` properties. If the record key schema or value schema rejects such an entry, Valibot creates an issue path containing that key. Passing the resulting issues to Valibot's documented `flatten()` helper causes `flatErrors.nested[dotPath]` to resolve to the inherited method instead of an own error array, and the helper calls `.push(...)` on that function.

This is not a global prototype pollution issue. The impact is availability/error handling: applications that validate user-controlled objects with `record()` and flatten validation errors for API responses can crash the request path with a `TypeError` instead of returning structured validation errors.

## Affected package

- Ecosystem: npm
- Package: `valibot`
- Affected version verified: `1.4.1`
- Fixed version: none known
- Repository: `open-circle/valibot`
- Current main ref tested by source review: `9bb6617`

## Root cause

`record()` uses `_isValidObjectKey()` before validating record entries. The helper blocks the three classic prototype pollution keys:

```ts
key !== '__proto__' &&
key !== 'prototype' &&
key !== 'constructor'
```

It does not block other inherited `Object.prototype` names such as `toString`, `valueOf`, and `hasOwnProperty`. These remain valid own JSON object keys and can appear in issue paths when either the record key schema or value schema rejects the entry.

`flatten()` then creates nested error storage with an ordinary object:

```ts
flatErrors.nested = {};
```

For a dot path such as `toString`, this check reads the inherited `Object.prototype.toString` function:

```ts
if (flatErrors.nested![dotPath]) {
  flatErrors.nested![dotPath]!.push(issue.message);
}
```

Because the inherited function is truthy, `flatten()` calls `.push(...)` on a function and throws `TypeError: flatErrors.nested[dotPath].push is not a function`.

## Impact

A remote attacker can trigger this if an application:

1. validates attacker-controlled JSON objects with `v.record(...)`;
2. receives an invalid key or invalid value under a key such as `toString`;
3. uses Valibot's `flatten(result.issues)` helper to prepare validation errors.

This is a common pattern in API/form validation: `safeParse()` collects issues and `flatten()` converts them into response-friendly error objects. Instead of a validation response, the request can hit an unexpected exception path.

The same root cause can also affect manually constructed issues or other schemas that place inherited Object property names into dot paths. I am reporting the `record()` path because it uses only public Valibot APIs and attacker-controlled JSON keys.

## Local reproduction

Run in a disposable directory:

```bash
npm install valibot@1.4.1
node poc_record_flatten_inherited_key_dos.mjs
```

Minimal example:

```js
import * as v from 'valibot';

const schema = v.record(v.string(), v.number());
const input = JSON.parse('{"toString":"not-a-number"}');

const result = v.safeParse(schema, input);
console.log(result.success); // false
console.log(result.issues[0].path.map((item) => item.key)); // ["toString"]

v.flatten(result.issues); // TypeError
```

Observed output from `valibot@1.4.1`:

```json
{
  "name": "record value schema rejects attacker-controlled value",
  "key": "toString",
  "success": false,
  "issueCount": 1,
  "firstPath": ["toString"],
  "firstMessage": "Invalid type: Expected number but received \"not-a-number\"",
  "flattened": {
    "ok": false,
    "exception": "TypeError",
    "message": "flatErrors.nested[dotPath].push is not a function"
  }
}
```

The local PoC also reproduces the same exception for `valueOf`, `hasOwnProperty`, `isPrototypeOf`, `propertyIsEnumerable`, and `toLocaleString`. A control case with an ordinary key produces normal flattened errors.

## Duplicate checks performed before submission

- npm metadata confirmed current `valibot` release is `1.4.1` and maps to `open-circle/valibot`.
- `gh api repos/open-circle/valibot/private-vulnerability-reporting` returned `{"enabled":true}`.
- `npm audit` for a clean project containing only `valibot@1.4.1` returned no vulnerabilities.
- Repository advisories and the GitHub Advisory Database only returned the historical emoji ReDoS advisory fixed in `1.2.0`.
- OSV exact-version query for npm `valibot` `1.4.1` returned no vulnerabilities.
- Public issue/PR searches for `flatten toString`, `flatten hasOwnProperty`, `record toString`, `__proto__`, `constructor`, and `prototype pollution` did not find a matching disclosure of this `record()` issue-path / `flatten()` exception.
- Reviewed related public PRs: `open-circle/valibot#67` added prototype pollution mitigation for `record()` by blacklisting `__proto__`, `prototype`, and `constructor`; it does not cover `flatten()` collisions with other inherited property names. `open-circle/valibot#1429` is an open plain-object / `record()` type semantics PR and does not disclose this `flatten()` exception behavior.

## Suggested remediation

Use null-prototype containers for flat error maps and/or perform own-property checks before appending:

- Initialize `flatErrors.nested` as `Object.create(null)`.
- Check nested entries with `Object.prototype.hasOwnProperty.call(flatErrors.nested, dotPath)` rather than truthiness.
- Consider filtering or escaping unsafe dot path segments in `getDotPath()` / `flatten()`, including inherited Object property names.
- Add regression tests for `flatten()` with paths `toString`, `valueOf`, `hasOwnProperty`, `__proto__`, `prototype`, and `constructor`.
- Consider using the same hardening for other accumulator objects that store attacker-controlled keys.

## References
- https://github.com/open-circle/valibot/security/advisories/GHSA-5qjj-4xww-7phc
- https://github.com/open-circle/valibot/pull/1522
- https://github.com/open-circle/valibot/commit/1bd01c304657cd0809cc92694360b6cc60f700bf
- https://github.com/open-circle/valibot
- https://github.com/open-circle/valibot/releases/tag/v1.4.2
