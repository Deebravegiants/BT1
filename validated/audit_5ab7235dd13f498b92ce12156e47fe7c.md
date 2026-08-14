### Title
Missing Runtime Schema/Size Validation on Fusion Cloud-Sync Data Ingested into Wallet Accounts and Hardware Public Keys - (File: features/wallet-accounts/src/module/wallet-accounts.ts)

### Summary
The `WalletAccounts` module accepts data pushed through the cross-device Fusion sync channel and merges it directly into local wallet state (`walletAccounts` map and `hardwareWalletPublicKeys`) with no runtime schema or size validation, mirroring the MetaMask Profile Sync bug class where `JSON.parse`'d remote data was trusted via a compile-time-only type assertion.

### Finding Description
The Fusion channel is registered with a `processOne` handler that receives arbitrary `data: FusionData` from the sync backend and stores it verbatim in `#rawFusionData`, then hands it to `#replaceAll`: [1](#0-0) 

`#replaceAll` takes the remote `walletAccounts` and `accounts` (hardware wallet public keys) fields and reconstructs local `WalletAccount` instances directly from the untyped, remotely-supplied field object, and unconditionally overwrites `#hardwareWalletPublicKeys` with whatever `accounts` value arrived over sync: [2](#0-1) 

The only structural interface contract is a TypeScript type (`FusionData`), which — exactly like the `as StoredGrantedPermission` assertion in the reported MetaMask bug — is a compile-time hint only and provides no runtime guarantee: [3](#0-2) 

The invariant checks that do exist (`updateWalletAccount`'s `assert` on `source`/`id`/`index`/`seedId` immutability) are only applied to locally-initiated `update()`/`updateMany()` calls, not to data arriving from `#replaceAll`/`processOne` — i.e., not to the actual cross-device sync ingestion path: [4](#0-3) 

No size-limit enforcement (analogous to the 400KB check recommended in the report) exists anywhere in the fusion sync path; a repo-wide search for size-limit constants near fusion/profile sync code returned no matches in this module.

### Impact Explanation
Because remote Fusion data is trusted without schema validation, malformed or malicious sync payloads (e.g., from a compromised secondary device linked to the same account, a corrupted/replayed sync record, or a backend-side data integrity failure) can inject or overwrite `hardwareWalletPublicKeys` and wallet-account metadata (`index`, `compatibilityMode`, `isHardware`, `isCustodial`-influencing fields) directly into wallet state that later drives address derivation and account classification (`isDeletedHardwareWallet`, `isCustodialWallet`, `accountPicker` logic in `#updateFusion`). This creates a path toward corrupted address/account state being trusted by the wallet — a direct wallet-compromise class impact — without any client-side structural or size gate to reject it.

### Likelihood Explanation
Fusion sync is a standard, always-on feature of authenticated multi-device sync, so the ingestion path (`processOne`) is reached on every sync cycle for every user; no additional user interaction is required beyond having sync enabled. The absence of validation is a structural gap rather than a theoretical edge case, directly paralleling the original report's root cause (no runtime schema enforcement of profile-sync data).

### Recommendation
Add runtime schema validation (e.g., with Zod or a similar validator) at the `processOne`/`#replaceAll` boundary in `features/wallet-accounts/src/module/wallet-accounts.ts` before constructing `WalletAccount` instances or assigning `#hardwareWalletPublicKeys`, reject payloads that fail validation or exceed defined size limits, and log/handle validation errors gracefully instead of trusting the TypeScript-only `FusionData` contract.

### Proof of Concept
1. Enable Fusion sync on an account across two devices (or intercept/replay a sync channel write, depending on the actual transport trust boundary).
2. From the second device (or via a crafted sync payload), push a `walletAccounts` channel entry via the same `channel.push({ type: 'walletAccounts', data: {...} })` contract used in `#updateFusion`, but with a malformed `accounts` (hardware public keys) object or unexpected fields not conforming to the expected `WalletAccountsData`/`HardwareWalletPublicKeys` shape.
3. Observe that `processOne` in `features/wallet-accounts/src/module/wallet-accounts.ts:118-130` accepts the payload unconditionally and `#replaceAll` (lines 246-285) merges it into local state — constructing `WalletAccount` objects and replacing `hardwareWalletPublicKeys` — with no schema or size check rejecting the malformed data.

I could not verify from the available index whether `WalletAccount`'s constructor performs deeper field-level validation beyond the immutability `assert`s shown (the full `libraries/models/src/wallet-account/index.ts` content was not retrievable within the tool budget), so the exact downstream exploitability (e.g., whether corrupted `accounts`/xpub data can concretely redirect address derivation) should be confirmed via a Devin session with full file access before treating this as fully proven.

### Citations

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L45-77)
```typescript
const updateWalletAccount = (
  walletAccounts: Record<string, WalletAccount> = Object.create(null),
  walletAccount: string,
  newData: Record<string, unknown>
) => {
  const before = walletAccounts[walletAccount]

  if (!before) throw new Error(`${walletAccount} is not a known wallet account`)

  if (walletAccount === DEFAULT_WALLET_ACCOUNT.toString() && newData.enabled === false) {
    throw new Error("Can't disable default walletAccount")
  }

  const after = new WalletAccount({
    ...before,
    ...newData,
  })

  for (const key of ['source', 'id', 'index']) {
    assert(
      (before as unknown as Record<string, unknown>)[key] ===
        (after as unknown as Record<string, unknown>)[key],
      `cannot change account ${key}`
    )
  }

  assert(
    !before.seedId || before.seedId === after.seedId,
    'seedId can only be set if previously undefined'
  )

  return after
}
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L118-130)
```typescript
    this.#channel = fusion.channel({
      ...walletAccountsChannel,
      processOne: async ({ data }: { data: FusionData }) => {
        this.#rawFusionData = data

        if (this.#pendingFusionUpdates > 0) {
          this.#pendingFusionUpdates -= 1
          return
        }

        await this.#replaceAll(data)
      },
    })
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L246-285)
```typescript
  #replaceAll = makeConcurrent(
    async ({
      walletAccounts,
      accounts,
    }: {
      walletAccounts: Record<string, Record<string, unknown>>
      accounts?: HardwareWalletPublicKeys
    }) => {
      // This will replace all the locally stored hardware wallet public keys
      // with the ones provided by fusion without any attempt to merge inconsistent states.
      this.#hardwareWalletPublicKeys = accounts || createEmptyAccounts()

      await this.#loaded.promise
      const primarySeedId = await this.#wallet.getPrimarySeedId()

      const currentWalletAccounts = (await this.#getInternalWalletAccountsWithFallback()) as Record<
        string,
        WalletAccount
      >
      // Warning: the following code between reading from currentWalletAccounts and writing back to it
      // needs to remain sync until this.#save or may lead to concurrency issues. "await" yields execution
      // and may allow .update(), .create(), etc to execute before
      // fusion syncing is done.
      const afterByName = Object.entries(walletAccounts).reduce(
        (
          instances: Record<string, WalletAccount>,
          [name, fields]: [string, Record<string, unknown>]
        ) => {
          instances[name] = new WalletAccount({
            ...fields,
            ...(fields.source === EXODUS_SRC && {
              seedId: primarySeedId,
              compatibilityMode:
                currentWalletAccounts[WalletAccount.DEFAULT_NAME]?.compatibilityMode,
            }),
          } as WalletAccountParams)
          return instances
        },
        {} as Record<string, WalletAccount>
      )
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L642-656)
```typescript
interface Fusion {
  channel(config: {
    type: string
    channelName: string
    syncStateKey: string
    startFromLatest: boolean
    processOne: (event: { data: FusionData }) => Promise<void>
  }): FusionChannel
}

interface FusionData {
  walletAccounts?: Record<string, Record<string, unknown>>
  accounts?: HardwareWalletPublicKeys
  [key: string]: unknown
}
```
