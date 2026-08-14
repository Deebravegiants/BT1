### Title
Hook listeners registered via `Application#hook` receive raw, unfrozen `createResult`/`importResult` objects, allowing in-place mutation of secret material before it is frozen for other consumers - ([File: features/application/src/modules/application.ts])

### Summary
`Application#fire` invokes `hook()`-registered listeners with the raw `params` object directly, completely bypassing `proxyFreeze`; only the subsequent `emit()` call at the end of `fire()` applies `proxyFreeze` to `on()`-style listeners. Since hooks share the same object by reference and run sequentially, any plugin registered via `application.hook(Hook.Create, ...)` or `application.hook(Hook.Import, ...)` can mutate nested mutable structures (e.g., a `Buffer` inside `createResult`/`importResult`) in place, and that corruption is visible to every hook/listener that runs afterward, including the final `emit()` consumers, because `proxyFreeze` only wraps the object after the damage is already done to the underlying data.

### Finding Description
`Application#fire` builds `hookFns` that call `hook(params)` directly with the unmodified `params` reference: [1](#0-0) 

Only afterwards does it call `this.emit(hookName, params)`, and it is only `emit` that applies `proxyFreeze`: [2](#0-1) 

Plugins are attached to the `hook()` path (not `on()`), as shown in the SDK's plugin-attachment code, which calls `application.hook(hookName, ...)` for every declared lifecycle method (`onCreate`, `onImport`, etc.): [3](#0-2) 

`Application#create` fires `Hook.Create` with `createResult` embedded directly (containing secret material such as the newly generated seed): [4](#0-3) 

and `Application#import` similarly fires `Hook.Import`/`Hook.PreImport` with `importResult`: [5](#0-4) 

Hooks execute sequentially (unless `concurrent: true`), each `await hook(params)` sharing the identical object reference: [6](#0-5) 

Because `proxyFreeze` wraps a Proxy around the *same underlying object* rather than deep-cloning it, any mutation performed on nested mutable values (e.g., zeroing/overwriting bytes of a `Buffer`, pushing to an array, or replacing properties of a plain nested object) by an earlier `hook()` listener persists in the underlying data. This corrupted data is what later `hook()` listeners see, and it is also what `emit()`'s `proxyFreeze` wraps at the end of `fire()` — the freeze happens too late to protect data integrity, it only prevents top-level reassignment on the read side for `on()` consumers, not corruption performed earlier via the un-proxied `hook()` reference. `hook.priority` sorting determines call order, so any module (including a lower-privilege/third-party plugin) registering a hook can arrange to run before a security-sensitive consumer (e.g., a backup/persistence plugin) that reads `createResult`/`importResult` later in the same `fire()` call, and tamper with the shared secret-bearing object before it's consumed.

### Impact Explanation
This breaks the "secrets stay secret / secrets stay intact" invariant for wallet creation and import flows: a plugin with hook access (not full wallet privilege) can silently corrupt or replace nested secret bytes (e.g., a mnemonic/seed buffer) inside `createResult`/`importResult` before other legitimate hook consumers (such as backup, persistence, or seed-restore plugins) process it. This can lead to persistence of corrupted/attacker-influenced seed material, mismatched seed state between subsystems, or denial of correct wallet creation/import — a data-integrity compromise of secret material shared across hook consumers, matching a "wrong data / integrity of secret material" class of impact in the Hydra bounty scope. It does not directly leak secrets off-device, since no encoding/exfiltration path is shown here, but it does allow a lower-privilege listener to tamper with data that higher-privilege listeners subsequently trust.

### Likelihood Explanation
The attack requires only that the attacker's module/plugin can register a lifecycle hook (`application.hook(...)`), which is the standard, ordinary integration mechanism for any plugin in this SDK — no elevated wallet permission is needed. Execution order is controllable via `hook.priority`, making the timing (run before the "victim" consumer processes the shared object) fully practical and repeatable. The lack of any freezing/cloning on the `hook()` path (as opposed to `emit()`) means this is deterministic, not a race condition.

### Recommendation
Apply the same `proxyFreeze` (or a deep-clone) to `params` before invoking `hook()` listeners in `fire()`, not just before `emit()`. Ideally, deep-clone parameters containing secret material (`createResult`, `importResult`) per-listener so that no listener can mutate data observed by another, rather than relying on a shared mutable reference with only a post-hoc, single-target Proxy wrapper.

### Proof of Concept
Unit test plan (in `features/application/src/modules/application.test.ts` or similar):
1. Instantiate `Application` with a `wallet` mock whose `create()` resolves `{ seedId: 'x', seed: Buffer.from('secret-bytes') }` as `createResult`.
2. Register two hooks via `application.hook(Hook.Create, listenerA)` and `application.hook(Hook.Create, listenerB)`, with `listenerA.priority` higher than `listenerB.priority` so `listenerA` runs first.
3. In `listenerA`, mutate `params.createResult.seed.fill(0)` (or `params.createResult.seed[0] = 0xff`) in place.
4. In `listenerB`, assert `params.createResult.seed` still equals `Buffer.from('secret-bytes')`.
5. Call `application.create()` and observe the assertion in `listenerB` fails — proving that `listenerA`, despite only having `hook()` access, corrupted the secret buffer before `listenerB` (and before the final frozen `emit('create', ...)` payload) could observe the original, untampered secret bytes.

### Citations

**File:** features/application/src/modules/application.ts (L111-114)
```typescript
  emit = (name: string, ...args: any) => {
    const isFreezable = (val: any) => val && typeof val === 'object'
    return super.emit(name, ...args.map((arg: any) => (isFreezable(arg) ? proxyFreeze(arg) : arg)))
  }
```

**File:** features/application/src/modules/application.ts (L210-218)
```typescript
  private executeHooks = async (hooksFns: HookFn[], concurrent = false) => {
    if (concurrent) {
      return Promise.allSettled(hooksFns.map((fn) => fn()))
    }

    for (const hook of hooksFns) {
      await hook()
    }
  }
```

**File:** features/application/src/modules/application.ts (L236-247)
```typescript
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

**File:** sdks/headless/src/plugins/attach.js (L34-45)
```javascript
  Object.entries(plugins).forEach(([name, lifecycleMethods]) => {
    const entries = Object.entries(lifecycleMethods || {})

    for (const [lifecycleMethod, fn] of entries) {
      const hookName = LIFECYCLE_METHOD_TO_HOOK_NAME[lifecycleMethod]
      if (hookName) {
        application.hook(hookName, lifecycleFuncWrapper(fn, `plugin ${name}.${lifecycleMethod}`))
      } else {
        logger.error(`plugin "${name}" declares unsupported lifecycle method "${lifecycleMethod}"`)
      }
    }
  })
```
