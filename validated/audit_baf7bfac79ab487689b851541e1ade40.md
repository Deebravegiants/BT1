### Title
Fire-and-forget passphrase re-caching in `unlock()` races with `lock()`/`clear()`, allowing a locked wallet to auto-unlock on restart - (File: `features/application/src/modules/passphrase-cache.ts`)

### Summary
`PassphraseCache.set()` is invoked from `Application.unlock()` without being awaited (`void this.#passphraseCache.set(opts.passphrase)`), while `Application.lock()` awaits `this.#passphraseCache.clear()` synchronously. If `lock()` is called immediately after `unlock()` resolves, the un-awaited `set()` write can land in storage *after* `clear()` has already run, leaving the passphrase cached even though the app believes the wallet is locked. On the next `start()`, `#autoUnlock()` will read that stale cached passphrase and silently unlock the wallet again, bypassing the intended lock boundary.

### Finding Description
`Application.unlock()` performs: [1](#0-0) 
Note that `void this.#passphraseCache.set(opts.passphrase)` is fired without `await`, so `unlock()` can return/resolve before the passphrase write (`#getTtl()` await + `storage.batchSet(...)`) actually completes.

`Application.lock()`, on the other hand, fully awaits the clear operation: [2](#0-1) 

If a caller invokes `unlock({ passphrase })` followed immediately by `lock()` (a legitimate reachable sequence: unlock then relock during normal app lifecycle, or an automated/attacker-timed sequence of API calls), the two chains of microtasks race:
- `unlock()`'s tail operation is `void passphraseCache.set(...)`, which itself awaits `#getTtl()` (an atom read) before calling `storage.batchSet(...)`.
- `lock()`'s `passphraseCache.clear()` calls `storage.clear()` directly, with fewer intermediate hops.

Because `set()` has an extra `await this.#getTtl()` before writing, and is never awaited by its caller, it is entirely possible for `storage.clear()` (from `lock()`) to complete before `storage.batchSet()` (from the pending `set()`) writes the `passphrase`/`addedAt`/`ttl` keys back into storage. The net result: after `lock()` returns, the passphrase cache is **not empty** - it still contains the freshly re-written passphrase, `addedAt`, and `ttl` values, because they were written after the clear.

On the next application `start()`, `#autoUnlock()` reads the cache: [3](#0-2) 
`PassphraseCache.get()` will find a valid (non-expired) passphrase and return it, causing `#autoUnlock()` to call `this.#wallet.unlock({ passphrase })` and fire `Hook.Unlock` — silently bypassing the "lock" the user believed they had performed, with no user-entered passphrase and no explicit approval step.

`PassphraseCache.clear()` itself performs a correct full storage clear: [4](#0-3) 
but the invariant "lock must fully reset secrets before reuse" is violated at the call-site level in `application.ts` because the `set()` write from a preceding `unlock()` is not sequenced (awaited) relative to a subsequent `lock()`'s `clear()`.

### Impact Explanation
If exploited, a wallet that the application/user believes is locked (`lockedAtom === true`, `wallet.isLocked() === true`) can still have the plaintext passphrase resident in the passphrase-cache storage. On process/app restart, `#autoUnlock()` will use that leftover passphrase to automatically unlock the wallet and derive/access the seed via `wallet.unlock({ passphrase })`, without the legitimate passphrase-entry gate. This maps to "Private key or private key generation leakage leading to unauthorized access to user funds," since the wallet seed becomes accessible without the expected authentication step that `lock()` was supposed to enforce.

### Likelihood Explanation
This requires only ordinary, unprivileged control over the application lifecycle API (`unlock()` immediately followed by `lock()`), which is exactly the kind of timing an attacker with local script/automation access to the headless/exodus instance (e.g., malicious extension code, compromised UI automation, or a race triggered by rapid user/programmatic interaction) can produce deterministically by calling both methods back-to-back without awaiting completion between them. The race outcome depends on the relative timing of the underlying storage adapter's `batchSet` vs `clear` calls (which, per `adapters/storage-memory/src/index.js`, are both async and not mutually exclusised), so it is feasible though timing-adapter-dependent — in slower or namespaced storage adapters (e.g., encrypted/session storage) the extra hop in `set()` (`await this.#getTtl()`) makes the race window more likely to manifest.

### Recommendation
Await `this.#passphraseCache.set(opts.passphrase)` in `Application.unlock()` instead of firing it with `void`, or otherwise serialize all passphrase-cache mutations (e.g., via `make-concurrent` per key, or a single sequenced queue) so `clear()` calls performed by `lock()`/`start()` cannot be overtaken by a stale, in-flight `set()` from a prior `unlock()`. Additionally, consider having `lock()` clear the cache **after** confirming no other cache write is pending, or have `PassphraseCache` internally track/cancel in-flight `set()` operations when `clear()` is invoked.

### Proof of Concept
Unit/integration test plan (extends existing test patterns in `sdks/headless/__tests__/wallet.test.js`):
1. Create a fake/instrumented `storage` adapter (or wrap the real `storage-memory` adapter) where `batchSet` is deliberately delayed (e.g., via a controllable promise) to simulate a slow write relative to `clear`.
2. `await exodus.application.create({ passphrase })`.
3. Call `exodus.application.unlock({ passphrase })` and, without awaiting the internal fire-and-forget `set()` to flush, immediately call `exodus.application.lock()`.
4. Delay the artificial `batchSet` resolution until after `clear()` has completed, simulating the race.
5. Assert that after `lock()` resolves, `passphraseCache.get()` unexpectedly returns the passphrase (i.e., storage still contains `passphrase`/`addedAt`/`ttl` keys) even though `wallet.isLocked()` is `true`.
6. Simulate a restart: create a new `exodus` instance sharing the same storage/adapters and call `application.start()`.
7. Assert that `#autoUnlock()` unlocks the wallet automatically (`wallet.isLocked()` becomes `false` and `Hook.Unlock`/`unlock` event fires) without any passphrase being supplied by the test — demonstrating the lock bypass.

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

**File:** features/application/src/modules/passphrase-cache.ts (L111-114)
```typescript
  async clear() {
    this.#logger.log('clearing cache')
    await this.#storage.clear()
  }
```
