### Title
Wallet `#isLocked` desynchronizes from `Keychain` seed state on partial `unlock()` failure, leaving seed material readable while wallet reports locked - ([File: features/wallet/module/wallet.js])

### Summary
`Wallet.unlock()` calls `#keychain.addSeed(seed)` (which immediately unlocks that seed inside the `Keychain`) and sets `#primarySeedIdAtom` *before* it finishes the rest of the unlock sequence. If any later step in the same `try` block throws (e.g. `#getExtraSeeds()` fails to decrypt/parse the extra-seeds blob, or one of the `Promise.all` extra-seed `addSeed` calls rejects), the `catch` block swallows the error and rethrows `"Wrong password. Try again."` without ever rolling back the keychain state, while `this.#isLocked` is never set to `false`. The wallet now reports `isLocked() === true`, but the primary seed (and possibly some extra seeds) is present and unlocked in `Keychain` (`#seedLockStatus[seedId] = false`), reachable by any consumer that talks to the keychain directly.

### Finding Description
`unlock()` in [1](#0-0)  executes:
1. `const { seed } = await this.#getSeed({ passphrase })`
2. `const primarySeedId = await this.#keychain.addSeed(seed)` — this call, per `Keychain.addSeed`, immediately does `this.#masters[seedId] = masters; this.#seedLockStatus[seedId] = false` [2](#0-1) , i.e. the seed is fully materialized and *unlocked* inside the keychain as a side effect with no rollback path.
3. `this.#primarySeedIdAtom.set(primarySeedId)`
4. `const extraSeeds = await this.#getExtraSeeds()` — this decrypts `EXTRA_SEEDS_KEY` from storage using a passphrase derived from `#getExtraSeedsPassphrase()`, which itself calls `this.#keychain.exportKey(...)` [3](#0-2) ; storage/decryption failures here throw.
5. `await Promise.all(extraSeeds.map(({ seed }) => this.#keychain.addSeed(seed)))` — if any extra seed is malformed/corrupted, `Keychain.addSeed`'s assertion `assert(seed instanceof Uint8Array && seed.length === 64, ...)` [4](#0-3)  throws, but `Promise.all` does not, and cannot, undo the other concurrent `addSeed` calls that already completed.
6. Only after all of the above succeeds does `this.#isLocked = false` execute [5](#0-4) .

If steps 4, 5, or the `primarySeedIdAtom.set` throws for any reason, control jumps to the `catch` block [6](#0-5) , which only logs and rethrows a generic "Wrong password" error — it does **not** call `this.#keychain.removeAllSeeds()` or otherwise revert the seed(s) already added in step 2/5. `Wallet.isLocked()` merely returns the private field `#isLocked` [7](#0-6) , which still reads `true`, but `Keychain`'s own lock bookkeeping (`#seedLockStatus`) is now `false` for the seed(s) that were added.

Critically, several downstream signing/export code paths consult `Keychain` directly and never call `Wallet.isLocked()`:
- `SeedBasedMessageSigner.signMessage` → `#keychain.signBuffer(...)` / `#keychain.getPublicKey(...)` [8](#0-7) 
- `KeyViewer.getEncodedPrivateKeys` → `#keychain.exportKey({ seedId, keyId, exportPrivate: true })` [9](#0-8) 

`Keychain.exportKey`/`signBuffer` only guard against locked seeds via `#assertPrivateKeysUnlocked`, which checks `#seedLockStatus` per seedId [10](#0-9)  — not the wallet's own `#isLocked` flag. Since `#seedLockStatus[primarySeedId]` was already flipped to `false` in step 2, these calls succeed and return private key material / signatures even though `Wallet.isLocked()` still reports `true`.

The premise in the question (that `#getSeed` itself throws *after* `addSeed` already ran) does not match the literal code order — `#getSeed` runs before `addSeed`. However, the underlying invariant violation described (lock state desync from keychain secret custody due to partial failure inside the guarded `try` block) is real and reachable through the subsequent steps of the same `unlock()` call (`#getExtraSeeds()` failure or extra-seed `addSeed` failure), which occur strictly after the primary seed has already been added and unlocked in the keychain.

### Impact Explanation
This is a secret-disclosure / auth-bypass class issue: an application (or a wallet-embedding dapp/UI layer) that trusts `wallet.isLocked()` as the sole gate for showing/using private key material can be tricked into exposing the primary seed's private keys, signatures, or public keys even though the wallet UI/state machine believes the wallet is locked. Any caller with access to `Keychain` (message signer, key viewer, public key provider, tx signer) can extract signatures or raw private keys for the seed that leaked into the keychain during the failed unlock, without ever passing a correct passphrase again.

### Likelihood Explanation
Triggering this requires: (a) a wallet configured to have extra seeds (`maxExtraSeeds > 0`) and existing corrupted/incompatible extra-seed storage data, or (b) any transient failure in `#getExtraSeeds()`/`#getExtraSeedsPassphrase()` (e.g., storage read error, decryption mismatch, or malformed stored extra-seed length) occurring after the primary seed has already been successfully decrypted and added. An attacker who can influence stored extra-seed data (e.g., via an import/restore flow, sync data, or a QR/deeplink-driven seed import prior to unlock) can deliberately corrupt this data to force the failure deterministically, then repeatedly call `unlock()` with the correct primary passphrase to reproduce the state where the primary seed sits unlocked in the keychain while `Wallet.isLocked()` reports `true`.

### Recommendation
Make `unlock()` atomic with respect to keychain state:
- Wrap the entire sequence so that on any failure, the `catch` block explicitly calls `this.#keychain.removeAllSeeds()` (or removes just the seeds added during this attempt) before rethrowing, guaranteeing `Keychain` and `Wallet` locked-state stay consistent.
- Only call `this.#primarySeedIdAtom.set(primarySeedId)` and mark seeds "committed" after every step (including extra-seed decryption/addition) has fully succeeded.
- Consider deriving `isLocked()` from `Keychain.arePrivateKeysLocked()` directly instead of a separately tracked `#isLocked` boolean, so the two can never diverge.

### Proof of Concept
```js
// features/wallet/module/__tests__/index.test.js (new test)
it('keeps keychain locked when unlock() partially fails after primary seed is added', async () => {
  await wallet.create()
  await wallet.unlock()
  // add a valid extra seed, then corrupt the stored extra-seeds blob so that
  // decrypting/parsing throws on next unlock
  await wallet.addSeed({ mnemonic: otherMnemonic })
  await wallet.lock()

  // Corrupt extra-seeds passphrase/storage so #getExtraSeeds() throws on unlock
  jest.spyOn(wallet, '#getExtraSeeds').mockRejectedValueOnce(new Error('corrupted extra seeds'))

  await expect(wallet.unlock()).rejects.toThrow('Wrong password. Try again.')

  // Invariant check: wallet reports locked...
  await expect(wallet.isLocked()).resolves.toBe(true)

  // ...but keychain still holds the unlocked primary seed added before the failure
  const primarySeedId = await primarySeedIdAtom.get()
  await expect(keychain.arePrivateKeysLocked([seed])).resolves.toBe(false) // FAILS current invariant

  // and a direct keychain export succeeds despite wallet.isLocked() === true
  const keyId = createKeyIdentifierForExodus({ exoType: 'FUSION' })
  await expect(
    keychain.exportKey({ seedId: primarySeedId, keyId, exportPrivate: true })
  ).resolves.toBeDefined() // secret disclosure while "locked"
})
```
Expected (fixed) behavior: after the mocked failure, `keychain.arePrivateKeysLocked([seed])` should resolve to `true` and `keychain.exportKey` for that seed should throw `"private keys are locked"`, matching `wallet.isLocked() === true`.

### Citations

**File:** features/wallet/module/wallet.js (L124-135)
```javascript
  #getExtraSeedsPassphrase = async () => {
    this.#assertMultiSeedSupport()

    const { privateKey } = await this.#keychain.exportKey({
      seedId: await this.#primarySeedIdAtom.get(),
      keyId: EXODUS_KEY_IDS.EXTRA_SEEDS_ENCRYPTION,
      exportPrivate: true,
      exportPublic: false,
    })

    return privateKey
  }
```

**File:** features/wallet/module/wallet.js (L274-274)
```javascript
  isLocked = async () => this.#isLocked
```

**File:** features/wallet/module/wallet.js (L282-298)
```javascript
  unlock = async ({ passphrase } = {}) => {
    try {
      const { seed } = await this.#getSeed({ passphrase })
      const primarySeedId = await this.#keychain.addSeed(seed)
      this.#primarySeedIdAtom.set(primarySeedId)

      const extraSeeds = await this.#getExtraSeeds()
      await Promise.all(extraSeeds.map(({ seed }) => this.#keychain.addSeed(seed)))

      this.#isLocked = false

      return { primarySeedId }
    } catch (err) {
      this.#logger.debug('unlock() failed: wrong password', err)
      throw new Error('Wrong password. Try again.')
    }
  }
```

**File:** features/keychain/module/keychain.js (L57-74)
```javascript
  #assertPrivateKeysUnlocked(seedIds) {
    const locked = this.#checkPrivateKeysLocked(seedIds)
    assert(!locked, 'private keys are locked')
  }

  #checkPrivateKeysLocked(seedIds) {
    if (!seedIds?.length) {
      return Object.values(this.#seedLockStatus).some(Boolean)
    }

    return seedIds.some((seedId) => {
      assert(
        Object.hasOwn(this.#seedLockStatus, seedId),
        `cannot check lock state for unknown seed "${seedId}"`
      )
      return this.#seedLockStatus[seedId]
    })
  }
```

**File:** features/keychain/module/keychain.js (L109-124)
```javascript
  async addSeed(seed) {
    assert(seed instanceof Uint8Array && seed.length === 64, 'seed must be Uint8Array of 64 bytes')
    if (!Buffer.isBuffer(seed)) seed = typedView(seed, 'buffer') // TODO: switch to Uint8Array

    const mastersEntries = await Promise.all(
      Object.entries(MAP_KDF).map(async ([key, fromSeed]) => [key, await fromSeed(seed)])
    )
    const masters = Object.assign(Object.create(null), Object.fromEntries(mastersEntries))
    throwIfInvalidMasters(masters)

    const seedId = await getSeedId(seed)
    this.#masters[seedId] = masters
    // manually unlock here since unlockPrivateKeys requires seed to already exist
    this.#seedLockStatus[seedId] = false
    return seedId
  }
```

**File:** features/message-signer/src/module/seed-signer.ts (L72-93)
```typescript
  #getSigner = ({ keyId, seedId }: { keyId: KeyIdentifier; seedId: WalletAccount['seedId'] }) => {
    return {
      getPublicKey: async () => this.#keychain.getPublicKey({ seedId, keyId }),

      sign: async ({
        data,
        signatureType,
        enc,
        tweak,
        extraEntropy,
      }: KeychainSignerParams): Promise<Buffer> =>
        this.#keychain.signBuffer({
          seedId,
          keyId,
          data,
          signatureType,
          enc,
          tweak,
          extraEntropy,
        }),
    }
  }
```

**File:** features/key-viewer/module/key-viewer.ts (L86-90)
```typescript
    const keyExport = this.#keychain.exportKey({
      seedId: walletAccount.seedId!,
      keyId,
      exportPrivate: true,
    })
```
