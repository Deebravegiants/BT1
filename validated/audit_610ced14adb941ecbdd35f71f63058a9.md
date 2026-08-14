### Title
Concurrent `unlock()` calls allow duplicate execution of storage migrations before their completion flag is persisted - (File: sdks/headless/src/migrations/attach.js)

### Summary
`attachMigrations()` implements a TOCTOU-style guard identical in structure to the Knox `processAuction()` bug: it reads a "has this run already" flag, and only persists that flag *after* the guarded action finishes. If the guarded hook (`migrate`) is fired a second time before the first invocation's flag write completes, the guarded logic runs twice.

### Finding Description
`attachMigrations` registers a `migrate` hook that determines which migrations still need to run by reading `migrationFlagsStorage.batchGet(migrationNames)` and computing a diff, then executes each migration and only afterwards calls `migrationFlagsStorage.set(name, true)`: [1](#0-0) [2](#0-1) 

The `migrate` hook is fired from `Application#unlock()` and `Application#autoUnlock()`, both of which are reachable via ordinary, unprivileged SDK/API calls (e.g. `exodus.application.unlock({ passphrase })`), and there is no lock preventing `unlock()` from being invoked concurrently or in rapid succession: [3](#0-2) [4](#0-3) 

If `unlock()` is invoked twice before the first `migrate` hook execution has finished writing its flag (e.g., two rapid unlock calls from the UI, a retried unlock request over the RPC/port bridge, or `autoUnlock()` racing a manual `unlock()`), the second `migrate` hook invocation will read the same "not yet migrated" flags — since `batchGet` is read before any migration in the first run has set its flag — and re-run the same migration factory concurrently with the first execution. This is structurally the same root cause as the Knox `processAuction()` issue: a guard/check that is snapshotted at the start of an operation and only "closed" at the very end, allowing the checked action to be invoked more than once whenever the caller triggers the entry hook again in the window before the flag write lands.

### Impact Explanation
Migrations in this codebase directly mutate wallet-account and seed-related state — for example `multi-seed-wallet-accounts` migration reads `walletAccounts` from storage, reassigns `seedId`/`compatibilityMode` on each account, and writes the result back: [5](#0-4) 

Two concurrent executions of the same migration factory against the same underlying storage can race on read-modify-write of `walletAccounts`, corrupting the persisted account-to-seed mapping (e.g., one run's write clobbering the other's, or partially-applied `compatibilityMode`/`seedId` assignment). Because `seedId` determines which key material is used to derive addresses and sign transactions for an account, corruption here can misassign an account to the wrong seed, leading to incorrect signing key usage or loss of access to funds — a direct wallet-compromise-adjacent impact, not merely a UX bug.

### Likelihood Explanation
This requires no privileged access — any caller of the public `unlock()` API (UI double-tap, auto-unlock racing manual unlock, or a retried RPC call across the port/webpage bridge) can trigger two `migrate` hook firings close together. The window is bounded by how long a migration factory's `factory(...)` call takes to resolve (storage I/O, `Promise.race` against a 5s timeout), which is a realistic window for a race to occur, especially under storage lock contention.

### Recommendation
Add an explicit re-entrancy guard around the `migrate` hook body in `attach.js` (e.g., a module-level in-flight promise/mutex that subsequent `migrate` invocations await instead of re-executing), and/or mark each migration's flag optimistically (write a "started" marker) before invoking `factory()` so a concurrent invocation cannot select the same migration to run again.

### Proof of Concept
1. Configure the SDK with a migration whose `factory` takes non-trivial time (simulating storage I/O), as in the test harness at [6](#0-5) .
2. Call `exodus.application.unlock({ passphrase })` twice without awaiting the first call (or trigger `autoUnlock()` concurrently with a manual `unlock()`), causing `application.fire(Hook.Migrate)` to be invoked twice before the first invocation's `migrationFlagsStorage.set(name, true)` executes.
3. Observe that `migration.factory` in `attach.js`'s `attachMigration()` is invoked twice for the same migration name, both operating on the same underlying `walletAccounts`/seed-related storage concurrently — analogous to `processAuction()` being re-entered before its `l.auctionProcessed = true` guard is committed.

Note: I could not fully trace the internal `hook`/`fire` implementation in `features/application/src/modules/application.ts` (whether hook handlers are serialized/queued) within the available tool budget, so I cannot conclusively confirm the absence of a lower-level serialization mechanism that might mitigate this race; this should be verified directly against that file's `hook`/`fire` implementation before treating this as fully confirmed.

### Citations

**File:** sdks/headless/src/migrations/attach.js (L22-48)
```javascript
    try {
      const start = performance.now()
      // `name` is a `safeString` here, that ensures it will be not omitted in Safe Reports when coerced to Safe Errors.
      // TODO: pass `name` into `safeString` with a more meaningful message once safeString supports passing in safeString variables.
      const timeout = rejectAfter(maxDuration, name)

      try {
        await Promise.race([
          factory({
            ...deps,
            config,
            adapters: migrationAdapters,
            modules: migrationModules,
            logger,
          }),
          timeout.promise,
        ])

        timeout.clear()

        const time = performance.now() - start

        logger.log(`migration successful in ${time.toFixed(2)}ms`)

        await migrationFlagsStorage.set(name, true)

        success = true
```

**File:** sdks/headless/src/migrations/attach.js (L84-90)
```javascript
      const migrationNames = migrations.map((migration) => migration.name)
      const migrationFlags = await migrationFlagsStorage.batchGet(migrationNames)
      const migrationsDiff = migrations.filter((v, k) => !migrationFlags[k])

      for (const migration of migrationsDiff) {
        await attachMigration(migration)
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

**File:** features/wallet-accounts/src/migrations/multi-seed-wallet-accounts.ts (L1-41)
```typescript
import { mapValues } from '@exodus/basic-utils'
import { EXODUS_SRC, type WalletAccountParams } from '@exodus/models/lib/wallet-account/index.js'
import { WalletAccount } from '@exodus/models'
import type { StorageAdapters, Wallet } from '../types.js'

const createMultiSeedWalletAccountsMigration = async ({ adapters, modules }: MigrationParams) => {
  const { wallet } = modules

  const primarySeedId = await wallet.getPrimarySeedId()
  const storage = adapters.storage.namespace('walletAccounts')
  const flagsStorage = adapters.unsafeStorage.namespace('flags')
  const compatibilityMode = (await flagsStorage.get('compatibilityMode')) as string | undefined

  const walletAccounts = (await storage.get('walletAccounts')) as
    | Record<string, WalletAccountJSON>
    | undefined

  const onFinish = async () => {
    await flagsStorage.delete('compatibilityMode')
  }

  if (!walletAccounts) {
    await onFinish()
    return
  }

  const migrated = mapValues(walletAccounts, (walletAccount) => {
    if (walletAccount.source === EXODUS_SRC) {
      return new WalletAccount({
        ...walletAccount,
        seedId: primarySeedId,
        compatibilityMode,
      } as WalletAccountParams).toJSON()
    }

    return walletAccount
  })

  await storage.set('walletAccounts', migrated)
  await onFinish()
}
```

**File:** sdks/headless/__tests__/attach.test.js (L228-252)
```javascript
      const migration = {
        name: 'test',
        factory: jest.fn(async () => {
          await new Promise((resolve) => setTimeout(resolve, 10))
        }),
      }

      attachMigrations({
        migrations: [migration],
        application,
        adapters,
        modules,
      })

      await application.fire('migrate')

      expect(migration.factory).toHaveBeenCalledTimes(1)
      expect(analytics.track).toHaveBeenCalledTimes(1)

      const calls = analytics.track.mock.calls
      expect(calls[0][0].properties.success).toBe(true)

      const flagsStorage = adapters.unsafeStorage.namespace('migrations')
      expect(await flagsStorage.get('test')).toBe(true)
    })
```
