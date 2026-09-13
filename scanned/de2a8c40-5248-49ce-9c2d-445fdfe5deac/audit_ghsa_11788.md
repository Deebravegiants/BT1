# [M] Locutus Prototype Pollution due to incomplete fix for CVE-2026-25521

## Summary
Severity: Medium
Advisory: GHSA-vc8f-x9pp-wf5p
CVE: CVE-2026-33994
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-vc8f-x9pp-wf5p
Type: github-advisory

## Affected
- npm: `locutus` — affected >=2.0.39 <3.0.25

## Details
## Summary

A prototype pollution vulnerability exists in the `parse_str` function of the npm package locutus. An attacker can pollute `Object.prototype` by overriding `RegExp.prototype.test` and then passing a crafted query string to `parse_str`, bypassing the prototype pollution guard.

This vulnerability stems from an incomplete fix for [CVE-2026-25521](https://github.com/locutusjs/locutus/security/advisories/GHSA-rxrv-835q-v5mh). The CVE-2026-25521 patch replaced the `String.prototype.includes()`-based guard with a `RegExp.prototype.test()`-based guard. However, `RegExp.prototype.test` is itself a writable prototype method that can be overridden, making the new guard bypassable in the same way as the original — trading one hijackable built-in for another.

## Package

locutus (npm)

## Affected versions

>= 2.0.39, <= 3.0.24

Tested and confirmed vulnerable on **2.0.39** and **3.0.24** (latest). Version 2.0.38 (pre-fix) uses a different guard (`String.prototype.includes`) and is not affected by this specific bypass.

---

## Description

### Details

The vulnerability resides in `parse_str.js` where the `RegExp.prototype.test()` function is used to check whether user-provided input contains forbidden keys:

```javascript
if (/__proto__|constructor|prototype/.test(key)) {
  break
}
```

The previous guard (fixed in CVE-2026-25521) used `String.prototype.includes()`:

```javascript
if (key.includes('__proto__')) {
  break
}
```

The CVE-2026-25521 fix correctly identified that `String.prototype.includes` can be hijacked. However, the replacement guard using `RegExp.prototype.test()` suffers from the same class of weakness — `RegExp.prototype.test` is a writable method on the prototype chain and can be overridden to always return `false`, completely disabling the guard.

The robust fix is to use direct string comparison operators (`===`) in native control flow (`for`/`if`) instead of prototype methods like `RegExp.prototype.test()`, since `===` is a language-level operator that cannot be overridden.

### PoC

#### Steps to reproduce

1. Install locutus using `npm install locutus`
2. Run the following code snippet:

```javascript
const parse_str = require('locutus/php/strings/parse_str');

// Hijack RegExp.prototype.test (simulates a prior prototype pollution gadget)
const original = RegExp.prototype.test;
RegExp.prototype.test = function () { return false; };

// Payload
const result = {};
parse_str('__proto__[polluted]=yes', result);

// Check
RegExp.prototype.test = original;
console.log(({}).polluted); // 'yes' — prototype is polluted
```

#### Expected behavior

Prototype pollution should be prevented and `({}).polluted` should print `undefined`.

```
undefined
```

#### Actual behavior

`Object.prototype` is polluted. This is printed on the console:

```
yes
```

### Impact

This is a prototype pollution vulnerability with the same impact as CVE-2026-25521. The attack requires a chaining scenario — an attacker needs a separate prototype pollution gadget (e.g., from another npm package in the same application) to override `RegExp.prototype.test` before exploiting `parse_str`. This is realistic in Node.js applications that use multiple npm packages, where one package's vulnerability can disable another package's defenses.

Any application that processes attacker-controlled input using `locutus/php/strings/parse_str` may be affected. It could potentially lead to:

1. Authentication bypass
2. Denial of service
3. Remote code execution (if polluted property is passed to sinks like `eval` or `child_process`)

### Resources

- Original advisory: https://github.com/locutusjs/locutus/security/advisories/GHSA-rxrv-835q-v5mh
- Fix commit (incomplete): https://github.com/locutusjs/locutus/commit/042af9ca7fde2ff599120783e720a17f335bb01c
- Vulnerable file: https://github.com/locutusjs/locutus/blob/main/src/php/strings/parse_str.js#L77

## Maintainer response

Thank you for the follow-up report. This issue was reproduced locally against `locutus@3.0.24`, confirming that the earlier `parse_str` guard was incomplete: if `RegExp.prototype.test` was already compromised, the guard could be bypassed and `parse_str('__proto__[polluted]=yes', result)` could still pollute `Object.prototype`.

This is now fixed on `main` and released in `locutus@3.0.25`.

## Fix Shipped In

- **PR:** [locutusjs/locutus#597](https://github.com/locutusjs/locutus/pull/597)
- **Merge commit on `main`:** `345a6211e1e6f939f96a7090bfeff642c9fcf9e4`
- **Release:** [v3.0.25](https://github.com/locutusjs/locutus/releases/tag/v3.0.25)

## What the Fix Does

The new fix no longer relies on a regex-prototype guard for safety. Instead, `src/php/strings/parse_str.ts` now rejects dangerous key paths during parsed-segment assignment, so the sink itself is hardened even if `RegExp.prototype.test` has been tampered with beforehand.

## Tested Repro Before the Fix

- Override `RegExp.prototype.test` to always return `false`
- Call `parse_str('__proto__[polluted]=yes', result)`
- Observe `({}).polluted === 'yes'`

## Tested State After the Fix in `3.0.25`

- Dangerous key paths are skipped during assignment
- The same chained repro no longer pollutes `Object.prototype`
- The regression is covered by `test/custom/parse_str-prototype-pollution.vitest.ts`

---

The locutus team is treating this as a real package vulnerability with patched version `3.0.25`. The vulnerable range should end at `< 3.0.25`.

## References
- https://github.com/locutusjs/locutus/security/advisories/GHSA-rxrv-835q-v5mh
- https://github.com/locutusjs/locutus/security/advisories/GHSA-vc8f-x9pp-wf5p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33994
- https://github.com/locutusjs/locutus/pull/597
- https://github.com/locutusjs/locutus/commit/345a6211e1e6f939f96a7090bfeff642c9fcf9e4
- https://github.com/locutusjs/locutus
- https://github.com/locutusjs/locutus/releases/tag/v3.0.25
