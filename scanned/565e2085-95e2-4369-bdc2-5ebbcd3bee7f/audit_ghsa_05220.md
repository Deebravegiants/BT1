# [H] flat-to-nested: Prototype pollution in flat-to-nested convert() via __proto__ parent/id key

## Summary
Severity: High
Advisory: GHSA-hp36-v28f-w3r4
CVE: CVE-2026-55091
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-hp36-v28f-w3r4
Type: github-advisory

## Affected
- npm: `flat-to-nested` — affected >=0 <1.1.2

## Details
### Summary
  `convert()` builds the nested tree by using each flat record's `id` and `parent` field values directly as object keys, with no guard against `__proto__` / `constructor` / `prototype`. A record whose `parent` is the string `"__proto__"` makes `temp[parent]` resolve to `Object.prototype`, and the following `initPush(...)` writes attacker-controlled data onto the global prototype. Any application that passes attacker-influenced records to `convert()` is affected, and the base prototype methods stay intact so the pollution is stealthy.

  ### Details
  In `index.js`, `convert()` (`FlatToNested.prototype.convert`):

  - `temp = {}` (line 45) and `pendingChildOf = {}` (line 46) are plain objects, so they inherit from `Object.prototype`.
  - For each record, `parent = flatEl[this.config.parent]` (line 51) is taken verbatim from input.
  - Line 57: `if (temp[parent] !== undefined)` — when `parent === "__proto__"`, `temp["__proto__"]` resolves via the prototype chain to `Object.prototype`, which is `!== undefined`, so the
  branch is taken.
  - Line 59: `initPush(this.config.children, temp[parent], flatEl)` → effectively `initPush("children", Object.prototype, flatEl)`.
  - `initPush` (lines 4-9): `Object.prototype["children"] = []` then `Object.prototype["children"].push(flatEl)` — **attacker-controlled data is written onto the global `Object.prototype`.**

  There is no sanitization of `id` / `parent` anywhere; they flow straight into `temp[id]`, `temp[parent]`, and `pendingChildOf[parent]` as dynamic keys.

  ### PoC
  ```js
  const FlatToNested = require('flat-to-nested');

  new FlatToNested().convert([
    { id: 1, parent: '__proto__', polluted: 'PWNED' }
  ]);

  console.log(({}).children); // => [ { id: 1, polluted: 'PWNED' } ]
  A freshly-created, unrelated object {} now carries an attacker-controlled children property. ({}).toString === Object.prototype.toString remains true, so existing methods are untouched (stealthy). If the consumer configures a custom children key, that arbitrary prototype property is polluted instead.
 ```
 
  ### Impact

  Prototype pollution (CWE-1321). Any service that builds a tree from attacker-influenced flat records (the package's core purpose — e.g. records derived from a DB/REST/user input) can have Object.prototype polluted. Consequences range from application-logic corruption and denial of service to serving as a gadget toward privilege escalation or RCE depending on downstream sinks. No special privileges or user interaction required; the malicious value is ordinary input data.

  ### Suggested fix

  Use prototype-less lookup tables so inherited keys like __proto__ cannot be reached:
  var temp = Object.create(null);
  var pendingChildOf = Object.create(null);
  (Optionally also reject id/parent values equal to __proto__, constructor, or prototype.) Verified: with Object.create(null) for both temp and pendingChildOf, the PoC no longer pollutes Object.prototype and normal nesting output is unchanged. A patch with a regression test is ready.

## References
- https://github.com/joaonuno/flat-to-nested-js/security/advisories/GHSA-hp36-v28f-w3r4
- https://github.com/joaonuno/flat-to-nested-js/commit/680a5ebe1194edda16fa93baaa56ff14fe0e3d7f
- https://github.com/joaonuno/flat-to-nested-js
