### Title
`connectedOrigins.add`/`connect`/`setAutoApprove` lack a lock-state guard, allowing pre-unlock injection of persisted trust/autoApprove state - ([File: features/connected-origins/module/connections.js])

### Finding Description
The `connectedOrigins` module (`features/connected-origins/module/connections.js`) exposes `add`, `connect`, `setAutoApprove`, `setFavorite`, `updateConnection`, `disconnect` etc. through `connectedOriginsApi` [1](#0-0)  with no check on wallet lock state whatsoever. Compare this to the sibling `address-provider` API, which explicitly wraps every sensitive method with `withWalletAccountInstance`, throwing `'address-provider: wallet should be unlocked'` if `lockedAtom.get()` is true [2](#0-1) . No equivalent guard exists in `connectedOrigins`'s `add`, `connect`, or `setAutoApprove` [3](#0-2) [4](#0-3) .

The `connectedOriginsAtom` itself is a persistent storage-backed atom (`createStorageAtomFactory`), not an in-memory atom that gets wiped on lock [5](#0-4) . The `connectedOriginsPlugin`'s `onLoad`/`onUnlock` lifecycle only controls whether the atom *observer* that broadcasts state changes over the `port` starts — it does not gate write access to the underlying module/API at all [6](#0-5) . `onLoad` merely returns early when locked to avoid starting the observer; it does not disable or block the `connectedOrigins` module's methods, which remain reachable via the same public API surface regardless of lock state.

Since `add()` only reads `enabledWalletAccountsAtom` and derives default addresses via `addressProvider.getDefaultAddress` (public-key/address derivation, not signing) [7](#0-6) , none of these operations inherently require the seed to be unlocked in the keychain, so there's no natural failure blocking the call while locked.

If an attacker-controlled dapp/RPC caller can invoke `connectedOrigins.add({ origin, trusted: true, autoApprove: true })` (or a subsequent `setAutoApprove`/`connect` call) while `isLocked` is true, the write persists directly to durable storage via `#setData` → `connectedOriginsAtom.set(data)` [8](#0-7) . Upon unlock, `isTrusted` and `isAutoApprove` read this persisted state without any re-validation step tied to the unlock event [9](#0-8) , and `onUnlock` only starts the observer and subscribes to account updates — it never re-audits or purges connections created while locked [10](#0-9) .

### Impact Explanation
An attacker origin can pre-seed `trusted: true` and `autoApprove: true` for itself while the wallet is locked. As soon as the legitimate user unlocks the wallet, any subsequent connect/signing request from that origin will be auto-approved without the normal approval prompt (since `isAutoApprove`/`isTrusted` are consulted by the signing/connect approval flow), letting the attacker page silently connect to and interact with the user's wallet accounts immediately post-unlock. This is a privilege-persistence / origin-trust bypass, not a key-disclosure or signing bypass, since actual transaction signing still goes through the keychain (which requires unlock/authorization for the seed itself).

### Likelihood Explanation
The likelihood depends on whether an unprivileged dapp/RPC caller can actually reach `connectedOrigins.add`/`setAutoApprove` while `isLocked` is true at the port/RPC dispatch layer. I did not find any global RPC/port middleware in `sdks/headless` that blocks all API calls while the wallet is locked; the only lock-gating found is per-API, implemented ad hoc (e.g., in `address-provider/api/index.js`). Since `connectedOrigins` has no equivalent guard, if the RPC entry point does route inbound dapp calls to this API while locked, the attack is directly reachable and repeatable with a simple integration test. I was unable to fully confirm from the indexed code whether a higher-level gate (e.g., in the browser-extension/mobile background service, port permission layer, or a wrapper not indexed here) blocks calls before dispatch while locked — this could not be conclusively ruled out given index coverage limits.

### Recommendation
Add an explicit lock-state guard to `connectedOrigins` module methods that mutate trust/auto-approve state (`add`, `connect`, `setAutoApprove`, `setFavorite`, `updateConnection`), mirroring the pattern used in `features/address-provider/api/index.js` (checking a `lockedAtom`/`isLocked` dependency and throwing before performing any write). Additionally, on `onUnlock`, re-validate or require re-confirmation of any `trusted`/`autoApprove` entries whose `createdAt` timestamp is newer than the last successful unlock, to eliminate any residual race window.

### Proof of Concept
Integration test in `features/connected-origins/module/__tests__/connections.test.js` style:
1. Construct `connectedOrigins` module with `enabledWalletAccountsAtom`, `connectedOriginsAtom` (persistent-style in-memory atom), and a `lockedAtom` (or a wallet mock) set to `isLocked = true`.
2. Call `await connectedOrigins.add({ origin: 'https://evil.example', trusted: true, autoApprove: true })`.
3. Assert this call throws/is rejected while `isLocked === true` (expected fixed behavior) — currently it will succeed and write to `connectedOriginsAtom`.
4. Simulate unlock (`isLocked = false`, trigger `onUnlock`).
5. Assert `connectedOrigins.isTrusted({ origin: 'https://evil.example' })` and `isAutoApprove({ origin: 'https://evil.example' })` are `false`/require re-approval post-unlock, rather than reflecting the pre-unlock-injected `true` values.

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

**File:** features/connected-origins/module/connections.js (L198-232)
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
