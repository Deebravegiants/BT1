### Title
Decrypted plaintext buffers are not wiped when `gunzip` throws in `decryptCompressed` - ([File: libraries/secure-container/src/compressed.js])

### Summary
`decryptCompressed` decrypts `encryptedData` into `expanded` (the AES-GCM-decrypted plaintext) and then calls `gunzip` on it (or on `gzipped`, derived from `expanded`). If `gunzip` throws (e.g. due to a corrupted/attacker-crafted gzip payload), the function returns via the exception path before reaching the `randomFill(databuffer)` / `randomFill(expanded)` / `randomFill(gzipped)` calls, leaving decrypted secret material resident in memory.

### Finding Description
The relevant code is: [1](#0-0) 

`databuffer` holds a copy of the encrypted input, `expanded` holds the plaintext returned by `decrypt()` (post-AES-GCM decryption), and `gzipped` is either the same buffer or a slice/view derived from it via `shrink32k`. `gunzip(gzipped, { format: 'buffer' })` is called with no surrounding `try/finally`. If this call throws — which happens whenever the decrypted payload is not a valid gzip stream — control unwinds immediately out of the `async` function, and none of the three `randomFill` cleanup calls on lines 41-43 execute. As a result the sensitive plaintext buffers (`databuffer`, `expanded`, and potentially `gzipped`) remain unwiped in the JS heap for as long as GC retains them, since nothing else in the function references them afterward and there is no explicit zeroing.

This is directly reachable by any caller that supplies attacker-influenced `encryptedData` (e.g. an untrusted encrypted blob/backup/import payload) that happens to decrypt successfully — either because the attacker knows/derives the correct passphrase for a blob they crafted, or because it is processed inside an already-unlocked session using a cached passphrase — but whose post-decryption payload is not valid gzip. No existing guard (lock/auth, validation, or serialization check) forces the cleanup to occur before the `gunzip` exception propagates.

### Impact Explanation
Failure to wipe decrypted plaintext on the gunzip-failure path leaves sensitive material (potentially seed/mnemonic bytes, since `decryptCompressed` is used for compressed secret blobs per the associated `seco-keyval.test.js` tests) resident in memory longer than intended. This expands the window during which a separate memory-disclosure primitive (e.g., a debug/log/heap-dump surface elsewhere in the wallet) could recover it — a real secret-disclosure risk, matching Hydra's "sensitive data disclosure via improper memory hygiene" impact category, though it requires chaining with a separate disclosure primitive to be directly exploitable.

### Likelihood Explanation
Preconditions: `decrypt()` must succeed against the supplied `passphrase` (either attacker-controlled crafted blob decrypted with attacker-known passphrase, or reached via an unlocked/cached-passphrase session), and the resulting plaintext must not be valid gzip so that `gunzip` throws. This is straightforward and fully attacker-controllable: an attacker can craft any bytes as the "plaintext" prior to encryption, so producing a payload that decrypts fine but fails gunzip is trivial and repeatable in a unit test.

### Recommendation
Wrap the `gunzip` call (and ideally the whole cleanup sequence) in a `try/finally` so that `randomFill(databuffer)`, `randomFill(expanded)`, and conditionally `randomFill(gzipped)` always execute regardless of whether `gunzip` succeeds or throws, e.g.:
```js
let result
try {
  result = await gunzip(gzipped, { format: 'buffer' })
} finally {
  randomFill(databuffer)
  randomFill(expanded)
  if (expanded !== gzipped) randomFill(gzipped)
}
```
Apply the analogous fix to `encryptCompressed` for consistency, since it has the same unwiped-on-throw pattern around `encrypt()`.

### Proof of Concept
Unit test in `libraries/secure-container/src/__tests__/`:
1. Mock/stub `gunzip` (from `@exodus/crypto/compress`) to throw a "corrupted gzip" error.
2. Call `encryptCompressed(data, { passphrase, ... })` normally to obtain valid `encryptedData` and blobKey, then separately encrypt a payload where the "compressed" bytes are actually invalid gzip content but still round-trip successfully through `decrypt()`.
3. Call `decryptCompressed(encryptedData, passphrase)` and expect it to throw (as it currently does).
4. Capture references/snapshots of `expanded`/`gzipped`/`databuffer` contents before the call (via spying on `randomFill` or by holding a reference to the buffer through a wrapped `decrypt`) and assert that after the thrown error, the buffer bytes are unchanged (not zeroed/randomized) — i.e., `randomFill` was never invoked, confirming the plaintext leak. This assertion currently fails to hold the desired invariant ("wiped even on error"), proving the vulnerability.

### Citations

**File:** libraries/secure-container/src/compressed.js (L35-46)
```javascript
export async function decryptCompressed(encryptedData, passphrase, { expandTo32k = false } = {}) {
  const databuffer = Buffer.from(encryptedData) // copy, destroyed later
  const { data: expanded, blobKey, metadata, header } = await decrypt(databuffer, passphrase)
  const gzipped = expandTo32k ? shrink32k(expanded) : expanded
  const result = await gunzip(gzipped, { format: 'buffer' })

  randomFill(databuffer)
  randomFill(expanded)
  if (expanded !== gzipped) randomFill(gzipped)

  return { data: result, blobKey, metadata, header }
}
```
