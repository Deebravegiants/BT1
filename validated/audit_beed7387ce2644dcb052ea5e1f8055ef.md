### Title
`ConnectedOrigins#add` silently merges/escalates `assetNames` and `walletAccount` scope on repeat calls with no consent-gating in the merge logic itself - ([File: features/connected-origins/module/connections.js])

### Summary
`ConnectedOrigins.add()` unconditionally unions any `assetNames` passed by a caller with the already-stored scope and carries forward `walletAccount` via a bare `??` fallback, then persists that expanded scope through `#setAttributes`. Nothing in `add()`, `#setAttributes()`, or `#addNewItem()` distinguishes a "fresh, explicitly re-approved" call from a routine replay, so any code path that re-invokes `add({ origin, assetNames, walletAccount })` for an already-connected origin will silently widen the persisted grant.

### Finding Description
The relevant logic: [1](#0-0) 

For an existing origin, `value.assetNames` is unioned with the newly supplied `assetNames` via `new Set([connectedAssetName, ...assetNames, ...(value?.assetNames ?? [])])`, and the result is written back through `#setAttributes`, which does a plain object spread merge with no diffing or consent flag: [2](#0-1) 

`walletAccount` is preserved/overwritten with `walletAccount ?? value.walletAccount` — i.e., whatever the caller passes wins, with no validation that the caller is authorized to change it. There is no field (e.g. `approvedAt`, `consentNonce`, or a "requires re-approval" flag) recorded anywhere in `newOrigin`/`attributes` that would let a caller assert "this specific set of assets/accounts was freshly consented to." The existing test suite confirms this merge-on-replay behavior is intentional current behavior rather than a guarded/gated one — e.g. `updates accounts when new assets added` calls `add()` twice with escalating `assetNames` and asserts the union takes effect: [3](#0-2) .

The publicly exposed API surface for this method has no additional gating either — `add` is passed straight through: [4](#0-3) 

I could not locate, within the indexed portion of this repo, the actual dapp-facing RPC/provider handler (e.g. the background implementation behind `solana.connect()`/`ethereum.connect()`) that ultimately calls `connectedOrigins.add()` on approval, so I cannot fully confirm whether every caller in production always re-shows a consent UI before invoking `add()` with an expanded scope, or whether an "eager"/`onlyIfTrusted` reconnect path (documented as explicitly skipping the pop-up for trusted origins) can pass dapp-supplied parameters straight into `add()`. The public docs do state that trusted-origin eager connect bypasses the pop-up entirely: [5](#0-4)  — which is consistent with the described risk, but the exact wiring from that RPC path into `add()`'s parameters is outside what I could verify in the indexed code.

### Impact Explanation
If any caller (background RPC handler for connect/eager-connect, WalletConnect handler, or similar) forwards origin-controlled `assetNames`/`walletAccount` into `add()` on a repeat/replay call, the module itself provides no barrier to scope escalation: the union/`??` merge logic in `add`/`#setAttributes` will happily persist the expanded grant, and `getConnectedAccounts` will subsequently expose addresses for the newly merged `assetNames`/`walletAccount` to that origin. This matches a privilege-persistence / wrong-account-scope class of impact if such a caller exists.

### Likelihood Explanation
Confirmed at the module level: repeated `add()` calls with escalated `assetNames`/`walletAccount` merge without any consent marker, purely as a function of the code in `connections.js`. What remains unverified (and thus lowers confidence in exploitability) is whether a genuinely attacker-controlled entry point (e.g., an eager `onlyIfTrusted` connect RPC or a WalletConnect session-update handler) forwards dapp-supplied `assetNames`/`walletAccount` into `add()` without an intervening explicit user approval. That RPC-to-module wiring was not found in the indexed codebase.

### Recommendation
- Require the caller of `add()` to explicitly pass an `approved: true`/consent token only produced by the popup-approval flow when the requested `assetNames`/`walletAccount` differ from the currently stored scope.
- In `#setAttributes`/`add`, diff the incoming `assetNames`/`walletAccount` against the stored value and reject (or route to a distinct "pending re-approval" state) any expansion that isn't accompanied by that consent token, rather than always union-merging.
- Audit all call sites of `connectedOrigins.add` (including any eager/`onlyIfTrusted` reconnect RPC handlers not present in this index) to confirm none of them pass dapp-supplied `assetNames`/`walletAccount` directly without a corresponding fresh-approval UI step.

### Proof of Concept
Integration test (extends `features/connected-origins/module/__tests__/connections.test.js`):
```js
test('replayed add() must not silently escalate scope without re-approval', async () => {
  await connectedOrigins.add({
    origin: 'exodus.com',
    connectedAssetName: 'solana',
    assetNames: ['solana'],
    walletAccount: 'exodus_0',
    trusted: true,
  })

  // Replay without any consent-gated API (simulating a background call that
  // forwards dapp-supplied params without fresh UI approval)
  await connectedOrigins.add({
    origin: 'exodus.com',
    assetNames: ['solana', 'ethereum'],
    walletAccount: 'exodus_1',
  })

  const origins = await connectedOriginsAtom.get()
  const entry = origins.find((o) => o.origin === 'exodus.com')

  // Expected (fixed) behavior: scope should NOT expand without an explicit
  // consent-gated call; today this assertion fails because assetNames/walletAccount
  // are merged unconditionally.
  expect(entry.assetNames).toEqual(['solana'])
  expect(entry.walletAccount).toEqual('exodus_0')
})
```
This test currently fails against the existing `add`/`#setAttributes` implementation, demonstrating the union/`??` merge silently expands `assetNames` to `['solana','ethereum']` and swaps `walletAccount` to `'exodus_1'` with no distinct consent-gated code path enforcing the invariant.

### Citations

**File:** features/connected-origins/module/connections.js (L51-64)
```javascript
  #setAttributes = async ({ origin, attributes }) => {
    const item = await this.#getOrigin({ origin })

    if (!item) return

    const data = await this.#getData()

    const newData = data.map((connection) => {
      if (origin !== connection.origin) return connection
      return { ...connection, ...attributes }
    })

    await this.#setData(newData)
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

**File:** features/connected-origins/module/__tests__/connections.test.js (L129-157)
```javascript
  test('updates accounts when new assets added', async () => {
    await connectedOrigins.add({
      origin: 'exodus.com',
      name: 'Exodus',
      icon: 'exodus_icon',
      connectedAssetName: 'solana',
      assetNames: ['solana'],
      trusted: true,
    })

    await connectedOrigins.add({
      origin: 'exodus.com',
      assetNames: ['solana', 'ethereum'],
    })

    await expect(connectedAccountsAtom.get()).resolves.toEqual({
      exodus_0: {
        addresses: {
          ethereum: '0xbf41610c6D5e6E1DF97f37249D118Cc6FC47d407',
          solana: 'ASwcbiBuegaMrNUuXeN5WDYKoRuDXxMRt5DdStjvdSro',
        },
      },
      exodus_1: {
        addresses: {
          ethereum: '0x1Dc234Aa1c77e3AA781BB2DdF2099489053E11B2',
          solana: '4orUhPn6CRzVcgq5DHfAVt2odiZpPjNy7wNQPYMT4bF1',
        },
      },
    })
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
