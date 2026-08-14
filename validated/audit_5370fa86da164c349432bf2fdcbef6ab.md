### Title
`wallet.create()` unconditionally overwrites an existing seed without requiring the current passphrase or unlock state - (File: `features/wallet/module/wallet.js`)

### Summary
`Wallet#create` (and the `Application#create` wrapper that calls it) never checks `this.exists()` or requires unlocking via `#assertWalletIsUnlocked` before calling `#setSeed`, so calling `wallet.create({ mnemonic, passphrase })` a second time silently replaces the primary seed stored at `SEED_KEY` regardless of the wallet's current lock state or the previous passphrase. Any caller with access to the `wallet.create`/`application.create` RPC surface can hijack an already-created wallet by supplying an attacker-chosen mnemonic.

### Finding Description
`create` is defined as: [1](#0-0) 

It never calls `this.exists()` nor `#assertWalletIsUnlocked` (defined at [2](#0-1) ) before invoking `#setSeed`. `#setSeed` unconditionally writes to storage: [3](#0-2) 
It only branches on whether a `passphrase` argument was *provided in this call*, not on whether one is required to authenticate against the *existing* seed. There is no read-then-compare against the old passphrase/seed, no lock check, and no `exists()` guard — `walletStorage.set(SEED_KEY, seed, { passphrase })` (line 109) simply overwrites whatever was there.

The `import` method reuses `create` directly with the same lack of guard: [4](#0-3) 

At the application layer, `Application#create` also performs no `exists()`/authentication check before delegating to `#wallet.create`: [5](#0-4) 

By contrast, other mutating wallet operations such as `addSeed` and `removeManySeeds` explicitly call `#assertWalletIsUnlocked` first: [6](#0-5) [7](#0-6) 
and `changePassphrase` requires successfully decrypting with `currentPassphrase` before calling `#setSeed`: [8](#0-7) 
`create` has none of these protections, making it an outlier among seed-mutating operations.

`makeConcurrent(..., { concurrency: 1 })` only serializes concurrent invocations of `create`; it provides no authentication or existence check whatsoever.

### Impact Explanation
An unprivileged caller with access to the `wallet.create` (or `application.create`) API can replace an existing wallet's seed with an attacker-controlled mnemonic without knowing the current passphrase and without the wallet being locked/unlocked in any particular state. This is a full wallet/seed hijack: subsequent operations (unlock, getMnemonic, signing) will operate against the attacker's seed, and the legitimate user's original seed material stored under `SEED_KEY` is destroyed/replaced, matching Hydra's "unauthorized signing / privilege persistence / wallet compromise" bounty impact category.

### Likelihood Explanation
The precondition is simply that the attacker can call `wallet.create`/`application.create` a second time via the exposed API surface — no leaked keys, no privileged state, no social engineering required. This is directly reachable and repeatable (each call to `create` succeeds unconditionally), matching the proof idea in the prompt.

### Recommendation
Add a guard in `Wallet#create` that throws if `await this.exists()` is true and the caller has not authenticated (e.g. require unlocking with the current passphrase first, or route "replace seed" flows exclusively through `changePassphrase`-style re-authentication). At minimum, `create` should mirror the guard pattern used by `addSeed`/`removeManySeeds` (`#assertWalletIsUnlocked`) and reject overwriting an existing `SEED_KEY` unless explicitly authorized (e.g. via a distinct, authenticated "recreate/reset wallet" API instead of reusing bare `create`).

### Proof of Concept
```js
// features/wallet/module/__tests__/index.test.js (new test)
it('create() must not silently overwrite an existing wallet seed', async () => {
  const { seedId: firstSeedId } = await wallet.create({ mnemonic })
  expect(await wallet.exists()).toBe(true)

  // Attacker calls create() again with a different mnemonic, no passphrase challenge
  const attackerMnemonic =
    'zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong'

  // Expected (secure) behavior: this should throw because a wallet already exists
  await expect(wallet.create({ mnemonic: attackerMnemonic })).rejects.toThrow()

  // Current (vulnerable) behavior observed instead:
  // const { seedId: secondSeedId } = await wallet.create({ mnemonic: attackerMnemonic })
  // expect(secondSeedId).not.toBe(firstSeedId) // seed silently replaced
})
```

### Citations

**File:** features/wallet/module/wallet.js (L61-64)
```javascript
  #assertWalletIsUnlocked = async () => {
    const isLocked = await this.isLocked()
    assert(!isLocked, 'wallet is locked')
  }
```

**File:** features/wallet/module/wallet.js (L94-114)
```javascript
  #setSeed = async ({ seed, passphrase }) => {
    if (this.#usePassword) {
      if (passphrase) {
        await this.walletStorage.delete(GENERATED_PASSPHRASE_KEY)
        await this.walletStorage.set(HAS_USER_SET_PASSPHRASE_KEY, true)
      } else {
        if (this.#useAutoGeneratedPassword) {
          passphrase = genPassphrase()
          await this.walletStorage.set(GENERATED_PASSPHRASE_KEY, passphrase)
        }

        await this.walletStorage.set(HAS_USER_SET_PASSPHRASE_KEY, false)
      }
    }

    await this.walletStorage.set(SEED_KEY, seed, { passphrase })
    // Restoring a seedless backup restarts the app immediately.
    // Wait a bit longer to ensure the data is fully stored before restarting.
    const storedSeed = await this.walletStorage.get(SEED_KEY, { passphrase })
    assert(storedSeed.seed.equals(seed.seed), safeString`setSeed failed`)
  }
```

**File:** features/wallet/module/wallet.js (L137-139)
```javascript
  addSeed = async ({ mnemonic, label, compatibilityMode }) => {
    await this.#assertWalletIsUnlocked()

```

**File:** features/wallet/module/wallet.js (L173-176)
```javascript
  removeManySeeds = async (seedIds) => {
    this.#assertMultiSeedSupport()
    await this.#assertWalletIsUnlocked()

```

**File:** features/wallet/module/wallet.js (L231-250)
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
    { concurrency: 1 }
  )
```

**File:** features/wallet/module/wallet.js (L252-259)
```javascript
  import = makeConcurrent(
    async ({ mnemonic, passphrase }) => {
      await assertMnemonic(mnemonic, this.#validMnemonicLengths)

      return this.create({ passphrase, mnemonic })
    },
    { concurrency: 1 }
  )
```

**File:** features/wallet/module/wallet.js (L328-344)
```javascript
  changePassphrase = async ({ currentPassphrase, newPassphrase }) => {
    if (this.#usePassword) {
      let seed

      try {
        seed = await this.#getSeed({ passphrase: currentPassphrase })
      } catch {
        this.#logger.debug('changePassphrase() failed: wrong password')
        throw new Error('Wrong password. Try again.')
      }

      try {
        await this.#setSeed({ seed, passphrase: newPassphrase })
      } catch {
        this.#logger.debug('changePassphrase() failed')
        throw new Error('Something went wrong. Try again.')
      }
```

**File:** features/application/src/modules/application.ts (L249-266)
```typescript
  create = async (opts?: CreateApplicationParams) => {
    this.#logger.log('creating wallet')

    await this.#applicationStarted
    const createResult = await this.#wallet.create(opts)

    const isLocked = await this.#wallet.isLocked()

    await this.fire(Hook.Create, {
      hasPassphraseSet: !!opts?.passphrase,
      isBackedUp: false,
      isLocked,
      isRestoring: false,
      walletExists: true,
      seedId: createResult.seedId, // will be deprecated
      createResult,
    })
  }
```
