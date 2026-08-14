### Title
`connectedOrigins.add()` and related methods trust a caller-supplied `origin` string with no verification against the actual message sender - (File: `features/connected-origins/module/connections.js`)

### Summary
The CNote bug is a classic "unauthenticated setter" — a function that grants a privileged role (`accountant`/`admin`) based purely on whoever calls it first, with no check that the caller is entitled to that role. Searching the Hydra/Exodus wallet codebase for an analogous unprivileged-caller-controls-identity pattern, the closest reachable analog is the `connectedOrigins` module, whose public API (`add`, `connect`, `disconnect`, `setAutoApprove`, `updateConnection`, `isTrusted`, `getConnectedAccounts`) is entirely keyed off an `origin` string parameter that is supplied by the caller rather than derived/verified by the RPC layer.

### Finding Description
`ConnectedOrigins#add` and its sibling methods take `{ origin, ... }` as an argument and use it directly as the lookup/storage key for trust and connection state, with no cross-check that `origin` matches the identity of the actual message sender: [1](#0-0) [2](#0-1) 

These module methods are exposed almost verbatim as an RPC-callable API surface via `connectedOriginsApi`, with no additional origin-binding/authorization wrapper applied before forwarding to the module: [3](#0-2) 

The underlying RPC transport (`@exodus/browser-extension-rpc` / `@exodus/sdk-rpc`) exposes methods generically over a port/channel and, in the code visible in the index, does not appear to bind an authenticated/verified sender origin into the call parameters before invoking the exposed method — the `senderMetadata` captured in the content script is only title/icon metadata, not a hardened origin claim enforced at the RPC boundary: [4](#0-3) [5](#0-4) 

If any code path invokes `connectedOrigins.add` (or `connect`/`setAutoApprove`) using an `origin` value that originates from the calling page's own claim (e.g. a `postMessage`/provider-injected request parameter) rather than a value independently derived from the actual browser tab/sender, an unprivileged dApp could self-report a different, more-trusted `origin` string (e.g. `"exodus.com"` or another popular protocol's domain) and inherit that origin's trust/auto-approve state and connected accounts, exactly analogous to the CNote bug where an unprivileged caller can claim a privileged identity because the setter never validates who is entitled to set it.

### Impact Explanation
If reachable through the provider/RPC entry point without independent origin binding, this allows an unprivileged site to:
- Mark itself as `trusted`/`autoApprove` for a wallet account without real user approval (bypassing the "eagerly connect"/`onlyIfTrusted` flow described for the Solana provider) [6](#0-5) 
- Read `getConnectedAccounts` addresses for a wallet account under an impersonated origin, or hijack `activeConnections` state of another origin via `connect`/`disconnect`.

This maps to the "cross-origin/account privilege bleed" impact bucket: unauthorized origin gains trusted-dApp status and account-connection state that should only be attainable by the real origin, paralleling the "anyone can become accountant/admin" root cause (missing access control on a state-mutating identity-setting function).

### Likelihood Explanation
Exploitability depends entirely on whether the RPC/provider boundary that ultimately calls `connectedOrigins.add`/`connect` binds `origin` to the verified sender (tab URL / content-script origin) before invoking the module, or instead passes through an origin value that is controllable by the calling page's script. From the visible RPC/content-script code, the boundary only forwards generic method calls and lightweight `senderMetadata` (title/icon) without an enforced, tamper-proof origin binding at this layer, which is exactly the pattern that would need to be checked before trusting the module boundary as authorization. I could not locate the exact call site in the dApp-provider/background feature that constructs the `origin` argument passed into `connectedOrigins.add`, so I cannot confirm with certainty whether an upstream layer (outside what indexing surfaced) already pins `origin` to the verified sender before this point. Given index size limits, some file contents (e.g. the dApp-provider background handler that wires the provider's `connect()` call to `connectedOrigins.add`) may not be fully available to me — a full-repo grep in a Devin session for the call sites of `connectedOrigins.add`/`.connect` outside of tests would be needed to confirm whether `origin` is attacker-controlled at the actual RPC entry point.

### Recommendation
- Derive `origin` exclusively from a verified, non-spoofable source (e.g., the browser extension's `sender.tab.url`/`sender.origin` captured server-side by the background RPC dispatcher), never from a parameter supplied inside the RPC call payload by the requesting page.
- Add an explicit assertion in `ConnectedOrigins#add`/`connect`/`setAutoApprove` (or in the RPC exposure layer wrapping `connectedOriginsApi`) that the `origin` argument matches the RPC-verified sender before mutating trust/auto-approve/connection state.
- As with the CNote fix, keep the setter minimal in privilege: don't let a single unauthenticated call establish both "connection" and "trust"/"autoApprove" state — require an explicit, UI-mediated approval step for trust escalation.

### Proof of Concept
Conceptual (cannot fully verify without the missing call-site code, per Likelihood section):
1. A malicious website's injected page script calls the wallet's exposed provider API method that internally calls `connectedOrigins.add({ origin, connectedAssetName, trusted, ... })`.
2. If the `origin` parameter is taken from data controlled by the requesting page's message (rather than a background-derived, verified sender origin), the malicious page sets `origin: 'exodus.com'` (or any target origin) instead of its own.
3. `ConnectedOrigins#add` performs no verification of `origin` against the actual sender and persists the entry as if the trusted origin itself made the request: [7](#0-6) 
4. Subsequent `isTrusted`/`isAutoApprove`/`getConnectedAccounts` calls for that `origin` now return the impersonated trusted/auto-approve state, exposing account addresses or bypassing the connect-approval popup for that origin.

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

**File:** features/connected-origins/module/connections.js (L198-216)
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

**File:** libraries/browser-extension-rpc/content.js (L1-41)
```javascript
import channels from '@exodus/browser-extension-channels'
import { createWindowRpcTransport } from '@exodus/window-rpc-transport'

import { getIcon, getTitle } from './src/metadata.js'

const metadata = new Promise((resolve) => {
  window.addEventListener('load', async () => {
    const title = getTitle()
    const icon = await getIcon()
    resolve({ title, icon })
  })
})

export const createRPCProxy = ({ extensionName, channelName }) => {
  if (typeof extensionName !== 'string' || typeof channelName !== 'string') {
    throw new TypeError(`Unable to create RPC because channelName or extensionName are missing`)
  }

  const channel = channels[channelName]
  const transport = createWindowRpcTransport({
    name: `${extensionName}-${channelName}`,
    target: `${extensionName}-${channelName}-window`,
  })

  transport.on('data', async (event) => {
    const isResponse = !JSON.parse(event).method
    const senderMetadata = await metadata
    const options = { senderMetadata }

    if (isResponse) {
      channel.sendMessage(event, options)
    } else {
      channel.call(event, options).then(transport.write)
    }
  })

  channel.onMessage((message, sender) => {
    if (sender.tab) return
    transport.write(message)
  })
}
```

**File:** docs/web3-providers/solana-provider-api.md (L80-102)
```markdown
#### Eagerly Connecting

After the user approves a Web3 site's connection to Exodus, the site becomes
trusted. This allows the site to automatically connect to Exodus on subsequent
visits or page refreshes. This is referred to as "eagerly connecting".

If you want to try to eagerly connect, you can pass the `onlyIfTrusted` option
to `connect()`.

```typescript
try {
  await window.exodus.solana.connect({ onlyIfTrusted: true })
} catch (err) {
  // { code: 4001, message: 'User rejected the request.' }
}
```

:::tip

When using this flag, Exodus will only connect if the site is trusted and won't
bother your users with a pop-up if they have not connected to Exodus before.

:::
```
