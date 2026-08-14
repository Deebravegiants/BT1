### Title
Missing "trusted" constraint check in `setAutoApprove` allows enabling auto-approval for connections that should require confirmation - ([File: features/connected-origins/module/connections.js])

### Summary
The `ConnectedOrigins` module enforces a `trusted` gate before granting access to sensitive origin-scoped operations (e.g. `untrust`, `getConnectedAccounts`), but the security-relevant `setAutoApprove` mutator, which flips the flag used to skip user confirmation for an origin, does not perform the same check before writing the new state.

### Finding Description
`ConnectedOrigins#untrust` and `ConnectedOrigins#getConnectedAccounts` both gate their logic behind an explicit `isTrusted` check: [1](#0-0) [2](#0-1) 

However, `setAutoApprove`, which persists the `autoApprove` attribute used elsewhere to decide whether a connected origin's requests can bypass confirmation, calls `#setAttributes` directly with no equivalent constraint: [3](#0-2) 

New origins are created with `autoApprove: false` by default [4](#0-3) , showing the codebase's intent that only trusted/explicitly-approved origins should reach `autoApprove: true`. `setAutoApprove` is exposed directly on the public `connectedOriginsApi` surface alongside `isTrusted`/`untrust`, without re-validating trust state inside the mutator itself: [5](#0-4) 

This mirrors the reported bug class exactly: a state-mutating function (`_setLookAheadPeriod`) omits a constraint check (`DEALLOCATION_DELAY > lookAheadPeriod`) that a sibling function (`_createQuorum`) enforces, breaking an invariant. Here, `setAutoApprove` omits the `isTrusted` constraint that sibling functions (`untrust`, `getConnectedAccounts`) enforce, breaking the invariant that only trusted origins can be granted auto-approval of signing/connection requests.

### Impact Explanation
If any caller path (background message handler, redux action, or a compromised/malicious dApp origin with access to the `connectedOriginsApi`) can invoke `setAutoApprove` for an origin whose `trusted` flag is `false` or unset, that origin would be flipped into an auto-approve state. Any downstream consumer that later reads `isAutoApprove` to decide whether to skip the user confirmation dialog for a connect/sign request would then treat that origin as pre-approved, effectively enabling unauthorized signing/connection actions without further user consent — a direct violation of the trust boundary the module is designed to enforce.

### Likelihood Explanation
Exploitability depends on whether `setAutoApprove` is reachable by an untrusted caller (e.g., directly from a dApp/content-script bridge, or from a UI action not itself gated by a trust check). I could not locate, within the indexed code, the concrete downstream consumer of `isAutoApprove` that decides to skip a confirmation UI, nor could I fully confirm the authorization boundary of the API/RPC bridge that exposes `connectedOriginsApi.setAutoApprove` to less-privileged callers. This limits certainty about full end-to-end exploitability versus a UI-only, already-trusted invocation path.

### Recommendation
Add the same `isTrusted` guard used in `untrust`/`getConnectedAccounts` to `setAutoApprove` (and ideally to `setFavorite`/`updateConnection` if they also gate trust-sensitive behavior), rejecting or ignoring calls for origins that are not trusted:
```js
setAutoApprove = async ({ origin, value }) => {
  const isTrusted = await this.isTrusted({ origin })
  if (!isTrusted) return
  return this.#setAttributes({ origin, attributes: { autoApprove: value } })
}
```

### Proof of Concept
Given the current implementation, the following sequence demonstrates the missing constraint:
1. An origin is added without `trusted: true` (or is later untrusted), so `isTrusted({ origin })` returns `false`.
2. Caller invokes `connectedOrigins.setAutoApprove({ origin, value: true })`.
3. `setAutoApprove` performs no trust check and writes `autoApprove: true` via `#setAttributes` [3](#0-2) .
4. `isAutoApprove({ origin })` now returns `true` for an origin that was never trusted [6](#0-5) , contradicting the invariant enforced by `untrust`/`getConnectedAccounts` that gate on `isTrusted` first.

**Note on confidence:** I was unable to locate the exact downstream code path (likely in the browser-extension RPC bridge or UI approval flow, outside what the index surfaced) that consumes `isAutoApprove` to skip a signing confirmation dialog, so the full unauthorized-signing impact chain is inferred from the module's design intent (default `autoApprove: false`, trust gating elsewhere) rather than directly observed end-to-end.

### Citations

**File:** features/connected-origins/module/connections.js (L76-100)
```javascript
  #addNewItem = async ({
    origin,
    name,
    icon,
    connectedAssetName,
    assetNames,
    accounts,
    trusted = false,
    favorite = false,
    walletAccount,
  }) => {
    const newOrigin = {
      origin,
      icon,
      name,
      trusted,
      favorite,
      connectedAssetName,
      assetNames,
      accounts,
      autoApprove: false,
      createdAt: Date.now(),
      activeConnections: [],
      walletAccount,
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

**File:** features/connected-origins/module/connections.js (L209-212)
```javascript
  isAutoApprove = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })
    return value?.autoApprove || false
  }
```

**File:** features/connected-origins/module/connections.js (L214-216)
```javascript
  setAutoApprove = async ({ origin, value }) => {
    return this.#setAttributes({ origin, attributes: { autoApprove: value } })
  }
```

**File:** features/connected-origins/module/connections.js (L249-252)
```javascript
  getConnectedAccounts = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })
    if (!isTrusted) return []

```

**File:** features/connected-origins/api/index.js (L1-21)
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
```
