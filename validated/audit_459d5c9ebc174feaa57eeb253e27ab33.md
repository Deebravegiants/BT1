### Title
`updateWalletAccount` fails to preserve `isMultisig`/`delegated` identity invariants, allowing silent account-type escalation via `update`/`updateMany` - ([File: features/wallet-accounts/src/module/wallet-accounts.ts])

### Summary
The module-level `updateWalletAccount` helper only guards `source`, `id`, `index`, and `seedId` as immutable when merging `newData` into an existing `WalletAccount`, but the `WalletAccount` model itself defines `isMultisig` and `delegated` as part of its `IMMUTABLE_PROPERTIES` list (enforced only in the model's own `.update()` method, which is bypassed here). Because `updateWalletAccount` constructs a fresh `WalletAccount` directly via `new WalletAccount({...before, ...newData})` instead of calling `before.update(newData)`, an attacker-controlled `newData` payload can silently flip `isMultisig` or `delegated` on an existing account. `isCustodial`/`isHardware`, by contrast, are pure getters derived from the immutable `source` field, so they cannot be spoofed this way — the question's premise about those two flags is not exploitable.

### Finding Description
`updateWalletAccount` in `features/wallet-accounts/src/module/wallet-accounts.ts` (lines 45-77) merges `newData` on top of the existing account and only asserts immutability for `source`, `id`, and `index`, plus a special-case check for `seedId`: [1](#0-0) 

Compare this to `libraries/models/src/wallet-account/index.ts`, which defines the account's own set of immutable properties as `['id', 'source', 'index', 'isMultisig', 'delegated']` and enforces them inside `WalletAccount.prototype.update()`: [2](#0-1) [3](#0-2) 

`updateWalletAccount` does not call `.update()`; it directly constructs a new instance with `new WalletAccount({...before, ...newData})`, which happily accepts `isMultisig` and `delegated` as ordinary constructor params (`WalletAccountParams`) and assigns them without any equality check against the prior value: [4](#0-3) [5](#0-4) 

This means calling `walletAccounts.update(name, { isMultisig: true })` or `{ delegated: true }` (reachable via `update`/`updateMany`, exposed publicly through `walletAccountsApi`) will silently change these fields for an already-existing account, even though the model's own design intends them to be fixed at creation time. [6](#0-5) [7](#0-6) 

Regarding the specific fields named in the question: `isCustodial` and `isHardware` are computed getters derived solely from `source`, not stored/settable fields, and `source` is protected by the explicit immutability assert in `updateWalletAccount`: [8](#0-7) 
Therefore they cannot be flipped via `newData`, and prototype-pollution-style keys (`__proto__`, `constructor`) are also inert here because object spread (`{...before, ...newData}`) copies them as ordinary own properties, and the `WalletAccount` constructor only destructures a fixed, known set of parameter names — unknown keys are silently dropped.

### Impact Explanation
The `isMultisig`/`delegated` bypass is a real violation of the documented identity-immutability invariant (`IMMUTABLE_PROPERTIES` in the model), but its downstream security impact could not be fully confirmed within this investigation — `isMultisig`/`delegated` usages appear in `features/asset-sources/*` and `features/address-provider/utils/addresses.js` related to available asset names and address derivation, but tracing whether flipping these post-creation can cause wrong-address generation, wrong-account signing, or asset-source mismatches requires deeper review of those consumers than was available. This is narrower and lower severity than the question's hypothesized "flip `isCustodial`/hardware flags" scenario, which is not achievable.

### Likelihood Explanation
`update`/`updateMany` are exposed as public module methods and re-exported through `walletAccountsApi` (`create`, `update`, `disable`, etc.), so any caller with access to that API surface (e.g. via RPC/SDK) can invoke `update(name, { isMultisig: true })` today with no additional check preventing it. Whether such API access requires wallet-unlock/authentication is outside what this file review confirms.

### Recommendation
In `updateWalletAccount`, extend the immutability check to cover all fields listed in `WalletAccount`'s own `IMMUTABLE_PROPERTIES` (`id`, `source`, `index`, `isMultisig`, `delegated`), or better, have `updateWalletAccount` call `before.update(newData)` instead of directly constructing `new WalletAccount({...before, ...newData})`, so the model's single source of truth for immutable fields is always enforced.

### Proof of Concept
```ts
// features/wallet-accounts/src/module/__tests__/index.test.ts (extension)
it('does not allow isMultisig/delegated to be changed via update', async () => {
  const { walletAccounts } = await prepare({
    walletAccounts: { exodus_0: { ...stored.exodus_0, isMultisig: false, delegated: false } },
  })

  await expect(
    walletAccounts.update('exodus_0', { isMultisig: true })
  ).rejects.toThrow(/immutable|cannot change/i)

  await expect(
    walletAccounts.update('exodus_0', { delegated: true })
  ).rejects.toThrow(/immutable|cannot change/i)
})
```
Expected (currently failing) assertion: both calls should throw, matching the behavior enforced by `WalletAccount.prototype.update()`'s `IMMUTABLE_PROPERTIES` check, but currently they succeed silently and mutate the stored account.

### Citations

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L58-74)
```typescript
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
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L329-341)
```typescript
  update = async (name: string, data: Record<string, unknown>) => {
    await this.updateMany({ [name]: data })
  }

  updateMany = async (dataByName: Record<string, Record<string, unknown>>) => {
    const currentWalletAccounts = await this.#getInternalWalletAccountsWithFallback()
    const updated = Object.entries(dataByName).map(([name, data]) => {
      const walletAccount = updateWalletAccount(currentWalletAccounts, name, data)
      return [walletAccount.toString(), walletAccount]
    })

    await this.#persistWalletAccounts(Object.fromEntries(updated))
  }
```

**File:** libraries/models/src/wallet-account/index.ts (L81-81)
```typescript
const IMMUTABLE_PROPERTIES = ['id', 'source', 'index', 'isMultisig', 'delegated']
```

**File:** libraries/models/src/wallet-account/index.ts (L83-98)
```typescript
export type WalletAccountParams = {
  source: WalletAccountSource
  index?: number | null
  id?: string | number
  label?: string
  model?: string
  lastConnected?: number
  is2FA?: boolean
  color?: string
  icon?: string
  enabled?: boolean
  seedId?: string
  compatibilityMode?: string
  isMultisig?: boolean
  delegated?: boolean
}
```

**File:** libraries/models/src/wallet-account/index.ts (L184-197)
```typescript
    this.source = source
    this.index = isNil(index) ? null : index
    this.id = id
    this.seedId = seedId
    this.label = label || ''
    this.model = model
    this.lastConnected = lastConnected
    this.is2FA = is2FA
    this.color = color
    this.icon = icon
    this.enabled = enabled
    this.compatibilityMode = compatibilityMode ?? (this.isHardware ? this.source : undefined)
    this.isMultisig = isMultisig
    this.delegated = delegated
```

**File:** libraries/models/src/wallet-account/index.ts (L267-283)
```typescript
  update(data: Partial<WalletAccount | WalletAccountParams>) {
    const fields: Record<string, any> = data instanceof WalletAccount ? data.toJSON() : data
    const current: Record<string, any> = this.toJSON()

    const isNoop = Object.keys(fields).every((field) => isEqual(current[field], fields[field]))
    if (isNoop) {
      return this
    }

    IMMUTABLE_PROPERTIES.forEach((immutable) => {
      if (fields[immutable] && fields[immutable] !== this[immutable as keyof WalletAccount]) {
        throw new Error(`property "${immutable}" is immutable`)
      }
    })

    return new WalletAccount(merge(Object.create(null), current, fields) as WalletAccountParams)
  }
```

**File:** libraries/models/src/wallet-account/index.ts (L285-295)
```typescript
  get isSoftware() {
    return SOFTWARE_SEED_SOURCES.includes(this.source)
  }

  get isHardware() {
    return HARDWARE_SOURCES.includes(this.source)
  }

  get isCustodial() {
    return CUSTODIAL_SOURCES.includes(this.source)
  }
```

**File:** features/wallet-accounts/src/api/index.ts (L10-21)
```typescript
  walletAccounts: {
    create: walletAccounts.create,
    update: walletAccounts.update,
    disable: walletAccounts.disable,
    disableMany: walletAccounts.disableMany,
    removeMany: walletAccounts.removeMany,
    enable: walletAccounts.enable,
    getEnabled: enabledWalletAccountsAtom.get,
    getActive: walletAccounts.getActive,
    setActive: walletAccounts.setActive,
    setMultipleEnabled: (value: boolean) => multipleWalletAccountsEnabledAtom.set(value),
  },
```
