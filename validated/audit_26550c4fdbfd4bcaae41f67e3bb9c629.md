Confirmed: this `secure-container` library is used by `browser-extension-adapters/seco-storage/seco.js` to encrypt/decrypt wallet vault data via `_encrypt`/`_decrypt` (passphrase-derived), and `metadata.decode` performs no validation on the scrypt parameters before they flow into `stretchPassphrase`.

### Title
Attacker-controlled scrypt parameters in secure-container metadata allow passphrase brute-force downgrade - (File: libraries/secure-container/src/crypto.js)

### Summary
The `secure-container` library derives the passphrase-stretching key using scrypt parameters (`n`, `r`, `p`) taken directly and unvalidated from the plaintext `metadata` blob, which is attacker-controlled in any imported/forged container. `metadata.decode` and `stretchPassphrase`/`createScryptParams` never enforce a minimum cost, so a forged container with `n=1,r=1,p=1` forces trivial scrypt work, drastically weakening the security of the AES key wrapping the `blobKey`.

### Finding Description
`metadata.decode()` parses the metadata blob's `scrypt.n/r/p` fields straight from an untrusted-format binary struct with no bounds checking: [1](#0-0) . This decoded object is then passed unmodified into `decryptBlobKey`, which calls `boxDecrypt(passphrase, metadata.blobKey.key, metadata.blobKey, metadata.scrypt)` using the metadata's own `scrypt` object: [2](#0-1) .

`boxDecrypt` merges the supplied params over `createScryptParams()` defaults, and then calls `stretchPassphrase` with the caller (attacker)-controlled `n, r, p`: [3](#0-2) . `stretchPassphrase` performs no clamping or minimum-cost enforcement — it just forwards `n, r, p` straight into the underlying `scrypt` call: [4](#0-3) .

The top-level `decrypt()` in `index.js` follows exactly the call sequence described in the question: `conFile.decode` → `conMetadata.decode` → `conMetadata.decryptBlobKey(metadata, passphrase)` → `boxDecrypt` → `stretchPassphrase`, with only a checksum equality check against the same attacker-supplied metadata (which an attacker can trivially recompute for a forged file), not a scrypt-cost sanity check: [5](#0-4) . This same code path is exercised in real product usage via `browser-extension-adapters/seco-storage/seco.js`'s `decryptString`, which wraps `_decrypt` from `secure-container` for wallet vault data: [6](#0-5) .

There is no code anywhere in `crypto.js`, `metadata.js`, or `index.js` that rejects or clamps out-of-range `n`/`r`/`p` values (e.g., minimum `n=16384`), so an attacker who can supply/import a crafted container (or replace a stored container on disk/extension-storage) fully controls the KDF cost used against the real user passphrase.

### Impact Explanation
If an attacker can get their crafted container imported/loaded (e.g., a malicious `.seco` backup file, a tampered extension-storage vault, or an imported wallet file), they can set `scrypt.n=1,p=1` to make the passphrase-derived key computable almost instantly instead of at the intended ~16384-iteration scrypt cost. This does not itself decrypt existing secrets without the correct passphrase, but it removes the offline brute-force cost multiplier that scrypt is meant to provide, drastically lowering the cost of a passphrase-guessing attack against any wallet backup/vault protected in this weakened form once such a file is force-loaded and used to re-encrypt/store secrets, or in scenarios where the attacker can substitute a container that the victim will decrypt with their real passphrase, exposing the passphrase to fast offline brute force.

### Likelihood Explanation
Exploitability requires the attacker to control the imported/forged container's metadata bytes, which the prompt explicitly grants as a precondition (imported/forged container). Given that `metadata.decode` performs zero validation, crafting `{n:1,r:1,p:1}` and re-serializing metadata is trivial and deterministic, and the checksum in the container is self-consistent because it's computed over the same attacker-controlled metadata, making this readily reproducible.

### Recommendation
Enforce minimum/maximum bounds on `n`, `r`, `p` (and salt length) in `metadata.decode` or in `stretchPassphrase`/`boxDecrypt`, rejecting or clamping any values below the library's intended defaults (e.g., `n >= 16384`, `p >= 1`, `r >= 8`) before they are used to derive a key, so untrusted persisted/imported metadata cannot downgrade KDF cost.

### Proof of Concept
```js
import { metadata, blob } from 'secure-container'

test('weak scrypt params in imported metadata are not rejected', async (t) => {
  const md = metadata.create({ n: 1, r: 1, p: 1, salt: Buffer.alloc(32) })
  const passphrase = 'correct horse battery staple'
  const blobKey = Buffer.alloc(32, 1)

  await metadata.encryptBlobKey(md, passphrase, blobKey) // uses n=1,r=1,p=1

  const start = Date.now()
  const decryptedKey = await metadata.decryptBlobKey(md, passphrase)
  const elapsed = Date.now() - start

  t.deepEqual(decryptedKey, blobKey)
  // Expected (fixed) behavior: this should throw/reject due to n below minimum.
  // Actual (current) behavior: succeeds in a few ms instead of the intended
  // scrypt cost (~16384 iterations), demonstrating the KDF cost downgrade.
  t.ok(elapsed < 50, 'scrypt completed almost instantly with attacker-supplied n=1,r=1,p=1')
})
```

### Citations

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

**File:** libraries/secure-container/src/crypto.js (L11-19)
```javascript
export function createScryptParams(params = {}) {
  return { salt: randomBytes(32), n: 16_384, r: 8, p: 1, ...params }
}

// always returns 32 byte key
export async function stretchPassphrase(passphrase, { salt, n, r, p } = createScryptParams()) {
  const key = await scrypt(passphrase, salt, { N: n, r, p, dkLen: 32 }, 'buffer')
  return { key, salt }
}
```

**File:** libraries/secure-container/src/crypto.js (L41-45)
```javascript
export async function boxDecrypt(passphrase, blob, { iv, authTag }, scryptParams) {
  scryptParams = { ...createScryptParams(), ...scryptParams }
  const { key } = await stretchPassphrase(passphrase, scryptParams)
  return aesDecrypt(key, blob, { iv, authTag })
}
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

**File:** libraries/browser-extension-adapters/seco-storage/seco.js (L27-43)
```javascript
export const decryptString = ({ data, key, encoding = 'base64' }) => {
  try {
    const databuffer = Buffer.from(data, encoding)

    const expanded = _decrypt(databuffer, key)
    const gzipped = shrink32k(expanded.data)
    const result = gunzipSync(gzipped)

    globalThis.crypto.getRandomValues(databuffer)
    globalThis.crypto.getRandomValues(expanded.data)
    globalThis.crypto.getRandomValues(gzipped)

    return result.toString()
  } catch {
    throw new Error('Unable to decrypt data')
  }
}
```
