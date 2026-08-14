### Title
Passphrase cache `maxTtl` hard cap can be bypassed indefinitely via `scheduleClear()`/`restartAutoLockTimer()` — analogous to unbounded renewal - ([File: features/application/src/modules/passphrase-cache.ts])

### Summary
The Sherlock report describes a renewal bug where a "grace period" check validates against the *previous* expiration, but the actual protection is (re)started from `block.timestamp`, letting a user repeatedly "renew" and get unbounded free coverage. The same renewal-without-bound pattern exists in `PassphraseCache`: the `#maxTtl` configuration is meant to be a hard cap on how long the raw wallet passphrase may remain cached in (session) storage, but once the "activity" branch (`inactiveAt`) is engaged, subsequent renewals via `scheduleClear()` reset the clock from `Date.now()` with no reference back to the original `addedAt` value or `#maxTtl` bound.

### Finding Description
`PassphraseCache.get()` validates cache freshness in two branches: [1](#0-0) 

- If `inactiveAt` is set, it only checks `inactiveAt + ttl > Date.now()` — i.e., "the plaintext passphrase cache is valid for `ttl` after last locking/idle event", with **no comparison to `addedAt + #maxTtl`**.
- If `inactiveAt` is not set, it falls back to `addedAt + #maxTtl > Date.now()`, which is the intended hard cap.

`scheduleClear()` sets `inactiveAt = Date.now()` every time it's called: [2](#0-1) 

`scheduleClear()` is reachable from the public `Application.restartAutoLockTimer()` API method: [3](#0-2) 

which is exposed on the public headless application API surface (`exodus.application.restartAutoLockTimer()`), documented for UI consumers as part of the auto-unlock/auto-lock functionality: [4](#0-3) 

Because entering the `inactiveAt` branch removes the `#maxTtl` bound entirely, any caller that repeatedly invokes `restartAutoLockTimer()` (or otherwise triggers `scheduleClear()`, e.g. through normal lock/unlock/backgrounding flows) before the configured `ttl` elapses will indefinitely renew the plaintext-passphrase cache validity window — exactly mirroring the reported bug class: renewal is computed from "now" instead of being bound by the originally intended maximum duration (`addedAt + maxTtl`), so the safety cap (`passphraseCacheMaxTtl`, configured at feature setup) provides no actual guarantee once the activity/renewal path is used even once: [5](#0-4) 

### Impact Explanation
`#maxTtl`/`passphraseCacheMaxTtl` exists specifically to bound the amount of time the user's raw decryption passphrase sits in (session) storage in plaintext, limiting the exposure window for secret disclosure (e.g., to local malware, forensic extraction, or another local unprivileged process/user with storage access) and enforcing a policy that re-authentication (full passphrase entry) is eventually required. By repeatedly calling the public `restartAutoLockTimer()` (or via ordinary background/foreground/lock cycling that triggers `scheduleClear()`) at an interval shorter than `ttl`, this hard cap is silently bypassed, and the cached plaintext passphrase can persist far longer than the configured `maxTtl`, weakening the encrypted-storage/secret-handling trust boundary. This does not require any special privilege beyond ordinary use of the app's own public API.

### Likelihood Explanation
The vulnerable code path is trivially reachable: any client that can call the public `exodus.application.restartAutoLockTimer()` method (documented API, intended to be called by the UI/app itself, e.g. on user activity) can repeat the call at any interval to keep resetting `inactiveAt`, and the `ttl`/`maxTtl` values are attacker/caller-adjustable in the sense that `changeLockTimer` can also update `ttl` used in the same check. No race condition or timing precision is required — a simple periodic call under the `ttl` window is sufficient.

### Recommendation
Bound the `inactiveAt` branch by the original `addedAt + #maxTtl` in `get()`, e.g. require `Math.min(inactiveAt + ttl, addedAt + #maxTtl) > Date.now()`, so that activity-based renewal can never extend the cache's validity beyond the originally configured hard cap. Additionally, consider capping `scheduleClear()`/`changeTtl()` so `inactiveAt` cannot be refreshed past `addedAt + #maxTtl`.

### Proof of Concept
1. Configure `application({ cachePassphrase: true, passphraseCacheMaxTtl: <N ms> })` per [5](#0-4) .
2. Unlock the wallet with a passphrase so `PassphraseCache.set()` stores `addedAt = Date.now()`.
3. Before `addedAt + maxTtl` is reached, call `exodus.application.restartAutoLockTimer()` (which calls `passphraseCache.scheduleClear()`, setting `inactiveAt = Date.now()`).
4. Repeat step 3 at an interval smaller than the configured `ttl` (`autoLockTimerAtom` value), indefinitely, well past the original `addedAt + maxTtl` deadline.
5. Observe that `PassphraseCache.get()` keeps returning the cached plaintext passphrase because it only checks `inactiveAt + ttl > Date.now()`, never re-validating against `addedAt + maxTtl` per [6](#0-5) , demonstrating the `maxTtl` hard cap is bypassed.

### Citations

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

**File:** features/application/src/index.ts (L21-27)
```typescript
type ApplicationConfig = {
  cachePassphrase?: boolean
  passphraseCacheMaxTtl?: number
}

const application = (
  { cachePassphrase, passphraseCacheMaxTtl }: ApplicationConfig = Object.create(null)
```
