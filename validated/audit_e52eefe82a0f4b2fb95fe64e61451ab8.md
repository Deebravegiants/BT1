Based on the investigation, `connectedOrigins.add` in this repo is exposed as an RPC-callable API method (via `connectedOriginsApi`, `sdks/headless`), and it is the same "app"-level API surface documented for `@exodus/headless` (the same channel that back-ends the injected web3 providers such as `ethereum`/`solana`). The function accepts a `trusted` boolean directly as a caller-supplied parameter and persists it verbatim into the origin's trust record, without any server-side verification that a legitimate user-approval flow (e.g., an actual popup approval, as documented for `solana.connect()`) preceded the call.

### Title
Unvalidated `trusted`/`autoApprove` flag accepted directly from RPC caller in `connectedOrigins.add` grants dApp origin trust without user approval - (File: features/connected-origins/module/connections.js)

### Summary
`ConnectedOrigins.add` [1](#0-0)  accepts a `trusted` parameter directly from the caller and stores it as-is on the origin record, and this method is exposed unauthenticated over the SDK/RPC API surface [2](#0-1) . Just like the GiantPool bug lets an attacker insert an unvetted LP token that is later trusted as if it were legitimately staked, this code lets any caller of the exposed `connectedOrigins.add` RPC method insert a `trusted: true` (and `autoApprove: true` via `setAutoApprove`) origin record without going through the documented user-approval popup flow (`solana.connect()`, `ethereum.request()` "trusted site" flow described in the web3-provider docs) [3](#0-2) . Downstream, `isTrusted`/`getConnectedAccounts` use only this stored flag to release wallet account addresses without any user-in-the-loop check [4](#0-3) [5](#0-4) .

### Finding Description
The `add` method takes `trusted`, `favorite`, and other flags straight from its input object and writes them into the persisted `connectedOriginsAtom` state: [6](#0-5) 

`isTrusted` and `isAutoApprove` simply read back this stored flag with no additional provenance check: [7](#0-6) 

`getConnectedAccounts`, which reveals all of the user's wallet-account addresses for the connected asset(s), is gated solely on this `isTrusted` check: [8](#0-7) 

The entire `connectedOrigins` module (including `add`, `connect`, `setAutoApprove`) is exposed as a flat, RPC-callable API object with no origin-authentication or approval-token requirement enforced in the module itself: [2](#0-1) 

This mirrors the root cause of the GiantPool bug: a function that mutates/reads a "trust" ledger accepts caller-supplied data (the LP token address in the original report; the `trusted`/`autoApprove` flag here) without verifying that the record was created through the legitimate, privileged pathway (staking ETH via the pool in the original; the user-approval popup flow in this codebase).

### Impact Explanation
If the surface that exposes `connectedOrigins.add`/`setAutoApprove` is reachable by an untrusted web page's provider bridge (the docs describe `connect()` as normally requiring a user-approval popup before this state is set — e.g. `solana.connect()`, `algorand.enable()` [9](#0-8) ), a malicious or compromised page could call the API directly to self-mark its own origin as `trusted: true`/`autoApprove: true`, bypassing the user-approval UI entirely. Once trusted, `getConnectedAccounts` discloses all wallet-account addresses for the connected chain(s) to that origin without any further user interaction, and `isAutoApprove` may allow subsequent signing requests to skip user confirmation. This is an account/address disclosure and connection-privilege-bypass issue analogous to the "worthless LP token trusted without provenance check" root cause in the report.

### Likelihood Explanation
Exploitability depends entirely on whether the background/RPC wiring restricts which callers (UI vs. content-script/page) can invoke `connectedOrigins.add`/`setAutoApprove`, which I could not fully confirm from the indexed files — I found the exposed API definition and RPC plumbing (`browser-extension-rpc`, `sdk-rpc`) but not the concrete manifest/permission wiring that would prove (or rule out) that an untrusted web page's channel is bound to this same "app" RPC methods object. This is a genuine gap in what I could verify from the available index; a Devin session with full repo access would be needed to trace the exact channel/port binding between the content-script-exposed provider and the `connectedOriginsApi` methods to confirm reachability from an unprivileged origin.

### Recommendation
Do not accept a caller-supplied `trusted`/`autoApprove` boolean directly in `ConnectedOrigins.add`. Trust/auto-approve status should only be settable through an internal, UI-gated call path that is invoked after the user has approved a connection popup, never via a parameter the RPC caller controls. Add server-side (background-process) provenance/authorization checks — analogous to storing which LP tokens were legitimately minted via staking in the original report — so that `trusted`/`autoApprove` can only be flipped by application code following a real user-approval event, not by the value passed in from an untrusted RPC caller.

### Proof of Concept
Not independently confirmed — the module-level PoC would be: call `exodus.connectedOrigins.add({ origin: 'attacker.example', connectedAssetName: 'ethereum', trusted: true })` (or `setAutoApprove`) directly through whatever RPC channel the injected page-provider uses, bypassing any approval popup, then call `exodus.connectedOrigins.getConnectedAccounts({ origin: 'attacker.example' })` to retrieve wallet addresses without user consent, as shown functionally working (minus the approval gate) in the existing test suite [10](#0-9) . Confirming actual end-to-end exploitability requires verifying the RPC channel binding between the page-injected provider and this API, which was not available in the indexed context.

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

**File:** features/connected-origins/module/connections.js (L198-212)
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

**File:** docs/web3-providers/solana-provider-api.md (L80-95)
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
```

**File:** docs/web3-providers/algorand-provider-arc-api.md (L61-62)
```markdown
asking the user to approve the connection. Upon approval, Exodus will return the
addresses of the user's accounts and network.
```

**File:** features/connected-origins/module/__tests__/connections.test.js (L90-127)
```javascript
  test('trust new origin', async () => {
    await connectedOrigins.add({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      connectedAssetName: 'solana',
      trusted: true,
    })
    const origins = await connectedOriginsAtom.get()

    expect(origins).toHaveLength(1)
    expect(origins[0]).toMatchObject({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      favorite: false,
      autoApprove: false,
      connectedAssetName: 'solana',
      activeConnections: [],
    })

    await expect(connectedAccountsAtom.get()).resolves.toEqual({
      exodus_0: {
        addresses: {
          solana: 'ASwcbiBuegaMrNUuXeN5WDYKoRuDXxMRt5DdStjvdSro',
        },
      },
      exodus_1: {
        addresses: {
          solana: '4orUhPn6CRzVcgq5DHfAVt2odiZpPjNy7wNQPYMT4bF1',
        },
      },
    })

    const stored = await connectedOriginsAtom.get()

    expect(stored).toHaveLength(1)
  })
```
