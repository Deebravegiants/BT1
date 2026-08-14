### Title
Unvalidated scrypt N/r/p parameters from attacker-controlled metadata enable memory/CPU exhaustion DoS on unlock path - ([File: libraries/secure-container/src/crypto.js])

### Summary
`metadata.decode()` deserializes `scrypt.n`, `scrypt.r`, and `scrypt.p` as raw `UInt32BE` fields with no range validation [1](#0-0) . These values flow unmodified from `decryptBlobKey` → `boxDecrypt` → `stretchPassphrase` directly into the `scrypt()` call as `N`, `r`, `p` cost parameters [2](#0-1) , with no upper bound enforced anywhere in this library.

### Finding Description
`struct` in `metadata.js` decodes `scrypt.n`, `scrypt.r`, `scrypt.p` as plain `UInt32BE` values from the raw byte buffer with no bounds checking beyond the type width [3](#0-2) . `decode()` only warns (via `console.warn`) if the overall metadata length exceeds `METADATA_LEN_BYTES`; it does not validate individual field contents and does not throw [4](#0-3) .

`decryptBlobKey(metadata, passphrase)` passes `metadata.scrypt` (containing attacker-controlled `n`/`r`/`p`) straight into `boxDecrypt` [5](#0-4) . `boxDecrypt` merges these into a scrypt params object (`{ ...createScryptParams(), ...scryptParams }`, so any explicit attacker value overrides the safe defaults) and calls `stretchPassphrase`, which forwards `N: n, r, p` unchecked into `scrypt()` from `@exodus/crypto/scrypt` [6](#0-5) .

No clamping, sanity check (e.g., max `N` of 2^20, max `r*p` product, or memory-cost bound as recommended by RFC 7914 / OWASP), or pre-flight cost estimation exists anywhere in `metadata.js` or `crypto.js`. If an attacker supplies a crafted SECO container/import (e.g., an "imported wallet backup" or synced storage blob) with `n`, `r`, or `p` near `UInt32` max, the resulting scrypt call would attempt to allocate memory on the order of `128 * N * r` bytes and perform commensurate CPU work, which for large `N`/`r` values is enough to exhaust available memory or hang/crash the process during the decrypt attempt that occurs on unlock.

### Impact Explanation
This is a resource-exhaustion Denial-of-Service on the unlock/import path: providing a malicious metadata blob with oversized scrypt cost parameters can cause the wallet application to hang or crash (or in constrained mobile environments, get OOM-killed) while attempting to derive the key, blocking the user's own unlock flow. Impact is scoped to availability disruption, not secret disclosure or signing bypass; there's no code path in `metadata.js`/`crypto.js` that would turn this DoS into a lock bypass — the invariant "locked means locked" itself is not defeated, only availability is affected.

### Likelihood Explanation
Exploitability requires the wallet to decode and attempt decryption of attacker-supplied metadata (e.g., a maliciously modified `.seco` import/backup file, or tampered synced-storage content) — a plausible reach for "imported file or synced storage" per the question's stated preconditions. The trigger requires no valid passphrase and no other bypass; simply calling `decode()` then `decryptBlobKey()` on the crafted bytes is sufficient, since the parameters are used before password verification failure (the scrypt hashing runs first, and the DoS occurs regardless of whether the auth ultimately succeeds or fails). No existing guard in `metadata.js` or `crypto.js` prevents this.

### Recommendation
Add explicit upper-bound validation for `scrypt.n`, `scrypt.r`, `scrypt.p` (and their product, since memory cost is `~128*N*r` bytes) immediately after `metadata.decode()` or inside `decryptBlobKey`/`stretchPassphrase`, rejecting values above sane limits (e.g., `N <= 2**20`, `r <= 16`, `p <= 16`, with a combined memory-cost ceiling) before invoking `scrypt()`. Throw a clear error rather than silently proceeding.

### Proof of Concept
Fuzz/unit test plan:
1. Construct a metadata object via `metadata.create()`, then set `scrypt.n = 0xFFFFFFFF`, `scrypt.r = 0xFFFFFFFF`, `scrypt.p = 0xFFFFFFFF` (or realistic large-but-still-huge values like `N=2**26, r=64`) and encode via `metadata.encode()`.
2. Call `metadata.decode(buf)` on the resulting buffer and assert it succeeds without validation error (demonstrating no bounds check).
3. Call `metadata.decryptBlobKey(decodedMetadata, 'any-passphrase')` and assert with a timeout/memory guard (e.g., `Promise.race` against a short timeout, or monitor `process.memoryUsage()`), expecting the call to either exceed a defined time/memory bound or throw an out-of-memory error — proving unbounded resource consumption is reachable purely from decoded metadata fields.
4. Expected fix behavior: the same test should instead assert that `decryptBlobKey` synchronously throws a validation error (e.g., "scrypt parameters exceed allowed maximum") before invoking `scrypt()`, with execution time/memory bounded regardless of attacker-supplied `n`/`r`/`p`.

### Citations

**File:** libraries/secure-container/src/metadata.js (L7-17)
```javascript
export const struct = varstruct(
  vsf([
    [
      'scrypt',
      [
        ['salt', Buf(32)],
        ['n', UInt32BE],
        ['r', UInt32BE],
        ['p', UInt32BE],
      ],
    ],
```

**File:** libraries/secure-container/src/metadata.js (L37-43)
```javascript
export function decode(metadataBlob) {
  if (metadataBlob.byteLength > METADATA_LEN_BYTES)
    console.warn(
      `metadata greater than ${METADATA_LEN_BYTES} bytes, are you sure this is the SECO metadata?`
    )
  return struct.decode(metadataBlob)
}
```

**File:** libraries/secure-container/src/metadata.js (L79-81)
```javascript
export async function decryptBlobKey(metadata, passphrase) {
  return boxDecrypt(passphrase, metadata.blobKey.key, metadata.blobKey, metadata.scrypt)
}
```

**File:** libraries/secure-container/src/crypto.js (L16-19)
```javascript
export async function stretchPassphrase(passphrase, { salt, n, r, p } = createScryptParams()) {
  const key = await scrypt(passphrase, salt, { N: n, r, p, dkLen: 32 }, 'buffer')
  return { key, salt }
}
```

**File:** libraries/secure-container/src/crypto.js (L41-44)
```javascript
export async function boxDecrypt(passphrase, blob, { iv, authTag }, scryptParams) {
  scryptParams = { ...createScryptParams(), ...scryptParams }
  const { key } = await stretchPassphrase(passphrase, scryptParams)
  return aesDecrypt(key, blob, { iv, authTag })
```
