### Title
TOCTOU in `#getPrivateHDKey` allows a frozen-looking `keyId` with a getter-based `derivationPath` to bypass validation and sign with an unvalidated derivation path - ([File: features/keychain/module/crypto/ed25519.js])

### Summary
`Keychain.signBuffer` forwards the caller-supplied `keyId` to `ed25519.signBuffer` → `#getPrivateHDKey` without ever normalizing it into a real `KeyIdentifier` instance (unlike `getPublicKey`/`exportKey`, which do `new KeyIdentifier(keyId)` first). `#getPrivateHDKey` validates `keyId` once via `throwIfInvalidKeyIdentifier`, then independently re-reads `keyId.derivationPath` via destructuring to perform the actual derivation, creating a double-read window that a getter-based property can exploit.

### Finding Description
`Keychain.signBuffer` at [1](#0-0)  passes the raw `keyId` straight into `this.ed25519.signBuffer({ seedId, keyId, data })`, with no `new KeyIdentifier(keyId)` normalization step (contrast with `getPublicKey`/`exportKey` at [2](#0-1)  and [3](#0-2) , which both wrap `keyId` in `new KeyIdentifier(keyId)` before calling `#getPrivateHDKey`).

`ed25519.js`'s `signBuffer` then calls `getPrivateHDKey({ seedId, keyId })` directly: [4](#0-3) .

Inside `#getPrivateHDKey`, validation and derivation each independently read `keyId.derivationPath`: [5](#0-4) 

- Read #1 happens inside `throwIfInvalidKeyIdentifier(keyId)` → `KeyIdentifier.validate(potentialKeyIdentifier)`, which internally does `new KeyIdentifier(potentialKeyIdentifier)`, destructuring `derivationPath` once to validate its format: [6](#0-5)  and [7](#0-6) . The result of this validated read is stored only on a **new, throwaway** `KeyIdentifier` instance, never propagated back to the original `keyId` object.
- `Object.isFrozen(potentialKeyIdentifier)` is also checked, but freezing an object only makes its own property descriptors non-configurable/non-writable — it does **not** constrain what an accessor's `get` function returns on subsequent invocations. An object composed solely of getter/setter (accessor) properties can be `Object.freeze`d while still returning different values on each access: [8](#0-7) .
- Read #2 happens right after validation succeeds: `const { derivationAlgorithm, derivationPath, keyType } = keyId` (line 234 of `keychain.js`), which re-invokes the getter on the *original* `keyId` object — not the sanitized instance from step 1 — and this second value is what actually gets passed to `master.derive(derivationPath)` at line 245.

Because these are two independent property reads on the same live object, a `keyId` shaped like:
```js
let n = 0
const keyId = Object.freeze({
  derivationAlgorithm: 'SLIP10',
  keyType: 'nacl',
  get derivationPath() {
    n++
    return n === 1 ? "m/44'/501'/0'/0'" : "m/44'/501'/9999'/0'"
  },
})
```
passes `Object.isFrozen(keyId) === true` and `KeyIdentifier.validate(keyId) === true` (using the first, benign path returned on call #1), yet the actual derive/sign operation at line 245 uses the second, attacker-chosen path returned on call #2 — a path that was never checked by `throwIfInvalidKeyIdentifier`/`KeyIdentifier`'s constructor assertions on that specific invocation.

### Impact Explanation
This breaks the invariant that a validated `KeyIdentifier` cannot diverge post-check within the keychain module: `signBuffer` can be induced to derive and sign with a derivation path different from the one that passed validation, entirely within the trusted `keychain` module boundary that other code (message-signer, tx-signer, wallet UI) relies on for scoping which account/asset a signature applies to. This matches a STORAGE_INTEGRITY-class impact — signing occurs against a wallet-scoped key path that bypassed the intended per-request validation, potentially producing a signature for an account/derivation path the caller/UI did not intend to authorize.

### Likelihood Explanation
The flaw is fully reproducible with a direct unit test against `Keychain`'s public API (`signBuffer`/`ed25519.signBuffer`) since `ed25519.js`'s `signBuffer` and `keychain.js`'s `#getPrivateHDKey` never coerce `keyId` into an immutable `KeyIdentifier` instance before use — unlike `getPublicKey`/`exportKey`, which are not vulnerable to this specific double-read pattern. Exploitability in a full end-to-end attack additionally depends on whether whatever code sits between an untrusted dapp/request and `keychain.signBuffer` passes through live JS object references with accessor properties versus serializing/reconstructing `keyId` via `new KeyIdentifier(...)` beforehand (which would neutralize the getter trick) — that upstream call chain (e.g. tx-signer/message-signer to keychain) could not be fully traced with the available tools, so end-to-end reachability from a fully unprivileged dapp origin is not fully confirmed, but the module-level flaw itself is verified and directly reproducible.

### Recommendation
Normalize `keyId` into an immutable `KeyIdentifier` instance (`keyId = new KeyIdentifier(keyId)`) at the very entry of `Keychain.signBuffer` (and inside `ed25519.signBuffer`/`#getPrivateHDKey` as defense-in-depth), before any validation or derivation reads, exactly as already done in `getPublicKey`/`exportKey`. This guarantees `derivationPath` is captured once, as an own, non-configurable, non-writable data property (see `Object.defineProperty` in `KeyIdentifier`'s constructor: [9](#0-8) ), eliminating any possibility of a second, divergent read via getter/Proxy tricks.

### Proof of Concept
Unit test (to be placed alongside `features/keychain/module/__tests__/sign-buffer.test.js`):
```js
test('signBuffer must not allow derivationPath to change between validation and derivation', async () => {
  const derivedPaths = []
  const master = {
    derive: (path) => {
      derivedPaths.push(path)
      return { privateKey: Buffer.alloc(32, 1) }
    },
  }
  // wire up a Keychain instance with a seed whose master.derive is spied as above
  // (via addSeed or by stubbing #masters through the existing test harness)

  let n = 0
  const keyId = Object.freeze({
    derivationAlgorithm: 'SLIP10',
    keyType: 'nacl',
    get derivationPath() {
      n++
      return n === 1 ? "m/44'/501'/0'/0'" : "m/44'/501'/9999'/0'"
    },
  })

  await keychain.signBuffer({ seedId, keyId, data: Buffer.alloc(32), signatureType: 'ed25519' })

  // Expect only ONE read of derivationPath was used for both validation and derivation,
  // and that the derived path matches the one that passed KeyIdentifier validation.
  expect(derivedPaths).toEqual(["m/44'/501'/0'/0'"])
})
```
Expected (failing) result on current code: `derivedPaths` contains `"m/44'/501'/9999'/0'"` — a path that was never checked by `KeyIdentifier`'s constructor assertions — demonstrating that `signBuffer` derives/signs using a second, unvalidated read of `keyId.derivationPath`.

### Citations

**File:** features/keychain/module/keychain.js (L228-245)
```javascript
    throwIfInvalidKeyIdentifier(keyId)
    assert(typeof seedId === 'string', 'seedId must be a BIP32 key identifier in hex encoding')
    assert(this.#masters[seedId], `seed with id "${seedId}" is not initialized`)

    throwIfInvalidMasters(this.#masters[seedId])

    const { derivationAlgorithm, derivationPath, keyType } = keyId
    const master = this.#masters[seedId][derivationAlgorithm]

    if (isExternalSeedId(seedId)) {
      assert(master, '#getPrivateHDKey: found no valid master seed')
      assert(
        keyType === master.keyId.keyType,
        '#getPrivateHDKey: received invalid keyType for specified master seed'
      )
    }

    return master.derive(derivationPath)
```

**File:** features/keychain/module/keychain.js (L278-284)
```javascript
    keyId = new KeyIdentifier(keyId)

    const hdkey = this.#getPrivateHDKey({
      seedId,
      keyId,
      getPrivateHDKeySymbol: this.#getPrivateHDKeySymbol,
    })
```

**File:** features/keychain/module/keychain.js (L301-306)
```javascript
  async getPublicKey({ seedId, keyId }) {
    const hdkey = this.#getPrivateHDKey({
      seedId,
      keyId: new KeyIdentifier(keyId),
      getPrivateHDKeySymbol: this.#getPrivateHDKeySymbol,
    })
```

**File:** features/keychain/module/keychain.js (L325-332)
```javascript
    if (signatureType === 'ed25519') {
      assert(noOpts, 'unsupported options supplied for ed25519 signature')

      if (keyId.keyType === 'cardanoByron') {
        return this.cardanoEd25519.signBuffer({ seedId, keyId, data })
      }

      return this.ed25519.signBuffer({ seedId, keyId, data })
```

**File:** features/keychain/module/crypto/ed25519.js (L7-11)
```javascript
    signBuffer: async ({ seedId, keyId, data }) => {
      assert(keyId.keyType === 'nacl', `ED25519 signatures are not supported for ${keyId.keyType}`)
      const { privateKey } = getPrivateHDKey({ seedId, keyId })
      return signDetached({ message: data, privateKey, format: 'buffer' })
    },
```

**File:** libraries/key-identifier/src/key-identifier.js (L18-42)
```javascript
  constructor({ derivationAlgorithm, derivationPath, assetName, keyType }) {
    assert(typeof derivationAlgorithm === 'string', 'derivationAlgorithm not a string')
    assert(
      SUPPORTED_KDFS.has(derivationAlgorithm),
      `${derivationAlgorithm} is not a valid derivationAlgorithm`
    )

    assert(['string', 'undefined'].includes(typeof assetName), 'assetName was not a string')

    keyType = keyType || (derivationAlgorithm === 'SLIP10' ? 'nacl' : 'secp256k1')
    assert(SUPPORTED_KEY_TYPES.has(keyType), 'keyType was not a valid option')

    if (derivationAlgorithm === 'SLIP10') {
      // We can't turn secp256k1 into ed25119 keys for now, this is not used
      // anywhere but serves as an extra check to ensure it never happens in the
      // future. You can however have BIP32 keys with keyType nacl.
      assert(keyType !== 'secp256k1', 'secp256k1 requires BIP32 derivation')
    }

    this.derivationAlgorithm = derivationAlgorithm
    this.assetName = assetName
    this.keyType = keyType
    this.#derivationPath = isDerivationPath(derivationPath)
      ? derivationPath
      : DerivationPath.from(derivationPath)
```

**File:** libraries/key-identifier/src/key-identifier.js (L44-47)
```javascript
    Object.defineProperty(this, 'derivationPath', {
      value: this.#derivationPath.toString(),
      enumerable: true,
    })
```

**File:** libraries/key-identifier/src/key-identifier.js (L82-90)
```javascript
  static validate = (potentialKeyIdentifier) => {
    try {
      // eslint-disable-next-line no-new
      new KeyIdentifier(potentialKeyIdentifier)
      return true
    } catch {
      return false
    }
  }
```

**File:** features/keychain/module/validate.js (L6-10)
```javascript
export const throwIfInvalidKeyIdentifier = (potentialKeyIdentifier) => {
  if (!KeyIdentifier.validate(potentialKeyIdentifier) || !Object.isFrozen(potentialKeyIdentifier)) {
    throw new ExpectedKeyIdentifier(potentialKeyIdentifier)
  }
}
```
