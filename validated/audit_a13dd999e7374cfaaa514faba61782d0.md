Found a strong analog: `connectedOrigins.untrust()` in `features/connected-origins/module/connections.js` performs a read-then-write (check-then-act) pattern without atomicity, exactly mirroring the `maxTotalSupply`/`deposit()` race in the report — a security-relevant authorization state (`trusted`/`assetNames`/`autoApprove`) is read, then written back later, allowing a concurrent `add()` (invoked by an untrusted dapp's connection flow) to interleave and restore or widen trust/asset-exposure that the user/system just tried to revoke.### Title
Read-Modify-Write Race in `connectedOrigins.untrust()`/`add()` Allows a Malicious dApp to Resurrect Revoked Trust and Asset/Account Exposure - (File: `features/connected-origins/module/connections.js`)

### Summary
`ConnectedOrigins` stores per-origin authorization state (`trusted`, `assetNames`, `autoApprove`, `connectedAssetName`) that gates which addresses/accounts a website can see via `getConnectedAccounts()`. All mutators (`add`, `untrust`, `setAttributes`, `connect`, `disconnect`, `updateConnection`) follow the same unsynchronized read-then-write pattern: read the full array with `#getData()`/`#getOrigin()`, compute a new array in memory, then write it back with `#setData()`. There is no locking, versioning, or concurrency guard around this sequence, so two concurrent calls touching the same origin can interleave and the later write silently clobbers/undoes the earlier one — the same class of bug as the reported `maxTotalSupply`/`deposit()` race, where an admin-facing security control (there: max supply cap; here: `trusted`/authorization state) can be raced by an unprivileged/attacker-controlled call.

### Finding Description
`untrust()` performs:
```js
untrust = async ({ origin }) => {
  const isTrusted = await this.isTrusted({ origin })   // read
  if (!isTrusted) return
  const data = await this.#getData()                    // read
  const newData = data.filter((connection) => connection.origin !== origin)
  await this.#setData(newData)                           // write (full array)
}
``` [1](#0-0) 

`add()` similarly reads the current origin record, merges attributes/`assetNames`, and writes the full array back:
```js
add = async ({ connectedAssetName, origin, name, icon, assetNames = [], trusted, favorite, walletAccount }) => {
  const value = await this.#getOrigin({ origin })
  ...
  if (value) {
    await this.#setAttributes({ origin, attributes: { ...., trusted: trusted ?? value.trusted, ... assetNames: [...allConnectedAssetNames] } })
    return
  }
  await this.#addNewItem({ ... })
}
``` [2](#0-1) 

`#setAttributes`, used by `add`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, and `updateConnection`, has the identical unsynchronized read-modify-write shape, operating on the *entire* origins array each time:
```js
#setAttributes = async ({ origin, attributes }) => {
  const item = await this.#getOrigin({ origin })
  if (!item) return
  const data = await this.#getData()
  const newData = data.map((connection) => (origin !== connection.origin ? connection : { ...connection, ...attributes }))
  await this.#setData(newData)
}
``` [3](#0-2) 

Because every mutator re-reads the whole `connectedOriginsAtom` snapshot and then writes back a whole new array, if a call to `untrust()` (triggered by the user, or by security automation revoking a compromised/malicious origin) races with a concurrent `add()` (triggered by that same malicious website re-issuing a "connect" request, which asset-provider UIs typically call on every page load/connection attempt without waiting for prior calls to settle), the following interleaving is possible:

1. `origin` is currently `trusted: true` with `assetNames: ['ethereum']`.
2. `untrust()` reads `isTrusted` → `true`, reads `data` (still containing the origin).
3. Concurrently, a malicious page calls `connectedOrigins.add({ origin, assetNames: ['solana', 'ethereum'], trusted: true })`, which also reads the *pre-removal* `data`/`value` and computes a merged record (widening `assetNames`) based on the stale value.
4. `add()`'s `#setAttributes` writes its full array back before or after `untrust()`'s `#setData` call — whichever write lands last wins and overwrites the other's effect (`#setData` is `this.#connectedOriginsAtom.set(data)`, a full overwrite, not a merge) [4](#0-3) .
5. Result: either (a) the `untrust` is lost entirely and the origin remains trusted with an attacker-widened `assetNames` set, or (b) `add()`'s widened `assetNames`/`trusted:true` write lands last and re-establishes trust immediately after the user revoked it.

`isTrusted()` and `getConnectedAccounts()` gate exposure of wallet addresses per-origin using exactly this racy `trusted`/`assetNames` state [5](#0-4) [6](#0-5) , so a successful race directly translates into unauthorized cross-account/cross-asset address disclosure to a site the user believed was disconnected/untrusted.

### Impact Explanation
This maps to "cross-origin/account privilege bleed": a dishonest or compromised website can race the wallet's `untrust`/revocation call with its own `add`/connect call to either (a) survive an intended revocation and keep receiving connected-account addresses via `getConnectedAccounts()`, or (b) expand the set of `assetNames`/accounts it is authorized to see beyond what the user approved, because the last writer wins on the full-array snapshot with no compare-and-swap or optimistic-concurrency check. This is directly analogous to the report's finding that the operator's `setMaxTotalSupply()` can be raced by a user's `deposit()` to leave the max-supply guard in an inconsistent, weaker state than intended.

### Likelihood Explanation
Medium: exploitation requires the attacker-controlled origin's page script to fire an `add`/connect call at (or immediately after) the moment the user/extension issues `untrust()` for that same origin — a timing window that is plausible given that dApp connection flows commonly re-invoke `connect`/`add` on page focus, reconnect, or via WalletConnect/session-restore logic, and the mutators here have no per-origin serialization (unlike other parts of the codebase, e.g. `wallet.js`'s `makeConcurrent(..., { concurrency: 1 })` pattern used for `create`/`import` [7](#0-6) , which is notably absent here).

### Recommendation
Serialize mutations per origin (or globally) using the same `makeConcurrent`/mutex pattern already used elsewhere in the codebase (e.g., `wallet.create`/`wallet.import`, `wallet-accounts.#replaceAll`) so that `add`, `untrust`, `#setAttributes`, `connect`, and `disconnect` cannot interleave for the same origin. Alternatively, implement optimistic concurrency (read a version/timestamp, and reject/retry the write if the underlying atom changed since the read) in `#setData`/`#setAttributes`, and make `untrust` take precedence over any in-flight `add` for the same origin (e.g., by re-checking trust status immediately before the final atom write, inside the same critical section).

### Proof of Concept
```js
// Assume `origin` starts trusted with assetNames: ['ethereum']
await Promise.all([
  connectedOrigins.untrust({ origin }),
  connectedOrigins.add({ origin, assetNames: ['solana'], trusted: true }),
])

// Depending on interleaving, one of two unauthorized outcomes occurs:
// (a) untrust() is silently undone: isTrusted({ origin }) === true even though
//     the user/system explicitly revoked it, OR
// (b) untrust() wins but add()'s assetNames merge is lost/partial, leaving
//     inconsistent state that a subsequent add() by the same origin can widen again.

const stillTrusted = await connectedOrigins.isTrusted({ origin })
console.log('unexpectedly trusted after untrust():', stillTrusted)
```
This mirrors the report's scenario of a front-run/race between a privileged state-change (`setMaxTotalSupply`/`untrust`) and a user-facing action (`deposit`/`add`) that leaves the guarded invariant (`maxTotalSupply` cap / origin trust-and-scope) inconsistent with intent, here weakening origin-based account/address exposure controls rather than a token-supply cap.

**Note on confidence:** I confirmed the exact read-then-write code shape in `connections.js` for all mutators, but I could not verify at what call sites/UI flows `add()` vs `untrust()` are actually invoked concurrently in production (e.g., whether the UI awaits one before firing the other), since those call sites were outside what the index surfaced. If Devin has full repo access, it would be worth tracing UI/dApp-provider call sites (e.g., `solana.connect`, `ethereum.request`) to confirm concurrent invocation is actually reachable from an untrusted origin without additional serialization at a higher layer.

### Citations

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

**File:** features/connected-origins/module/connections.js (L51-64)
```javascript
  #setAttributes = async ({ origin, attributes }) => {
    const item = await this.#getOrigin({ origin })

    if (!item) return

    const data = await this.#getData()

    const newData = data.map((connection) => {
      if (origin !== connection.origin) return connection
      return { ...connection, ...attributes }
    })

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

**File:** features/connected-origins/module/connections.js (L198-212)
```javascript
  isTrusted = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) {
      return false
    }

    // backward compatibility
    return value.trusted === undefined || value.trusted
  }

  isAutoApprove = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })
    return value?.autoApprove || false
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

**File:** features/wallet/module/wallet.js (L231-259)
```javascript
  create = makeConcurrent(
    async ({ mnemonic, passphrase } = {}) => {
      mnemonic = mnemonic || (await generateMnemonic({ bitsize: 128 }))

      const dateCreated = this.#clock.now()
      const seedBuffer = await mnemonicToSeed({ mnemonic, format: 'buffer', validate: false })
      const seed = { mnemonic, seed: seedBuffer, dateCreated }
      const seedId = await getSeedId(seedBuffer)

      await this.#setSeed({ seed, passphrase })

      this.#seedMetadataAtom.set((previous) => ({
        ...previous,
        [seedId]: { dateCreated },
      }))

      return { seedId }
    },
    { concurrency: 1 }
  )

  import = makeConcurrent(
    async ({ mnemonic, passphrase }) => {
      await assertMnemonic(mnemonic, this.#validMnemonicLengths)

      return this.create({ passphrase, mnemonic })
    },
    { concurrency: 1 }
  )
```
