### Title
setFavorite widens an origin's assetNames beyond consent, unlocking address disclosure for unapproved assets - (File: features/connected-origins/module/connections.js)

### Summary
`ConnectedOrigins#setFavorite` passes a caller-supplied `assetNames` array straight into `#setAttributes`, which unconditionally spreads it over the stored connection object with no comparison against the asset set that was actually consented to at `add()`-time. Because `getConnectedAccounts` derives the exposed address set purely from `connection.assetNames`, calling `setFavorite({origin, value, assetNames: [...extra]})` on an already-trusted origin can inject new asset names and cause subsequent `getConnectedAccounts` calls to disclose addresses for assets the user never approved for that origin.

### Finding Description
`setFavorite` is defined as:
```js
setFavorite = async ({ origin, value, assetNames = [] }) => {
  return this.#setAttributes({ origin, attributes: { favorite: value, assetNames } })
}
``` [1](#0-0) 

`#setAttributes` performs a blind merge with no whitelist/diff check:
```js
const newData = data.map((connection) => {
  if (origin !== connection.origin) return connection
  return { ...connection, ...attributes }
})
``` [2](#0-1) 

This differs from `add()`, which explicitly unions the *new* `assetNames` with the *existing* trusted set (`allConnectedAssetNames`) before calling `#setAttributes` — i.e., `add()` treats asset widening as an append operation tied to the add-consent flow, while `setFavorite` simply overwrites `connection.assetNames` with whatever the caller passes, with no union/whitelist against the previously consented set: [3](#0-2) 

`getConnectedAccounts` then trusts `value.assetNames` verbatim to decide which per-account addresses to disclose:
```js
const assetNames = [value.connectedAssetName, ...(value.assetNames ?? [])].filter(...)
...
connectedAccounts.push({ name, addresses: pick(accounts[name].addresses, assetNames) })
``` [4](#0-3) 

The only gate is `isTrusted({origin})` — once an origin is trusted for asset A, `setFavorite` can silently rewrite `assetNames` to include asset B, and the trust check passes since it's the same origin object. The function name/semantics ("mark as favorite") give no indication it also mutates asset scoping, and callers of the public `connectedOriginsApi.setFavorite` [5](#0-4)  are not required to preserve or diff the existing `assetNames` before calling it.

One caveat on exploitability: `getConnectedAccounts` (and `#getWalletAccountAddresses`) will attempt to look up/derive an address for every asset name in `value.assetNames`/`#getConnectedAssets`, via `#addressProvider.getDefaultAddress`. If `assetNames` includes an asset not actually supported/enabled by `assetsModule`, this could throw rather than silently succeed — I could not fully verify from the indexed code whether arbitrary/unsupported asset name strings passed through `setFavorite` are validated anywhere upstream (e.g., in whatever UI/RPC handler calls `connectedOriginsApi.setFavorite`) before reaching this module. That upstream reachability from an actual "ordinary dapp/origin request" was not confirmed in the available code — `setFavorite` appears to be wallet-UI-facing (paired with `value: true/false` for "favorite" toggling) rather than a method invoked directly by dapp-origin RPC calls with attacker-controlled `assetNames`.

### Impact Explanation
If a caller (whether wallet UI code or any code with access to the `connectedOriginsApi`) invokes `setFavorite` with an expanded `assetNames` array, the trust/consent scope recorded via `add()` is silently widened without going through the union-with-existing-consent logic in `add()`. This causes `getConnectedAccounts` to return addresses for assets across all wallet accounts that were never explicitly approved for that origin — an unconsented cross-asset address disclosure to an already-trusted origin.

### Likelihood Explanation
Preconditions: origin already trusted for at least one asset (via `add()`), and something in the app invokes `setFavorite` with a non-matching/wider `assetNames` array. Within the provided module and its unit tests [6](#0-5) , `setFavorite` is only ever exercised with `value` and no `assetNames`, defaulting to `[]` — which would actually *clear* `assetNames` rather than widen it, since `attributes: { favorite: value, assetNames }` overwrites the field unconditionally. I could not find, in the indexed code, any call site that invokes `setFavorite` with a non-empty `assetNames` array, nor a dapp/origin-facing RPC handler that maps untrusted external input directly into `setFavorite`'s `assetNames` parameter. Without a confirmed reachable caller passing attacker/user-influenced `assetNames`, this is a latent API design defect (missing whitelist/diff in `#setAttributes`) rather than a demonstrated end-to-end exploit from ordinary dapp/origin/deeplink input.

### Recommendation
Have `#setAttributes` (or specifically `setFavorite`) merge `assetNames` via union with the existing trusted `connection.assetNames` rather than overwriting, mirroring the logic already used in `add()`; alternatively, remove `assetNames` from `setFavorite`'s attribute payload entirely (it should only toggle `favorite`), since asset-scope changes should exclusively go through the explicit `add()` consent path.

### Proof of Concept
```js
// features/connected-origins/module/__tests__/connections.test.js
test('setFavorite must not widen consented assetNames beyond add()-time scope', async () => {
  await connectedOrigins.add({
    origin: 'exodus.com',
    connectedAssetName: 'solana',
    assetNames: ['solana'],
    trusted: true,
  })

  await connectedOrigins.setFavorite({
    origin: 'exodus.com',
    value: true,
    assetNames: ['solana', 'bitcoin'],
  })

  const accounts = await connectedOrigins.getConnectedAccounts({ origin: 'exodus.com' })
  for (const account of accounts) {
    expect(account.addresses).not.toHaveProperty('bitcoin')
  }
})
```
Expected (per invariant): the assertion should pass, i.e., `bitcoin` addresses must not appear unless re-approved via `add()`. Running this against the current implementation is expected to fail the assertion, confirming `setFavorite` can widen the asset scope — assuming a reachable caller supplies a non-default `assetNames` to `setFavorite`, which was not conclusively found in the indexed code.

### Citations

**File:** features/connected-origins/module/connections.js (L58-61)
```javascript
    const newData = data.map((connection) => {
      if (origin !== connection.origin) return connection
      return { ...connection, ...attributes }
    })
```

**File:** features/connected-origins/module/connections.js (L150-167)
```javascript
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
```

**File:** features/connected-origins/module/connections.js (L218-220)
```javascript
  setFavorite = async ({ origin, value, assetNames = [] }) => {
    return this.#setAttributes({ origin, attributes: { favorite: value, assetNames } })
  }
```

**File:** features/connected-origins/module/connections.js (L253-270)
```javascript
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
```

**File:** features/connected-origins/api/index.js (L6-21)
```javascript
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
```

**File:** features/connected-origins/module/__tests__/connections.test.js (L434-452)
```javascript
  test('setFavorite to true for existing origin', async () => {
    await connectedOriginsAtom.set([{ origin: 'exodus.com', favorite: false }])
    await connectedOrigins.setFavorite({ origin: 'exodus.com', value: true })

    const origins = await connectedOriginsAtom.get()

    expect(origins).toHaveLength(1)
    expect(origins).toMatchObject([{ origin: 'exodus.com', favorite: true }])
  })

  test('setFavorite to false for existing origin', async () => {
    await connectedOriginsAtom.set([{ origin: 'exodus.com', favorite: true }])
    await connectedOrigins.setFavorite({ origin: 'exodus.com', value: false })

    const origins = await connectedOriginsAtom.get()

    expect(origins).toHaveLength(1)
    expect(origins).toMatchObject([{ origin: 'exodus.com', favorite: false }])
  })
```
