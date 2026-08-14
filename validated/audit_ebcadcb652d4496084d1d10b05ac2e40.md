### Title
Missing caller-authorization checks in `ConnectedOrigins` module allow any RPC caller to trust/auto-approve arbitrary origins - (File: features/connected-origins/module/connections.js)

### Summary
The `ConnectedOrigins` module (`features/connected-origins/module/connections.js`) exposes state-mutating methods such as `add`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, and `untrust` directly via `connectedOriginsApiDefinition` [1](#0-0)  with no verification of who is invoking them or that the caller-supplied `origin` string corresponds to the actual message sender. This mirrors the `RM_UpdateReward` bug class: a function intended to be gated behind a privileged/attested flow (a user-approved dApp connection popup) is instead reachable by any caller that can reach the RPC surface, with the security-critical parameter (`origin`, analogous to the reward-manager identity) taken entirely at face value.

### Finding Description
`ConnectedOrigins.add()` accepts an arbitrary `origin`, `trusted`, and `autoApprove`-adjacent state and persists it without any authentication of the caller [2](#0-1) . Likewise, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, and `updateConnection` all trust the caller-supplied `origin` field and mutate the persisted trust state (`#connectedOriginsAtom`) purely based on data existing for that origin key — they never check that the request actually originated from that origin [3](#0-2) .

These methods are exported unmodified through `connectedOriginsApi`, which simply re-exposes the module's methods as-is: `add: connectedOrigins.add`, `setAutoApprove: connectedOrigins.setAutoApprove`, `connect: connectedOrigins.connect`, etc. [4](#0-3) . This API is resolved into the IoC container and becomes callable over the SDK's generic method-dispatch RPC layer (`@exodus/sdk-rpc`), which flattens any nested API object into RPC-callable method names with no built-in per-method access control — `exposeMethods`/`callMethod` blindly dispatch to whatever is registered [5](#0-4) , and the browser-extension transport (`libraries/browser-extension-rpc/src/index.js`) wires up this RPC purely based on port connection, not per-call origin validation [6](#0-5) .

By contrast, `getConnectedAccounts` at least performs an `isTrusted` check before returning sensitive address data [7](#0-6) , showing the module's authors were aware trust boundaries mattered here — yet the corresponding *write* operations (`add`, `setAutoApprove`, `untrust`, `connect`) have no analogous check that the caller is authorized to mutate trust/connection state for the given `origin`.

### Impact Explanation
If this RPC surface is reachable by content-script/dApp-facing code (as the `@exodus/sdk-rpc` design explicitly supports wrapping wallet APIs for cross-process RPC consumption, per its README examples of exposing SDK methods over RPC transports) [8](#0-7) , a malicious website could call `connectedOrigins.add({ origin: 'attacker.com', trusted: true, autoApprove: true, connectedAssetName: 'solana' })` and immediately be marked trusted/auto-approved, bypassing the intended user-facing connection popup described in the Web3 provider docs (`solana.connect()` is documented to require a user-approved pop-up) [9](#0-8) . This would let an attacker's origin silently gain the "trusted"/"auto-approve" flag, exposing wallet account addresses via `getConnectedAccounts` (since it checks only `isTrusted`, which the attacker just set to `true`) without any real user consent — a direct authorization-bypass affecting the dApp connection trust boundary.

### Likelihood Explanation
Likelihood depends on whether this API is exposed to untrusted content-script/webpage-originated RPC calls versus only trusted background/UI-process calls in the shipped browser-extension/mobile builds. I was not able to fully confirm, within the indexed code, the exact process boundary that gates which processes can call `connectedOriginsApi` methods (e.g., whether a content-script-to-background bridge restricts which method namespaces a dApp-injected provider can invoke). The module and API layer themselves clearly lack per-call authorization, which is the root cause identified, but confirming full end-to-end reachability from an untrusted webpage would require inspecting the browser-extension's content-script/background message-routing code, which is not fully available in the indexed context.

### Recommendation
Add explicit authorization checks in `ConnectedOrigins` (or at the API-exposure layer) so that state-mutating methods (`add`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, `untrust`, `updateConnection`) can only be invoked by the trusted extension/UI process, and validate that the `origin` parameter matches the actual sender's origin/tab context rather than trusting a caller-supplied string. Consider separating "read-only, dApp-facing" methods from "privileged, UI-only" methods into distinct API surfaces with different RPC exposure/namespacing so that a compromised or malicious content-script/webpage cannot directly call mutation methods.

### Proof of Concept
Conceptual PoC (pending confirmation of process-boundary exposure):
```js
// From a malicious website whose injected provider bridges to the same RPC surface:
await exodusRpcClient.connectedOrigins.add({
  origin: 'attacker.com',
  name: 'Legit-looking dApp',
  trusted: true,
  autoApprove: true,
  connectedAssetName: 'solana',
})
// No popup is shown because `add`/`setAutoApprove` perform no caller verification
// (features/connected-origins/module/connections.js:140-185, 209-220)
await exodusRpcClient.connectedOrigins.getConnectedAccounts({ origin: 'attacker.com' })
// Returns wallet addresses because isTrusted() now returns true for the attacker's origin
```

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

**File:** features/connected-origins/module/connections.js (L209-291)
```javascript
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

  updateConnection = async ({ origin, icon, connectedAssetName }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) return

    const attributes = {}

    if (icon) {
      attributes.icon = icon
    }

    if (connectedAssetName) {
      attributes.connectedAssetName = connectedAssetName
    }

    await this.#setAttributes({ origin, attributes })
  }
```

**File:** libraries/json-rpc/index.js (L42-71)
```javascript
  exposeMethods(methods) {
    if (!(methods instanceof Map)) {
      methods = Object.entries(methods).reduce(
        (map, [name, impl]) => map.set(name, impl),
        new Map()
      )
    }

    const oldImpl = this._methods
    this._methods = methods
    return oldImpl
  }

  exposeFunction(name, implementation) {
    if (typeof name !== 'string') {
      throw new TypeError('Function name must be a string')
    }

    if (typeof implementation !== 'function') {
      throw new TypeError('Invalid function implementation')
    }

    this._methods.set(name, implementation)
  }

  async callMethod(method, params) {
    const id = this._generateId()
    const request = this._makeRequestObject({ method, params, id })
    return this._sendRequest({ request })
  }
```

**File:** libraries/browser-extension-rpc/src/index.js (L36-67)
```javascript
export const createBackgroundRpc = ({
  name = DEFAULT_PORT_NAME,
  methods,
  serialize,
  deserialize,
  onData,
  onConnect,
  onDisconnect,
}) => {
  const rpcManager = new RPCManager()

  const handlePortConnect = (port) => {
    const id = port.sender.tab?.id || port.sender.documentId

    if (port.name !== name) return

    const rpc = createRpc({ port, methods, serialize, deserialize, onData })

    port.onDisconnect.addListener(() => {
      rpc.end()
      onDisconnect?.()
    })

    rpcManager.add(id, rpc)

    onConnect?.()
  }

  chrome.runtime.onConnect.addListener(handlePortConnect)

  return rpcManager
}
```

**File:** libraries/sdk-rpc/README.md (L11-29)
```markdown
## Usage

This library is ideally to be used as a wrapper around `@exodus/headless` or `@exodus/wallet-sdk` to expose the methods of the SDK to be called over RPC.

```ts
// in the process that instantiates the RPC server
import createWalletSdk from '@exodus/wallet-sdk'
import { RPC } from '@exodus/sdk-rpc'

const rpc = new RPC({
  transport: windowTransport,
})

const walletSdkApi = createWalletSdk({
  // ...deps
}).resolve()

rpc.exposeMethods(walletSdkApi)
```
```

**File:** docs/web3-providers/solana-provider-api.md (L61-64)
```markdown
Use `connect()` to request access to the user's account. This will open a pop-up
asking the user to approve the connection. Upon approval, Exodus will expose the
public key of the user's account via [`solana.publicKey`](#solanapublickey) and
emit a [`connect`](#connect) event.
```
