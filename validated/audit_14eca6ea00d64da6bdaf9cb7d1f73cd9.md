Confirmed: this is critical. `WalletAccount.toString()` for `exodus`-source accounts deliberately **excludes** `seedId` (test `toString() for "exodus" account does not include seedId"` proves `new WalletAccount({ source: EXODUS_SRC, seedId: 'A', index: 0 }).toString()` → `'exodus_0'`, same key regardless of seed). [1](#0-0) [2](#0-1) 

This directly enables the stale-cache scenario in `updateConnectedAccounts`, whose only invalidation trigger is a **key-set** diff (`xor(Object.keys(walletAccounts), Object.keys(connectedAccounts))`), not a content/seed diff: [3](#0-2) 

### Title
Stale cross-seed address/xpub disclosure via key-collision in `connectedAccountsAtom` cache invalidation - (File: features/connected-origins/module/connections.js, features/connected-origins/atoms/connected-accounts.js)

### Summary
`createConnectedAccountsAtom` is a bare, un-namespaced key/value cache keyed by `walletAccount.toString()`. Because `WalletAccount.toString()` deliberately omits `seedId` for `exodus`-source accounts, rotating/replacing the primary seed while keeping the same account index (e.g. `exodus_0`) produces an identical cache key. `updateConnectedAccounts` only refreshes the cache when the *set of account-name keys* changes (`xor` of keys), so a seed rotation that keeps the same account names is treated as "up-to-date" and the stale addresses/xpubs from the previous seed remain served to connected dapps via `getConnectedAccounts` / `#getWalletAccountAddresses`.

### Finding Description
`connected-accounts.js` simply wraps `createStorageAtomFactory` with `dedupe`; it has no notion of seed identity, only stores `{ [walletAccountName]: { addresses: {...} } }`. [4](#0-3) 

`#getWalletAccountAddresses` in `connections.js` treats any existing entry in the cache as authoritative and reuses it without checking whether the underlying seed for that account name has changed: [5](#0-4) 

`updateConnectedAccounts` — the only refresh path wired to `enabledWalletAccountsAtom.observe(...)` on unlock — decides "up to date" purely from the `xor` of account-name keys: [6](#0-5) [3](#0-2) 

Because `WalletAccount.toString()` for `EXODUS_SRC` intentionally strips `seedId`, when a user replaces/rotates their primary seed (restore from a different mnemonic re-using account index 0, or a multi-seed migration such as `multi-seed-wallet-accounts.ts` which rewrites `seedId` on existing entries while index/source/name stay the same), the key set `{exodus_0, exodus_1, ...}` is unchanged. `updateConnectedAccounts` therefore performs a no-op, and `getConnectedAccounts({ origin })` continues returning addresses derived from the *old* seed under the same account name to any already-trusted/auto-approved connected origin. [7](#0-6) 

The only place the cache is fully wiped is the generic `clear()` call from `onClear`, which is not guaranteed to be triggered on every seed-rotation/restore code path that keeps the wallet-account name identical; `untrust()` only removes the origin, it doesn't invalidate the shared `connectedAccountsAtom` cache for accounts still referenced by other trusted origins. [8](#0-7) [9](#0-8) 

### Impact Explanation
A connected/auto-approved dapp origin can receive an address/xpub belonging to a wallet-account entry that was actually derived under a previous seed, rather than the currently active one — a wrong-account/stale-key disclosure that violates the seed-rotation invalidation invariant. This matches the "Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction" bounty class, since the leaked/cross-seed address ends up served into the dapp's session state and local storage keyed by the connected wallet account, without the user re-approving after rotating the seed.

### Likelihood Explanation
Preconditions: user has previously trusted/auto-approved an origin (one click of interaction) with account name `exodus_0`, then performs a seed rotation/restore that reuses the same account index/name (a realistic, documented flow given `multi-seed-wallet-accounts.ts` migration and `WalletAccount.toString()`'s intentional seedId omission for exodus accounts). No privileged access or leaked keys needed — it only requires ordinary use of restore/seed-change functionality plus a previously-approved dapp connection. This is reliably reproducible because the invalidation logic is purely a key-set diff.

### Recommendation
Include `seedId` (and any other identity-affecting fields) in the cache-invalidation comparison for `connectedAccountsAtom`, not just account-name key membership — e.g., compare full serialized wallet-account content (or at minimum `seedId`) between `enabledWalletAccountsAtom` and the cached entries in `updateConnectedAccounts`, and force a full `connectedAccountsAtom` refresh whenever any account's `seedId`/derivation-affecting fields change, in addition to on `clear()`.

### Proof of Concept
Integration test extending `features/connected-origins/module/__tests__/connections.test.js`:
1. Seed A: create `enabledWalletAccountsAtom` with `exodus_0` under seed A; add a trusted origin for `solana`; assert `connectedAccountsAtom.get()` caches seed-A-derived address for `exodus_0`.
2. Simulate seed rotation: replace the underlying `addressProvider`/`publicKeyProvider` keychain with seed B, and update `enabledWalletAccountsAtom` value for `exodus_0` to a `WalletAccount` instance whose `seedId` is seed B but same `toString()` (`exodus_0`) — i.e., set the *same key* with different content, keeping `Object.keys` unchanged.
3. Call `connectedOrigins.updateConnectedAccounts()`.
4. Assert (expected failure demonstrating the bug): `connectedAccountsAtom.get()` still returns the seed-A address for `exodus_0` instead of refreshing to the seed-B address, and `connectedOrigins.getConnectedAccounts({ origin: 'exodus.com' })` returns the stale seed-A address to the dapp.

### Citations

**File:** libraries/models/src/wallet-account/index.ts (L217-225)
```typescript
  toString() {
    return [
      this.source,
      this.index,
      ...(this.source === SEED_SRC ? [this.seedId, this.compatibilityMode] : [this.id]),
    ]
      .filter((v) => v != null)
      .join('_')
  }
```

**File:** libraries/models/src/wallet-account/__tests__/index.test.ts (L286-290)
```typescript
test('toString() for "exodus" account does not include seedId', () => {
  expect(new WalletAccount({ source: EXODUS_SRC, seedId: 'A', index: 0 }).toString()).toBe(
    'exodus_0'
  )
})
```

**File:** features/connected-origins/module/connections.js (L71-74)
```javascript
  clear = async () => {
    await this.#connectedOriginsAtom.set(undefined)
    await this.#connectedAccountsAtom.set(undefined)
  }
```

**File:** features/connected-origins/module/connections.js (L123-138)
```javascript
  #getWalletAccountAddresses = async (walletAccount, assetNames) => {
    const connectedAccounts = await this.#connectedAccountsAtom.get()
    const entries = await Promise.all(
      assetNames.map(async (assetName) => {
        const existingAddress = connectedAccounts[walletAccount]?.addresses[assetName]
        if (existingAddress) {
          return [assetName, existingAddress]
        }

        const address = await this.#addressProvider.getDefaultAddress({ assetName, walletAccount })
        return [assetName, address.toString()]
      })
    )

    return Object.fromEntries(entries)
  }
```

**File:** features/connected-origins/module/connections.js (L187-196)
```javascript
  untrust = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })

    if (!isTrusted) return

    const data = await this.#getData()
    const newData = data.filter((connection) => connection.origin !== origin)

    await this.#setData(newData)
  }
```

**File:** features/connected-origins/module/connections.js (L249-273)
```javascript
  getConnectedAccounts = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })
    if (!isTrusted) return []

    const value = await this.#getOrigin({ origin })
    const assetNames = [value.connectedAssetName, ...(value.assetNames ?? [])].filter(
      (name, index, ary) => Boolean(name) && ary.indexOf(name) === index
    )

    const activeWalletAccount = await this.#activeWalletAccountAtom.get()
    const accounts = await this.#connectedAccountsAtom.get()

    const connectedAccounts = []
    for (const name of Object.keys(accounts)) {
      if (name === activeWalletAccount) continue
      connectedAccounts.push({ name, addresses: pick(accounts[name].addresses, assetNames) })
    }

    connectedAccounts.unshift({
      name: activeWalletAccount,
      addresses: pick(accounts[activeWalletAccount].addresses, assetNames),
    })

    return connectedAccounts
  }
```

**File:** features/connected-origins/module/connections.js (L299-314)
```javascript
  updateConnectedAccounts = async () => {
    const walletAccounts = await this.#enabledWalletAccountsAtom.get()
    const connectedAccounts = await this.#connectedAccountsAtom.get()

    const difference = xor(Object.keys(walletAccounts), Object.keys(connectedAccounts))
    if (difference.length === 0) {
      // up-to-date
      return
    }

    const connectedOrigins = await this.#connectedOriginsAtom.get()
    const assetNames = this.#getConnectedAssets(connectedOrigins)
    const updatedAccounts = await this.#getAccounts(assetNames)

    await this.#connectedAccountsAtom.set(updatedAccounts)
  }
```

**File:** features/connected-origins/atoms/connected-accounts.js (L1-16)
```javascript
import { createStorageAtomFactory, dedupe } from '@exodus/atoms'

/**
 * This atom caches addresses of connected accounts so they can be used when eagerly connecting without a user interaction.
 * We cannot use address provider in that case because the wallet may not be unlocked. This atom however sits on top of
 * the unsafe storage.
 */
export default function createConnectedAccountsAtom({ storage }) {
  return dedupe(
    createStorageAtomFactory({ storage })({
      key: 'accounts',
      defaultValue: {},
      isSoleWriter: true,
    })
  )
}
```

**File:** features/connected-origins/plugin/index.js (L23-25)
```javascript
  const onUnlock = async () => {
    connectedOriginsAtomObserver.start()
    unsubscribe = enabledWalletAccountsAtom.observe(connectedOrigins.updateConnectedAccounts)
```
