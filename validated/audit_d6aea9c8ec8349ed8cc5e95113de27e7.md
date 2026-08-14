### Title
Non-atomic read-modify-write on the connected-origins list allows lost updates that bypass a user's disconnect/untrust action - (File: features/connected-origins/module/connections.js)

### Summary
`ConnectedOrigins` maintains a single array of connected dApp origins (trust status, `activeConnections`, `assetNames`) inside `connectedOriginsAtom`. Every mutating operation (`add`, `#setAttributes`, `connect`, `disconnect`, `untrust`, `clearConnections`) follows the same unsynchronized pattern: read the full list, compute a new array in memory, then write the whole array back. There is no locking around this read-modify-write sequence, so concurrent invocations can silently clobber each other's changes — the same bug class described in the external report (lost updates on a shared master list due to non-atomic read-modify-write), but here it affects origin/connection trust state instead of session key material.

### Finding Description
Every mutator in `ConnectedOrigins` does:
1. Read the current array via `#getData()` [1](#0-0) 
2. Compute a new array in JS (e.g. append, filter, or map over `origin`) [2](#0-1) 
3. Write the entire array back via `#setData()` [3](#0-2) 

`add()` (used both to create a new connection and to update an existing one) itself performs a read (`#getOrigin`) followed by a conditional write via `#setAttributes` or `#addNewItem`, both of which independently re-read and re-write the full list: [4](#0-3) . `#addNewItem` appends a brand-new origin object to a stale snapshot of the array: [5](#0-4) . `connect`/`disconnect` similarly mutate `activeConnections` based on a stale read: [6](#0-5) .

None of these steps are wrapped in a mutex or `makeConcurrent`-style serialization at the `ConnectedOrigins` module level (unlike other modules in the codebase, e.g. `AddressCache#update` and `PersonalNotes#update`, which explicitly wrap their read-modify-write cycle with `restrictConcurrency`/`makeConcurrent` to avoid exactly this race) [7](#0-6) . The underlying atom's own `get`/`set` calls are individually serialized, but that does not make the higher-level "read array → mutate → write array" sequence atomic — two concurrent top-level calls can both read the same starting array, compute divergent updates, and the second `set()` fully overwrites the first's result.

Concretely: if a `disconnect({ id, origin })` call (triggered by the user revoking a dApp connection) races with any other concurrent mutator on the same array — e.g., another `connect()`/`add()` for a different origin, or `setFavorite`/`updateConnection` for the same or a different origin — the second write is computed from a snapshot taken before the disconnect took effect. The final state written back can silently drop the disconnect, leaving `activeConnections` populated as if the user's revoke never happened. The same applies to `untrust()`: a concurrent `#setAttributes` call (e.g. `setFavorite`) can capture the array before the origin is removed and write it back, restoring the "untrusted"/removed origin as if `untrust` never executed.

### Impact Explanation
`connectedOriginsAtom` governs the origin-isolation trust boundary between the wallet and connected dApps (trusted origins get address/account exposure via `getConnectedAccounts`, and `activeConnections` gate which origins receive live connection state) [8](#0-7) . A lost update on `untrust`/`disconnect` means a user-initiated revoke of a dApp's access can be silently reverted by an unrelated, concurrent connection event, leaving that origin's trust/connection state intact and its access to wallet addresses/accounts persisted beyond the user's intent — a cross-origin privilege-bleed condition. This does not directly leak private keys, but it does defeat the app's origin-trust revocation guarantee, which is the analogous "ghost" state to the report's ghost sessions (persisted state that should have been removed but remains reachable).

### Likelihood Explanation
Triggering the race does not require a malicious node/peer or any privileged actor — it only requires two dApp-driven RPC calls (e.g. one dApp's `connect` and the user's `disconnect`/`untrust` for another origin, or rapid double-invocation from a single dApp) landing concurrently, which is plausible in normal browser-extension usage with multiple tabs/dApps interacting with the wallet simultaneously. No mocked-only path or dependency bug is involved; the vulnerable logic is entirely first-party application code in `connections.js`.

### Recommendation
Serialize all read-modify-write sequences on the connected-origins list behind a single mutex/queue (e.g., wrap the entire mutator body — read, compute, write — with `make-concurrent`'s `{ concurrency: 1 }`, as already done in `AddressCache#update` and `PersonalNotes#update`) rather than relying only on the atom's own per-call concurrency. Additionally, prefer atomic updater semantics (`atom.set(current => next)`) over separate `get()` then `set()` calls so intermediate state cannot be interleaved with concurrent mutators.

### Proof of Concept
1. Call `connectedOrigins.disconnect({ id, origin: 'evil.com' })` and, before it resolves, concurrently call `connectedOrigins.connect({ id: otherId, origin: 'other.com' })` (or any other mutator that also goes through `#setData`).
2. Both operations read the same pre-disconnect array via `#getData()`.
3. `connect` finishes second and writes back an array computed from the stale snapshot, which still includes `evil.com`'s `activeConnections` entry that `disconnect` intended to remove.
4. Result: `evil.com` remains listed with an active connection (and, if applicable, its trust status), even though the disconnect call returned successfully to the caller.

### Citations

**File:** features/connected-origins/module/connections.js (L27-29)
```javascript
  #getData = async () => {
    return this.#connectedOriginsAtom.get()
  }
```

**File:** features/connected-origins/module/connections.js (L41-49)
```javascript
  #setData = async (data) => {
    const assetNames = this.#getConnectedAssets(data)
    const accounts = await this.#getAccounts(assetNames)

    return Promise.all([
      this.#connectedOriginsAtom.set(data),
      this.#connectedAccountsAtom.set(accounts),
    ])
  }
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

**File:** features/connected-origins/module/connections.js (L222-243)
```javascript
  connect = async ({ id, origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) return

    const activeConnections = value.activeConnections || []
    const newConnection = { id, createdAt: Date.now() }
    const newConnections = uniqBy([...activeConnections, newConnection], 'id')

    await this.#setAttributes({ origin, attributes: { activeConnections: newConnections } })
  }

  disconnect = async ({ id, origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) return

    const activeConnections = value.activeConnections || []
    const newConnections = activeConnections.filter((connection) => connection.id !== id)

    await this.#setAttributes({ origin, attributes: { activeConnections: newConnections } })
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

**File:** features/address-provider/module/address-cache/index.js (L53-54)
```javascript
  #update = restrictConcurrency(async (addressCacheChanges, { fromSync } = Object.create(null)) => {
    await this.#loaded.promise
```
