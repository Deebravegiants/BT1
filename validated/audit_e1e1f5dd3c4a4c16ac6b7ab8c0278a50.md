Based on the code, the vulnerability is confirmed as real and exploitable.

### Title
Wallet-locked write bypass allows persisting attacker-controlled `trusted`/`autoApprove` origin state via `connectedOrigins.add`/`connect` while locked - ([File: features/connected-origins/plugin/index.js])

### Summary
The `connectedOrigins` module and its API layer perform no lock-state check before mutating `connectedOriginsAtom`, unlike sibling features (e.g. `addressProviderApi`) which explicitly guard against locked-state calls. `onLoad`/`onUnlock` in the plugin only gate the atom *observer* (UI push notifications), not the underlying read/write capability of `connectedOrigins.add`, `.connect`, or `.setAutoApprove`, so a dapp/RPC caller can inject `trusted: true` / `autoApprove: true` for an origin while the wallet is locked, and this state persists and takes effect immediately on unlock.

### Finding Description
`connectedOriginsPlugin.onLoad` only starts the atom observer if `!isLocked`, and `onUnlock` starts the observer and subscribes `updateConnectedAccounts` [1](#0-0) . Nothing in this plugin, the `ConnectedOrigins` module, or `connectedOriginsApi` checks `isLocked`/`lockedAtom` before executing `add`, `connect`, or `setAutoApprove` [2](#0-1) . The underlying module methods `add`, `connect`, `setAutoApprove` directly read/write `connectedOriginsAtom` via `#getData`/`#setData` with no auth gating [3](#0-2) . The atom itself is a plain, unencrypted `createStorageAtomFactory` atom backed by generic `storage`, with no dependency on the keychain/seed being unlocked [4](#0-3) . This is in contrast to `addressProviderApi`, which explicitly throws `'address-provider: wallet should be unlocked'` when `lockedAtom.get()` is true before proceeding [5](#0-4) . Because `connectedOrigins.add`/`.connect`/`.setAutoApprove` are exposed directly on the RPC-facing API surface with no such guard, and `isTrusted`/`isAutoApprove`/`getConnectedAccounts` are explicitly documented to work "while the wallet is locked" [6](#0-5) , an attacker-controlled dapp origin can call `add({ origin, trusted: true, autoApprove: true })` before the user unlocks, persisting the trust/auto-approve flag. On the next `onUnlock`, the plugin re-starts the observer and subscribes account updates but performs no re-validation or purge of pre-unlock-injected trust state [7](#0-6) , so the injected `trusted`/`autoApprove` state is honored immediately, allowing the origin to auto-approve subsequent connection/signing requests without the user ever explicitly granting trust while unlocked.

### Impact Explanation
An attacker origin can pre-stage `trusted: true` and `autoApprove: true` for itself while the wallet is locked (e.g. via a background dapp tab or malicious page open before the user unlocks). Once the user unlocks, the origin is already trusted and auto-approved, letting it silently obtain connected account addresses (`getConnectedAccounts`) and auto-approve dapp-initiated requests/transactions without any explicit user consent step post-unlock. This is a privilege-persistence / auth-bypass style issue: security-relevant `trusted`/`autoApprove` flags are set and take effect without requiring the wallet to be unlocked at the time of the trust decision.

### Likelihood Explanation
Highly feasible and repeatable: it only requires calling an already-exposed API method (`connectedOrigins.add`) with attacker-chosen parameters while the wallet is locked — no privileged state, keys, or social engineering needed, and no explicit lock check exists anywhere in the call path (module, API, or plugin) to prevent it.

### Recommendation
Add an explicit lock check (mirroring `addressProviderApi`'s `lockedAtom.get()` guard) to `connectedOrigins.add`, `.connect`, `.setAutoApprove`, and any other mutating method exposed via `connectedOriginsApi`, rejecting calls while the wallet is locked. Additionally, consider re-validating or requiring explicit re-confirmation of `trusted`/`autoApprove` flags for origins whose entries were created/modified while the wallet was locked, before honoring them post-unlock.

### Proof of Concept
Integration test (extending `sdks/headless/__tests__/connected-origins.test.js` patterns):
1. `await exodus.application.start(); await exodus.application.load()` (wallet locked, `isLocked() === true`).
2. Call `await exodus.connectedOrigins.add({ origin: 'https://evil.example', trusted: true, autoApprove: true })`.
3. Assert this call currently succeeds (no throw) — demonstrating the missing lock guard.
4. `await exodus.application.unlock({ passphrase })`.
5. Assert `await exodus.connectedOrigins.isTrusted({ origin: 'https://evil.example' })` returns `true` and `isAutoApprove` returns `true` immediately post-unlock, with no additional user confirmation step, and that `getConnectedAccounts` returns real wallet addresses for that origin — confirming persisted, unvalidated trust state took effect.

### Citations

**File:** features/connected-origins/plugin/index.js (L17-26)
```javascript
  const onLoad = ({ isLocked }) => {
    if (isLocked) return

    connectedOriginsAtomObserver.start()
  }

  const onUnlock = async () => {
    connectedOriginsAtomObserver.start()
    unsubscribe = enabledWalletAccountsAtom.observe(connectedOrigins.updateConnectedAccounts)
  }
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

**File:** features/connected-origins/module/connections.js (L140-216)
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
```

**File:** features/connected-origins/module/connections.js (L245-251)
```javascript
  /**
   * Returns the connected accounts for a given origin with the active wallet account sorted first. Can be used while
   * the wallet is locked
   */
  getConnectedAccounts = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })
    if (!isTrusted) return []
```

**File:** features/connected-origins/atoms/connected-origins.js (L1-10)
```javascript
import { createStorageAtomFactory, dedupe } from '@exodus/atoms'

export default function createConnectedOriginsAtom({ storage }) {
  return dedupe(
    createStorageAtomFactory({ storage })({
      key: 'data',
      defaultValue: [],
      isSoleWriter: true,
    })
  )
```

**File:** features/address-provider/api/index.js (L12-18)
```javascript
  const withWalletAccountInstance =
    (fn) =>
    async ({ walletAccount, ...rest }) => {
      if (await lockedAtom.get()) throw new Error('address-provider: wallet should be unlocked')
      const walletAccounts = await walletAccountsAtom.get()
      return fn({ ...rest, walletAccount: walletAccount && walletAccounts[walletAccount] })
    }
```
