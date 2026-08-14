### Title
Unauthenticated header allows forging appName/appVersion in secure-container without failing checksum validation - (File: libraries/secure-container/src/compressed.js)

### Summary
`decrypt()` in `libraries/secure-container/src/index.js` computes and verifies the checksum only over `metadata` and `blob` via `conFile.computeChecksum(fileObj.metadata, fileObj.blob)`, never including `fileObj.header`. This means `decryptCompressed` (and `decrypt`) will happily decrypt and return a `header` object whose `appName`/`appVersion` bytes were swapped by an attacker who can modify the container at rest, without any exception being raised.

### Finding Description
In `libraries/secure-container/src/index.js`, `decrypt()` decodes the file with `conFile.decode(encryptedData)`, then computes `checksum = await conFile.computeChecksum(fileObj.metadata, fileObj.blob)` and compares only that against `fileObj.checksum` [1](#0-0) . The `computeChecksum` implementation in `libraries/secure-container/src/file.js` confirms the SHA-256 digest is computed over `metadata || blobLength || blob` only, with `header` completely excluded from the hashed bytes [2](#0-1) . This is also documented explicitly in the README's file-format description, stating the checksum covers only metadata and blob [3](#0-2) .

Because `conFile.struct` decodes `header`, `checksum`, `metadata`, and `blob` as independent fixed/var-length fields [4](#0-3) , an attacker who can write to the container bytes at rest (e.g., a synced backup blob) can take a legitimately checksummed `{metadata, checksum, blob}` triple and splice in an arbitrary 224-byte `header` (any `appName`/`appVersion`, still satisfying `header.decode`'s varstruct format and the `SECO` magic check in `conHeader.checkMagic`) [5](#0-4) . `decrypt()` will decode this forged header via `conHeader.decode(fileObj.header)` and return it unmodified, without ever validating it against the checksum [6](#0-5) . `decryptCompressed` in `compressed.js` passes this forged `header` straight through to its caller [7](#0-6) .

### Impact Explanation
Any consumer that uses the returned `header.appName`/`appVersion` to make origin/app-attribution decisions (e.g., deciding which application "owns" a decrypted secret container, or performing cross-app/cross-origin authorization based on which app produced the container) can be misled into treating attacker-controlled metadata as trustworthy provenance, since the header content is not cryptographically bound to the authenticated `metadata`/`blob` payload. This matches PERSISTED_STATE_AUTHENTICITY / origin-scoping concerns — a decrypted container's origin/app claim can be forged despite passing the passphrase-derived checksum check, potentially misdirecting downstream logic that gates data by app/origin.

### Likelihood Explanation
The precondition is that an attacker can tamper with header bytes of an encrypted container at rest before it is decrypted (e.g., intercept/modify a synced backup file) — no privileged wallet state, keys, or the passphrase are needed, since header bytes are not encrypted and not authenticated. The attack is deterministic and fully reproducible: swap the header segment of the varstruct-encoded file and decryption succeeds without exception.

### Recommendation
Include `header` (its serialized bytes) in the checksum computation in `conFile.computeChecksum` / `encrypt()` and `decrypt()` (e.g., `sha256(header || metadata || blobLength || blob)`), or otherwise authenticate the header as AAD in the blob's AEAD cipher, so any header tampering causes checksum verification to fail.

### Proof of Concept
Unit test outline (extends `libraries/secure-container/src/__tests__/usage.test.js` style):
1. Use `encrypt()` (from `libraries/secure-container/src/index.js`) to build a legitimate container with `header = { appName: 'Exodus', appVersion: '1.0.0' }`.
2. Decode it with `conFile.decode`, then replace `fileObj.header` with a different serialized header (e.g., `conHeader.serialize({ appName: 'Evil', appVersion: '9.9.9' })`), keeping `checksum`, `metadata`, `blob` untouched.
3. Re-encode with `conFile.encode(fileObj)` to produce the forged container.
4. Call `decrypt(forgedContainer, passphrase)` (or `decryptCompressed`).
5. Assert: no exception thrown, and `result.header.appName === 'Evil'` / `appVersion === '9.9.9'`, proving the header was accepted despite mismatching what was originally checksummed.

### Citations

**File:** libraries/secure-container/src/index.js (L42-47)
```javascript
export async function decrypt(encryptedData, passphrase) {
  const fileObj = conFile.decode(encryptedData)

  const checksum = await conFile.computeChecksum(fileObj.metadata, fileObj.blob)
  if (!fileObj.checksum.equals(checksum))
    throw new Error('seco checksum does not match; data may be corrupted')
```

**File:** libraries/secure-container/src/index.js (L49-54)
```javascript
  const metadata = conMetadata.decode(fileObj.metadata)
  const blobKey = await conMetadata.decryptBlobKey(metadata, passphrase)
  const header = conHeader.decode(fileObj.header)
  const data = await conBlob.decrypt(fileObj.blob, metadata, blobKey)

  return { data, blobKey, metadata, header }
```

**File:** libraries/secure-container/src/file.js (L9-20)
```javascript
export const struct = varstruct(
  vsf([
    ['header', Buf(HEADER_LEN_BYTES)],
    ['checksum', Buf(32)],
    ['metadata', Buf(METADATA_LEN_BYTES)],
    ['blob', VarBuffer(UInt32BE)],
  ])
)

export function decode(fileContents) {
  return struct.decode(fileContents)
}
```

**File:** libraries/secure-container/src/file.js (L26-28)
```javascript
export async function computeChecksum(metadata, blob) {
  return scCrypto.sha256(Buffer.concat([metadata, fromUInt32BE(blob.byteLength), blob]))
}
```

**File:** libraries/secure-container/README.md (L185-191)
```markdown
### Checksum

32-byte `sha256` checksum of the following data:

1. The `metadata`.
1. Byte-length of the `blob`, stored as `UInt32BE`.
1. The `blob`.
```

**File:** libraries/secure-container/src/header.js (L9-22)
```javascript
export function checkMagic(magic) {
  if (!magic.equals(MAGIC)) throw new RangeError('Invalid secure container magic.')
}

export const struct = varstruct(
  vsf([
    ['magic', Bound(varstruct.Buffer(4), checkMagic)],
    ['version', UInt32BE], // should be all 0's for now
    ['reserved', UInt32BE], // should be all 0's for now
    ['versionTag', VarString(UInt8)],
    ['appName', VarString(UInt8, 'utf-8')],
    ['appVersion', VarString(UInt8, 'utf-8')],
  ])
)
```

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
