This confirms the analog exists but requires stating explicit limits, since I could not fully verify whether an actual client can call further state-mutating methods (e.g. `unlock`, `import`, `create`) in the window between `delete()` setting the flag and the actual process restart being enacted by the host application (browser extension / mobile shell).

### Title
`Application.delete()` marks wallet deletion via a flag but does not itself clear or lock the wallet, leaving a window where `unlock`/`create`/`import` can be called on the "deleted" wallet before restart - (File: `features/application/src/modules/application.ts`)

### Summary
The GMX report shows that an "irreversible" emergency-close action can be undone because the code that performs the closing operation (`emergencyClose`) does not set any permanent flag, so later calls to state-changing functions (`emergencyPause`/`emergencyResume`) can still run and effectively reopen the vault. The Hydra `Application.delete()` flow has the same structural weakness: deletion is not enforced synchronously and atomically. Instead, `delete()` [1](#0-0)  only sets a persisted `DELETE_FLAG` and fires `Hook.Restart`; the actual wallet clearing (`this.#wallet.clear()`) only happens later inside `start()` [2](#0-1) , which is expected to run only after the host process has fully restarted.

### Finding Description
`delete()` does not lock, clear, or otherwise invalidate the currently running `Application` instance/wallet object — it merely persists an intent flag (`DELETE_FLAG`) and fires the `Hook.Restart` hook [1](#0-0) . `Hook.Restart` is a normal, listener-driven event dispatched through `fire()` [3](#0-2) ; in the SDK wiring, this event is simply forwarded to the host process over `port.emit('restart', payload)` [4](#0-3) . Whether/when the actual process restart happens is entirely up to the host application (extension background script, mobile app, etc.) reacting to that port event — it is not guaranteed to happen synchronously or to prevent the in-memory `Application`/`Wallet` instance from continuing to service calls in the interim.

Because `#applicationStarted` is already resolved by the time `delete()` is called, other public methods such as `unlock()` [5](#0-4) , `create()` [6](#0-5) , `import()` [7](#0-6) , and `changePassphrase()` [8](#0-7)  remain fully callable on the same in-memory instance with no check of `DELETE_FLAG` (that flag is only consulted inside `start()`). This mirrors the vault bug: an operation intended to be a final, irreversible action (`emergencyClose` / `delete`) sets no in-memory guard that blocks subsequent state-mutating operations (`emergencyPause`/`emergencyResume` / `unlock`, `create`, `import`) from running before the "closing" transition (the actual vault status change / actual process restart) is fully completed and enforced.

### Impact Explanation
If the host restart is delayed, asynchronous, or can be raced (e.g., a compromised/malicious dApp or script that keeps invoking wallet RPCs immediately after triggering `delete()`, or a host implementation that does not immediately tear down the running SDK instance), an attacker or buggy caller could: unlock the wallet and extract the mnemonic via `getMnemonic()`, before deletion is finalized; or overwrite state via `import()`/`create()` while `DELETE_FLAG` is still pending, leading to inconsistent state where the flag causes the *newly created/imported* wallet to be wiped on the next actual `start()` (data loss on the new seed) rather than the originally-intended one. This directly touches the auth/secret-disclosure and account-isolation trust boundaries called out in scope (unlock/getMnemonic before finalized deletion).

### Likelihood Explanation
This requires that the host process's handling of the `restart` port event is not perfectly synchronous/atomic with respect to further RPC calls into the same running `Application` instance — I was not able to verify the actual browser-extension/mobile host-side restart handler in the indexed portion of the codebase to confirm or rule out this race window. The existing unit test `sdks/headless/__tests__/wallet.test.js` [9](#0-8)  only verifies the *intended* sequential flow (delete → restart → new instance → clear → start) and does not test concurrent/racing calls against the same instance during the gap, so the codebase's own test suite does not rule out the race.

### Recommendation
1. Make `delete()` synchronously lock and neutralize the running `Application` instance (e.g., immediately call `this.#wallet.lock()`/clear sensitive in-memory state and set an in-memory "deleted" guard) before firing `Hook.Restart`, mirroring the recommendation to set a permanent flag before allowing any other state transition.
2. Add a guard at the top of `unlock`, `create`, `import`, `changePassphrase`, `getMnemonic`, and `addSeed` that checks the in-memory "deleted" flag (not just the persisted `DELETE_FLAG` consulted only in `start()`) and throws/rejects if a deletion has been requested but not yet finalized by restart.

### Proof of Concept
Could not be constructed/verified with the available indexed context: the host-process restart handler (browser-extension/mobile background script that actually reacts to `port.emit('restart', …)`) is outside the indexed portion of this monorepo, so I could not confirm from code alone whether calls like `unlock()`/`import()` can actually be raced against `delete()` in a real deployment before the process is torn down. Due to index size limits, some file contents (particularly platform-specific background/host process code) may not be available — a Devin session with full repository access would be needed to trace the exact `restart` event handler and confirm whether the race window is exploitable in practice.

### Citations

**File:** features/application/src/modules/application.ts (L116-131)
```typescript
  start = async ({ restoring, importing }: StartApplicationParams = {}) => {
    const [deleteFlag, importFlag] = await this.#flagsStorage.batchGet([DELETE_FLAG, IMPORT_FLAG])

    if (restoring) {
      await this.#flagsStorage.set(RESTORE_FLAG, true)
    }

    const isDeleting = !!deleteFlag
    const isImporting = importing || !!importFlag

    if (isDeleting) await this.#wallet.clear()

    if (isDeleting || isImporting) {
      await this.#flagsStorage.batchDelete([DELETE_FLAG, IMPORT_FLAG])
      await this.#passphraseCache.clear()
    }
```

**File:** features/application/src/modules/application.ts (L220-247)
```typescript
  fire = async (
    hookName: ValueOf<typeof Hook>,
    params?: unknown[] | unknown,
    { concurrent }: { concurrent?: boolean } = {}
  ) => {
    assert(HOOKS.has(hookName), `no such hook: ${hookName}`)

    this.#logger.debug(`firing hooks ${concurrent ? 'concurrently' : 'sequentially'}`, hookName)

    const hooks = this.#hooks[hookName] || []

    if (this.#hookNeedsSorting[hookName]) {
      hooks.sort((a, b) => (b.priority || 0) - (a.priority || 0))
      this.#hookNeedsSorting[hookName] = false
    }

    const hookFns = hooks.map((hook) => async () => {
      try {
        await hook(params)
      } catch (err) {
        this.#logger.error(`application lifecycle hook failed: ${hookName}`, hook.name, params, err)
        throw err
      }
    })

    await this.executeHooks(hookFns, concurrent)
    this.emit(hookName, params)
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

**File:** features/application/src/modules/application.ts (L409-426)
```typescript
  unlock = async (opts?: UnlockWalletParams) => {
    this.#logger.log('unlocking')

    await this.#applicationStarted
    await this.#wallet.unlock(opts)
    await this.#lockedAtom.set(false)

    await this.fire(Hook.Migrate)
    await this.fire(Hook.Unlock)

    void this.#restoreIfNeeded()

    if (opts?.passphrase) {
      void this.#passphraseCache.set(opts.passphrase)
    }

    this.#logger.log('unlocked')
  }
```

**File:** features/application/src/modules/application.ts (L428-438)
```typescript
  changePassphrase = async (opts: WalletChangePassphraseParams) => {
    this.#logger.log('changing passphrase')

    const { currentPassphrase, newPassphrase } = opts
    await this.#applicationStarted
    await this.#wallet.changePassphrase({ currentPassphrase, newPassphrase })
    await this.#passphraseCache.set(newPassphrase)
    await this.fire(Hook.ChangePassphrase)

    this.#logger.log('passphrase changed')
  }
```

**File:** features/application/src/modules/application.ts (L440-445)
```typescript
  delete = async (opts: DeleteApplicationParams = {}) => {
    const { forgotPassphrase, restartOptions } = opts
    await this.#flagsStorage.set(DELETE_FLAG, true)
    await this.#flagsStorage.delete(RESTORE_FLAG)
    await this.fire(Hook.Restart, { ...restartOptions, reason: 'delete', forgotPassphrase })
  }
```

**File:** sdks/headless/src/index.js (L164-164)
```javascript
    application.on('restart', (payload) => port.emit('restart', payload))
```

**File:** sdks/headless/__tests__/wallet.test.js (L223-253)
```javascript
  test('should delete wallet', async () => {
    const expectRestart = expectEvent({ port, event: 'restart', payload: { reason: 'delete' } })

    await exodus.application.start()

    await exodus.application.create({ passphrase })

    await expect(exodus.wallet.exists()).resolves.toBe(true)

    await exodus.application.unlock({ passphrase })

    await exodus.application.delete()

    await expectRestart

    // Simulate new wallet after restart
    const newPort = new Emitter()

    const newExodus = createExodus({ adapters: { ...adapters, port: newPort }, config }).resolve()
    const expectClear = expectEvent({ port: newPort, event: 'clear' })
    const expectStart = expectEvent({ port: newPort, event: 'start' })

    await newExodus.application.start()
    await expectClear
    await expectStart

    await expect(newExodus.wallet.exists()).resolves.toBe(false)

    await newExodus.application.stop()
    await exodus.application.stop()
  })
```
