### Title
Passphrase-cache expiry decay bypassed by repeated activity refresh, allowing cached plaintext secret to outlive its configured max TTL - (File: features/application/src/modules/passphrase-cache.ts)

### Summary
`PassphraseCache` caches the user's plaintext wallet passphrase in storage to support auto-unlock, and is meant to decay/expire under two independent bounds: an absolute `maxTtl` from the moment it was cached, and a rolling inactivity `ttl` refreshed on user activity. Just like the veRAACToken `increase()` bug (which recomputed voting power from the *original* locked amount instead of the currently decayed value, letting a user keep "renewing" power without ever paying for decay), `PassphraseCache.get()`/`scheduleClear()` stop referencing the original decay anchor (`addedAt` + `maxTtl`) once any inactivity refresh has occurred, and instead perpetually renew validity from `inactiveAt + ttl`, indefinitely bypassing the intended absolute expiry.

### Finding Description
`PassphraseCache.get()` decides whether the cached passphrase is still valid using two different branches: [1](#0-0) 

- If `inactiveAt` has never been set, validity is bounded by the absolute decay: `addedAt + this.#maxTtl > Date.now()`.
- However, once `inactiveAt` is set even once (via `scheduleClear()`, reachable through `Application.restartAutoLockTimer` / `changeLockTimer`), the check permanently switches to `inactiveAt + ttl > Date.now()` and the original `addedAt`/`maxTtl` decay bound is never consulted again: [2](#0-1) [3](#0-2) 

Because `scheduleClear()` (and `restartAutoLockTimer`) can be invoked by the unprivileged user/UI repeatedly (e.g., on every interaction, exactly analogous to calling `increase()` repeatedly on a decaying lock), each call resets `inactiveAt = Date.now()` and reschedules the alarm for another `ttl` window — with no reference back to the amount of time that has actually elapsed since the passphrase was first cached. This mirrors the root cause of the reported ve-token bug: a value that is supposed to monotonically decay from a fixed anchor point is instead recalculated from a moving/refreshed reference, letting the "boost" (here, continued caching of the plaintext secret) persist far beyond what the system's own decay parameter (`maxTtl`, set via `application/src/modules/passphrase-cache.ts:33` from `config.maxTtl`) is designed to allow. [4](#0-3) 

### Impact Explanation
`maxTtl` is the hard security ceiling intended to force the plaintext passphrase to be purged from storage after a fixed absolute duration, regardless of activity, limiting the exposure window of the wallet's decryption secret. The decay-bypass described above means as long as a normal (unprivileged) user or any code path that calls `restartAutoLockTimer`/`changeLockTimer` triggers periodically, the plaintext passphrase can remain cached in storage indefinitely — well beyond the configured `maxTtl`. This directly enlarges the window during which an attacker with local/device access (the standard threat model for wallet auto-unlock caches) can recover the plaintext seed passphrase from storage, defeating the auto-lock/expiry security control and leading to unauthorized wallet unlock/asset compromise if the device is later accessed.

### Likelihood Explanation
This requires only unprivileged, ordinary application usage (any flow invoking `changeLockTimer`/`restartAutoLockTimer`, which are part of the public `ApplicationApi`), no privileged keys or attacker-controlled input beyond normal interaction cadence, matching the "malicious/careless normal user or automated UI activity" attacker profile. It does not require a malicious operator/peer, and is reachable purely through documented public API surface: [5](#0-4) 

### Recommendation
`scheduleClear()`/`get()` should always bound validity by the original `addedAt + maxTtl` decay anchor in addition to the rolling `inactiveAt + ttl` window, i.e. cap `inactiveAt`-based renewal so it can never extend the cached passphrase past `addedAt + maxTtl`, analogous to fixing `increase()` by computing from the currently-decayed value instead of the stale original amount.

### Proof of Concept
1. Cache a passphrase: `PassphraseCache.set(passphrase)` sets `addedAt = now`.
2. Before `maxTtl` elapses, repeatedly call `restartAutoLockTimer()` (→ `scheduleClear()`), which sets `inactiveAt = now` each time and reschedules the clear alarm for another `ttl`.
3. Because every subsequent `get()` check now uses `inactiveAt + ttl > now` instead of `addedAt + maxTtl > now`, continuing to call `restartAutoLockTimer()` before each `ttl` window expires keeps the passphrase valid forever, exceeding the configured `maxTtl` bound with no upper limit enforced.

### Citations

**File:** features/application/src/modules/passphrase-cache.ts (L21-34)
```typescript
export class PassphraseCache {
  #alarms
  #storage
  #autoLockTimerAtom
  #logger
  #maxTtl

  constructor({ storage, alarms, autoLockTimerAtom, logger, config }: PassphraseCacheParams) {
    this.#storage = storage
    this.#alarms = alarms
    this.#autoLockTimerAtom = autoLockTimerAtom
    this.#logger = logger
    this.#maxTtl = (config.maxTtl || 60) * ms('1m')
  }
```

**File:** features/application/src/modules/passphrase-cache.ts (L40-48)
```typescript
  #scheduleClear = async () => {
    const ttl = await this.#getTtl()

    this.#logger.log('rescheduling cache clear', ttl / ms('1m'))
    await this.#alarms.clear('clear-passphrase')
    await this.#alarms.create('clear-passphrase', {
      delayInMinutes: ttl / ms('1m'),
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

**File:** features/application/src/api/index.ts (L145-169)
```typescript
    changePassphrase: Application['changePassphrase']

    /**
     * Changes the auto lock timer TTL (time to live).
     * @remarks
     * This is used as part of the auto unlock functionality, the wallet will be considered locked after the timer expires.
     * @param opts - An object containing the `ttl` in milliseconds.
     * @example
     * ```typescript
     * await exodus.application.changeLockTimer({ lockTimer: 1000 })
     * ```
     */
    changeLockTimer: Application['changeLockTimer']

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
