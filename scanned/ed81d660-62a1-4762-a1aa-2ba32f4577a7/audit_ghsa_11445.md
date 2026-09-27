# [C] Locutus vulnerable to RCE via unsanitized input in create_function()

## Summary
Severity: Critical
Advisory: GHSA-vh9h-29pq-r5m8
CVE: CVE-2026-32304
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-vh9h-29pq-r5m8
Type: github-advisory

## Affected
- npm: `locutus` — affected >=0 <3.0.14

## Details
## Summary

The `create_function(args, code)` function passes both parameters directly to the `Function` constructor without any sanitization, allowing arbitrary code execution.

This is distinct from CVE-2026-29091 (GHSA-fp25-p6mj-qqg6) which was `call_user_func_array` using `eval()` in v2.x. This finding affects `create_function` using `new Function()` in v3.x.

## Root Cause

`src/php/funchand/create_function.ts:17`:
```typescript
return new Function(...params, code)
```

Zero input validation on either parameter.

## PoC

```javascript
const { create_function } = require('locutus/php/funchand/create_function');
const rce = create_function('', 'return require("child_process").execSync("id").toString()');
console.log(rce());
// Output: uid=501(user) gid=20(staff) ...
```

Confirmed on locutus v3.0.11, Node.js v24.13.1.

## Impact

Full RCE when an attacker can control either argument to `create_function()`. 597K weekly npm downloads.

## Suggested Fix

Remove `create_function` or replace `new Function()` with a safe alternative. PHP itself deprecated `create_function()` in PHP 7.2 for the same reason.

## Response

Thanks for the report.

We confirmed that `php/funchand/create_function` was still present through `locutus@3.0.13` and that it exposed dynamic code execution via `new Function(...)`.

While this was intended behavior, `create_function()` inherently needs to be unsafe in order for it to work, `create_function()` was deprecated in PHP 7.2 and removed in PHP 8.0. Given that Locutus' parity target today is 8.3, this function shouldn't have been in Locutus at all anymore.

We fixed this in `locutus@3.0.14` by removing `php/funchand/create_function` entirely. That matches our PHP 8.3 parity target more closely: . 

We also updated `php/var/var_export` so closures now export using the PHP 8-style `\Closure::__set_state(array(...))` form instead of referencing the removed API.

Release:
- npm: `locutus@3.0.14`
- GitHub release: https://github.com/locutusjs/locutus/releases/tag/v3.0.14

Credit to @ByamB4 for the report.

## References
- https://github.com/locutusjs/locutus/security/advisories/GHSA-vh9h-29pq-r5m8
- https://nvd.nist.gov/vuln/detail/CVE-2026-32304
- https://github.com/locutusjs/locutus
- https://github.com/locutusjs/locutus/releases/tag/v3.0.14
