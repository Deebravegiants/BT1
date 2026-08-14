### Title
Unvalidated `origin` parameter to `connectedOrigins.add`/`getConnectedAccounts` allows cross-origin trust and address disclosure - (File: features/connected-origins/module/connections.js)

### Summary
This is analogous to the AI Arena finding: a public API (`mintFromMergingPool`) accepts caller-supplied, unchecked struct fields (`customAttributes`) and persists them without any allow-listing or validation, corrupting downstream invariants. In `hydra--011`, the `connectedOrigins` module's `add`, `getConnectedAccounts`, `isTrusted`, `updateConnection`, `connect`/`disconnect` methods accept a caller-supplied `origin` (and other attributes like `trusted`, `assetNames`, `walletAccount`) with no schema/format validation, and these are exposed directly through the public API surface `connectedOriginsApi` as raw pass-throughs.

### Finding Description
The `ConnectedOrigins` class methods take an `origin` string and various attributes (`trusted`, `assetNames`, `connectedAssetName`, `walletAccount`) directly as parameters with no type/format checks, similar to how `mintFromMergingPool` took `customAttributes` without checking `weight`/`element` ranges: [1](#0-0) 

These methods are exposed verbatim through the public API layer, with no additional validation added at the boundary: [2](#0-1) 

Once an origin record is marked `trusted` (a caller-controlled boolean passed straight into storage), `getConnectedAccounts` will disclose the addresses of **all enabled wallet accounts** (not just the active one) to that origin: [3](#0-2) 

`isTrusted` treats any record with `trusted !== false` as trusted, and `add` will happily upsert `trusted: true` if a caller supplies it: [4](#0-3) 

The module and API layer never independently determine trust from a verified browser/page origin — trust is simply whatever the caller passes in when invoking `add`. If any RPC bridge or UI-adjacent code path allows an untrusted/renderer-controlled context to invoke `connectedOrigins.add` with an arbitrary `origin` string and `trusted: true`, it can register itself (or spoof a different domain string) as trusted and then call `getConnectedAccounts` to enumerate every enabled wallet account's addresses — a cross-origin/account privilege bleed, directly matching the report's bug class of "no check on input values allows arbitrary/attacker-chosen state."

### Impact Explanation
If reachable from an unprivileged/renderer context (e.g., a compromised or malicious dApp-facing bridge that forwards `origin` as supplied by the page rather than a verified browser-derived value), this allows:
- Spoofing of the `origin` field to impersonate a different (trusted-looking) domain in the stored connection list.
- Self-elevation to `trusted: true` without a genuine user-approval flow, since `trusted` is accepted as a raw pass-through parameter.
- Subsequent disclosure of every enabled wallet account's per-asset addresses via `getConnectedAccounts`, not just the requesting origin's own connected account — a privacy/account-isolation bleed across the multi-account boundary.

This does not constitute unauthorized signing or secret-key disclosure, but it is a concrete violation of the account/origin isolation boundary that the `connectedOrigins` feature is meant to enforce.

### Likelihood Explanation
Likelihood is **uncertain from static index review alone**: I could not locate, within the indexed files, the exact RPC/IPC wiring (e.g., in a browser-extension or provider-bridge adapter) that determines what an actual untrusted webpage/dApp can pass as `origin`/`trusted` when calling `connectedOrigins.add`, versus a trusted background-computed value. The `sdks/headless` test harness calls `exodus.connectedOrigins.add(origin)` directly, which shows the API accepts these fields at face value, but production wiring in the browser extension/dApp-provider bridge may sanitize or override `origin`/`trusted` before reaching this module (this is common practice for `postMessage`/`sender.origin`-derived values). Given the index size limits, I was unable to fully confirm whether such sanitization exists at the RPC boundary; a Devin session with full repo access should verify the actual dApp-provider → `connectedOrigins.add` call sites (e.g., in browser-extension background scripts) to determine if `origin` and `trusted` are ever passed through unsanitized from page-controlled input.

### Recommendation
- Derive `origin` exclusively from a trusted, non-spoofable source (e.g., `sender.origin`/`sender.url` in the extension's message-handling layer), never from any value forwarded by the page/dApp itself.
- Never allow `trusted: true` to be settable via a directly-invokable API from a dApp-facing bridge; trust should only be settable through a dedicated, user-approval-gated flow.
- Add explicit schema validation (format/length/enum) for `origin`, `assetNames`, and `walletAccount` in `connectedOrigins.add`/`updateConnection`, mirroring the `zod`/`typeforce` validation patterns already used elsewhere in the codebase (e.g., `libraries/analytics-validation`, `features/asset-sources`).
- Add regression tests asserting that `getConnectedAccounts` cannot be invoked with a forged `origin` to enumerate non-active wallet accounts.

### Proof of Concept
Conceptual PoC based on the exposed API and module code (not independently verified against the RPC bridge wiring due to index limits):
```js
// If an untrusted context can invoke this with attacker-controlled `origin`/`trusted`:
await exodus.connectedOrigins.add({
  origin: 'attacker-controlled-or-spoofed.example',
  connectedAssetName: 'ethereum',
  trusted: true,           // caller-controlled, no server-side authorization check
})

// Now any code path that can call getConnectedAccounts with that origin
// discloses ALL enabled wallet accounts' addresses, not just the caller's own:
const accounts = await exodus.connectedOrigins.getConnectedAccounts({ origin: 'attacker-controlled-or-spoofed.example' })
// accounts => [{ name: 'exodus_0', addresses: {...} }, { name: 'exodus_1', addresses: {...} }, ...]
``` [5](#0-4)

### Citations

**File:** features/connected-origins/module/connections.js (L140-273)
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
