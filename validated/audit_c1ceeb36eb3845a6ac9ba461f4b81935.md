### Title
Reducing the passphrase cache TTL does not account for elapsed inactivity time, extending the passphrase's cached lifetime beyond the newly configured cap - (File: `features/application/src/modules/passphrase-cache.ts`)

### Summary
`PassphraseCache.changeTtl()` mirrors the `RateLimited.setBufferCap` bug class: it updates the "cap" (the auto-lock TTL) and reschedules the clearing timer relative to the *current time*, without accounting for the amount of the previous cap already "consumed" (i.e., time already elapsed since the passphrase went inactive). This means a newly reduced TTL is not retroactively applied to time already spent inactive, allowing the cached (sensitive) passphrase to remain valid/persisted in storage for longer than the newly configured cap intends.

### Finding Description
`PassphraseCache` caches the user's wallet passphrase in `sessionStorage` so the wallet can auto-unlock, guarded by a TTL (`autoLockTimerAtom`) and an inactivity timestamp (`INACTIVE_AT_KEY`):

<cite repo="AYontt/hydra--012" path="features/application/src/modules/passphrase-cache.ts" start="40="48" /> [1](#0-0) 

When the app backgrounds, `scheduleClear()` marks the passphrase inactive and reschedules an alarm based on the *current* TTL: [2](#0-1) 

The TTL can be changed later via `changeTtl()`: [3](#0-2) 

This is structurally identical to `_setBufferCap`: it writes the new "cap" (`newTtl`) to the atom/storage and then reschedules the clearing alarm (`#scheduleClear`) from **now**, exactly like `RateLimited._setBufferCap` applied the *old* buffer cap to stored usage before overwriting it. Here, the analogous flaw is that the *elapsed inactivity time already accrued under the old TTL* is discarded/ignored — `#scheduleClear()` in `changeTtl` computes `delayInMinutes` from `Date.now()`, not from the original `inactiveAt` value, so a reduced TTL is not applied against time already spent inactive.

Concretely: if the passphrase became inactive at `t0` under TTL `T1` (e.g., 60 min), and after 50 minutes elapse the user (or app) calls `changeLockTimer` to shrink the TTL to `T2` (e.g., 5 min), `changeTtl()`:
1. Sets `autoLockTimerAtom` and `TTL_KEY` to `T2`.
2. Calls `#scheduleClear()`, which clears the old alarm and creates a new one firing `T2` minutes from **now** — i.e., at `t0 + 55min`, not immediately, even though the new cap (`T2 = 5min`) was already exceeded 45 minutes ago relative to `inactiveAt`.

The only place that correctly re-derives expiry against `inactiveAt` is `get()`: [4](#0-3) 

So the passphrase is only actually purged early if `get()` happens to be called before the stale, over-long alarm fires. Absent that call (e.g., extension/service-worker not woken, or platform doesn't invoke `get()` proactively), the plaintext passphrase remains sitting in session storage well past the newly configured (tighter) auto-lock TTL, purely because the background alarm was rescheduled from "now" instead of accounting for already-elapsed inactive time — the exact "does not reduce current buffer/usage to the new cap" defect described in the report.

### Impact Explanation
The passphrase cache stores the wallet's decryption passphrase in cleartext in `sessionStorage` to support auto-unlock. The auto-lock TTL is a user/config-configurable security control meant to bound how long that secret persists after the app becomes inactive. This flaw causes the *effective* enforcement window (the background alarm that would call `clear()`) to silently extend beyond the newly configured, more restrictive TTL — a direct, unauthorized retention/disclosure-adjacent bug for a highly sensitive secret (the wallet passphrase). Any process or attacker with transient access to the session storage (e.g., malicious script, memory/disk forensics, malicious dependency) has a longer real window to read the still-cached passphrase than the security policy intends.

### Likelihood Explanation
Reachable whenever `application.changeLockTimer({ ttl })` is invoked while the passphrase is already cached and inactive (background) — a supported, documented public API (`exodus.application.changeLockTimer`) — with no privileged access required beyond normal app usage, e.g., a user/config lowering the auto-lock timer while the wallet is backgrounded.

### Recommendation
When rescheduling the clear alarm in `changeTtl`/`#scheduleClear`, compute the remaining delay relative to the original `inactiveAt` timestamp rather than `Date.now()`. If `inactiveAt + newTtl <= Date.now()`, clear the passphrase immediately instead of scheduling a future alarm; otherwise schedule the alarm for `(inactiveAt + newTtl) - Date.now()`, mirroring the recommended fix of applying the new cap to already-accrued usage before persisting the new value.

### Proof of Concept
1. Configure `passphraseCacheMaxTtl` and set `autoLockTimerAtom` TTL to 60 minutes; call `application.unlock({ passphrase })`, which caches the passphrase via `PassphraseCache.set()`.
2. Background the app: `PassphraseCache.scheduleClear()` sets `inactiveAt = t0` and schedules alarm `clear-passphrase` to fire in 60 minutes.
3. Wait 50 minutes (still under the 60-minute cap, alarm not yet fired).
4. Call `exodus.application.changeLockTimer({ ttl: 5 * 60 * 1000 })` (5 minutes) — see [5](#0-4)  which forwards to `changeTtl`.
5. `changeTtl()` sets `TTL_KEY = 5min` and calls `#scheduleClear()`, which clears the old alarm and creates a new one firing 5 minutes from **now** (`t0 + 55min`) instead of recognizing that `t0 + 5min` (the new cap applied to elapsed time) has already passed.
6. Inspect `sessionStorage` between `t0+50min` and `t0+55min`: the passphrase key is still present in plaintext, even though the newly configured 5-minute cap was exceeded 45 minutes earlier — demonstrating the cap was not retroactively applied to already-elapsed usage.

### Citations

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

**File:** features/application/src/modules/application.ts (L451-453)
```typescript
  changeLockTimer = async ({ ttl }: { ttl: number }) => {
    return this.#passphraseCache.changeTtl(ttl)
  }
```
