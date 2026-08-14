### Title
Untrusted RPC callers can invoke `connectedOrigins` privileged methods with an arbitrary/spoofed `origin` argument - ([File: features/connected-origins/api/index.js])

### Summary
The Gondi finding is that `addNewTranche()` performs a privileged, state-mutating action (creating a tranche and moving funds tied to a specific `loan.borrower`) while validating only the counterparty's (`lender`) signature and never checking that the caller (`msg.sender`) is actually the entity the action is being performed on behalf of (`_loan.borrower`). The root-cause pattern is: a sensitive operation takes a "subject" identifier as a plain function argument and never cross-checks it against the actual authenticated caller/context.

`@exodus/connected-origins` shows the same pattern in the wallet's origin-trust boundary. `ConnectedOrigins.add`, `untrust`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, and `getConnectedAccounts` all key their logic exclusively off a caller-supplied `{ origin }` string parameter, with no verification that this string corresponds to the actual dApp/tab that issued the RPC call: [1](#0-0) [2](#0-1) 

These module methods are exposed directly, unwrapped, as RPC API surface: [3](#0-2) 

The API is wired onto the general SDK method table (`rpc.exposeMethods(sdk)`), meaning any code capable of invoking SDK methods over the RPC transport can call `connectedOrigins.add`, `setAutoApprove`, `getConnectedAccounts`, etc. and pass any `origin` string it likes: [4](#0-3) 

### Finding Description
`isTrusted`, `isAutoApprove`, `getConnectedAccounts`, `add`, `connect`, `disconnect`, `untrust`, `setFavorite`, and `setAutoApprove` all resolve which stored origin record to read/mutate purely from the `origin` field the caller supplies: [5](#0-4) 

There is no step anywhere in `ConnectedOrigins` (nor in the exposed API wrapper) that derives `origin` from an authenticated transport-level sender (e.g., `sender.tab`/`sender.url`/`senderMetadata` captured by the content-script channel) and compares it to the caller-supplied value, the way `_baseLoanChecks`/caller checks were supposed to bind `addNewTranche()`'s privileged action to the actual `_loan.borrower`. The RPC/channel layer *does* capture real sender metadata (`libraries/browser-extension-channels/channel.js`, `libraries/browser-extension-rpc/content.js`) but that metadata is not threaded into `connectedOrigins`'s authorization decisions — it is only used for UI display purposes elsewhere in the pipeline. As a result the "subject" of the privileged action (`origin`) is taken entirely at face value from the invoking code, exactly mirroring the missing-borrower-check root cause: a caller-supplied identity parameter is trusted in place of a real caller-identity check.

### Impact Explanation
If a malicious or compromised in-page script (e.g., a malicious website's content script or an npm-supply-chain-compromised third party script running with SDK RPC access) can reach these RPC methods with a spoofed `origin`, it can:
- Call `getConnectedAccounts({ origin: 'reputable-dapp.com' })` to read the addresses that are exposed to a different, higher-trust origin, causing cross-origin account/address disclosure.
- Call `setAutoApprove({ origin: 'reputable-dapp.com', value: true })` to silently flip a legitimate dApp's connection into auto-approve mode, so future signing/transaction requests attributed to that origin bypass the user popup-confirmation flow — a direct path toward unauthorized transaction signing.
- Call `add`/`untrust`/`setFavorite` to corrupt another origin's trust state.

This crosses the same class of boundary the Gondi bug crossed (an operation scoped to one identity/account being performed on behalf of another identity without checking the real caller), and specifically threatens the "cross-origin privilege bleed" / "unauthorized signing enablement" outcomes called out as acceptable impact classes.

### Likelihood Explanation
Exploitability depends entirely on whether an untrusted context (a malicious webpage, not the trusted content-script/extension background boundary) can actually invoke `connectedOrigins.*` RPC methods directly with attacker-chosen parameters, or whether the content-script/page-injected provider strictly forwards only asset-specific, pre-validated calls (e.g., `window.exodus.solana.connect()`) rather than the raw `connectedOrigins` namespace. From the available index, the SDK's RPC exposure mechanism (`rpc.exposeMethods(sdk)`) generically flattens and exposes the entire API surface, including `connectedOrigins`, to whatever is on the other end of the RPC transport, and I could not find code that filters/scopes which methods a given untrusted transport endpoint (vs. the trusted extension UI) may call. This is the key uncertainty: if the content-script/page-provider bridge only exposes a curated subset of methods to web pages (rather than the full `connectedOrigins` API), the practical reachability from an untrusted origin is reduced, and this would be a Medium/context-only issue similar to how Gondi's finding was rated. I was not able to fully trace the page-provider-to-background method whitelist within the indexed files to conclusively confirm or rule out that restriction.

### Recommendation
- In `ConnectedOrigins` (features/connected-origins/module/connections.js), do not trust a caller-supplied `origin` string for privileged/mutating operations (`add`, `untrust`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, `getConnectedAccounts`). Instead, derive `origin` from the authenticated sender context provided by the RPC/channel transport (`sender.tab.url` / `senderMetadata`) and pass it down explicitly rather than accepting it as a free-form parameter.
- At the API boundary (`features/connected-origins/api/index.js`), wrap each exposed method so any `origin` parameter received over an untrusted (page/content-script) transport is overridden/validated against the transport's actual sender origin before being forwarded to the module.
- Ensure the RPC exposure to untrusted page contexts (`rpc.exposeMethods(sdk)`) only whitelists methods intended for dApp consumption and does not blanket-expose internal wallet-management APIs like `connectedOrigins` to page-originated RPC calls; enforce this via an explicit per-transport method allowlist.

### Proof of Concept
Conceptual PoC (subject to the reachability caveat above): a malicious webpage, if it can obtain a reference to the RPC channel used by the extension's provider bridge, calls:
```js
await rpc.callMethod('connectedOrigins.setAutoApprove', [{ origin: 'trusted-dapp.io', value: true }])
await rpc.callMethod('connectedOrigins.getConnectedAccounts', [{ origin: 'trusted-dapp.io' }])
```
Per `ConnectedOrigins.setAutoApprove`/`getConnectedAccounts`, both calls succeed because the module only checks whether an origin record for `'trusted-dapp.io'` exists and is `trusted`, with no verification that the actual caller is `trusted-dapp.io`: [6](#0-5) [7](#0-6) 

This flips `trusted-dapp.io`'s auto-approve flag and discloses its connected account addresses to the malicious page — analogous to how any `lender` could originally add a malicious tranche against any `_loan.borrower` because `addNewTranche()` never checked that the caller was the actual borrower.

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

**File:** features/connected-origins/module/connections.js (L187-220)
```javascript
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

**File:** apps/sdk-minimal-demo/src/__tests__/setup-bg.ts (L1-16)
```typescript
import adapters from '../background/adapters/index'
import config from '../background/config'
import createSDK from '../background/exodus'
import { createProcessRPC, Thread } from './multi-process'

const setupBG = () => {
  const sdk = createSDK({ adapters, config, debug: false })
  const thread = new Thread()
  const { rpc } = createProcessRPC(thread)
  // this deep-traverses the SDK object and exposes all APIs from 'api' nodes
  rpc.exposeMethods(sdk)
  // when the SDK emits an event, broadcast it over RPC to the UI thread
  sdk.subscribe(({ type, payload }: { type: string; payload: any }) => rpc.notify(type, payload))
  return { sdk, thread }
}

```
