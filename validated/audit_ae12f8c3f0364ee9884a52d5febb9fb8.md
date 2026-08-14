### Title
`connectedOrigins.add()` Accepts a Caller-Supplied `trusted` Flag With No Server-Side Validation, Allowing Unauthorized Cross-Origin Trust/Auto-Approval Escalation - (File: `features/connected-origins/module/connections.js`)

### Summary
`ConnectedOrigins.add()` takes a `trusted` boolean directly from its caller and persists it verbatim into the `connectedOriginsAtom` store, exactly like `Vether.addExcluded()` let any caller flip a security-relevant flag (`mapAddress_Excluded`) for themselves with no authorization check. Here, `trusted` (and `isTrusted()`/`getConnectedAccounts()` gate wallet-account address disclosure on it) is likewise settable by whoever can invoke `add`, with no check that the request actually originated from a privileged, user-approved flow.

### Finding Description
`add()` in `features/connected-origins/module/connections.js` destructures `trusted` straight from its input and writes it into the stored origin record without any authorization/approval-flow check: [1](#0-0) 

This `trusted` flag is the sole authorization gate used by `isTrusted()` and `getConnectedAccounts()` to decide whether an origin may read the user's connected wallet addresses without further prompting: [2](#0-1) [3](#0-2) 

`add` (along with `trusted`) is exposed unmodified through the public `connectedOriginsApi`, with no wrapping guard restricting who can supply `trusted: true`: [4](#0-3) 

This mirrors the Vether analog precisely: `addExcluded()` had no restriction on who could set the privileged flag for an address; `add()` has no restriction on who supplies `trusted` for an origin. Documentation confirms `trusted` is meant to be set only after the user approves a connection popup, i.e., it is intended to be a privileged flag set exclusively by the trusted extension/background flow after user consent, not by the RPC caller's raw input: [5](#0-4) 

### Impact Explanation
I was not able to fully verify, within the scope of this index, that an actual unprivileged/cross-origin caller (e.g., a webpage via the in-page provider RPC bridge) can invoke `connectedOriginsApi.add` directly with an attacker-controlled `trusted: true`. The `add` method itself is provably unguarded at the module level, but confirming the full RPC exposure surface (whether `connectedOriginsApi` is exposed to the in-page/content-script bridge in `libraries/browser-extension-rpc` or only to the trusted extension UI process) requires inspecting the RPC method-exposure wiring in the background script, which I could not fully trace with the available search results. If `add` is reachable from the untrusted web page/content-script boundary, the impact is a full authorization bypass: any website could mark itself `trusted: true` and call `getConnectedAccounts()` to read all of the user's wallet addresses across accounts without any approval popup, and could gain `autoApprove`-adjacent trust status for future connections — a direct violation of the origin-isolation trust boundary the feature is designed to enforce.

### Likelihood Explanation
Uncertain/Medium — contingent on confirming that `connectedOriginsApi.add` is reachable through the untrusted RPC surface (webpage → content script → background) rather than only through the privileged extension UI process. The `ConnectedOrigins` class itself performs no caller-identity check on `trusted`, so if the API is exposed on that boundary at all, exploitation would be trivial (single RPC call, no additional preconditions).

### Recommendation
- Do not accept `trusted` (or any equivalent authorization flag) as a raw parameter from the RPC-facing `add()` API. Split `add()` into an internal privileged mutator (settable only by the background/UI flow after explicit user approval) and a public, unprivileged `add()`/`connect()` surface that always defaults new/existing origins to `trusted: false` and ignores caller-supplied trust values.
- Explicitly verify, via the background RPC exposure code (`libraries/browser-extension-rpc`, `libraries/sdk-rpc`), which process/context can call `connectedOriginsApi.add`, and ensure it is not reachable from the in-page/web3-provider content-script channel with unrestricted parameters.
- Add regression tests asserting that a caller cannot set `trusted: true` on an origin without going through the user-approval popup path.

### Proof of Concept
Based on the code as read (not fully confirmed to be reachable cross-boundary):
```js
// If connectedOriginsApi.add is reachable via the RPC bridge from a webpage/content script:
await exodus.connectedOrigins.add({
  origin: 'attacker.com',
  name: 'Attacker Site',
  connectedAssetName: 'ethereum',
  trusted: true,        // caller-supplied, no server-side check
})

// Now attacker.com is treated as trusted:
await exodus.connectedOrigins.isTrusted({ origin: 'attacker.com' }) // -> true
await exodus.connectedOrigins.getConnectedAccounts({ origin: 'attacker.com' })
// -> discloses wallet addresses for all wallet accounts, without any user approval popup
```
This exploit path matches the `add`/`isTrusted`/`getConnectedAccounts` chain shown in [6](#0-5)  and the unrestricted API exposure in [4](#0-3) , but full end-to-end confirmation requires tracing the RPC method-exposure boundary further than the available index allows.

### Citations

**File:** features/connected-origins/module/connections.js (L140-256)
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
