### Title
Connected-origins module exposes addresses for all wallet accounts to any trusted origin, regardless of which account was actually authorized - ([File: features/connected-origins/module/connections.js])

### Summary
`connectedOrigins.getConnectedAccounts()` is exposed as a public API method callable from any trusted dApp/origin. [1](#0-0)  Instead of returning only the wallet account(s) that were actually connected/authorized for that specific origin, it returns the addresses of every wallet account currently enabled in the entire wallet. [2](#0-1) 

### Finding Description
This is the same root-cause bug class as the external report: **a permission/whitelist record is not associated with the specific target it should be scoped to**, so a check that should be per-entity ends up being applied globally.

In the external report, an address is whitelisted as an "owner" in a flat `permission_list` with no link to *which* multisig it belongs to, so it is treated as valid for every multisig in the system. In this codebase, the analogous flaw is in `ConnectedOrigins`:

- Each connected origin record stores its own `walletAccount` and `activeConnections` (the specific account/tab actually connected), populated by `add()` and `connect()`. [3](#0-2) [4](#0-3) 
- However, `getConnectedAccounts()` never reads `value.walletAccount` or `value.activeConnections` to scope which accounts to return. It only checks `isTrusted(origin)` and then iterates over **every account in `#connectedAccountsAtom`**, which is populated from `#enabledWalletAccountsAtom` — i.e., all wallet accounts, not just the one(s) tied to that origin: [5](#0-4) [6](#0-5) 

```js
const accounts = await this.#connectedAccountsAtom.get()
const connectedAccounts = []
for (const name of Object.keys(accounts)) {
  if (name === activeWalletAccount) continue
  connectedAccounts.push({ name, addresses: pick(accounts[name].addresses, assetNames) })
}
```

The only per-origin data used to filter the result is `assetNames`/`connectedAssetName` (which asset chains to expose), not *which wallet accounts* should be exposed. [7](#0-6)  Just as in the report — where "whitelisted owner" was checked as a global property instead of being tied to a specific multisig — here "trusted" is checked as a global property of the origin, and once true, addresses for *all* wallet accounts in the wallet are disclosed, not just the account(s) the user actually connected to that origin.

### Impact Explanation
Any origin that the user trusts for one wallet account (e.g., connecting Account #1 to a dApp) gets the addresses of every other enabled wallet account in the user's wallet (Account #2, #3, ...), even though the user never authorized exposure of those other accounts to that origin. [8](#0-7)  This is a cross-account privilege bleed / account-isolation bypass: it discloses addresses belonging to unrelated wallet accounts to a third-party origin without per-account consent, undermining the account isolation the "connect" flow is supposed to enforce.

### Likelihood Explanation
Likelihood is high given normal usage: `add`/`connect` are the standard flow for any dApp connection, and `getConnectedAccounts` is directly exposed via the public API (`connectedOrigins.getConnectedAccounts`) with no additional gating beyond the origin-level `trusted` flag. [9](#0-8)  No malicious node/peer/operator is required — any web page the user has approved for wallet connection can trigger this call through the exposed RPC/provider API to enumerate all of the user's wallet accounts and their addresses for the connected asset(s).

### Recommendation
Scope `getConnectedAccounts` (and the underlying `#connectedAccountsAtom` population) to the specific wallet account(s) recorded on the origin record (`value.walletAccount` / the accounts tied to `activeConnections`) rather than iterating over all enabled wallet accounts. Associate each connected origin with an explicit list of authorized wallet-account identifiers at connect time, and use that list — not the global `enabledWalletAccountsAtom` snapshot — to build the response of `getConnectedAccounts`.

### Proof of Concept
1. User has two enabled wallet accounts, `exodus_0` and `exodus_1`.
2. User connects `exodus_0` to `dapp.example.com` via `connectedOrigins.add({ origin: 'dapp.example.com', connectedAssetName: 'ethereum', walletAccount: 'exodus_0', trusted: true })`.
3. `dapp.example.com` calls `connectedOrigins.getConnectedAccounts({ origin: 'dapp.example.com' })`.
4. Per `connections.js:249-273`, the result includes an entry for `exodus_1` with its `ethereum` address, even though `exodus_1` was never connected or authorized for `dapp.example.com` — confirmed by the implementation iterating `Object.keys(accounts)` (all enabled accounts) rather than filtering by `value.walletAccount`/`activeConnections`. [10](#0-9)

### Citations

**File:** features/connected-origins/api/index.js (L1-22)
```javascript
const connectedOriginsApi = ({
  connectedOrigins,
  connectedOriginsAtom,
  connectedAccountsAtom,
}) => ({
  connectedOrigins: {
    get: connectedOriginsAtom.get,
    getAccounts: connectedAccountsAtom.get,
    add: connectedOrigins.add,
    clear: connectedOrigins.clear,
    untrust: connectedOrigins.untrust,
    isTrusted: connectedOrigins.isTrusted,
    isAutoApprove: connectedOrigins.isAutoApprove,
    setFavorite: connectedOrigins.setFavorite,
    setAutoApprove: connectedOrigins.setAutoApprove,
    connect: connectedOrigins.connect,
    disconnect: connectedOrigins.disconnect,
    updateConnection: connectedOrigins.updateConnection,
    clearConnections: connectedOrigins.clearConnections,
    getConnectedAccounts: connectedOrigins.getConnectedAccounts,
  },
})
```

**File:** features/connected-origins/module/connections.js (L76-106)
```javascript
  #addNewItem = async ({
    origin,
    name,
    icon,
    connectedAssetName,
    assetNames,
    accounts,
    trusted = false,
    favorite = false,
    walletAccount,
  }) => {
    const newOrigin = {
      origin,
      icon,
      name,
      trusted,
      favorite,
      connectedAssetName,
      assetNames,
      accounts,
      autoApprove: false,
      createdAt: Date.now(),
      activeConnections: [],
      walletAccount,
    }

    const data = await this.#getData()
    const newData = [...data, newOrigin]

    await this.#setData(newData)
  }
```

**File:** features/connected-origins/module/connections.js (L108-121)
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
```

**File:** features/connected-origins/module/connections.js (L222-232)
```javascript
  connect = async ({ id, origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) return

    const activeConnections = value.activeConnections || []
    const newConnection = { id, createdAt: Date.now() }
    const newConnections = uniqBy([...activeConnections, newConnection], 'id')

    await this.#setAttributes({ origin, attributes: { activeConnections: newConnections } })
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
