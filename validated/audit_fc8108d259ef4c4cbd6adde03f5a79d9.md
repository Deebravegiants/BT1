Based on the investigation, `changeLockTimer` is confirmed exposed as a **BE-only** RPC method on the multi-process wallet API ` [1](#0-0) `, reachable through the RPC bridge from the UI/renderer process ` [2](#0-1) ` ` [3](#0-2) `. This confirms the analog is reachable via an unprivileged-user-facing RPC boundary, matching one of the allowed threat-boundary categories.

### Title
`PassphraseCache.changeTtl` retroactively extends the auto-lock inactivity window, allowing extended unauthorized auto-unlock access - (File: `features/application/src/modules/passphrase-cache.ts`)

### Summary
`PassphraseCache.changeTtl` mutates the stored `TTL_KEY` in place without first "closing out"/re-evaluating the currently pending inactivity window recorded at `INACTIVE_AT_KEY`. This mirrors the `CashManager.setEpochDuration` root cause: a duration parameter is changed without transitioning/finalizing the value that was already accruing under the old duration, so the same stored `inactiveAt` timestamp is later re-evaluated against an inconsistent (new) duration, producing an outcome dependent on transaction/call ordering rather than deterministic security policy.

### Finding Description
`PassphraseCache.get()` authorizes silent auto-unlock (`#autoUnlock` in `features/application/src/modules/application.ts`) by checking `inactiveAt + ttl > Date.now()` [4](#0-3) , where `ttl` is read live from storage at call time, not the `ttl` that was in effect when `inactiveAt` was recorded.

`changeTtl(ttl)` is the analog of `setEpochDuration`: it directly overwrites `TTL_KEY` (and the `autoLockTimerAtom`) without invoking any "transition" step that would first finalize/consume the currently-elapsed portion of the existing inactivity period under the old TTL [5](#0-4) :
```ts
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
Because `scheduleClear()`/`#scheduleClear()` only reschedule the `clear-passphrase` alarm from "now" using the new TTL, but do **not** update `INACTIVE_AT_KEY`, the pre-existing `inactiveAt` timestamp is retroactively re-interpreted under the new TTL when `get()` runs its `inactiveAt + ttl > Date.now()` check. This is exactly the "front-run vs back-run" inconsistency from the report: if `changeLockTimer` executes while a lock-timer window is already counting down (i.e., before the old TTL has elapsed and before a `transitionEpoch`-equivalent finalize happens), the effective allowed inactivity period for the *already elapsed* time is silently recomputed with the new (potentially much larger) TTL.

`changeLockTimer` is reachable through the public multi-process RPC boundary (`applicationApi` → `sdks/headless`), the same class of boundary called out in the rules (RPC bridge) [6](#0-5) [7](#0-6) .

### Impact Explanation
If `changeLockTimer` is invoked (e.g. by any code/UI reachable over the RPC bridge, or by a bug/race in the settings UI) while the wallet is already inactive and counting down toward auto-lock under an old, short TTL, the cached passphrase's effective validity window is retroactively extended using the new TTL applied to the old `inactiveAt` timestamp. This can keep `#autoUnlock` silently unlocking the wallet with the cached passphrase far longer than the security policy that was actually in force when the device went inactive intended — a direct weakening of the wallet's lock/auto-unlock security boundary, i.e. unauthorized continued access to the unlocked wallet/cached secret beyond the originally configured timeout.

### Likelihood Explanation
Requires a call to `changeLockTimer` to race with an already-pending inactivity window (i.e., call order matters, exactly as in the CashManager PoC) rather than requiring privileged access — `changeLockTimer` is a normal, unprivileged application API reachable over RPC and intended to be user-controllable, so the ordering condition is plausible in real usage (e.g. app is backgrounded, then TTL setting is changed before the old timer would have expired).

### Recommendation
Before applying a new TTL in `changeTtl`, finalize/"transition" the currently pending inactivity window: if `INACTIVE_AT_KEY` is already set, either (a) evaluate `get()`'s expiry check against the *old* TTL first and clear the cache if already expired, or (b) reset `INACTIVE_AT_KEY` to `Date.now()` when the TTL changes so the new TTL only applies prospectively, never retroactively to time already elapsed under the old TTL.

### Proof of Concept
1. Unlock wallet, `passphraseCache.set(passphrase)` caches with `ttl = 5min`.
2. App backgrounds → `scheduleClear()` sets `INACTIVE_AT_KEY = T0`, alarm scheduled for `T0 + 5min`.
3. Before `T0 + 5min`, call `application.changeLockTimer({ ttl: 60min })` (e.g. via RPC/settings while still inactive).
4. `changeTtl` sets `TTL_KEY = 60min`, reschedules alarm for `now + 60min`, but `INACTIVE_AT_KEY` is unchanged (still `T0`).
5. At time `T0 + 30min` (well past the original 5-minute policy), call `passphraseCache.get()` → `inactiveAt (T0) + ttl (60min) > now` is `true`, so the cached passphrase is returned and `#autoUnlock` silently unlocks the wallet — even though the policy in force at the moment the device went inactive was only 5 minutes.

### Citations

**File:** sdks/headless/README.md (L184-184)
```markdown
| changeLockTimer          | `async ({ ttl: number }) => void`                                                   | Change auto unlock ttl (`BE Only`)                                                |
```

**File:** sdks/headless/src/api/index.js (L15-18)
```javascript
const createApi = ({ ioc, port, config, debug, logger }) => {
  const apis = ioc.getByType('api')
  const { application } = ioc.get('applicationApi')

```

**File:** sdks/headless/src/api/index.js (L51-67)
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
```

**File:** features/application/src/api/index.ts (L209-238)
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
```

**File:** features/application/src/modules/passphrase-cache.ts (L61-78)
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

**File:** features/application/src/modules/application.ts (L451-453)
```typescript
  changeLockTimer = async ({ ttl }: { ttl: number }) => {
    return this.#passphraseCache.changeTtl(ttl)
  }
```
