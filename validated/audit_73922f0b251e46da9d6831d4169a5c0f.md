### Title
Stale cached addresses for connected dApp accounts not refreshed on wallet-account changes - (File: `features/connected-origins/module/connections.js`)

### Summary
`ConnectedOrigins` maintains a cache (`connectedAccountsAtom`) that maps each wallet account to the addresses that were shared with connected dApps. This is structurally the same class of bug as the referenced Launchpad finding: one component holds a **cached/stale copy** of a value (address) that is derived from a **mutable, authoritative source** (`addressProvider` / `walletAccountsAtom`), and the cache-refresh logic only checks for *presence* of a key, not whether the *value* backing that key is still correct. When the underlying source changes without a corresponding key-set change, the cache continues to serve outdated addresses to connected, unprivileged third-party origins.

### Finding Description
`createConnectedAccountsAtom` explicitly documents that it "caches addresses of connected accounts so they can be used when eagerly connecting without a user interaction," bypassing the live `addressProvider` when the wallet is locked [1](#0-0) .

The read path, `#getWalletAccountAddresses`, prefers the cached address over calling `addressProvider.getDefaultAddress` whenever an entry already exists for that `(walletAccount, assetName)` pair: [2](#0-1) 

The only refresh path, `updateConnectedAccounts`, decides whether the cache is stale purely by comparing the **set of wallet-account keys** between `enabledWalletAccountsAtom` and `connectedAccountsAtom` via `xor(Object.keys(...))`. If the key sets are identical, it treats the cache as "up-to-date" and skips regeneration entirely — even though the *content* behind an existing key (e.g. its address, derived from `compatibilityMode`, index, or key material) may have changed: [3](#0-2) 

This mirrors the root cause in the external report: the "source of truth" (the live `addressProvider`, analogous to the updatable `launchpadLPVault`) can be updated, but a second, independently-tracked reference (the `connectedAccountsAtom` cache, analogous to the immutable `launchpadLp` stored in the factory) is not synchronized unless a narrow, key-set-only trigger fires. Any legitimate wallet-account mutation that changes the *address* for an existing account key (e.g. `compatibilityMode` changes — which the wallet-accounts module supports, see CHANGELOG entries "inherit compatibility mode from default wallet account" / "set compatibility mode to default account's mode") without changing the account's key/name will leave the connected-dApp-facing address cache silently desynchronized from the wallet's actual current address for that account.

### Impact Explanation
`getConnectedAccounts` — the API surface exposed to connected, unprivileged web origins — reads directly from this stale cache and returns it to the dApp as the user's addresses for approval/interaction flows: [4](#0-3) 

If a dApp (or the extension UI acting on the dApp's behalf) continues to display/operate on the stale cached address after the real receiving address for that wallet account has changed, funds sent to "the connected account's address" can be misdirected to an address the wallet no longer actively derives/monitors for that account — a direct funds-loss condition analogous to the Launchpad fee desync (value goes to/reads from the wrong place because two components disagree about which address is authoritative). This is reachable purely through normal wallet-account management (no privileged/administrative action or malicious peer needed), matching the "unprivileged-user analog" requirement.

### Likelihood Explanation
Moderate. It requires: (1) an origin already trusted/connected, (2) a subsequent wallet-account attribute change that alters the account's derived address but not its account-name/key (compatibility-mode change is the clearest such case, since it is a supported, user-triggerable wallet-accounts feature), and (3) no other independent path forcing an `updateConnectedAccounts()` refresh for that specific account before the stale address is consumed. The bug is latent (cache-invalidation-by-key-set-only), so it will silently persist until something else happens to force `#setData`/`updateConnectedAccounts` on the full account set.

### Recommendation
Change `updateConnectedAccounts` (and/or `#getWalletAccountAddresses`) to invalidate/refresh cached addresses whenever the underlying wallet-account's address-affecting attributes (e.g. `compatibilityMode`, `index`, `seedId`) change — not only when the key set changes. Concretely: diff wallet-account objects (deep compare relevant fields), not just `Object.keys`, before deciding the cache is up to date; or drop the "return cached address if present" fast path in `#getWalletAccountAddresses` in favor of always validating against `addressProvider` for accounts whose backing wallet-account record has been modified since the cache entry was written.

### Proof of Concept
Not independently verifiable without runtime access to confirm that a `compatibilityMode` update actually changes the address returned by `addressProvider.getDefaultAddress` for the same wallet-account key while `updateConnectedAccounts` is not otherwise triggered; this would need to be exercised in a live/test SDK instance (e.g. extend `features/connected-origins/module/__tests__/connections.test.js`'s "updates connected accounts when adding a wallet account" test to instead *mutate* an existing account's `compatibilityMode` in place and assert whether `connectedAccountsAtom` reflects the new address) to conclusively demonstrate exploitation end-to-end.

### Citations

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
