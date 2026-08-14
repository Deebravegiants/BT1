### Title
Unvalidated caller-supplied `origin` in `@exodus/connected-origins` module allows cross-origin trust/account privilege bleed - (File: features/connected-origins/module/connections.js)

### Summary
The `ConnectedOrigins` module treats the `origin` string as a pure data key supplied by the RPC caller, never cross-checking it against the actual authenticated origin of the calling web page/tab. This mirrors the referenced `OVM_FraudVerifier` bug class: a field that should carry authoritative provenance (`l1QueueOrigin` in the original report, `origin` here) is accepted at face value from untrusted input instead of being derived/verified from the trusted channel, allowing an attacker to spoof provenance and cross a trust boundary.

### Finding Description
`connectedOrigins.add`, `isTrusted`, `isAutoApprove`, `connect`, `disconnect`, `setAutoApprove`, `updateConnection`, and `getConnectedAccounts` all accept `{ origin }` directly as a parameter and use it as the sole key for trust decisions, with no verification that it matches the real origin of the caller: [1](#0-0) [2](#0-1) [3](#0-2) 

These module methods are exposed verbatim as RPC-callable API surface via `connectedOriginsApi`, with no additional origin-binding wrapper: [4](#0-3) 

Tracing the RPC path from an untrusted web page to the background: the in-page injected provider (`inapp.js`) forwards a `window.postMessage`-based call to the content script (`content.js`), which relays it into `@exodus/browser-extension-channels` and ultimately to the background RPC exposing `connectedOriginsApi`'s methods. The only metadata attached along that path is `senderMetadata` (title/icon), not a verified origin: [5](#0-4) [6](#0-5) 

Because nothing in this call chain constrains the `origin` argument to the sender's real page origin, a malicious website can invoke `exodus.connectedOrigins.isTrusted({ origin: 'some-other-trusted-site.com' })`, `getConnectedAccounts({ origin: 'some-other-trusted-site.com' })`, or even `connectedOrigins.add({ origin: 'some-other-trusted-site.com', trusted: true, autoApprove: true, connectedAssetName, walletAccount })` while running under a completely different real origin. `getConnectedAccounts` in particular discloses wallet account addresses for any `origin` string once it is marked `trusted`, with no re-validation against the real requester: [3](#0-2) 

This is directly analogous to the `OVM_FraudVerifier`/`OVM_CanonicalTransactionChain` bug: the `l1QueueOrigin` field was accepted from the untrusted transaction submitter without validating it against the true enqueue origin, letting a malicious actor spoof provenance and break invariants downstream. Here, the `origin` field plays the same authoritative-provenance role (which sites are allowed to see accounts / auto-approve), and is likewise accepted unchecked from the caller side of the trust boundary (dApp ↔ extension background).

### Impact Explanation
If exploitable end-to-end (see caveat below), a malicious website could:
- Mark itself as `trusted`/`autoApprove` under an arbitrary origin string, bypassing user-approval popups for future connection requests claiming that origin.
- Call `getConnectedAccounts({ origin: <spoofed-trusted-origin> })` to read out wallet account addresses associated with a different, legitimately-trusted dApp connection, without ever having gone through the real approval flow for that origin.
- Pollute or corrupt the `connectedOrigins` persisted list (shared UI trust state) by injecting fabricated origin entries, affecting what the extension UI displays as "connected sites."

This is a cross-origin privilege bleed within the RPC bridge trust boundary: the module is designed so that only a site whose real origin matches the record should get treated as trusted/auto-approved, but the field is never bound to a verified sender identity.

### Likelihood Explanation
Likelihood depends on whether an outer layer (e.g., the popup/background message-handling code that decides when to call `connectedOrigins.add`/`connect`, which was not found within the indexed portion of this repository) independently binds `origin` to the real `sender`/`event.origin` before invoking these module methods. Within the code reachable and indexed here, `connectedOriginsApi` exposes these methods directly and unconditionally to RPC callers, and the RPC/channel bridge code inspected (`browser-extension-rpc`, `browser-extension-channels`) does not perform or enforce such binding. I could not locate the concrete `web3-providers`/background handler code (e.g., an `ethereum-provider`/`solana-provider` background module) that calls these methods to confirm whether it authoritatively passes `sender.tab.url`/`event.origin` rather than an attacker-suppliable value — this file was not found in the indexed content, so exploitability of the exact call site is unconfirmed.

### Recommendation
- Derive the `origin` used by `ConnectedOrigins` exclusively from the verified RPC/message sender context (e.g., `sender.tab.url`'s origin or the `postMessage` `event.origin`), never from a caller-supplied field in the RPC parameters.
- If `origin` must be passed as a parameter for internal convenience, validate it server-side against the trusted sender-derived origin before executing `add`, `connect`, `isTrusted`, `isAutoApprove`, or `getConnectedAccounts`.
- Add tests asserting that a caller cannot invoke these APIs with an `origin` different from its authenticated channel origin.

### Proof of Concept
Not independently reproducible from the indexed codebase alone: the popup/background wiring that calls into `connectedOrigins.add`/`connect` from a real `web3-providers` connection-approval flow (which would show whether `origin` is bound to `sender`/`event.origin` before being handed to the module) is not present in the indexed files. Based on the code that is available, the conceptual PoC is:
```js
// From a malicious page's injected provider context
await window.exodus.request({
  method: 'connectedOrigins.add',
  params: [{ origin: 'https://trusted-dapp.example', trusted: true, autoApprove: true, connectedAssetName: 'solana' }]
})
// Later, still from the malicious page:
const accounts = await window.exodus.request({
  method: 'connectedOrigins.getConnectedAccounts',
  params: [{ origin: 'https://trusted-dapp.example' }]
})
```
This should be treated as unconfirmed pending review of the background handler that mediates real dApp connection requests, since Devin could not access that file within the current index.

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

**File:** libraries/browser-extension-rpc/inapp.js (L1-16)
```javascript
import RPC from '@exodus/json-rpc'
import { createWindowRpcTransport } from '@exodus/window-rpc-transport'

export const createRPC = ({ extensionName, channelName }) => {
  if (typeof extensionName !== 'string' || typeof channelName !== 'string') {
    throw new TypeError(`Unable to create RPC because channelName or extensionName are missing`)
  }

  const contentTransport = createWindowRpcTransport({
    name: `${extensionName}-${channelName}-window`,
    target: `${extensionName}-${channelName}`,
  })
  return new RPC({ transport: contentTransport })
}


```

**File:** libraries/browser-extension-rpc/content.js (L14-41)
```javascript
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
