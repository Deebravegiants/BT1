### Title
getConnectedAccounts discloses addresses for all enabled wallet accounts regardless of per-origin `walletAccount` scope - ([File: features/connected-origins/module/connections.js])

### Summary
`ConnectedOrigins#getConnectedAccounts` returns address entries for every wallet account present in `connectedAccountsAtom`, ignoring the per-origin `walletAccount` field that `add()` stores to scope consent to a single account. Any trusted origin that was granted access to only one wallet account (`walletAccount: 'exodus_1'`, for example) still receives addresses for all other enabled wallet accounts (e.g. `exodus_0`).

### Finding Description
`add()` accepts and persists a `walletAccount` attribute per origin via `#addNewItem`/`#setAttributes` [1](#0-0) , implying that consent can be scoped to a specific wallet account. However, `getConnectedAccounts` never reads or filters on `value.walletAccount`. It only checks `isTrusted`, computes `assetNames`, then iterates over **all** keys of `accounts` (from `#connectedAccountsAtom.get()`, which contains every enabled wallet account) and returns an entry for each one, moving only the currently active wallet account to the front: [2](#0-1) 

Since `accounts` is populated from `#enabledWalletAccountsAtom` for all enabled accounts via `#getAccounts` [3](#0-2) , and `getConnectedAccounts` does not intersect this with `value.walletAccount`, any origin that was granted (via `add`) access scoped to a single account still gets addresses for every other enabled account in the wallet. The existing test suite only exercises the unscoped case (no `walletAccount` passed to `add`) and asserts both `exodus_0`/`exodus_1` are returned [4](#0-3) , so this scoping gap has no regression coverage.

### Impact Explanation
This is cross-account address disclosure beyond the granted scope: an origin explicitly restricted to `walletAccount: 'account-1'` can learn public addresses (across all connected asset names) of every other wallet account enabled in the wallet, via the exposed `connectedOrigins.getConnectedAccounts` API surfaced through `features/connected-origins/api/index.js` [5](#0-4) . This is an address/privacy disclosure rather than a signing or fund-loss primitive — no private keys or transaction authorization are exposed, only address linkage across the user's separate wallet accounts to a dapp that was not supposed to see them.

### Likelihood Explanation
Precondition: the origin must already be trusted/connected (via a prior `add()` call with `trusted: true`), and the wallet must have more than one enabled wallet account. Once connected with a `walletAccount` scope, the attacker origin simply calls `getConnectedAccounts({origin})` — a normal, expected dapp-facing call — and receives the unscoped result. This is fully reproducible and doesn't require any privileged state, deeplinks, or social engineering, only the ordinary dapp-connection flow.

### Recommendation
In `getConnectedAccounts`, after fetching `value`, if `value.walletAccount` is set, filter the `accounts` object (or the constructed `connectedAccounts` array) to only include the entry whose key/`name` equals `value.walletAccount`, before applying the active-account reordering logic.

### Proof of Concept
Integration test (extending `features/connected-origins/module/__tests__/connections.test.js`):
```js
test('getConnectedAccounts should be scoped to the granted walletAccount', async () => {
  await connectedOrigins.add({
    origin: 'exodus.com',
    name: 'Exodus',
    icon: 'exodus_icon',
    connectedAssetName: 'solana',
    assetNames: ['solana'],
    trusted: true,
    walletAccount: 'exodus_1',
  })

  const accounts = await connectedOrigins.getConnectedAccounts({ origin: 'exodus.com' })

  // Expected: only the granted account is returned
  expect(accounts).toEqual([
    {
      name: 'exodus_1',
      addresses: { solana: '4orUhPn6CRzVcgq5DHfAVt2odiZpPjNy7wNQPYMT4bF1' },
    },
  ])
})
```
Running this against the current implementation fails because `accounts` also includes `exodus_0`'s addresses, demonstrating the scope bypass.

### Citations

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

**File:** features/connected-origins/module/__tests__/connections.test.js (L160-196)
```javascript
  test('returns connected accounts with active wallet account first', async () => {
    await connectedOrigins.add({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      connectedAssetName: 'solana',
      assetNames: ['solana'],
      trusted: true,
    })

    await connectedOrigins.add({
      origin: 'wayne.foundation',
      name: 'Wayne Foundation',
      icon: 'exodus_icon',
      connectedAssetName: 'ethereum',
      assetNames: ['ethereum'],
      trusted: true,
    })

    await activeWalletAccountAtom.set('exodus_1')

    const accounts = await connectedOrigins.getConnectedAccounts({ origin: 'exodus.com' })
    expect(accounts).toEqual([
      {
        name: 'exodus_1',
        addresses: {
          solana: '4orUhPn6CRzVcgq5DHfAVt2odiZpPjNy7wNQPYMT4bF1',
        },
      },
      {
        name: 'exodus_0',
        addresses: {
          solana: 'ASwcbiBuegaMrNUuXeN5WDYKoRuDXxMRt5DdStjvdSro',
        },
      },
    ])
  })
```

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
