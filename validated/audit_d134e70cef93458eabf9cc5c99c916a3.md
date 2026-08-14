### Title
Passphrase cache validity check uses static `maxTtl` instead of user-configured lock timer, extending auto-unlock window beyond intended duration - ([File: features/application/src/modules/passphrase-cache.ts])

### Summary
`PassphraseCache.get()` in `features/application/src/modules/passphrase-cache.ts` determines whether a cached passphrase is still valid using two different, inconsistent time bases depending on whether `inactiveAt` has been recorded. When `inactiveAt` is unset, it falls back to `addedAt + this.#maxTtl > Date.now()` — using the fixed configuration constant `#maxTtl` (default 60 minutes) — rather than the dynamically user-configured `ttl` value that is stored per-session and exposed via `changeLockTimer`/`autoLockTimerAtom`. This mirrors the pattern in the referenced Sherlock report where a lock/expiry calculation used the wrong time reference, causing the effective lock/expiry duration to diverge from (and exceed) what the user configured.

### Finding Description
`PassphraseCache.set()` stores `addedAt = Date.now()` and the current `ttl` (from `autoLockTimerAtom`) when a passphrase is cached: [1](#0-0) 

`get()` then validates the cache with two branches: [2](#0-1) 

The `inactiveAt` branch correctly uses the per-session `ttl` value. However the `addedAt` branch (taken whenever the public `scheduleClear()` — which is the only method that sets `INACTIVE_AT_KEY` — has not yet been called since the passphrase was cached) uses `this.#maxTtl` instead of the stored `ttl`. `#maxTtl` is a fixed config constant set at construction time, unrelated to what the user configured via `changeLockTimer`: [3](#0-2) 

`changeTtl()` (invoked by `Application.changeLockTimer`) updates `TTL_KEY` and reschedules the alarm, but it does not touch `ADDED_AT_KEY`/`INACTIVE_AT_KEY`, and it never causes `get()`'s `addedAt` branch to actually use the new `ttl`: [4](#0-3)  and [5](#0-4) .

The passphrase cache is what powers `Application.#autoUnlock()`, which fetches the cached passphrase and unlocks the wallet automatically if the wallet was left locked: [6](#0-5) .

Because the `addedAt`-branch check ignores the user's configured `ttl` and instead honors the larger, fixed `#maxTtl`, a user who explicitly shortens the auto-lock/session timer (e.g., to 1 minute) still has their cached passphrase considered valid for up to `#maxTtl` (default 60 minutes) as long as `scheduleClear()` (which sets `INACTIVE_AT_KEY`) hasn't run in that window. This directly parallels the reported bug class: the enforced expiry window silently extends beyond what the user intended/configured, because the wrong time reference is used in the validity calculation.

### Impact Explanation
The impact is a secret (cached wallet passphrase) remaining usable for automatic unlock for a duration exceeding what the user explicitly configured as their security/auto-lock policy. If `restartAutoLockTimer`/`scheduleClear()` is not triggered promptly on activity/backgrounding (e.g., app killed, backgrounded without triggering the relevant hook, or timing gaps between events), `#autoUnlock()` can silently unlock the wallet using the still-cached passphrase up to `maxTtl` after caching, even though the user set a much shorter auto-lock timer. This is a auth/session-boundary violation: someone with access to the device/session within that unintended extended window gets automatic access to the unlocked wallet, contrary to the user's configured expectations — a direct analog of the "lock duration extended beyond intended period" bug class, but here manifesting as reduced protection rather than mere inconvenience.

### Likelihood Explanation
This triggers under a realistic, common condition: any time the cached passphrase's `inactiveAt` has not yet been set (i.e., since it's set only by the public `scheduleClear()`, which is invoked from `unload`/`restartAutoLockTimer`, not from `set()`/`unlock()`) and the user has configured a `ttl` shorter than `#maxTtl`. This is the default state immediately after every unlock/passphrase caching event until an idle/unload/lock-timer-restart hook fires. It doesn't require attacker action beyond having transient device/session access within the extended window; likelihood is moderate-to-high depending on how frequently `restartAutoLockTimer`/`unload` fire relative to unlocks in the actual app integrations.

### Recommendation
In `PassphraseCache.get()`, use the currently stored `ttl` consistently in both branches instead of `#maxTtl` for the `addedAt` check, e.g. `addedAt + ttl > Date.now()`, reserving `#maxTtl` purely as an upper clamp applied when *setting* the ttl (as already done in `changeTtl`). Additionally, ensure `set()`/`unlock()` initializes an `inactiveAt`/schedules the clear alarm immediately (rather than leaving a window where only the `addedAt` branch governs validity), so the effective auto-unlock window is always driven by the user-configured lock timer, not a stale fixed default.

### Proof of Concept
1. Set auto-lock timer to a short duration, e.g. `application.changeLockTimer({ ttl: ms('1m') })` (`#maxTtl` default remains 60 minutes) — see [4](#0-3) .
2. Unlock the wallet with a passphrase: `application.unlock({ passphrase })`, which calls `passphraseCache.set(passphrase)`, storing `addedAt = now`, `ttl = 1m` [7](#0-6) .
3. Do not trigger `restartAutoLockTimer()`/`unload()` (so `INACTIVE_AT_KEY` is never set) — plausible if the app is killed or the relevant lifecycle hook doesn't fire before the process restarts.
4. Lock the app/device, wait more than 1 minute but less than 60 minutes, then restart the application process, triggering `Application.start()` → `#autoUnlock()` → `passphraseCache.get()` [8](#0-7) .
5. In `get()`, since `inactiveAt` is falsy, the check `addedAt + this.#maxTtl > Date.now()` (60 minutes) succeeds despite the user's configured 1-minute lock timer having long expired, returning the cached passphrase and auto-unlocking the wallet [9](#0-8) .

### Citations

**File:** features/application/src/modules/passphrase-cache.ts (L28-34)
```typescript
  constructor({ storage, alarms, autoLockTimerAtom, logger, config }: PassphraseCacheParams) {
    this.#storage = storage
    this.#alarms = alarms
    this.#autoLockTimerAtom = autoLockTimerAtom
    this.#logger = logger
    this.#maxTtl = (config.maxTtl || 60) * ms('1m')
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

**File:** features/application/src/modules/passphrase-cache.ts (L87-99)
```typescript
  async changeTtl(ttl: number) {
    const newTtl = Math.min(this.#maxTtl, ttl)

    await this.#autoLockTimerAtom.set(newTtl)

    const passphrase = await this.#storage.get(PASSPHRASE_KEY)

    if (passphrase) {
      await this.#storage.set(TTL_KEY, newTtl)

      void this.#scheduleClear()
    }
  }
```

**File:** features/application/src/modules/application.ts (L165-165)
```typescript
    await this.#autoUnlock()
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

**File:** features/application/src/modules/application.ts (L451-453)
```typescript
  changeLockTimer = async ({ ttl }: { ttl: number }) => {
    return this.#passphraseCache.changeTtl(ttl)
  }
```
