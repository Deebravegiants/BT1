### Title
`PassphraseCache.changeTtl()` retroactively extends session validity for already-elapsed inactivity time using the new TTL instead of the TTL in effect when the wallet went inactive - (File: `features/application/src/modules/passphrase-cache.ts`)

### Summary
`PassphraseCache` caches the decrypted wallet passphrase and expires it based on an inactivity TTL. `changeTtl()` (invoked via `Application.changeLockTimer` → `exodus.application.changeLockTimer({ ttl })`) overwrites the stored `TTL_KEY` in place without re-basing the already-elapsed `inactiveAt` timestamp, so a longer TTL is applied retroactively to time that has already elapsed under the old (potentially much shorter) TTL.

### Finding Description
The cache tracks three timestamps/values in storage: `PASSPHRASE_KEY`, `ADDED_AT_KEY`/`INACTIVE_AT_KEY`, and `TTL_KEY` [1](#0-0) .

`get()` determines whether the cached passphrase is still valid by comparing `inactiveAt + ttl` (the currently stored `ttl`) against `Date.now()`: [2](#0-1) 

`changeTtl()` simply writes the new TTL over the old one and reschedules the clear alarm, without recomputing `inactiveAt` or otherwise "settling" the previous state under the old TTL first: [3](#0-2) 

This is the same bug class as the Sherlock report: a time-dependent state (accrued interest / elapsed inactivity) is evaluated lazily against whatever configuration parameter (interest rate / TTL) happens to be current at read time, rather than being "settled" against the parameter that was in effect while that time elapsed. Here, `inactiveAt` is set once when the app goes inactive (`scheduleClear()` writes `INACTIVE_AT_KEY = Date.now()` [4](#0-3) ), but the TTL used against that fixed `inactiveAt` can be freely swapped afterward by `changeTtl()`, causing the entire elapsed-since-inactive window to be judged under the new TTL — not the TTL policy that was actually in force while the device was inactive.

`changeLockTimer` is exposed on the public `application` API surface (`exodus.application.changeLockTimer({ ttl })`) and is also exposed (deprecated alias) as `wallet.changeLockTimer`, reachable from any code with access to the `exodus` SDK instance (e.g. the wallet UI process over the RPC transport) [5](#0-4) [6](#0-5) .

### Impact Explanation
`changeTtl()` clamps to `#maxTtl` but places no floor relative to elapsed inactivity or any re-authentication requirement [7](#0-6) . Consider: the wallet goes inactive with a short TTL (e.g., 1 minute), and `inactiveAt` is recorded. Before the 1-minute window naturally expires and the decrypted passphrase is cleared, a call to `changeLockTimer({ ttl: <max> })` retroactively extends validity of the *already-stale* `inactiveAt` checkpoint to the new, much longer TTL. The net effect is that a decrypted, cached passphrase (which unlocks the keychain/seed) that should have expired under the policy that applied while the device was locked/inactive is kept valid far longer than the security policy intended, extending the exposure window of highly sensitive material without requiring the user to re-enter their passphrase. This directly weakens the wallet's auto-lock protection, which is the primary defense of the decrypted seed while the app is not actively supervised by the user.

### Likelihood Explanation
The `changeLockTimer` call is a first-class, documented public API on `exodus.application`/`exodus.wallet`, not restricted to a privileged origin check within `application.ts` or `passphrase-cache.ts` themselves [8](#0-7) . Any caller (compromised/legitimate UI code, or any code path with SDK access) that can invoke this one method can trigger the retroactive extension; no race condition or complex chain is required — a single call after the app goes inactive is sufficient.

### Recommendation
When changing the TTL via `changeTtl()`, do not blindly overwrite `TTL_KEY` for an already-elapsed inactivity period. Instead, re-evaluate/settle the current state under the *old* TTL first (i.e., call the equivalent of `get()`'s expiry check and clear if already expired) before applying the new TTL, and/or re-base `inactiveAt` to "now" when the TTL changes, so the new TTL only governs future elapsed time rather than retroactively re-validating a window that should already have expired under the previous, shorter policy.

### Proof of Concept
1. Configure `maxTtl` generously (e.g., default `60m` via `#maxTtl`) and set a short lock timer: `await exodus.application.changeLockTimer({ ttl: ms('1m') })`.
2. Put the app in background/inactive state so `restartAutoLockTimer()` → `passphraseCache.scheduleClear()` records `INACTIVE_AT_KEY = Date.now()` with `TTL_KEY = 1m` [4](#0-3) .
3. Wait 50 seconds (within the 1-minute window, but close to expiry).
4. Call `await exodus.application.changeLockTimer({ ttl: ms('60m') })`. This invokes `changeTtl(60m)`, which overwrites `TTL_KEY` to `60m` without resetting `INACTIVE_AT_KEY` [7](#0-6) .
5. Call `passphraseCache.get()` at, say, 30 minutes after the original inactivity timestamp. Because `inactiveAt + ttl` (`inactiveAt + 60m`) is still greater than `Date.now()`, the cached passphrase is returned as valid [9](#0-8) , even though under the original 1-minute policy that governed the actual inactive period, it should have been cleared long ago.

**Uncertainty note:** I was not able to fully verify from the indexed code whether any UI-level guardrail (e.g. requiring re-authentication before allowing `changeLockTimer` calls, or origin/permission checks upstream of the RPC bridge) exists outside of `application.ts`/`passphrase-cache.ts`, since such checks—if they exist—could live in UI code not covered by the current index. Given index size limits, some file contents may not have been available; a full Devin session with complete repository access would be needed to confirm whether any such caller-side restriction mitigates this at the UI layer.

### Citations

**File:** features/application/src/modules/passphrase-cache.ts (L8-11)
```typescript
const TTL_KEY = 'ttl'
const PASSPHRASE_KEY = 'passphrase'
const ADDED_AT_KEY = 'addedAt'
const INACTIVE_AT_KEY = 'inactiveAt'
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

**File:** features/application/src/api/index.ts (L209-240)
```typescript
const factory = ({ application, eventLog, passphraseCache }: FactoryParams): ApplicationApi => {
  const restoreFromCurrentPhrase = async ({ passphrase }: RestoreFromCurrentPhraseParams = {}) => {
    await eventLog.record({ event: 'restore_with_current_phrase' })

    if (!passphrase && passphraseCache) passphrase = await passphraseCache.get()
    const mnemonic = await application.getMnemonic({ passphrase })
    await application.import({ passphrase, mnemonic })
  }

  return {
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

**File:** sdks/headless/src/api/index.js (L51-68)
```javascript
  const applicationWalletApi = {
    addSeed: application.addSeed,
    start: deprecated(application.start),
    stop: deprecated(application.stop),
    load: deprecated(application.load),
    unload: deprecated(application.unload),
    create: deprecated(application.create),
    lock: deprecated(application.lock),
    unlock: deprecated(application.unlock),
    import: deprecated(application.import),
    delete: deprecated(application.delete),
    getMnemonic: deprecated(application.getMnemonic),
    setBackedUp: deprecated(application.setBackedUp),
    changePassphrase: deprecated(application.changePassphrase),
    changeLockTimer: deprecated(application.changeLockTimer),
    restartAutoLockTimer: deprecated(application.restartAutoLockTimer),
    restoreFromCurrentPhrase: deprecated(application.restoreFromCurrentPhrase),
  }
```

**File:** features/application/src/modules/application.ts (L451-453)
```typescript
  changeLockTimer = async ({ ttl }: { ttl: number }) => {
    return this.#passphraseCache.changeTtl(ttl)
  }
```
