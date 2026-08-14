Found a legitimate analog in the wallet's passphrase auto-unlock cache mechanism. The bug class here (a stored maturity/expiry boundary that never gets truly enforced because a "renewal" timestamp is repeatedly reset without ever being checked against the original absolute cap) maps directly onto `PassphraseCache` in `features/application/src/modules/passphrase-cache.ts`.

### Title
Passphrase Cache `maxTtl` Cap Bypassed via Repeated `inactiveAt` Refresh, Enabling Indefinite Auto-Unlock - (File: features/application/src/modules/passphrase-cache.ts)

### Summary
`PassphraseCache` is designed to cache the wallet's unlock passphrase for at most `maxTtl` from the moment it was set (`addedAt`), and to auto-unlock the wallet with it while it remains valid. However, every time `scheduleClear()`/`restartAutoLockTimer()` runs (triggered on app backgrounding or via the public `restartAutoLockTimer` API), the code resets `INACTIVE_AT_KEY` to `Date.now()` and thereafter validates the cache purely against `inactiveAt + ttl`, never re-checking it against the original `addedAt + maxTtl` boundary. As a result, the intended absolute expiry (`maxTtl`) can be perpetually postponed, letting the cached passphrase (and thus wallet auto-unlock) remain valid indefinitely — the same root cause class as the reported bug: a maturity/expiry timestamp that is supposed to bound a privileged benefit is never actually enforced against the current time in the code path that grants that benefit.

### Finding Description
`PassphraseCache.get()` decides whether the cached passphrase can still be used to auto-unlock the wallet: [1](#0-0) 

- If `inactiveAt` is set, validity is judged solely by `inactiveAt + ttl > Date.now()`.
- Only if `inactiveAt` is *not* set does it fall back to the absolute cap `addedAt + this.#maxTtl > Date.now()`.

`scheduleClear()` is the only place that sets `inactiveAt`, and it does so unconditionally to `Date.now()` every time it's called, with no comparison to `addedAt`/`maxTtl`: [2](#0-1) 

`scheduleClear()` is invoked from two flows that don't require re-authentication:
- `Application.unload()`, run whenever the app is unloaded/backgrounded: [3](#0-2) 
- `Application.restartAutoLockTimer()`, exposed directly on the public SDK API surface (`exodus.application.restartAutoLockTimer()`): [4](#0-3) [5](#0-4) 

Because `scheduleClear` keeps rewriting `inactiveAt` to "now" (rather than being bounded by `addedAt + maxTtl`), each refresh restarts a fresh `ttl` window measured from an ever-advancing `inactiveAt`. This means the code never re-derives validity from the original `addedAt` once `inactiveAt` exists, so the operator-configured `maxTtl` (`passphraseCacheMaxTtl`, wired in `features/application/src/index.ts:21-27,50-55`) stops being an actual hard cap — it only limits the *first* idle window, not the lifetime of the cache.

`#autoUnlock()` then directly consumes whatever `PassphraseCache.get()` returns to unlock the wallet without any additional maturity check: [6](#0-5) 

This is structurally identical to the reported bug: a benefit (here, continued wallet auto-unlock capability from a cached secret) is supposed to be time-boxed by an absolute deadline (`maxTtl`, analogous to option maturity), but the code path that grants the benefit checks a renewable, resettable timestamp (`inactiveAt`, analogous to `optionsRenewedTimeStamp`) instead of validating against the original deadline.

### Impact Explanation
Any process capable of triggering routine app-lifecycle events (backgrounding/foregrounding the wallet app, or calling the public `restartAutoLockTimer` API) can keep the cached passphrase perpetually "fresh" from the perspective of `get()`, defeating the operator's configured `passphraseCacheMaxTtl` security control. On a device that is left logged in and periodically backgrounded (a very ordinary usage pattern, not requiring any special privilege), the wallet will continue auto-unlocking with the original passphrase far beyond the intended maximum caching window, undermining the security guarantee that the cached secret expires and forces re-authentication after `maxTtl`. This weakens the auth boundary intended to limit exposure of an unlocked/auto-unlockable wallet.

### Likelihood Explanation
High likelihood of occurring passively: the vulnerable refresh path (`unload()` → `scheduleClear()`) fires on normal app backgrounding, which happens routinely during regular use, and `restartAutoLockTimer` is directly callable through the public SDK/API without any authorization check beyond having API access. No cryptographic break or privileged access is required — only ordinary interaction with the app lifecycle.

### Recommendation
In `PassphraseCache.get()` and `scheduleClear()`, always validate against the absolute deadline derived from `addedAt + maxTtl` in addition to the `inactiveAt + ttl` idle check — i.e., cap `inactiveAt`'s effective validity so it can never extend the cache past `addedAt + maxTtl`. Concretely, `get()` should require `Date.now() < Math.min(inactiveAt + ttl, addedAt + maxTtl)` rather than treating the `inactiveAt` branch as an independent, unbounded extension of validity.

### Proof of Concept
1. Unlock the wallet with `passphrase`, causing `PassphraseCache.set()` to record `addedAt = T0` and cache the passphrase, with `maxTtl` configured (e.g., 60 minutes) via `passphraseCacheMaxTtl`. [7](#0-6) 
2. Every ~50 minutes (before `maxTtl` elapses), background the app (or call `exodus.application.restartAutoLockTimer()`), causing `scheduleClear()` to reset `inactiveAt = Date.now()`. [2](#0-1) 
3. Repeat this cycle indefinitely (well past the original `maxTtl` window from `T0`).
4. On each app restart/load, `Application.#autoUnlock()` calls `PassphraseCache.get()`, which — because `inactiveAt` was just refreshed — passes the `inactiveAt + ttl > Date.now()` check and returns the passphrase, auto-unlocking the wallet indefinitely, well beyond the operator-configured `maxTtl` from the original `addedAt`. [6](#0-5)

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

**File:** features/application/src/modules/passphrase-cache.ts (L61-85)
```typescript
  async get() {
    const [passphrase, addedAt, inactiveAt, ttl] = (await this.#storage.batchGet([
      PASSPHRASE_KEY,
      ADDED_AT_KEY,
      INACTIVE_AT_KEY,
      TTL_KEY,
    ])) as [string, number, number, number]

    if (passphrase) {
      if (inactiveAt) {
        if (inactiveAt + ttl > Date.now()) {
          this.#logger.log('fetched cached passphrase, in activity period')
          return passphrase
        }
      } else if (addedAt + this.#maxTtl > Date.now()) {
        this.#logger.log('fetched cached passphrase')
        return passphrase
      }

      this.#logger.log('fetched expired passphrase, clearing and preventing unlock')
      void this.clear()
    }

    this.#logger.log('passphrase not in cache')
  }
```

**File:** features/application/src/modules/passphrase-cache.ts (L101-109)
```typescript
  async scheduleClear() {
    const passphrase = await this.#storage.get(PASSPHRASE_KEY)

    if (passphrase) {
      await this.#storage.set(INACTIVE_AT_KEY, Date.now())

      void this.#scheduleClear()
    }
  }
```

**File:** features/application/src/modules/application.ts (L193-197)
```typescript
  unload = async () => {
    await this.#applicationStarted
    await this.#passphraseCache.scheduleClear()
    await this.fire(Hook.Unload)
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

**File:** features/application/src/modules/application.ts (L455-457)
```typescript
  restartAutoLockTimer = async () => {
    await this.#passphraseCache.scheduleClear()
  }
```

**File:** features/application/src/api/index.ts (L159-169)
```typescript
    /**
     * Changess the auto lock timer.
     * @remarks
     * This is used as part of the auto unlock functionality, the wallet will be considered locked after the timer expires.
     * @param opts - An object containing the `ttl` in milliseconds.
     * @example
     * ```typescript
     * await exodus.application.restartAutoLockTimer()
     * ```
     */
    restartAutoLockTimer: Application['restartAutoLockTimer']
```
