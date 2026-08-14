### Title
Unawaited passphrase cache write in `Application#unlock` can race with `Application#lock`, leaving a live cached passphrase after lock - (File: `features/application/src/modules/application.ts`)

### Summary
`Application#unlock` fires `void this.#passphraseCache.set(opts.passphrase)` without awaiting it before returning, while `Application#lock` awaits `this.#passphraseCache.clear()`. Because there is no mutex/queue serializing calls into `Application`, an attacker with unrestricted RPC access can call `unlock({passphrase})` immediately followed by `lock()`, causing the unawaited `set()` write to land in storage after `clear()` has already executed, leaving a persisted passphrase despite the wallet reporting `lockedAtom === true`.

### Finding Description
`unlock()` awaits `this.#wallet.unlock`, sets `lockedAtom` to `false`, fires hooks, then non-deterministically caches the passphrase via a fire-and-forget call: [1](#0-0) 

`lock()` awaits `this.#wallet.lock()`, sets `lockedAtom` to `true`, and awaits `this.#passphraseCache.clear()`: [2](#0-1) 

`PassphraseCache.set` and `PassphraseCache.clear` both perform async storage I/O (`batchSet` / `storage.clear`) with no locking between them: [3](#0-2) [4](#0-3) 

Both `unlock` and `lock` are exposed directly as RPC-callable API methods with no additional serialization/mutex layer between calls: [5](#0-4) 

Because `unlock()` returns to the caller (and therefore the RPC caller can immediately issue the next `lock()` call) before the passphrase-cache `set()` promise settles, and because there is no queueing mechanism forcing `Application` method calls to run sequentially, an attacker-controlled interleaving can result in `set()`'s `storage.batchSet` write completing after `clear()`'s `storage.clear()` has already run. The result: `lockedAtom` is `true` (UI/state reports locked) but `PassphraseCache.get()` still returns a valid passphrase, which is subsequently consumable by `#autoUnlock` to silently re-unlock the wallet.

### Impact Explanation
This breaks the "locked means locked" invariant: after a caller observes/waits on `lock()` resolving, secret unlock material (the passphrase) can still be recoverable from cache storage. Any code path with access to that storage (e.g., `#autoUnlock`, `restoreFromCurrentPhrase` when passphrase is omitted) can use it to re-derive access without prompting the user, constituting persistence of unlock authority beyond an explicit lock action (privilege persistence / secret isolation violation).

### Likelihood Explanation
The precondition is simply the ability to issue two back-to-back RPC calls (`unlock` then `lock`) with no delay, which matches the stated threat model (no rate limiting, unprivileged RPC caller with valid passphrase — e.g., the legitimate user's own client automation, or a compromised dapp/UI layer that can drive these calls). No cryptographic bypass is needed; it is a pure TOCTOU race enabled by the fire-and-forget (`void`) call combined with lack of call serialization in `Application`. Under realistic storage latency (e.g., a slower storage backend/queued IndexedDB/AsyncStorage writes), the window is easily wide enough to be won deterministically in tests and plausibly in production under load.

### Recommendation
Await the passphrase cache write in `unlock()` before returning, or otherwise ensure `set()` and `clear()` cannot interleave — e.g., await `this.#passphraseCache.set(opts.passphrase)` synchronously within `unlock()`, and/or add a per-instance mutex/queue around all `PassphraseCache` mutating operations (`set`, `clear`, `changeTtl`, `scheduleClear`) so they execute atomically relative to each other, and serialize `Application#lock`/`Application#unlock` calls.

### Proof of Concept
Integration test:
1. Construct `PassphraseCache` with an injected `storage` mock whose `batchSet` resolves after a controllable delay (e.g., via a deferred promise) while `clear` resolves immediately.
2. Call `application.unlock({ passphrase: 'secret' })` and immediately (without awaiting the cache-set side effect) call `await application.lock()`.
3. Resolve the delayed `batchSet` after `lock()` has completed.
4. Assert `await passphraseCache.get()` is `undefined` immediately after `lock()` resolves, and again after the delayed `batchSet` settles — expected failure: passphrase reappears in cache after `lock()` reports done, violating the "locked means locked" invariant.

### Citations

**File:** features/application/src/modules/application.ts (L352-362)
```typescript
  lock = async () => {
    this.#logger.log('locking')

    await this.#applicationStarted
    await this.#wallet.lock()
    await this.#lockedAtom.set(true)
    await this.#passphraseCache.clear()
    await this.fire(Hook.Lock)

    this.#logger.log('locked')
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

**File:** features/application/src/modules/passphrase-cache.ts (L111-114)
```typescript
  async clear() {
    this.#logger.log('clearing cache')
    await this.#storage.clear()
  }
```

**File:** features/application/src/api/index.ts (L219-240)
```typescript
    application: {
      start: application.start,
      stop: application.stop,
      load: application.load,
      unload: application.unload,
      create: application.create,
      lock: application.lock,
      unlock: application.unlock,
      import: application.import,
      restart: application.restart,
      delete: application.delete,
      getMnemonic: application.getMnemonic,
      setBackedUp: application.setBackedUp,
      changePassphrase: application.changePassphrase,
      changeLockTimer: application.changeLockTimer,
      restartAutoLockTimer: application.restartAutoLockTimer,
      addSeed: application.addSeed,
      removeSeed: application.removeSeed,
      restoreFromCurrentPhrase,
    },
  }
}
```
