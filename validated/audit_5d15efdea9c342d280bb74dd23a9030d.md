### Title
`Wallet.create()` can silently reinitialize an existing wallet, overwriting the seed without authentication - (File: `features/wallet/module/wallet.js`)

### Summary
The `create` method of the `Wallet` class never checks whether a wallet already exists before writing a (possibly attacker-supplied) mnemonic into the seed slot. Unlike `changePassphrase`, which requires the `currentPassphrase` to decrypt and re-encrypt the seed, `create` unconditionally derives a seed and persists it via `#setSeed`, clobbering any pre-existing seed and passphrase-related flags. This mirrors the CoreCollection `initialize` bug class: a state-mutating "setup" function that sets up core secrets but has no guard preventing it from being re-run against an already-initialized instance.

### Finding Description
`Wallet.create` accepts an optional `mnemonic`/`passphrase`, generates the seed, and immediately calls `#setSeed`, with no precondition check against `exists()`: [1](#0-0) 

Compare this to `exists()`, which is only used for read purposes elsewhere and never enforced inside `create`: [2](#0-1) 

`#setSeed` itself has no "already initialized" guard either - it just writes over `SEED_KEY`/`HAS_USER_SET_PASSPHRASE_KEY`/`GENERATED_PASSPHRASE_KEY`, and does not require the current passphrase (unlike `changePassphrase`, which does): [3](#0-2) [4](#0-3) 

At the SDK boundary, `application.create` simply proxies to `wallet.create` with the same lack of any `walletExists` guard, and even hard-codes `walletExists: true` in the emitted lifecycle payload, so downstream consumers cannot distinguish "created" from "reinitialized": [5](#0-4) 

This API is exposed as an ordinary RPC-callable method through the SDK's API layer (`exodus.wallet.create` / `exodus.application.create`), reachable by any code with access to the RPC client on the UI side of the process boundary: [6](#0-5) 

Because there is no `assert(!(await this.exists()))`-style check (the `onlyUnInitialized`-equivalent for this codebase), any call to `create()` after the wallet has already been initialized will silently discard the previous seed/passphrase state without requiring proof of ownership of the existing wallet (no current passphrase, no unlock check).

### Impact Explanation
An unprivileged caller with access to the wallet API surface (e.g., a compromised or buggy UI/renderer, or any code path that can invoke `wallet.create`/`application.create` a second time) can overwrite the user's existing seed with an attacker-chosen mnemonic and passphrase. Because `#setSeed` requires no proof of the current passphrase, this is not "changing" the wallet with authorization, but a raw overwrite. Consequences:
- The legitimate user permanently loses access to their existing seed/funds (the old mnemonic is gone; `exists()` still reports `true` so the loss may not be immediately apparent).
- An attacker can plant a known mnemonic; if the victim later deposits funds into addresses derived from what they believe is still "their" wallet, the attacker can drain them - a direct wallet-compromise scenario, analogous to CoreCollection's `payableToken` reset enabling fund retrieval.

### Likelihood Explanation
Likelihood is bounded by the same factor the original report flagged for CoreCollection: it requires the caller to already have access to the privileged `create`/`import` API surface (roughly analogous to `onlyOwner`). However, exactly as in the CoreCollection finding, the absence of an "already initialized" guard turns any accidental or malicious re-invocation of this owner-gated function into a full state reset with wallet-compromise consequences, which is why the C4 judges ultimately rated the analogous bug High severity.

### Recommendation
Add an explicit guard at the start of `Wallet.create` (and/or `Wallet.import`) that throws if the wallet is already initialized, mirroring the `onlyUnInitialized` mitigation from the report:

```js
create = makeConcurrent(async ({ mnemonic, passphrase } = {}) => {
  if (await this.exists()) {
    throw new Error('wallet already exists; use import({ forceRestart: true }) or delete the wallet first')
  }
  // ... existing logic
})
```
Any legitimate "recreate" flow (e.g. restore/import replacing an existing wallet) should go through the existing `import`/`delete` + restart flow, which already requires explicit `forceRestart`/`forgotPassphrase` flags, rather than through a silent `create()` re-run.

### Proof of Concept
1. Start the SDK and create a wallet: `await exodus.application.create({ passphrase: 'pw1' })`. `wallet.exists()` now returns `true`, seed `S1` stored.
2. Without unlocking or providing `pw1`, call `await exodus.application.create({ mnemonic: attackerMnemonic, passphrase: 'pw2' })`.
3. `Wallet.create` runs `#setSeed` again, overwriting `SEED_KEY`, `HAS_USER_SET_PASSPHRASE_KEY`, and clearing `GENERATED_PASSPHRASE_KEY`, without ever checking `exists()` or requiring `pw1`.
4. `wallet.exists()` still returns `true`, but `getMnemonic({ passphrase: 'pw1' })` now fails ("Wrong password") and `getMnemonic({ passphrase: 'pw2' })` returns the attacker's mnemonic - the original seed `S1` is unrecoverable, and any funds sent afterward derive from the attacker-controlled seed. [1](#0-0)

### Citations

**File:** features/wallet/module/wallet.js (L66-69)
```javascript
  exists = async () => {
    const encryptedSeed = await this.walletStorage.get(SEED_KEY)
    return !!encryptedSeed
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

**File:** features/wallet/module/wallet.js (L328-348)
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
    } else {
      throw new Error('Password support is disabled')
    }
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

**File:** sdks/headless/src/api/index.js (L51-68)
```javascript
  const applicationWalletApi = {
    addSeed: application.addSeed,
    start: deprecated(application.start),
    stop: deprecated(application.stop),
    load: deprecated(application.load),
    unload: deprecated(application.unload),
    create: deprecated(application.create),
    lock: deprecated(application.lock),
    unlock: deprecated(application.unlock),
    import: deprecated(application.import),
    delete: deprecated(application.delete),
    getMnemonic: deprecated(application.getMnemonic),
    setBackedUp: deprecated(application.setBackedUp),
    changePassphrase: deprecated(application.changePassphrase),
    changeLockTimer: deprecated(application.changeLockTimer),
    restartAutoLockTimer: deprecated(application.restartAutoLockTimer),
    restoreFromCurrentPhrase: deprecated(application.restoreFromCurrentPhrase),
  }
```
