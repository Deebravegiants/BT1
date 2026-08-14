### Title
Stale `connectedAccountsAtom` cache can serve incorrect wallet addresses to connected dApp origins due to an insufficient staleness check - (File: `features/connected-origins/module/connections.js`)

### Summary
`@exodus/connected-origins` caches wallet-account addresses in `connectedAccountsAtom` and serves them to connected/trusted dApp origins via `getConnectedAccounts`. The cache is refreshed only when `updateConnectedAccounts` detects a change, but that "is this cache stale?" check compares only the **set of wallet-account key names**, not the actual address values behind them. This is the same bug class as the Rio/EigenLayer report: a value is captured once and then reused across a trust boundary without re-validating that the underlying value hasn't diverged, and the dirtiness heuristic used to decide whether to recompute is too coarse to catch the divergence.

### Finding Description
`updateConnectedAccounts` is the only mechanism that refreshes the address cache after initial connection: [1](#0-0) 

It computes `xor(Object.keys(walletAccounts), Object.keys(connectedAccounts))` and treats the cache as "up-to-date" whenever the **key sets** match — i.e. whenever the set of wallet-account names (`exodus_0`, `exodus_1`, ...) is unchanged. It never compares the actual cached address values against what `addressProvider` would currently return for those same account names. This function is wired as the sole subscriber that reacts to account changes: [2](#0-1) 

Compounding this, when the cache *is* rebuilt, `#getWalletAccountAddresses` preferentially reuses the existing cached address instead of re-deriving it fresh: [3](#0-2) 

Finally, `getConnectedAccounts` — explicitly documented as usable "while the wallet is locked" (i.e., without requiring a fresh unlock/user-interaction re-check) — trusts this cache wholesale and hands the addresses straight to the calling origin: [4](#0-3) 

If the address that a given wallet-account name (`exodus_0`) resolves to ever changes while the name itself persists — for example after a wallet-account slot is repopulated by a different seed/import flow, or any other scenario where `addressProvider.getDefaultAddress` would now return a different address for the same account name — `xor()` on the key sets reports no difference, `updateConnectedAccounts` short-circuits and skips recomputation, and `#getWalletAccountAddresses` also refuses to re-derive because it finds an `existingAddress` already cached. The stale, no-longer-correct address then keeps being returned by `getConnectedAccounts` to the connected origin indefinitely, exactly as the Rio bug served a stale (pre-appreciation) EigenLayer-share value because the reconciliation check couldn't detect that the underlying quantity had moved while the identifying key (the account/epoch) stayed the same.

### Impact Explanation
A dApp origin that was previously trusted continues to receive wallet addresses from `getConnectedAccounts` that no longer reflect the wallet's actual current addresses for those account slots. Since these addresses are used by the connected dApp to route asset transfers/requests to the user, this is a cross-account address-disclosure/isolation bleed: funds or signing requests could be directed at an address that no longer represents the intended account, and stale address material for one account context leaks into a session tied to a different underlying account state. This crosses the account-isolation trust boundary that `connectedAccountsAtom`'s cache/access design is meant to protect (note its own comment that it exists specifically to serve address data "without a user interaction," i.e. with reduced scrutiny).

### Likelihood Explanation
This requires a concrete sequence where a wallet-account name is reused for a different underlying address (e.g., certain seed/account restore or multi-seed reconfiguration flows) without the key set changing, which I could not fully trace end-to-end within the available index (in particular, the exact conditions under which `addressProvider.getDefaultAddress({assetName, walletAccount})` would return a different value for the same `walletAccount` name were not verifiable here — `docs/development/multi-seed.md` likely documents this but wasn't inspected in full). The staleness-detection defect itself, however, is directly demonstrated in the code: the reconciliation logic in `updateConnectedAccounts` is provably keyed only on account-name-set membership, not on address value equality, so any code path that changes an account's resolved address while keeping its name is unprotected by design.

### Recommendation
Change `updateConnectedAccounts`'s staleness check to compare actual resolved addresses (or a version/generation counter bumped whenever an account's underlying key material changes), not just the set of account-name keys. Additionally, `#getWalletAccountAddresses` should not unconditionally prefer the cached `existingAddress`; it should re-derive from `addressProvider` whenever invoked to refresh, or invalidate cache entries tied to any account whose underlying seed/derivation changed.

### Proof of Concept
1. Trust an origin and call `connectedOrigins.add(...)`, which populates `connectedAccountsAtom` with `{ exodus_0: { addresses: { solana: <addrA> } } }` via `#setData` → `#getAccounts` (`features/connected-origins/module/connections.js:41-49`, `108-121`).
2. Cause the wallet-account slot `exodus_0` to resolve to a different address for `solana` (e.g., through a seed/account reconfiguration path that keeps the account name `exodus_0` in `enabledWalletAccountsAtom` but changes what `addressProvider.getDefaultAddress({assetName:'solana', walletAccount:'exodus_0'})` returns).
3. `enabledWalletAccountsAtom.observe(connectedOrigins.updateConnectedAccounts)` fires (`features/connected-origins/plugin/index.js:25`), but since `Object.keys(walletAccounts)` still equals `Object.keys(connectedAccounts)` (`exodus_0` didn't disappear or get added), `xor(...).length === 0` and the function returns early without refreshing (`connections.js:303-307`).
4. The origin calls `getConnectedAccounts({ origin })`; it still returns the old, stale `<addrA>` for `exodus_0` (`connections.js:249-273`), even though the wallet's real current address is now different.

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

**File:** features/connected-origins/module/connections.js (L245-273)
```javascript
  /**
   * Returns the connected accounts for a given origin with the active wallet account sorted first. Can be used while
   * the wallet is locked
   */
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

**File:** features/connected-origins/plugin/index.js (L23-26)
```javascript
  const onUnlock = async () => {
    connectedOriginsAtomObserver.start()
    unsubscribe = enabledWalletAccountsAtom.observe(connectedOrigins.updateConnectedAccounts)
  }
```
