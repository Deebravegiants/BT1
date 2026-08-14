### Title
Mnemonic and derived key material remain unencrypted in JS heap memory across lock/unlock, with `removeAllSeeds()` providing no memory-clearing guarantee - (File: `features/keychain/module/keychain.js`)

### Summary
The `Wallet` and `Keychain` modules operate on the raw BIP39 mnemonic and its derived 64-byte seed as plain, unencrypted JS values (`string`/`Buffer`) whenever the wallet is created, imported, or unlocked. `Keychain#lock`/`removeAllSeeds()` only unset object references (`this.#masters = Object.create(null)`), which does not zero or otherwise scrub the underlying memory occupied by the previous seed/master-key buffers, and this limitation is explicitly acknowledged in the module's own README.

### Finding Description
`Wallet.unlock()`, `Wallet.create()`, `Wallet.import()`, and `Wallet.getMnemonic()` all pass the plaintext mnemonic/seed around as ordinary JS values: [1](#0-0) [2](#0-1) [3](#0-2) 

`getMnemonic()` returns the raw mnemonic string directly to the caller, and `unlock()` feeds the raw seed buffer into `Keychain#addSeed`, which stores derived master keys in the `#masters` private field: [4](#0-3) 

When the wallet is locked, `Keychain#lock`/`removeAllSeeds()` merely reassigns `this.#masters` and `this.#seedLockStatus` to fresh objects; it does not overwrite/zero-fill the `Buffer`s that previously held the seed or derived master keys: [5](#0-4) [6](#0-5) 

This is a documented, acknowledged limitation of the module itself: [7](#0-6) 

Additionally, `PassphraseCache.set()` persists the wallet passphrase in plaintext (no encryption) to its backing storage so that `#autoUnlock` can re-derive the seed automatically: [8](#0-7) [9](#0-8) 

The `@exodus/wallet` README itself flags that encryption of the seed at rest is delegated entirely to the injected `seedStorage`, with no mention of in-memory protection of the mnemonic once it is decrypted for use: [10](#0-9) 

### Impact Explanation
Any process capable of reading the application's JS heap (e.g., a compromised renderer/extension context, a memory-scraping malware on the user's machine, or a malicious dependency executing in the same process) can recover the plaintext mnemonic, the raw 64-byte seed, and derived master keys well after the wallet has been "locked," because dead references are dropped from `#masters`/`#seedLockStatus` but the actual memory is left intact until garbage collected and potentially overwritten by unrelated allocations. Recovery of the mnemonic is equivalent to full compromise of every asset controlled by the wallet — an irreversible, total loss of funds.

### Likelihood Explanation
The exposure window is broad: it occurs on every `wallet.create()`, `wallet.import()`, `wallet.unlock()` (including the automatic `#autoUnlock` path using the cached passphrase), and `wallet.getMnemonic()` call, i.e. essentially every normal, day-to-day wallet operation for every user, not just an edge case. No additional user action beyond ordinary use of the extension/app is required, and the plaintext-passphrase persistence in `PassphraseCache` extends the exposure to storage as well as memory.

### Recommendation
- Use zero-filled `Buffer`s for seeds/mnemonics wherever feasible and explicitly `.fill(0)` them on `lock()`/`removeAllSeeds()` rather than merely dropping references.
- Avoid keeping the raw mnemonic string in memory longer than strictly necessary in `getMnemonic()`/`create()`/`import()`; prefer buffer-based representations that support secure wiping.
- For `PassphraseCache`, encrypt the passphrase before persisting it (e.g., derive an ephemeral key protected by platform-specific secure storage) instead of storing it in cleartext.
- Consider leveraging OS/platform primitives (e.g., `sodium_malloc`/`sodium_memzero` equivalents already used elsewhere in `keychain.sodium`) consistently for all secret material, including the raw mnemonic and seed, not just for keys already routed through the sodium encryptor.

### Proof of Concept
1. `await exodus.wallet.create({ passphrase })` — mnemonic and seed exist as plaintext values in `Wallet#create` and are copied into `Keychain#masters`.
2. `await exodus.wallet.getMnemonic({ passphrase })` — returns the plaintext mnemonic string to the caller; a heap snapshot taken at this point (analogous to the Halborn screenshots) will show the mnemonic in cleartext.
3. `await exodus.wallet.lock()` → internally calls `Keychain#removeAllSeeds()`, which only does `this.#masters = Object.create(null)`. The underlying `Buffer` objects that held the seed/derived keys are not zero-filled, so a subsequent heap inspection can still recover them until GC reclaims and overwrites that memory — mirroring the original report's "Mnemonic Leakage in Memory after unlocking the Wallet and then locking it" scenario.

### Citations

**File:** features/wallet/module/wallet.js (L231-248)
```javascript
  create = makeConcurrent(
    async ({ mnemonic, passphrase } = {}) => {
      mnemonic = mnemonic || (await generateMnemonic({ bitsize: 128 }))

      const dateCreated = this.#clock.now()
      const seedBuffer = await mnemonicToSeed({ mnemonic, format: 'buffer', validate: false })
      const seed = { mnemonic, seed: seedBuffer, dateCreated }
      const seedId = await getSeedId(seedBuffer)

      await this.#setSeed({ seed, passphrase })

      this.#seedMetadataAtom.set((previous) => ({
        ...previous,
        [seedId]: { dateCreated },
      }))

      return { seedId }
    },
```

**File:** features/wallet/module/wallet.js (L274-280)
```javascript
  isLocked = async () => this.#isLocked

  lock = async () => {
    this.#keychain.removeAllSeeds()

    this.#isLocked = true
  }
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

**File:** features/wallet/module/wallet.js (L300-326)
```javascript
  getMnemonic = async ({ passphrase, seedId } = {}) => {
    try {
      // always need to get primary seed first to make sure the user entered the right passphrase
      // even if passed seedId is not primary
      const { mnemonic } = await this.#getSeed({ passphrase })
      if (!mnemonic) throw new Error('Wrong password. Try again.')

      if (!seedId || (await this.getPrimarySeedId()) === seedId) return mnemonic

      // Sequential, as sync fallback is slower
      for (const seed of await this.#getExtraSeeds()) {
        if (seedId !== (await getSeedId(seed.seed))) continue
        if (!seed.mnemonic) throw new Error('No mnemonic found for seedId.')
        return seed.mnemonic
      }

      throw new Error('No seed matches seedId.')
    } catch (err) {
      if (err.message === 'No seed matches seedId.') {
        this.#logger.debug('getMnemonic() failed: no seed matches seedId.')
        throw err
      }

      this.#logger.debug('getMnemonic() failed: wrong password')
      throw new Error('Wrong password. Try again.')
    }
  }
```

**File:** features/keychain/module/keychain.js (L109-129)
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

  removeAllSeeds() {
    this.#masters = Object.create(null)
    this.#seedLockStatus = Object.create(null)
  }
```

**File:** features/keychain/README.md (L1-9)
```markdown
# `@exodus/keychain`

The keychain is a module designed to work more securely with private key material. It can be compared with a walled garden from which private keys should not escape. All operations using private keys, such as signing and encryption data should be executed within the module, with `KeyIdentifier`s used to specify which key to use for which operation. Notice the "should," as we're not quite there yet.

In its current state, this library aims to provide a good interface for working with cryptographic material. However, it has some security limitations, which are on our roadmap to address:

- Private key material is passed directly to asset libraries which can contain code by third party developers. This is on our roadmap to eliminate by refactoring asset libraries to accept signing functions instead of keys.
- Private keys _can_ be exported, via `keychain.exportKey`
- `keychain.removeAllSeeds()` does not guarantee that private keys get completely cleared from memory
```

**File:** features/application/src/modules/passphrase-cache.ts (L50-59)
```typescript
  async set(passphrase: string) {
    this.#logger.log('caching passphrase')
    const ttl = await this.#getTtl()

    await this.#storage.batchSet({
      [PASSPHRASE_KEY]: passphrase,
      [ADDED_AT_KEY]: Date.now(),
      [TTL_KEY]: ttl,
    })
  }
```

**File:** features/application/src/modules/application.ts (L387-407)
```typescript
  #autoUnlock = async () => {
    const walletLocked = await this.#wallet.isLocked()
    const passphrase = await this.#passphraseCache.get()

    if (!walletLocked || !passphrase) return

    try {
      this.#logger.log('unlocking with cache')

      await this.#wallet.unlock({ passphrase })
      await this.#lockedAtom.set(false)

      await this.fire(Hook.Migrate)
      await this.fire(Hook.Unlock)

      void this.#restoreIfNeeded()
      this.#logger.log('unlocked with cache')
    } catch (err) {
      this.#logger.error('failed to unlock, outdated cached passphrase?', err)
    }
  }
```

**File:** features/wallet/README.md (L5-6)
```markdown
> [!IMPORTANT]
> This feature uses the injected `seedStorage` implementation to store mnemonic phrases. It passes the `passphrase` provided to `wallet.create|import|changePassphrase` down to `seedStorage.set`, e.g. `seedStorage.set(value, { passphrase })`. Depending on the security of the platform where you're running the wallet, and the media that `seedStorage` uses on that platform, you may want to use a `seedStorage` implementation that supports encryption, e.g. [storage-seco](../../adapters/storage-seco).
```
