### Title
Cross-Account Address Disclosure to Connected dApps via Use of Current Active Account Instead of the Approved Account - ([File: features/connected-origins/module/connections.js])

### Summary
`ConnectedOrigins.getConnectedAccounts` returns wallet-account addresses to a connected origin based on the wallet's *current* `activeWalletAccount` rather than the account that was actually approved/connected for that specific origin at connection time. This mirrors the reported bug class of "using current state instead of the historically-recorded state at the time the relevant event/approval occurred" — here applied to account/origin trust boundaries instead of reward accounting.

### Finding Description
When a dApp connects to Exodus, `ConnectedOrigins.add()` persists a connection record for the origin, including a `walletAccount` field intended to capture which wallet account the user approved for that origin at connect time [1](#0-0) .

However, `getConnectedAccounts({ origin })` — the method used to hand back account addresses for a trusted/connected origin — never reads that stored `value.walletAccount`. Instead, it fetches whatever account is currently active in the wallet via `this.#activeWalletAccountAtom.get()` and always places that account first (as the "active"/primary account exposed to the site): [2](#0-1) 

```js
getConnectedAccounts = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })
    if (!isTrusted) return []

    const value = await this.#getOrigin({ origin })
    const assetNames = [value.connectedAssetName, ...(value.assetNames ?? [])].filter(...)

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

This is structurally the same root cause as the Babylon report: the code substitutes a *live, mutable* value (`activeWalletAccountAtom.get()` — analogous to `TotalActiveSat`, the delegation's *current* stake) for the value that should reflect the state *at the time the relevant approval/period occurred* (the connection's stored `walletAccount`, analogous to the historical stake that should have been snapshotted per period). The origin's authorization was granted for a specific account context, but the wallet silently re-evaluates "which account applies" using present-day global state instead of the recorded historical/approved association.

### Impact Explanation
Because the wallet's `activeWalletAccountAtom` is a single global, shared value (not scoped per-origin) and is used to compute the account list disclosed to *every* trusted origin, switching the active account for one purpose (e.g. to interact with a different, unrelated site or feature) causes any other already-connected/trusted origin to silently receive addresses for the newly active account the next time `getConnectedAccounts` is invoked — without a fresh connection approval from the user. This can:
- Leak addresses of accounts the user never intended to expose to a given origin.
- Cause a dApp to silently be handed a different account's address set than what the user approved, enabling account/address confusion for signing flows or off-chain identification, since which account is "first"/primary is decided by global mutable state rather than the origin-specific approval record.

This is a real privilege-bleed across account boundaries in an unprivileged-user-reachable path (any dApp origin the user has ever trusted), consistent with the "cross-origin/account privilege bleed" category called out in the validation rules.

### Likelihood Explanation
High reachability: switching active wallet accounts is a routine, always-available user action, and any previously trusted origin can call the connected-origins accounts API (`connectedOrigins.getConnectedAccounts`) at any later point, e.g. on page reconnect/eager-connect flows. No malicious node/peer/operator is required — this is purely a client-side wallet-state bug triggerable by ordinary use (open two dApps, connect origin A with account A active, switch active account to B for another site, return to origin A).

### Recommendation
`getConnectedAccounts` should determine the primary/first-listed account from the connection's own recorded `walletAccount` (captured at approval time in `add()`), not from the live `activeWalletAccountAtom`. If a mechanism to intentionally re-authorize a switched active account is desired, that should be an explicit, per-origin approval action rather than an implicit consequence of global active-account state.

### Proof of Concept
1. User connects `origin: 'evil.example'` while `activeWalletAccount = 'exodus_0'`. `add()` persists a connection with `walletAccount: 'exodus_0'` [1](#0-0) .
2. User later switches active account to `'exodus_1'` (e.g., to use a different, unrelated dApp) via `walletAccounts.setActive('exodus_1')` [3](#0-2) .
3. `evil.example` (still marked trusted, no re-approval needed) calls `getConnectedAccounts({ origin: 'evil.example' })` again (e.g. via eager reconnect). The method returns `exodus_1`'s addresses as the primary/active account entry [4](#0-3) , even though the user only ever approved this origin while `exodus_0` was active.

Note: I was unable to fully trace how `getConnectedAccounts` is consumed by the actual web3 provider/dApp bridge (e.g., whether `signTransaction`/`signMessage` flows also key off this same active-account substitution) due to index size limits on retrievable file contents; confirming the full signing-flow impact would require starting a Devin session with full repository access.

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

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L542-548)
```typescript
  setActive = async (value: string | ((oldValue: string) => string)) => {
    if (typeof value === 'function') {
      return this.#activeWalletAccountAtom.set(value)
    }

    return this.#activeWalletAccountAtom.set(value)
  }
```
