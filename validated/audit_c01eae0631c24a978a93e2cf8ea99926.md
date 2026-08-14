### Title
Connected-Origin Asset Scope Silently Grows on Repeated `add()` Calls, Expanding a dApp's Address Exposure Without Fresh User Consent - ([File: features/connected-origins/module/connections.js])

### Summary
The `add()` method in the `ConnectedOrigins` module unions new `assetNames` with the origin's previously stored `assetNames` instead of replacing/re-approving the list, so the scope of wallet accounts/addresses exposed to a connected origin can only ever grow, never shrink, across repeated connection requests — the same "monotonically growing entitlement" bug class as the xToken `approve()` issue where the approved amount could only grow due to rebasing.

### Finding Description
When a dApp/origin is added or re-added via `connectedOrigins.add()`, the code computes the new asset scope as a union of the incoming asset names and whatever was already stored, rather than treating each `add()` call as a fresh, explicit grant: [1](#0-0) 

Specifically: [2](#0-1) 

`allConnectedAssetNames` is built as `new Set([connectedAssetName, ...assetNames, ...(value?.assetNames ?? [])])` — the existing `value.assetNames` is always merged in, never dropped. This means that once a user approves origin `X` for asset `A` (e.g., Solana), a later `add()` call — which may be triggered automatically by the dApp requesting a *different* asset connection (e.g., Ethereum) — silently expands the origin's `assetNames` to `[A, B]` rather than requiring a new, isolated consent flow scoped to `B` only, or replacing the prior grant.

This scope is then used directly to compute which addresses are exposed to the origin via `getConnectedAccounts`: [3](#0-2) 

`getConnectedAccounts` reads `value.assetNames` (the ever-growing set) and returns `addresses` for every wallet account across all of those assets — for every enabled wallet account, not just the one the user actively approved. There is no `remove`/`shrink` counterpart to `add`; `untrust` is all-or-nothing (drops the whole origin), and there is no per-asset revocation. Thus the "approved" surface area strictly increases over time and across enabled wallet accounts, analogous to how xToken's un-overridden `approve()` let the effective spend allowance grow via rebasing instead of being fixed at the value the user intended when calling `approve`.

### Impact Explanation
An origin that a user trusts for a narrow purpose (e.g., "connect for Solana only") can end up with standing access to addresses across additional assets and additional wallet accounts it never received explicit approval for in an isolated grant, because each subsequent internal `add()` call folds the new scope into the old one rather than replacing it. Since `getConnectedAccounts` is usable "while the wallet is locked" per its docstring, and returns `addresses` for all wallet accounts (not the one initially approved) once `assetNames` includes an asset, this expands the address-disclosure surface for a connected origin beyond what the user consented to at any single approval step. This is a privilege-bleed within the trust/authorization boundary between the wallet and web3-connected origins.

### Likelihood Explanation
Requires: (1) an origin already trusted/connected for some asset, and (2) that origin (or wallet-internal logic) subsequently calling `add()` again with a different `connectedAssetName`/`assetNames` set — e.g., a multi-chain dApp that first requests Solana, then later requests Ethereum from the same origin. This is a plausible, unprivileged, wallet-external interaction path (any web3-connected site), not a mocked-only or malicious-node scenario, but it does depend on the specific sequence of connection requests a dApp issues, similar to how the original finding required "external assumptions" (a party issuing repeated/legitimate-looking approve calls) — hence comparable to the medium severity assigned to the original issue.

### Recommendation
Do not silently union `assetNames` across `add()` calls. Each new asset-scope request should either (a) require a fresh, explicit user-approval step scoped only to the newly requested assets, or (b) be stored as a separate, revocable grant so it can be removed independently (mirroring the report's recommendation to track allowances such that they don't grow implicitly, and to support decrementing/removing the specific granted amount/scope rather than only an all-or-nothing revoke). Add a corresponding "remove asset from scope" operation so scope can shrink, and audit `getConnectedAccounts` to ensure it only ever returns addresses for the specific assets/accounts the user most recently and explicitly approved.

### Proof of Concept
1. User visits `dapp.example` and approves connection for Solana only: `connectedOrigins.add({ origin: 'dapp.example', connectedAssetName: 'solana', trusted: true })`. Stored: `assetNames: ['solana']`.
2. Later, without a distinct/isolated consent UI, the same origin (or wallet logic acting on its behalf) calls `add({ origin: 'dapp.example', connectedAssetName: 'ethereum' })`.
3. Per [4](#0-3) , the stored `assetNames` becomes `['solana', 'ethereum']` — the prior scope was never discarded.
4. `getConnectedAccounts({ origin: 'dapp.example' })` now returns Ethereum addresses for the origin in addition to Solana ones, for every enabled wallet account, even though the user's original, isolated approval only covered Solana.

### Citations

**File:** features/connected-origins/module/connections.js (L140-185)
```javascript
  add = async ({
    connectedAssetName,
    origin,
    name,
    icon,
    assetNames = [],
    trusted,
    favorite,
    walletAccount,
  }) => {
    const value = await this.#getOrigin({ origin })

    const allConnectedAssetNames = new Set([
      connectedAssetName,
      ...assetNames,
      ...(value?.assetNames ?? []),
    ])

    if (value) {
      await this.#setAttributes({
        origin,
        attributes: {
          icon: icon ?? value.icon,
          name: name ?? value.name,
          connectedAssetName: connectedAssetName ?? value.connectedAssetName,
          trusted: trusted ?? value.trusted,
          favorite: favorite ?? value.favorite,
          assetNames: [...allConnectedAssetNames],
          walletAccount: walletAccount ?? value.walletAccount,
        },
      })

      return
    }

    await this.#addNewItem({
      origin,
      icon,
      name,
      connectedAssetName,
      trusted,
      favorite,
      assetNames: [...allConnectedAssetNames],
      walletAccount,
    })
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
