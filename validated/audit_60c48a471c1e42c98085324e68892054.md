### Title
Missing scrypt cost-parameter validation allows weak-KDF wallet secret exposure - (File: libraries/secure-container/src/crypto.js, metadata.js)

### Summary
`metadata.decryptBlobKey`/`metadata.encryptBlobKey` pass `metadata.scrypt` (`n`, `r`, `p`, `salt`) straight into `boxDecrypt`/`boxEncrypt` → `stretchPassphrase` with no bounds checking. Any code path that accepts externally-supplied metadata (imported backup, remote-config-driven migration) and feeds it into these functions will silently derive the passphrase-based key using attacker-chosen, arbitrarily weak cost parameters (e.g. `n=1`), making the derived key/passphrase trivially brute-forceable offline.

### Finding Description
The scrypt parameters used to stretch the user's passphrase originate entirely from `metadata.scrypt`, which is decoded from an untrusted byte blob via `metadata.decode`/`struct.decode` [1](#0-0) . `decryptBlobKey` forwards that structure directly to `boxDecrypt` with no validation: [2](#0-1) . Likewise `encryptBlobKey` forwards `metadata.scrypt` to `boxEncrypt` unchecked: [3](#0-2) .

In `crypto.js`, `boxDecrypt` merges the caller-supplied params over the (safe) defaults — `{...createScryptParams(), ...scryptParams}` — so any attacker-controlled `n`/`r`/`p` field completely overrides the safe defaults, and `stretchPassphrase` calls the underlying `scrypt` primitive with whatever values were provided, with no minimum-cost enforcement anywhere: [4](#0-3) . There is no clamping, no minimum threshold check, and no rejection of degenerate values (e.g. `n=1`, `n=0`, `r=1`, `p=1`) anywhere in `crypto.js` or `metadata.js`. The existing test suite even demonstrates that `createScryptParams({ n: 16 })` is accepted verbatim without complaint [5](#0-4) , confirming there is no validation layer at all.

The consuming `index.js decrypt`/`encrypt` flow does an integrity checksum over `(metadata || blobLen || blob)` [6](#0-5) , but this checksum is computed from the same untrusted `metadata`/`blob` bytes — it only detects accidental corruption, not deliberate crafting, since an attacker who controls the whole file can trivially recompute a matching checksum. Nothing in `header.js` or `file.js` validates KDF cost either.

Where this becomes exploitable in a real wallet-compromise sense is the re-encryption/migration path: if an application built on `secure-container` imports metadata from a backup/remote-config source and uses it as the template for `metadata.encryptBlobKey` (e.g., to preserve/replicate scrypt settings across a migration) while supplying the real user passphrase and blobKey, the resulting *newly produced* backup/container will have its passphrase-derived key protected by attacker-chosen, weak cost parameters. Anyone who later obtains that container (including the original attacker) can brute-force the passphrase offline in a fraction of the time normally required, then successfully run `blob.decrypt` against the real wallet ciphertext, since `blob.decrypt` performs no independent strength check on the key it receives — it just calls `aesDecrypt` [7](#0-6) .

### Impact Explanation
If an attacker can influence the `scrypt` parameters embedded in metadata that is subsequently used (via `encryptBlobKey`) to protect a real passphrase/blobKey, or if any decrypt call path accepts attacker metadata for an already-existing container, the passphrase-derived key protecting wallet secrets can be reduced to a KDF cost of `n=1`/`r=1`/`p=1`, collapsing the brute-force cost by orders of magnitude. This directly threatens the "locked means locked / secrets stay secret" invariant and matches a secret-disclosure / wallet-secret-recovery impact class.

### Likelihood Explanation
The library itself contains no defense — no minimum threshold, no clamping — for `n`, `r`, `p` in either `boxEncrypt`/`boxDecrypt` or the `metadata.encryptBlobKey`/`decryptBlobKey` wrappers, which is confirmed by direct code reading of `crypto.js` and `metadata.js` and corroborated by the unit tests accepting an arbitrary low `n`. However, exploitability strictly depends on how a consuming application wires untrusted metadata (imported backup, remote-config migration) into `encryptBlobKey`/`decryptBlobKey` for a *real* wallet's passphrase/blobKey — this repository (`secure-container`) is a low-level container/crypto library, and I could not locate, within this library, the actual "import backup" or "remote-config-fed migration" call site that feeds untrusted `metadata.scrypt` into these APIs for a live wallet. That integration point (if it exists) is outside `libraries/secure-container` and was not found in this codebase, so the full end-to-end attack chain described (attacker fully controls the metadata reaching a live wallet's passphrase re-encryption) is not proven reachable from this library alone.

### Recommendation
Add minimum-bound validation for `n`, `r`, `p` (and reasonable maxima to avoid DoS) inside `createScryptParams`, `stretchPassphrase`, `boxEncrypt`, and `boxDecrypt` in `libraries/secure-container/src/crypto.js`, and/or validate `metadata.scrypt` immediately after `metadata.decode` before it can reach `decryptBlobKey`/`encryptBlobKey`. Reject (throw) rather than silently proceed when parameters fall below a defined safe floor (e.g. `n < 16384`, `r < 8`, `p < 1`).

### Proof of Concept
Unit test plan for `libraries/secure-container/src/__tests__/crypto.test.js`:
1. Call `scCrypto.boxEncrypt(passphrase, message, { salt, n: 1, r: 1, p: 1 })` and assert it throws / is rejected with a "scrypt parameters below safe threshold" error, instead of succeeding.
2. Call `scCrypto.boxDecrypt(passphrase, blob, { iv, authTag }, { salt, n: 1, r: 1, p: 1 })` and assert rejection for the same reason.
3. Craft a `metadata` object via `metadata.create()` with `metadata.scrypt.n = 1` and call `metadata.encryptBlobKey`/`metadata.decryptBlobKey`; assert both reject rather than deriving a key.
Expected (currently failing) assertion: these calls should throw before reaching `stretchPassphrase`/`aesDecrypt`; presently they succeed, confirming the missing guard.

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

**File:** libraries/secure-container/src/metadata.js (L71-77)
```javascript
export async function encryptBlobKey(metadata, passphrase, blobKey) {
  const { authTag, blob, iv, salt } = await boxEncrypt(passphrase, blobKey, metadata.scrypt)
  // eslint-disable-next-line @exodus/mutable/no-param-reassign-prop-only
  metadata.scrypt.salt = salt
  // eslint-disable-next-line @exodus/mutable/no-param-reassign-prop-only
  metadata.blobKey = { authTag, iv, key: blob }
}
```

**File:** libraries/secure-container/src/metadata.js (L79-81)
```javascript
export async function decryptBlobKey(metadata, passphrase) {
  return boxDecrypt(passphrase, metadata.blobKey.key, metadata.blobKey, metadata.scrypt)
}
```

**File:** libraries/secure-container/src/crypto.js (L11-45)
```javascript
export function createScryptParams(params = {}) {
  return { salt: randomBytes(32), n: 16_384, r: 8, p: 1, ...params }
}

// always returns 32 byte key
export async function stretchPassphrase(passphrase, { salt, n, r, p } = createScryptParams()) {
  const key = await scrypt(passphrase, salt, { N: n, r, p, dkLen: 32 }, 'buffer')
  return { key, salt }
}

export async function aesEncrypt(key, message) {
  if (key.length !== KEY_LEN) throw new Error('Unexpected key size for aes-256')
  const iv = randomBytes(IV_LEN_BYTES)
  const merged = await encryptGCM({ data: message, key, nonce: iv, format: 'buffer' })
  const blob = merged.subarray(0, -AUTH_TAG_LEN)
  const authTag = merged.subarray(-AUTH_TAG_LEN)
  return { authTag, blob, iv }
}

export async function aesDecrypt(key, blob, { iv, authTag }) {
  if (key.length !== KEY_LEN) throw new Error('Unexpected key size for aes-256')
  return decryptGCM({ data: Buffer.concat([blob, authTag]), key, nonce: iv, format: 'buffer' })
}

export async function boxEncrypt(passphrase, message, scryptParams) {
  const { key, salt } = await stretchPassphrase(passphrase, scryptParams)
  const { authTag, blob, iv } = await aesEncrypt(key, message)
  return { authTag, blob, iv, salt }
}

export async function boxDecrypt(passphrase, blob, { iv, authTag }, scryptParams) {
  scryptParams = { ...createScryptParams(), ...scryptParams }
  const { key } = await stretchPassphrase(passphrase, scryptParams)
  return aesDecrypt(key, blob, { iv, authTag })
}
```

**File:** libraries/secure-container/src/__tests__/crypto.test.js (L83-90)
```javascript
test('createScryptParams', (t) => {
  t.plan(1)

  const params = scCrypto.createScryptParams({ n: 16 })
  t.is(params.n, 16, 'var is set')

  t.end()
})
```

**File:** libraries/secure-container/src/index.js (L42-55)
```javascript
export async function decrypt(encryptedData, passphrase) {
  const fileObj = conFile.decode(encryptedData)

  const checksum = await conFile.computeChecksum(fileObj.metadata, fileObj.blob)
  if (!fileObj.checksum.equals(checksum))
    throw new Error('seco checksum does not match; data may be corrupted')

  const metadata = conMetadata.decode(fileObj.metadata)
  const blobKey = await conMetadata.decryptBlobKey(metadata, passphrase)
  const header = conHeader.decode(fileObj.header)
  const data = await conBlob.decrypt(fileObj.blob, metadata, blobKey)

  return { data, blobKey, metadata, header }
}
```

**File:** libraries/secure-container/src/blob.js (L10-12)
```javascript
export async function decrypt(blob, metadata, blobKey) {
  return scCrypto.aesDecrypt(blobKey, blob, metadata.blob)
}
```
