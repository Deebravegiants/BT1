### Title
Unsynchronized read-modify-write races in `ConnectedOrigins` allow an untrusted origin to nullify user revocation of dApp access - (File: `features/connected-origins/module/connections.js`)

### Summary
`ConnectedOrigins` stores per-origin trust/connection state (`trusted`, `autoApprove`, `activeConnections`, etc.) using a plain read-then-write pattern with no concurrency control. Every mutator (`add`, `untrust`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, `updateConnection`) reads the full array from `#connectedOriginsAtom`, computes a new array in memory, then writes the whole array back. Because none of these operations are serialized (unlike other modules in the same codebase that explicitly wrap similar state updates in `makeConcurrent`), two concurrent calls produce a lost-update race analogous to the `change_gauge_weight` front-running bug: a privileged action (the user revoking a site's access) can be raced and effectively undone by an unprivileged actor (a connected website) re-adding/re-connecting itself before the revoke's write lands, or vice versa.

### Finding Description
`#setAttributes`, `#setData`, `add`, and `untrust` in `features/connected-origins/module/connections.js` follow this pattern: [1](#0-0) [2](#0-1) 

Every mutating method (`add`, `untrust`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, `updateConnection`) calls `#getData()`/`#getOrigin()` to read the current snapshot, computes a modified copy, and calls `#setData`/`#setAttributes` to overwrite storage with the whole array. None of these methods share a lock or are wrapped in `makeConcurrent`, unlike comparable state-mutation code elsewhere in the repo that explicitly guards against this race, e.g. `features/enabled-assets/module/index.js` (`#setAssetsEnabled = makeConcurrent(...)`) and `features/wallet-accounts/src/module/wallet-accounts.ts` (`#replaceAll = makeConcurrent(..., { concurrency: 1 })`), and even explicitly documents the danger: [3](#0-2) [4](#0-3) 

These methods are exposed directly through the public API surface reachable from a connected dApp/website (an unprivileged, remote origin) and from the wallet UI (the "admin"/user side): [5](#0-4) 

Because `untrust` (user revoking access — the analog of `change_gauge_weight`) and `add`/`connect` (a website (re-)establishing trust/connection — the analog of `vote_for_gauge_weights`) both perform unsynchronized read→compute→write cycles on the same underlying atom, interleaving them causes a classic TOCTOU lost update: if `untrust`'s read happens before a concurrent `add`/`connect` write completes, `untrust`'s final `#setData(newData)` (computed from the stale, pre-add snapshot) can overwrite and silently discard the just-connected state, or conversely a racing `add`/`connect` write issued right after the revoke's read can restore the (deleted) origin entry once `untrust`'s stale write lands, leaving the origin trusted/connected again despite the user's revoke action having "succeeded".

### Impact Explanation
This breaks the account/origin isolation trust boundary the module is meant to enforce: the list of `connectedOrigins` gates whether a website can call `getConnectedAccounts`/receive addresses and remain "connected" without further approval (`autoApprove`/`trusted`). If a malicious or compromised website races its own `connect`/`add` calls against a user's `untrust`/`disconnect` action (e.g. triggered from the wallet UI's revoke-access flow), it can retain its trusted/connected state, silently regaining access to wallet accounts and addresses after the user believed access was revoked. This is the same class of impact as the referenced report: a "set"-style overwrite operation racing against concurrent legitimate mutations changes the final privilege state to something the initiator did not intend.

### Likelihood Explanation
The race requires the dApp's script (fully attacker-controlled, since it runs on the connected origin) to fire concurrent RPC calls (`connect`, `add`) timed against the user's revoke action, which is plausible for any origin that is actively loaded/scripted while the user browses to wallet settings to revoke it — no special privileges or mempool visibility are needed (unlike the on-chain original), just ordinary concurrent async calls into the same wallet backend, which the origin can trigger at will while connected.

### Recommendation
Serialize all mutating operations on `ConnectedOrigins` state (wrap `add`, `untrust`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, `updateConnection`, `clearConnections` in a single `makeConcurrent`/mutex, similar to `enabled-assets` and `wallet-accounts`), or perform atomic compare-and-swap updates keyed by origin rather than whole-array read/replace, so that a revoke (`untrust`) cannot be raced and undone by a concurrent `add`/`connect` from the same origin.

### Proof of Concept
1. User has connected `exodus.com` (`trusted: true`).
2. User initiates `connectedOrigins.untrust({ origin: 'exodus.com' })` from the UI to revoke access; this call performs `isTrusted` → `#getData()` → filters origin out → is about to `#setData(newData)`.
3. Before that write lands, the still-running dApp script on `exodus.com` calls `connectedOrigins.connect({ id, origin: 'exodus.com' })` (or `add(...)` for eager reconnection), which does its own `#getOrigin` read (still sees the origin as present) → `#setAttributes` → `#setData(dataWithConnection)`.
4. Whichever write resolves last wins: if the dApp's `connect`/`add` write lands after `untrust`'s stale-based write, the origin re-appears in `connectedOriginsAtom` as trusted/connected — effectively nullifying the user's revoke, mirroring how the front-run `vote_for_gauge_weights` calls landed after `change_gauge_weight` in the original report to produce an unintended final state. [6](#0-5)

### Citations

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

**File:** features/connected-origins/module/connections.js (L140-243)
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

  untrust = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })

    if (!isTrusted) return

    const data = await this.#getData()
    const newData = data.filter((connection) => connection.origin !== origin)

    await this.#setData(newData)
  }

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

  setAutoApprove = async ({ origin, value }) => {
    return this.#setAttributes({ origin, attributes: { autoApprove: value } })
  }

  setFavorite = async ({ origin, value, assetNames = [] }) => {
    return this.#setAttributes({ origin, attributes: { favorite: value, assetNames } })
  }

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

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L265-268)
```typescript
      // Warning: the following code between reading from currentWalletAccounts and writing back to it
      // needs to remain sync until this.#save or may lead to concurrency issues. "await" yields execution
      // and may allow .update(), .create(), etc to execute before
      // fusion syncing is done.
```

**File:** features/enabled-assets/module/index.js (L95-117)
```javascript
  #setAssetsEnabled = makeConcurrent(async (enabledByAssetName) => {
    if (Object.keys(enabledByAssetName).length === 0) return

    const storageData = await this.#enabledAndDisabledAssetsAtom.get()
    const disabledByAssetName = mapValues(enabledByAssetName, (enabled) => !enabled)
    if (
      Object.keys(disabledByAssetName).every(
        (assetName) => storageData.disabled[assetName] === disabledByAssetName[assetName]
      )
    ) {
      this.#logger.debug('prevent enabling already enabled assets', enabledByAssetName)
      return
    }

    const newStorageData = {
      ...storageData,
      disabled: {
        ...storageData.disabled,
        ...disabledByAssetName,
      },
    }
    await this.#enabledAndDisabledAssetsAtom.set(newStorageData)
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
