### Title
Passphrase-cache TTL boundary logic can extend cached-secret validity beyond configured `maxTtl` - ([File: features/application/src/modules/passphrase-cache.ts])

### Summary
The Teller `calculateAmountOwed()` bug class is a boundary/ternary miscalculation where a "special-case" time window (the last payment cycle) is checked independently from the overall bound, allowing the check to diverge from the intended invariant ("last cycle should equal entire remaining balance", not a fluctuating window). The Hydra analog is in `PassphraseCache.get()` in [1](#0-0) , where the cached-passphrase validity check branches into two independent time windows (`inactiveAt`-based vs. `addedAt`-based) instead of always being bounded by the overall `maxTtl` invariant.

### Finding Description
`PassphraseCache` stores a cached wallet passphrase so the wallet can auto-unlock without re-entering the password, gated by a `maxTtl` security ceiling configured to force periodic re-authentication [2](#0-1) .

`get()` decides whether the cached passphrase is still valid using two mutually exclusive branches:
```js
if (inactiveAt) {
  if (inactiveAt + ttl > Date.now()) { return passphrase }
} else if (addedAt + this.#maxTtl > Date.now()) {
  return passphrase
}
``` [3](#0-2) 

The `addedAt + maxTtl` bound — the actual security ceiling — is only enforced while `inactiveAt` is unset. Once `inactiveAt` is set (via `scheduleClear()`, which is called on every app backgrounding/unload event through `application.unload()`/`restartAutoLockTimer()` [4](#0-3) [5](#0-4) ), validity is instead computed purely as `inactiveAt + ttl`, with no comparison at all to `addedAt + maxTtl`. `scheduleClear()` resets `inactiveAt` to `Date.now()` every time it is invoked: [6](#0-5) .

Since any normal app lifecycle transition (background/foreground, `restartAutoLockTimer`) re-invokes `scheduleClear()` and rewrites `inactiveAt`, an app/session that repeatedly triggers this path before each `ttl` window elapses can keep pushing the “valid” window forward indefinitely — the `maxTtl` ceiling that the sponsor-equivalent design intends ("force re-auth after N minutes no matter what") is never re-checked once `inactiveAt` exists. This mirrors the Teller root cause exactly: a special-case branch (last cycle / inactive-state) computes its own bounded value instead of being clamped against the overall invariant, silently diverging from the intended "hard ceiling" semantics.

### Impact Explanation
If exploitable, this allows the cached plaintext passphrase to remain retrievable (and used for `#autoUnlock()` [7](#0-6) ) well past the configured `maxTtl` security boundary, as long as backgrounding/foregrounding events keep resetting `inactiveAt`. This weakens the auto-lock/passphrase-cache security control and could let an attacker with transient device/session access (e.g., a malicious app triggering app-state transitions, or a user simply toggling app foreground/background) obtain a valid unlock long after the intended maximum caching window, effectively bypassing the "cache-must-expire" invariant, which is the wallet's defense against long-lived plaintext secret exposure.

### Likelihood Explanation
Moderate-to-uncertain. The mechanism requires the wallet's `unload`/`restartAutoLockTimer` (both wired to `scheduleClear()`) to fire repeatedly at intervals shorter than the current `ttl`, which happens naturally with normal user app-switching behavior (e.g., mobile app backgrounding, per `features/app-process-mobile` lifecycle events observed in the test file [8](#0-7) ). I was not able to fully trace whether any other invariant elsewhere clamps `inactiveAt + ttl` against `addedAt + maxTtl` outside this file, or whether platform-specific callers impose additional limits before invoking `scheduleClear()`/`restartAutoLockTimer()` — this should be verified against the full call graph across platform adapters, which the index may not fully capture.

### Recommendation
In `get()`, always bound validity by the absolute ceiling regardless of branch, e.g.:
```js
const validUntil = Math.min(
  inactiveAt ? inactiveAt + ttl : Infinity,
  addedAt + this.#maxTtl
)
if (passphrase && validUntil > Date.now()) { return passphrase }
```
This ensures the `inactiveAt`-based short-lived extension can never push validity past the original `addedAt + maxTtl` hard limit, matching the Teller fix's intent of never letting a special-case branch diverge from the overall bound.

### Proof of Concept
Conceptual reproduction (needs live-environment verification, not confirmed via test run):
1. `unlock({ passphrase })` is called, setting `addedAt = T0`, `ttl = configured autoLockTimer` [9](#0-8) .
2. Before `T0 + maxTtl`, the app is backgrounded (triggers `application.unload()` → `passphraseCache.scheduleClear()`), setting `inactiveAt = T1`.
3. Repeat step 2 periodically (foreground/background cycling), each time resetting `inactiveAt` to "now" before its own `ttl` window expires.
4. `get()` now only checks `inactiveAt + ttl > Date.now()`, which is satisfied indefinitely, `addedAt + maxTtl` is never re-checked.
5. `#autoUnlock()` therefore returns the cached passphrase and unlocks the wallet far beyond the intended `maxTtl` ceiling.

I was unable to execute this against a running instance to confirm the exact exploitability window and whether any external caller enforces a stricter limit; this should be validated with a live Devin session to trace all callers of `scheduleClear()`/`changeTtl()` and confirm the timing invariant is genuinely broken end-to-end.

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

**File:** features/app-process-mobile/module/__tests__/app-process.test.js (L132-153)
```javascript
  test('extends lock by extension duration', async () => {
    setup({ historyLimit: 2 })
    await appProcess.load()

    await appProcess.requestLockTimerExtension()

    const { lockActivatesAt } = await appProcessAtom.get()
    expect(lockActivatesAt).toBeDefined()
  })

  test('does not extend lock if existing lock is not expired', async () => {
    setup({ historyLimit: 2 })
    await appProcess.load()

    await appProcess.requestLockTimerExtension()
    const { lockActivatesAt } = await appProcessAtom.get()

    await appProcess.requestLockTimerExtension()
    const { lockActivatesAt: lockActivatesAt2 } = await appProcessAtom.get()

    expect(lockActivatesAt).toBe(lockActivatesAt2)
  })
```
