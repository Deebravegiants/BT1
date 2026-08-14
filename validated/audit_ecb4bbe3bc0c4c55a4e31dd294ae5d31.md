### Title
Wallet creation can silently overwrite an existing wallet's seed (missing "already exists" guard, analogous to unguarded `initialize()`) - ([File: features/wallet/module/wallet.js])

### Summary
The external report flags `ERC20Facet.initialize()` for lacking a guard (`require(!finalized, ...)`) that would prevent it from being invoked more than once, letting critical state be silently re-initialized/overwritten. The same bug class exists in hydra's wallet lifecycle: `Wallet.create()` and its caller `Application.create()` never check whether a wallet already exists before generating/storing a new seed, so calling `exodus.application.create()` a second time overwrites the primary seed of an already-initialized wallet.

### Finding Description
`Wallet.create()` is only concurrency-limited (`makeConcurrent(..., { concurrency: 1 })`), not idempotency-guarded: [1](#0-0) 

It unconditionally generates (or accepts) a mnemonic, derives a seed, and calls `#setSeed`, which persists it under the `SEED_KEY` — overwriting whatever was previously stored, with no `exists()` check before doing so: [2](#0-1) 

`exists()` is defined and available, but `create()` never calls it before persisting: [3](#0-2) 

The public SDK-level `Application.create()` simply forwards to `wallet.create(opts)` with no pre-check for `walletExists`, unlike `Application.import()`, which explicitly reads `walletExists` and branches into a forced-restart/import flow to protect an existing wallet: [4](#0-3) [5](#0-4) 

`create` is exposed directly through the public `application` API surface (`exodus.application.create`), reachable by any caller with access to that API surface (e.g. UI/RPC bridge callers), exactly as `import` is: [6](#0-5) 

This mirrors the reported bug class precisely: a lifecycle "initialize"-style method (`create`) that is meant to run exactly once per wallet, but has no guard (`assert(!(await this.exists()))` / `require(!finalized)`) preventing re-invocation, so a second call clobbers already-initialized secret state instead of throwing.

### Impact Explanation
If `application.create()`/`wallet.create()` is invoked a second time against an existing wallet (whether via a UI bug, a compromised/malicious caller on the RPC/port bridge, or unexpected re-entrancy in app startup logic), the previously stored mnemonic/seed is silently replaced by a brand-new one under the same storage key. This is a direct wallet-compromise/loss scenario:
- The user's original seed becomes irrecoverable (no restore path retains the old seed once overwritten).
- Because the new seed is written without requiring proof of the current passphrase, `create()` could be used to unilaterally replace another party's wallet secret if reachable across a trust boundary (e.g. an RPC bridge/UI channel that should only permit wallet creation on a fresh install), unlike `changePassphrase`/`import`-with-existing-wallet flows, which reference the notion of an existing wallet and are handled specially.

### Likelihood Explanation
`create` and `import` are both part of the always-exposed public `application` API (`applicationApiDefinition`), so any code path that can call into this API (extension background/UI messaging, SDK integration bugs, or a compromised UI component) can trigger `create()` again. There's no client-side or module-side "already exists" check acting as a backstop, so likelihood depends entirely on whether some other layer (UI state machine) always prevents a second call — which is not enforced at the module boundary itself, making it a latent trap rather than a hardened invariant.

### Recommendation
Add an explicit guard mirroring the suggested fix in the report (`require(!finalized, ...)`) before persisting a newly created seed:
```js
create = makeConcurrent(
  async ({ mnemonic, passphrase } = {}) => {
    assert(!(await this.exists()), 'wallet already exists')
    // ... existing logic
  },
  { concurrency: 1 }
)
```
Alternatively, enforce this check in `Application.create()` before calling `this.#wallet.create(opts)`, consistent with how `Application.import()` already inspects `walletExists` and routes through a distinct, explicit "overwrite" flow (`forceRestart`/`IMPORT_FLAG`) rather than silently mutating state in place.

### Proof of Concept
1. `await exodus.application.start()`
2. `await exodus.application.create({ passphrase: 'A' })` → wallet created with mnemonic M1, `exists() === true`.
3. `await exodus.application.create({ passphrase: 'B' })` → succeeds again with no error; internally `Wallet.create` regenerates a new mnemonic M2 (or uses a caller-supplied one) and overwrites `SEED_KEY` in `walletStorage`.
4. `await exodus.application.getMnemonic({ passphrase: 'B' })` now returns M2; M1 (and any funds/addresses derived from it) is permanently lost because nothing in `create()` verified `exists()` first — confirmed by reading `features/wallet/module/wallet.js:231-250` (`create`) and `:66-69` (`exists`), which are never composed together.

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

**File:** features/application/src/modules/application.ts (L268-312)
```typescript
  import = async (opts: ImportApplicationParams) => {
    this.#logger.log('importing wallet')

    await this.#eventLog.record({
      event: 'restore_wallet',
      applicationImportOpts: {
        forceRestart: opts.forceRestart,
        forgotPassphrase: opts.forgotPassphrase,
        backupType: opts.backupType,
      },
    })

    await this.#flagsStorage.set(RESTORE_FLAG, true)

    await this.#applicationStarted

    const walletExists = await this.#wallet.exists()

    const { forceRestart, compatibilityMode, backupType, forgotPassphrase, ...wallet } = opts

    if (backupType) {
      await this.#storage.set('backupType', backupType)
    }

    await this.fire(Hook.PreImport, { backupType, walletExists, forgotPassphrase })

    const importResult = await this.#wallet.import(wallet)
    const importParams = {
      compatibilityMode,
      backupType,
      importResult,
      seedId: importResult.seedId, // will be deprecated
    }

    if (forceRestart || walletExists) {
      await this.#flagsStorage.set(IMPORT_FLAG, true)

      await this.#storage.set('importParams', importParams)
      await this.fire(Hook.Restart, { reason: 'import', backupType, forgotPassphrase })
    } else {
      await this.fire(Hook.Import, importParams)

      this.#logger.log('wallet imported')
    }
  }
```

**File:** features/application/src/api/index.ts (L54-61)
```typescript
    /**
     * Creates a new wallet.
     * @example
     * ```typescript
     * await exodus.application.create()
     * ```
     */
    create: Application['create']
```
