# [H] defu: Prototype pollution via `__proto__` key in defaults argument

## Summary
Severity: High
Advisory: GHSA-737v-mqg7-c878
CVE: CVE-2026-35209
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-737v-mqg7-c878
Type: github-advisory

## Affected
- npm: `defu` — affected >=0 <6.1.5

## Details
### Impact

Applications that pass unsanitized user input (e.g. parsed JSON request bodies, database records, or config files from untrusted sources) as the first argument to `defu()` are vulnerable to prototype pollution.

A crafted payload containing a `__proto__` key can override intended default values in the merged result:

```js
import { defu } from 'defu'

const userInput = JSON.parse('{"__proto__":{"isAdmin":true}}')
const config = defu(userInput, { isAdmin: false })

config.isAdmin // true — attacker overrides the server default
```

### Root Cause

The internal `_defu` function used `Object.assign({}, defaults)` to copy the defaults object. `Object.assign` invokes the `__proto__` setter, which replaces the resulting object's `[[Prototype]]` with attacker-controlled values. Properties inherited from the polluted prototype then bypass the existing `__proto__` key guard in the `for...in` loop and land in the final result.

### Fix

Replace `Object.assign({}, defaults)` with object spread (`{ ...defaults }`), which uses `[[DefineOwnProperty]]` and does not invoke the `__proto__` setter.

### Affected Versions

<= 6.1.4

### Credits

Reported by [@BlackHatExploitation](https://github.com/BlackHatExploitation)

## References
- https://github.com/unjs/defu/security/advisories/GHSA-737v-mqg7-c878
- https://nvd.nist.gov/vuln/detail/CVE-2026-35209
- https://github.com/unjs/defu/pull/156
- https://github.com/unjs/defu/commit/3942bfbbcaa72084bd4284846c83bd61ed7c8b29
- https://github.com/unjs/defu
- https://github.com/unjs/defu/releases/tag/v6.1.5
