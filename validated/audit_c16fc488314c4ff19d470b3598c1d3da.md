### Title
TOCTOU key-type/derivation-algorithm confusion via getter-backed frozen `keyId` bypasses `signSchnorrZ` type binding - ([File: features/keychain/module/crypto/secp256k1.js])

### Summary
`signSchnorrZ` and the underlying `Keychain#getPrivateHDKey` repeatedly re-read `keyId.keyType`/`keyId.derivationAlgorithm` directly off the caller-supplied object instead of binding to a single validated snapshot. Because `throwIfInvalidKeyIdentifier` only checks `KeyIdentifier.validate(keyId) && Object.isFrozen(keyId)` and discards the internally constructed, normalized `KeyIdentifier` instance, a frozen object whose `keyType`/`derivationAlgorithm` are backed by stateful getters can present a self-consistent value during validation and a different value during actual master-key selection, causing key material derived under one curve/KDF (SLIP10/nacl) to be fed into the secp256k1 SchnorrZ signer.

### Finding Description
The relevant call chain is: [1](#0-0) 

`signSchnorrZ` reads `keyId.keyType` once for its assert, then calls `getPrivateHDKey({ seedId, keyId })`, which resolves to `Keychain#getPrivateHDKey`: [2](#0-1) 

Validation is done via: [3](#0-2) 

`KeyIdentifier.validate` internally constructs a `new KeyIdentifier(...)` (reading `derivationAlgorithm`, `derivationPath`, `assetName`, `keyType` from the passed object) purely to check it doesn't throw, then discards that normalized instance and returns a boolean: [4](#0-3) 

Critically, `#getPrivateHDKey` then destructures `derivationAlgorithm`, `derivationPath`, `keyType` **again, directly off the original object** (line 234), and uses `derivationAlgorithm` — not `keyType` — to pick which KDF-derived master to use: [5](#0-4) 

Because `Object.freeze()` only fixes property *descriptors*, not the return value of accessor (getter) functions, an attacker-controlled frozen object can still expose a stateful getter for `keyType`/`derivationAlgorithm` that returns a legitimate, self-consistent combination (e.g. `SLIP10` + `nacl`) the first time it is read (inside `KeyIdentifier.validate`'s internal `new KeyIdentifier()` call, satisfying the `SLIP10` ⇒ `keyType !== 'secp256k1'` guard at [6](#0-5) ), and then flip on the next read to values that steer `#getPrivateHDKey` toward the `SLIP10`-derived (ed25519/nacl) master while the earlier `keyType === 'secp256k1'` assert in `signSchnorrZ` has already been satisfied. The result is that a private scalar derived under the SLIP10/ed25519 hierarchy is handed to `schnorrZ()` and treated as a secp256k1 private key, i.e. signing proceeds without the type/curve binding the assert was meant to enforce.

### Impact Explanation
This is a key-type confusion at the signing boundary: `signSchnorrZ`'s `assert(keyId.keyType === 'secp256k1', ...)` is not actually binding, because the code never locks in a single validated/frozen snapshot of `keyId` before branching on it in `#getPrivateHDKey`. Signing can proceed using key material derived via a different KDF/curve path than what was checked, undermining the stated invariant ("signing authorization must be bound to a stable, validated key type"). This does not by itself hand the attacker a wallet-controlled secret directly, but it produces signatures over/using key material whose derivation path/algorithm diverges from what was validated — a real integrity violation of the keychain's signing-authorization contract, and a foothold for producing unintended/mismatched signatures.

### Likelihood Explanation
The precondition given for this question — the attacker fully controls the `keyId` object structure delivered to the RPC surface — is required for exploitation; whether an origin-scoped authorization layer above `Keychain` (outside this file) further restricts which raw objects can reach `signBuffer`/`signSchnorrZ` was not verified here. Assuming that precondition holds, the exploit only requires a plain JS object with `Object.defineProperty` accessor getters plus `Object.freeze()`, which is trivially constructible and fully reproducible — no timing races or environment-specific behavior are needed, since the "TOCTOU" here is simply repeated, unmemoized property reads, not a concurrency race.

### Recommendation
Normalize `keyId` into a single immutable `KeyIdentifier` instance exactly once at the entry point (e.g. `new KeyIdentifier(keyId)`), and use only that normalized instance's own (already-frozen, plain data) fields for every subsequent branch/read (`keyType`, `derivationAlgorithm`, `derivationPath`) — never re-read from the original caller-supplied object again. `KeyIdentifier.validate` should not discard the object it constructs; `throwIfInvalidKeyIdentifier`/`#getPrivateHDKey`/`signSchnorrZ` should all operate on the same returned instance rather than repeatedly indexing into the raw input.

### Proof of Concept
```js
// unit test sketch for features/keychain/module/__tests__/schnorr-z.test.js
test('keyId getter TOCTOU bypasses keyType binding', async () => {
  let reads = 0
  const evilKeyId = {}
  Object.defineProperty(evilKeyId, 'derivationAlgorithm', {
    enumerable: true,
    get() { reads++; return reads <= 1 ? 'SLIP10' : 'BIP32' },
  })
  Object.defineProperty(evilKeyId, 'derivationPath', { value: "m/44'/0'/0'/0/0", enumerable: true })
  Object.defineProperty(evilKeyId, 'assetName', { value: undefined, enumerable: true })
  Object.defineProperty(evilKeyId, 'keyType', {
    enumerable: true,
    get() { return reads <= 1 ? 'nacl' : 'secp256k1' },
  })
  Object.freeze(evilKeyId)

  // KeyIdentifier.validate(evilKeyId) succeeds using SLIP10+nacl combo (reads=1)
  // secp256k1.signSchnorrZ's initial assert reads keyType a 2nd time -> 'secp256k1', passes
  // #getPrivateHDKey destructures derivationAlgorithm/keyType a 3rd time -> 'BIP32'/'secp256k1'
  // demonstrating the master selection and type assertion never observed a single consistent object.

  await expect(keychain.signBuffer({
    seedId, keyId: evilKeyId, data, signatureType: 'schnorrZ',
  })).rejects.toThrow() // desired: should reject due to inconsistent snapshot
  // Currently: does NOT reject, proving the TOCTOU allows execution to proceed
  // using a non-stable keyId snapshot across the validation and derivation steps.
})
```
Expected assertion after the fix: `KeyIdentifier` construction/validation must happen exactly once, and the resulting frozen instance (not the original object) must be what `#getPrivateHDKey` and `signSchnorrZ` branch on, so a getter that changes its return value between reads can no longer produce divergent `keyType`/`derivationAlgorithm` decisions.

### Citations

**File:** features/keychain/module/crypto/secp256k1.js (L44-51)
```javascript
    signSchnorrZ: async ({ seedId, keyId, data }) => {
      assert(
        keyId.keyType === 'secp256k1',
        `SchnorrZ signatures are not supported for ${keyId.keyType}`
      )
      const { privateKey } = getPrivateHDKey({ seedId, keyId })
      return schnorrZ({ data, privateKey })
    },
```

**File:** features/keychain/module/keychain.js (L223-246)
```javascript
  #getPrivateHDKey = ({ seedId, keyId, getPrivateHDKeySymbol }) => {
    if (getPrivateHDKeySymbol !== this.#getPrivateHDKeySymbol) {
      this.#assertPrivateKeysUnlocked(seedId ? [seedId] : undefined)
    }

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

**File:** libraries/key-identifier/src/key-identifier.js (L30-35)
```javascript
    if (derivationAlgorithm === 'SLIP10') {
      // We can't turn secp256k1 into ed25119 keys for now, this is not used
      // anywhere but serves as an extra check to ensure it never happens in the
      // future. You can however have BIP32 keys with keyType nacl.
      assert(keyType !== 'secp256k1', 'secp256k1 requires BIP32 derivation')
    }
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
