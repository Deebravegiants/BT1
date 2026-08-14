### Title
Passphrase cache activity-window check ignores the user-configured auto-lock TTL, disclosing the cached passphrase for up to `maxTtl` after a shorter TTL is set - (File: features/application/src/modules/passphrase-cache.ts)

### Summary
`PassphraseCache.changeTtl()` updates the stored `ttl` value used to *reschedule* the alarm-based clear, but it never resets `ADDED_AT_KEY`, and `PassphraseCache.get()`'s "still active" branch validates the cache against the fixed `#maxTtl` config value instead of the currently configured `ttl`. This is the same bug class as the Flayer `modifyListings()` issue: a partial update (changing only one field of a time-bound resource) leaves the anchor timestamp/duration pairing inconsistent, so a security-relevant time window is computed incorrectly.

### Finding Description
`PassphraseCache.set()` stores `addedAt = Date.now()` and `ttl` together [1](#0-0) .

`PassphraseCache.get()` decides whether the cached passphrase (used for silent auto-unlock) is still valid using two different anchors depending on whether the cache has gone "inactive" yet:
- if `inactiveAt` is set, it checks `inactiveAt + ttl > Date.now()` (correctly uses the configured `ttl`),
- otherwise it checks `addedAt + this.#maxTtl > Date.now()` — using the hard-coded `#maxTtl` config ceiling, not the actual `ttl` the user configured [2](#0-1) .

`changeTtl()` is the only place a user can shorten their auto-lock window (via `Application.changeLockTimer`) [3](#0-2) . It writes the new `ttl` to storage and reschedules the alarm via the private `#scheduleClear()`, but it never touches `ADDED_AT_KEY`/`INACTIVE_AT_KEY` [4](#0-3) . `INACTIVE_AT_KEY` is only ever set by the *public* `scheduleClear()` method, which is a distinct code path invoked from `Application.restartAutoLockTimer` [5](#0-4) [6](#0-5) .

Consequence: exactly like the Flayer report where `listing.created` is only refreshed on the `duration` branch and not on a `floorMultiple`-only change (so the later full-duration tax calculation uses a stale/incorrect anchor), here `addedAt` is never refreshed when only `ttl` changes, and the validity check silently falls back to comparing against `#maxTtl` instead of the newly-set `ttl` until some other event (backgrounding) triggers `scheduleClear()`. A user who tightens their auto-lock TTL for security (e.g., from the default 60 minutes down to 1 minute) gets no actual reduction in the passphrase cache's exposure window as long as the session is still "active" (never went inactive) — the passphrase remains retrievable by `get()` for up to `#maxTtl` (default 60 minutes) from when it was cached, regardless of the shorter TTL the user just set.

### Impact Explanation
`get()` returning the cached passphrase feeds directly into `Application.#autoUnlock()`, which calls `wallet.unlock({ passphrase })` [7](#0-6) . Anyone with access to the storage/process during that unintended extended window (e.g. a second user of a shared device, or any code path able to trigger auto-unlock) can silently unlock the wallet even though the user explicitly reduced the auto-lock timer to prevent exactly that. This is a direct secret-disclosure / wallet-unlock-bypass impact, not merely a UX inconsistency, since the passphrase itself (the wallet's master secret) is disclosed to the auto-unlock flow past the user-intended TTL.

### Likelihood Explanation
This triggers on the ordinary user action of calling `changeLockTimer`/`changeTtl` to shorten the auto-lock timer while the app remains "active" (i.e., before any background/inactivity event calls `scheduleClear()` to set `INACTIVE_AT_KEY`). This is a common and expected user flow (tightening security settings without necessarily backgrounding the app immediately afterward), making the bug easily reachable without any special privileges — an "unprivileged user" who merely changes their own settings ends up with a weaker security window than what they configured.

### Recommendation
In `changeTtl()`, when a passphrase is cached, reset `ADDED_AT_KEY` to `Date.now()` (mirroring `set()`), or alternatively make the "still active" branch in `get()` compare `addedAt + ttl` (the actual configured TTL) rather than `addedAt + this.#maxTtl`, so a reduced TTL takes effect immediately rather than only after `INACTIVE_AT_KEY` is separately established.

### Proof of Concept
1. Config `maxTtl` = 60 minutes (default).
2. User creates/unlocks wallet with a passphrase → `PassphraseCache.set()` stores `addedAt = t0`, `ttl = 60m`.
3. User calls `application.changeLockTimer({ ttl: 1m })` to tighten security → `changeTtl` sets `TTL_KEY = 1m` in storage, but `ADDED_AT_KEY` stays `t0`, and `INACTIVE_AT_KEY` is still unset (assuming the app has not gone to background yet).
4. At `t0 + 5 minutes` (5x past the newly configured 1-minute TTL, but well within the original 60-minute `maxTtl`), some flow calls `PassphraseCache.get()` (e.g. auto-unlock on relaunch). Since `inactiveAt` is falsy, the code evaluates `addedAt + maxTtl > Date.now()` → `t0 + 60m > t0 + 5m` → true, so the passphrase is returned and auto-unlock proceeds — despite the user having configured a 1-minute auto-lock timer. [8](#0-7)

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

**File:** features/application/src/modules/passphrase-cache.ts (L61-99)
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

**File:** features/application/src/modules/application.ts (L451-453)
```typescript
  changeLockTimer = async ({ ttl }: { ttl: number }) => {
    return this.#passphraseCache.changeTtl(ttl)
  }
```

**File:** features/application/src/modules/application.ts (L455-457)
```typescript
  restartAutoLockTimer = async () => {
    await this.#passphraseCache.scheduleClear()
  }
```
