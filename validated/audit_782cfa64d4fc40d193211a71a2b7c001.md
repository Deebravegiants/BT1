### Title
Stale full-account-map snapshot in `WalletAccounts.createMany` overwrites concurrent account updates - ([File: features/wallet-accounts/src/module/wallet-accounts.ts])

### Summary
`WalletAccounts.createMany` (and its wrapper `create`) captures a full local copy of *all* existing wallet accounts before an `await` point, and later persists that entire stale copy — not just the newly created entries — by spreading it over a freshly re-read state. Any account mutation performed concurrently through `updateMany`/`disableMany`/`enableMany`/`removeMany` (which are not covered by `createMany`'s own concurrency lock) is silently reverted, exactly analogous to the reported `TroveManager::openTrove` bug where a value cached before an internal state-mutating call was used to overwrite the post-mutation state.

### Finding Description
`createMany` snapshots the current accounts and clones them into a local mutable object: [1](#0-0) 

It then awaits `this.#wallet.getPrimarySeedId()` — an async operation that yields the event loop — after the snapshot has already been taken. Any subsequent bookkeeping (index derivation, compatibility mode mirroring, new account creation) operates on this stale `walletAccounts` object, which is the *entire* account map (all pre-existing accounts plus the newly created ones), not a diff: [2](#0-1) 

This full stale object is then handed to `#persistWalletAccounts`: [3](#0-2) 

`#persistWalletAccounts` re-reads the atom for the *current* (fresh) state, but then merges it by spreading the stale `walletAccounts` argument last, so every key present in the stale snapshot silently wins over the freshly persisted state: [4](#0-3) 

`createMany` is wrapped with its own `makeConcurrent({ concurrency: 1 })` lock, but that lock only serializes calls to `createMany` itself — it does **not** protect against concurrent calls to `updateMany`, `disableMany`, `enableMany`, or `removeMany`, all of which read-modify-write the same atom without any shared lock: [5](#0-4) [6](#0-5) 

This is structurally identical to the reported bug class: a value (here, the entire account map) is cached before an async operation, that async window allows the underlying store to be legitimately mutated elsewhere, and the stale cached value is later used to compute/overwrite the final persisted state — discarding the concurrent update.

### Impact Explanation
If a user (or app-internal logic) disables a wallet account (e.g., `disableMany`, which removes a hardware account's public key and/or flips `enabled: false`) while a `createMany`/`create` call is in flight (e.g., during the `await getPrimarySeedId()` window), the disable is silently reverted once `createMany` completes: the disabled/removed account reappears as enabled with its prior data, because `createMany`'s stale full-map snapshot overwrites the freshly-disabled state. Similarly, an `updateMany` change (such as `compatibilityMode` changes or other account metadata updates) performed concurrently can be discarded. This causes wallet account state corruption — an account the user explicitly disabled (potentially because it was compromised or no longer wanted) can be silently resurrected with stale enabled/associated-key state, which is an account-isolation/state-integrity violation affecting which keys/accounts are considered active in the wallet.

### Likelihood Explanation
The race requires two account-mutating operations to interleave around the microtask boundary created by `await this.#wallet.getPrimarySeedId()` inside `createMany`. Because `create`/`createMany` and `disable`/`disableMany`/`enable`/`enableMany`/`update`/`updateMany` are all public, unprivileged-caller-reachable module methods that can be triggered independently from UI actions or app bootstrap code without any shared serialization, this is plausible under normal concurrent usage (e.g., rapid UI actions, or automated flows creating and disabling accounts near-simultaneously), though it requires a specific timing window rather than being deterministic on every call.

### Recommendation
Ensure `createMany` re-reads or merges only the diff (newly created accounts) against the freshest state at persist time, rather than carrying forward a full stale snapshot of all accounts. Concretely, `#persistWalletAccounts` should merge fresh state with only the *changed/added* entries, and/or `createMany` should be serialized against `updateMany`/`disableMany`/`enableMany`/`removeMany` using a shared concurrency lock (similar to `#replaceAll`), so no account-mutating operation can silently clobber another's freshly committed state.

### Proof of Concept
1. App has an existing enabled hardware wallet account `ledger_0`.
2. Call `walletAccounts.create({...})` — this triggers `createMany`, which reads and clones all accounts (including `ledger_0: {enabled: true, ...}`) into `walletAccounts`, then awaits `this.#wallet.getPrimarySeedId()`.
3. Before that await resolves, call `walletAccounts.disable('ledger_0')` — this runs unguarded (`disableMany` has no shared lock with `createMany`), deletes `ledger_0` from the atom's stored map, and persists successfully.
4. `createMany` resumes, finishes deriving the new account's index/data using its stale `walletAccounts` object (which still contains `ledger_0`), and calls `#persistWalletAccounts(walletAccounts)`.
5. `#persistWalletAccounts` re-reads the atom (now without `ledger_0`), but merges `{...currentWalletAccounts, ...walletAccounts}` — since `walletAccounts` still contains the stale `ledger_0` entry, it is written back into the atom, effectively undoing the disable that just completed in step 3.

### Citations

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L203-221)
```typescript
  #persistWalletAccounts = async (
    walletAccounts: Record<string, WalletAccount>,
    options: { useOptimisticWrite?: boolean } = {}
  ) => {
    const currentWalletAccounts = await this.#walletAccountsInternalAtom.get()

    if (currentWalletAccounts && containWalletAccounts(currentWalletAccounts, walletAccounts)) {
      return
    }

    const updatedWalletAccounts = { ...currentWalletAccounts, ...walletAccounts }
    await this.#walletAccountsInternalAtom.set(updatedWalletAccounts)

    if (options.useOptimisticWrite) {
      void this.#updateFusion()
    } else {
      await this.#updateFusion()
    }
  }
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L333-341)
```typescript
  updateMany = async (dataByName: Record<string, Record<string, unknown>>) => {
    const currentWalletAccounts = await this.#getInternalWalletAccountsWithFallback()
    const updated = Object.entries(dataByName).map(([name, data]) => {
      const walletAccount = updateWalletAccount(currentWalletAccounts, name, data)
      return [walletAccount.toString(), walletAccount]
    })

    await this.#persistWalletAccounts(Object.fromEntries(updated))
  }
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L348-356)
```typescript
  createMany = makeConcurrent(
    async (
      walletAccountsData: WalletAccountsData[],
      options?: { useOptimisticWrite?: boolean }
    ) => {
      const currentWalletAccounts = await this.#getInternalWalletAccountsWithFallback()
      const walletAccounts = { ...currentWalletAccounts }
      const primarySeedId = await this.#wallet.getPrimarySeedId()

```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L359-407)
```typescript
      const created = walletAccountsData.map((_data) => {
        const data = { ..._data }
        if (!data.source) data.source = WalletAccount.EXODUS_SRC

        if (data.source === WalletAccount.EXODUS_SRC) {
          assert(
            !data.seedId || data.seedId === primarySeedId,
            'expected seedId to be the primarySeedId for "exodus" accounts'
          )

          data.seedId = primarySeedId
          // mirror compatibilityMode from default account unless we create it
          data.compatibilityMode = walletAccounts[WalletAccount.DEFAULT_NAME]
            ? walletAccounts[WalletAccount.DEFAULT_NAME].compatibilityMode
            : data.compatibilityMode
        }

        if (shouldDeriveIndex(data as { index?: number; source: string })) {
          data.index = getNextIndex({
            walletAccounts,
            seedId: data.seedId ?? '',
            source: data.source ?? WalletAccount.EXODUS_SRC,
            compatibilityMode: data.compatibilityMode,
            fillIndexGapsOnCreation: this.#fillIndexGapsOnCreation,
          })
        }

        const walletAccount = new WalletAccount(data as WalletAccountParams)
        const exists = Boolean(walletAccounts[walletAccount.toString()])
        if (exists && !this.#fillIndexGapsOnCreation) {
          throw new Error(`WalletAccount already exists: ${walletAccount.toString()}`)
        }

        // allow updating existing ones
        if (!exists) {
          const tag = getUniqueTagForWalletAccount(walletAccount)
          const match = byUniqueFields[tag]?.[0]
          if (match) {
            throw new Error(
              `Already have walletAccount with same .source, .id, .seedId, and .index: ${JSON.stringify(
                match.toJSON()
              )}`
            )
          }
        }

        walletAccounts[walletAccount.toString()] = walletAccount
        return walletAccount
      })
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L409-409)
```typescript
      await this.#persistWalletAccounts(walletAccounts, options)
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L420-448)
```typescript
  disableMany = async (walletAccountNames: string[]) => {
    const currentWalletAccounts = await this.#getInternalWalletAccountsWithFallback()
    walletAccountNames = walletAccountNames.filter(
      (walletAccount) => currentWalletAccounts[walletAccount]
    )

    if (walletAccountNames.length === 0) return

    const walletAccounts = { ...currentWalletAccounts }

    await this.setActive((oldValue) =>
      walletAccountNames.includes(oldValue) ? WalletAccount.DEFAULT_NAME : oldValue
    )

    for (const walletAccount of walletAccountNames) {
      if (walletAccounts[walletAccount].isHardware) {
        delete walletAccounts[walletAccount]
        delete this.#hardwareWalletPublicKeys[walletAccount]
      } else {
        walletAccounts[walletAccount] = this.#disableWalletAccount(walletAccounts, walletAccount)
      }
    }

    if (equalWalletAccounts(currentWalletAccounts, walletAccounts)) return

    await this.#walletAccountsInternalAtom.set(walletAccounts)
    await this.#savePublicKeys()
    await this.#updateFusion()
  }
```
