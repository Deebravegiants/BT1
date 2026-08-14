### Title
Stale/lazily-refreshed `connectedAccountsAtom` cache can desynchronize from actual wallet-account addresses, causing connected dApp origins to receive incorrect account address bindings - ([File: features/connected-origins/module/connections.js])

### Summary
The Cabal report describes an internal accounting variable (`m_store.staked_amounts`) that is updated by simply adding deltas without ever re-syncing against the ground-truth state (`get_real_total_stakes`), causing a growing desync that corrupts an exchange-rate-sensitive calculation. The closest analog in this codebase is the `ConnectedOrigins` module's `connectedAccountsAtom` cache, which is populated incrementally (reusing previously cached addresses instead of re-deriving/verifying them) and is only refreshed via an incomplete drift-detection heuristic (`updateConnectedAccounts`), rather than always being resynced against the authoritative account/address state before being served to a connected origin.

### Finding Description
`ConnectedOrigins#getConnectedAccounts` is the unprivileged, origin-facing entry point that returns wallet addresses to a connected dApp for a given origin: [1](#0-0) 

It reads directly from `this.#connectedAccountsAtom`, a cache object keyed by wallet-account name, without querying the authoritative address source (`addressProvider`) at read time.

This cache is built by `#getAccounts` / `#getWalletAccountAddresses`, which explicitly prefers whatever is *already* in `connectedAccountsAtom` over freshly deriving the address, only falling back to `addressProvider.getDefaultAddress` when no cached value exists: [2](#0-1) 

The cache is only rebuilt in two places: (1) `#setData`, triggered on origin-list mutations (add/untrust/setAttributes/etc.), and (2) `updateConnectedAccounts`, which is gated by an `xor` of the *account-name key sets* between `enabledWalletAccountsAtom` and `connectedAccountsAtom` — i.e. it only detects when accounts were added/removed, not when the underlying addresses for existing accounts changed (e.g., due to address rotation, re-derivation, or `assetNames` changing without an origin mutation): [3](#0-2) 

Because the reconciliation logic only compares account-name sets and never re-verifies address correctness against `addressProvider`, the accounting for "what address belongs to this wallet account" can silently drift out of sync with the real, authoritative address state — the same root-cause pattern as the Cabal bug: a monotonically-updated internal cache that is trusted without being reconciled against ground truth before being used in a security/trust-boundary-relevant computation.

### Impact Explanation
If `connectedAccountsAtom` diverges from the true current address for a wallet account (stale cache entry persists because the account-key-set comparison shows no difference), a connected origin calling `getConnectedAccounts` receives a stale address bound to the wrong/outdated key material for that account name. Since dApps rely on this API to determine which address to request signatures for or display as "connected," this cross-account/address desynchronization can misdirect the origin/trust boundary — the origin may be shown or act upon an address that no longer corresponds to the account's actual current derivation, undermining the account-isolation guarantee this module is meant to enforce.

### Likelihood Explanation
This requires a state transition where an account's address changes without a change in the set of account-name keys (e.g., address-index rotation or asset-name expansion for the same accounts), which is a normal, reachable operational path rather than a privileged/malicious-operator scenario. However, I could not fully verify from available context how frequently `#getWalletAccountAddresses`'s cache-reuse branch is actually exercised versus overwritten by `#setData` in practice, nor could I confirm all call sites of `updateConnectedAccounts` (e.g. in `features/connected-origins/plugin/index.js`, whose content I was unable to fully inspect) to determine how promptly it runs relative to account-state changes. This uncertainty tempers confidence in the exact trigger conditions.

### Recommendation
Do not trust the cached `connectedAccountsAtom` entries opportunistically. On every read via `getConnectedAccounts` (or at minimum in `#getWalletAccountAddresses`), re-derive/verify the address from `addressProvider` for the requested asset/account pair, or perform a value-level diff (not just key-set diff) between `enabledWalletAccountsAtom`-derived addresses and the cache in `updateConnectedAccounts`, refreshing whenever any address value differs from source of truth, not only when account keys are added/removed.

### Proof of Concept
Conceptual trace (not exploit code, since this requires internal account-rotation timing that I could not fully confirm via static review):
1. Origin `X` connects and is granted `assetNames: ['ethereum']`; `connectedAccountsAtom` caches `{ accountA: { addresses: { ethereum: addr1 } } }` via `#getAccounts`.
2. Account `accountA`'s ethereum address is rotated/re-derived internally (same account name key, new address) — `enabledWalletAccountsAtom` key set is unchanged, so `updateConnectedAccounts`'s `xor` check reports "up-to-date" and skips refresh: [4](#0-3) 
3. Origin `X` calls `getConnectedAccounts({ origin: 'X' })`; the response still contains the stale `addr1` for `accountA` instead of the new address, because `#getWalletAccountAddresses` prefers the cached value: [5](#0-4) 

This mirrors the Cabal root cause exactly: an internal cache is advanced/maintained by incremental heuristics instead of being reconciled against the authoritative source before being relied upon by an external, unprivileged consumer.

### Citations

**File:** features/connected-origins/module/connections.js (L108-138)
```javascript
  #getAccounts = async (assetNames) => {
    const walletAccounts = Object.values(await this.#enabledWalletAccountsAtom.get())

    const entries = await Promise.all(
      walletAccounts.map(async (walletAccount) => [
        walletAccount.toString(),
        {
          addresses: await this.#getWalletAccountAddresses(walletAccount, assetNames),
        },
      ])
    )

    return Object.fromEntries(entries)
  }

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
