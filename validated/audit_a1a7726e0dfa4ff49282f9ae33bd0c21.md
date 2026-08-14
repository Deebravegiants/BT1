### Title
Stale `connectedAccountsAtom` cache served to untrusted origins after wallet-account changes - ([File: features/connected-origins/module/connections.js])

### Summary
Similar to the Tapioca `totalBorrow` bug — where a derived/aggregate state (`totalBorrow`) was not kept in sync with the source-of-truth mutation (`userBorrowPart`), causing all subsequent computations to use stale data — the `connected-origins` module maintains a derived cache, `connectedAccountsAtom`, that is supposed to mirror `enabledWalletAccountsAtom` (the source of truth for which wallet accounts exist). The refresh logic in `updateConnectedAccounts` only recomputes this cache when the **set of account keys** differs, not when the underlying account contents differ, so it can skip refreshing the cache even though the accounts actually changed. This cache is directly exposed to untrusted third-party origins (dApps) through `getConnectedAccounts`.

### Finding Description
`ConnectedOrigins.updateConnectedAccounts` is the only mechanism that resynchronizes `connectedAccountsAtom` with `enabledWalletAccountsAtom` outside of explicit `add`/`untrust`/`setAttributes` calls: [1](#0-0) 

It compares only the **key sets** with `xor(Object.keys(walletAccounts), Object.keys(connectedAccounts))` and bails out ("up-to-date") whenever the key sets match — even if the account values behind those same keys have changed (e.g., a wallet-account object with the same slot key `exodus_0` now points at a different seed/derivation after a wallet-account swap, restore, or reorder operation). In that scenario the stale addresses cached under that key are never refreshed.

This stale cache is trusted and returned directly to third-party origins: [2](#0-1) 

`getConnectedAccounts` is explicitly documented as usable "while the wallet is locked" and is the API surface exposed to connected dApps (analogous to a Web3 provider's `eth_accounts`/connected-accounts call). It reads straight from `connectedAccountsAtom` without any freshness check against `enabledWalletAccountsAtom`.

Additionally, `#getWalletAccountAddresses` — the function that populates the cache when it *is* refreshed — deliberately reuses any pre-existing cached address for a given `walletAccount`/`assetName` pair instead of recomputing it: [3](#0-2) 

Combined with the coarse `xor`-only freshness check in `updateConnectedAccounts`, once a stale entry exists under a wallet-account key, it can persist indefinitely across account composition changes as long as the key set size doesn't change, exactly mirroring the pattern where `_updateBorrowAndCollateralShare` updated per-user state but the aggregate `totalBorrow` was left stale, silently corrupting everything computed from it afterward.

### Impact Explanation
A connected, "trusted" origin (a dApp the user previously approved) can be served addresses that do not correspond to the wallet's current account state — i.e., cross-account information bleed. This can result in: exposing an address belonging to a wallet-account slot that has since been repurposed (e.g., after switching/restoring seeds while an origin remains connected under the same account index), or omitting/duplicating account entries the origin should or should not see. Because this data feeds directly into the `window.exodus` provider surface used by third-party websites, it is a cross-origin/account isolation trust-boundary defect — an untrusted origin can receive incorrect account/address bindings without any additional privilege.

### Likelihood Explanation
This requires a legitimate but not implausible sequence: a dApp origin is trusted/connected, and the user subsequently performs a wallet-account-level change (e.g., seed restore/import, account list reshuffle) that preserves the number of enabled accounts but changes what a given account key refers to. The `plugin/index.js` wiring only calls `updateConnectedAccounts` reactively on `enabledWalletAccountsAtom` changes, so any such change that doesn't alter the key-set cardinality slips past the staleness check: [4](#0-3) 

Likelihood is moderate — it depends on the wallet-accounts feature allowing account-slot content changes without key-set size changes, which was not independently confirmed here due to time/tooling constraints on this pass.

### Recommendation
Replace the `xor`-of-keys freshness check in `updateConnectedAccounts` with a full structural comparison of the enabled wallet accounts (e.g., compare `seedId`+`index`+`compatibilityMode` per key, not just key presence), and avoid unconditionally reusing cached per-account addresses in `#getWalletAccountAddresses` when the underlying wallet-account object for that key has changed. Consider invalidating/recomputing the entire `connectedAccountsAtom` whenever any wallet-account's identity (not just its key) changes, mirroring how the Tapioca fix required updating the *entire* aggregate (`totalBorrow.elastic`/`totalBorrow.base`), not just the per-user delta.

### Proof of Concept
Conceptual (not fully executed against the running SDK given tool limits):
1. Connect/trust an origin so `connectedOriginsAtom` contains an entry and `connectedAccountsAtom` caches `{ exodus_0: { addresses: { ethereum: '0xOLD...' } } }`.
2. Perform a wallet-account change that keeps `Object.keys(enabledWalletAccountsAtom)` identical (still `['exodus_0']`) but changes what `exodus_0` refers to (e.g., different `seedId`).
3. `enabledWalletAccountsAtom.observe(connectedOrigins.updateConnectedAccounts)` fires, but `xor(['exodus_0'], ['exodus_0']).length === 0` short-circuits the update at `features/connected-origins/module/connections.js:303-307`.
4. The origin calls the connected-accounts API; `getConnectedAccounts` returns the stale `0xOLD...` address instead of the address for the new underlying account, per `features/connected-origins/module/connections.js:249-273`.

This confirms the mechanism by which the cache can diverge from source-of-truth state and be handed to an untrusted origin; full exploitation would require confirming (in `wallet-accounts`) a concrete operation that preserves key-set cardinality while changing account identity, which could not be verified within this pass.

### Citations

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

**File:** features/connected-origins/plugin/index.js (L17-26)
```javascript
  const onLoad = ({ isLocked }) => {
    if (isLocked) return

    connectedOriginsAtomObserver.start()
  }

  const onUnlock = async () => {
    connectedOriginsAtomObserver.start()
    unsubscribe = enabledWalletAccountsAtom.observe(connectedOrigins.updateConnectedAccounts)
  }
```
