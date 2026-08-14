### Title
Fire-and-forget passphrase cache writes/clears in `unlock()`/`lock()` allow stale unlock material to survive a lock transition, enabling silent auto-unlock on next `start()` - ([File: features/application/src/modules/passphrase-cache.ts])

### Summary
`Application.unlock()` writes the passphrase into `PassphraseCache` via an un-awaited `void this.#passphraseCache.set(opts.passphrase)` call, while `Application.lock()` `await`s `this.#passphraseCache.clear()`. Because these two async storage operations are not sequenced against each other, a rapid unlock→lock cycle (fully reachable through the normal, ordinary `application.unlock`/`application.lock` API surface) can let the deferred `set()` complete after `clear()`, leaving the passphrase cached after an explicit lock that is supposed to erase it.

### Finding Description
`PassphraseCache.set()` and `PassphraseCache.clear()` both perform independent async storage writes with no locking/ordering guarantee: [1](#0-0) [2](#0-1) 

`Application.unlock()` deliberately fires `passphraseCache.set()` without awaiting it (`void this.#passphraseCache.set(opts.passphrase)`), presumably to avoid blocking the unlock response on the cache write: [3](#0-2) 

`Application.lock()`, however, `await`s `passphraseCache.clear()` synchronously as part of the lock sequence: [4](#0-3) 

Exploit flow: the ordinary application lifecycle (an app/extension UI or any code path that can invoke `exodus.application.unlock({ passphrase })` immediately followed by `exodus.application.lock()`, e.g. quick unlock-then-relock, or a lock triggered by an auto-lock timer/backgrounding event racing with a just-completed unlock) can create the following ordering:

1. `unlock({ passphrase })` resolves (all its `await`ed steps — `wallet.unlock`, `lockedAtom.set(false)`, hook firing — complete), but the un-awaited `passphraseCache.set(passphrase)` promise is still pending on the storage backend.
2. `lock()` is invoked immediately after, and its `await this.#passphraseCache.clear()` runs `storage.clear()` on the same underlying session storage.
3. If the underlying storage adapter interleaves these two pending write operations such that the deferred `set()` batchSet completes after `clear()`'s clear() (e.g., different storage keys resolved out of order, or a slower `batchSet` overtaking a faster `clear`), the passphrase persists in the cache storage even though `lock()` has already reported success and set `lockedAtom` to `true`.
4. On the next application `start()`, `#autoUnlock()` reads `passphraseCache.get()` and, finding a (stale) valid passphrase, silently calls `wallet.unlock({ passphrase })` and fires `Hook.Unlock`, bypassing the re-authentication that the explicit `lock()` was meant to require: [5](#0-4) 

This violates the invariant that fallback/background unlock (`#autoUnlock`, the passphrase-cache-based path) must not weaken the guarantee established by an explicit `lock()` call — namely that after locking, wallet access requires full re-authentication. Existing code has no protective check preventing this: `clear()` and `set()` do not synchronize, there is no generation/version counter to invalidate an in-flight `set()` once `clear()` runs, and `#autoUnlock` trusts any non-expired cache entry unconditionally.

Additionally, `PassphraseCache.set()` never resets `INACTIVE_AT_KEY`, so a stale `inactiveAt` value from a prior caching cycle can persist into a newly-set entry and affect TTL evaluation in `get()`, though this by itself is a correctness/availability issue rather than a direct compromise. The primary, concretely exploitable issue is the `set()`/`clear()` race described above.

### Impact Explanation
If the stale passphrase in the cache survives an explicit lock, whoever next triggers `application.start()` (a routine lifecycle event — extension service-worker restart, background page reload, app relaunch) obtains a silently unlocked wallet without providing the passphrase/PIN/biometric factor. This is a private-key-generation-adjacent unlock bypass: the seed becomes decryptable and usable for signing (`wallet.unlock` re-adds the seed into the keychain) without the authentication step the user/lock explicitly required, matching "Private key or private key generation leakage leading to unauthorized access to user funds" in cases where a device/session is later accessed by someone other than the user who performed the lock (e.g., shared/borrowed device, physical access, or another local surface that can invoke `application.start()`/`load()`).

### Likelihood Explanation
This requires no privileged state or leaked keys — only the ability to trigger the two ordinary, unauthenticated-by-account-scope lifecycle calls (`unlock` immediately followed by `lock`) back-to-back, which is part of normal app/extension operation (e.g., an auto-lock timer firing right after an unlock, or a user/script issuing unlock then immediately re-locking). The race window depends on the concrete storage adapter's scheduling of the pending `batchSet` versus `clear` operations, so it is not guaranteed on every call, but it is repeatable under load/timing pressure and is a structural flaw (no synchronization primitive at all) rather than a one-off timing fluke — repeated attempts driven by scripted rapid unlock/lock cycles will trigger it probabilistically.

### Recommendation
- Make `Application.unlock()` `await` `this.#passphraseCache.set(...)` instead of firing it with `void`, so the cache write is guaranteed to complete before `unlock()` resolves and before any subsequent `lock()` call can be issued by the caller.
- In `PassphraseCache`, serialize `set()`/`clear()`/`changeTtl()`/`scheduleClear()` calls (e.g., via an internal promise chain/mutex) so overlapping calls cannot interleave their underlying storage writes.
- Add a monotonically increasing generation/version token to cached entries; `clear()` should bump the generation and any in-flight `set()` from a prior generation should no-op instead of writing.
- Reset `INACTIVE_AT_KEY` in `set()` to avoid stale TTL bookkeeping across cache cycles.

### Proof of Concept
Integration test plan (extending existing test style in `sdks/headless/__tests__/application/port-events.test.js`):
1. Create a wallet with a passphrase and start the application.
2. Call `exodus.application.unlock({ passphrase })` but do not await the internal cache write — instead, immediately call `exodus.application.lock()` right after `unlock()`'s promise resolves (simulate by racing: use a storage adapter test double whose `batchSet` for the passphrase cache resolves on a delayed microtask/timer relative to `clear`'s resolution, or by monkey-patching `PassphraseCache.set` to add an artificial delay in a test harness).
3. Assert that after `lock()` resolves, `passphraseCache.get()` still returns the passphrase (demonstrating the clear did not take effect against the delayed `set`).
4. Restart the application (`exodus.application.stop()` + re-create container + `exodus.application.start()`), and assert that `wallet.isLocked()` becomes `false` automatically via `#autoUnlock`, i.e., the wallet unlocks without any passphrase being supplied — confirming the explicit lock was bypassed.

Expected (fixed) behavior: after awaiting the cache `set()` inside `unlock()` (or serializing cache operations), `passphraseCache.get()` after `lock()` must always return `undefined`/empty regardless of call timing, and the restarted application must remain locked until a fresh `unlock` with the correct passphrase is supplied.

### Citations

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
