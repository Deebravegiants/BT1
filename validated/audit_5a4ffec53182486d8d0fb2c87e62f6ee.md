### Title
Trusted-origin `add()` silently extends dApp permissions to new assets without re-approval - (File: `features/connected-origins/module/connections.js`)

### Summary
The `LockZap.setPoolHelper()` bug centers on a setter that changes a critical trusted party but fails to (re-)grant the permissions that party needs, breaking the intended trust boundary. The closest concrete analog in this Hydra codebase is the inverse failure mode of the same root cause — a setter (`ConnectedOrigins.add()`) that changes what a trusted party (a connected dApp origin) is authorized to access, but does so by silently inheriting the previous trust decision instead of requiring a fresh, scoped approval for the newly added permission.

### Finding Description
`ConnectedOrigins.add()` is the function responsible for creating/updating a dApp's authorization record (trust, auto-approve, and the set of assets/accounts it is allowed to read): [1](#0-0) 

When an origin record already exists (`value` is truthy), the new call to `add()` merges the previously stored `assetNames` with whatever new `assetNames`/`connectedAssetName` are passed in: [2](#0-1) 

Critically, the `trusted` flag for the updated record is computed as `trusted ?? value.trusted` — i.e., if the caller of `add()` does not explicitly pass a `trusted` value for this specific call (which is the case whenever only new assets are being added, not a fresh full "connect" flow), the origin's pre-existing trust status is carried over unchanged and applied to the newly merged asset list. This is confirmed by the test `updates accounts when new assets added`, where a second `add()` call supplies only `assetNames: ['solana', 'ethereum']` (no `trusted` field) and the previously-trusted origin immediately receives Ethereum addresses in `connectedAccountsAtom` without any new consent step: [3](#0-2) 

Once `assetNames` includes the new asset and `trusted` remains `true`, `getConnectedAccounts()` — which gates disclosure solely on `isTrusted()` — will return addresses for the new asset to the origin, since it does not check whether the specific asset was individually approved: [4](#0-3) [5](#0-4) 

This mirrors the audited bug class exactly: a state-mutating setter (`setPoolHelper` / `add`) changes what a previously-approved party is entrused with, but the enforcement of "was this specific grant actually approved" is not re-evaluated — it is inherited from a stale, narrower approval.

### Impact Explanation
If any caller in the extension/SDK invokes `connectedOrigins.add()` to register additional assets for an already-connected origin without re-confirming the `trusted` flag for that call (e.g., a "switch/add chain" or "request additional accounts" flow that reuses the generic `add` API), a dApp that was granted access to one asset only would silently gain read access to wallet addresses (and consequently connect/sign eligibility gated on `isTrusted`) for additional assets/chains it was never explicitly approved for. This is a privilege-bleed across the origin trust boundary, exposing address/account information for assets the user did not consent to share with that origin.

### Likelihood Explanation
The `add` function is exposed directly on the public `connectedOriginsApi` surface (`add: connectedOrigins.add`), so it is reachable by any code path (background/UI) that manages the origin-approval flow without an intermediate check forcing an explicit `trusted` value on every invocation: [6](#0-5) 

Because the merge logic defaults to the previous trust state rather than requiring explicit re-approval per call, any legitimate multi-asset/multi-chain connection-update flow that calls `add()` incrementally (which the test suite explicitly exercises) triggers this behavior. I was not able to fully trace every internal caller of `connectedOrigins.add()` outside of tests within the indexed code, so I cannot confirm with certainty whether a production call site invokes it with attacker-influenced `assetNames` and no `trusted` override; this should be verified directly in the full repository.

### Recommendation
Require the `trusted`/consent decision to be explicit and scoped per asset addition rather than defaulting to the prior record's trust value. Specifically, in `add()` in `features/connected-origins/module/connections.js`, do not fall back to `value.trusted` when new `assetNames`/`connectedAssetName` are being introduced that were not previously part of `value.assetNames`; instead, require the caller to pass an explicit `trusted` decision (obtained via a fresh user-approval UI step) for the incremental grant, and only merge assets into the trusted set once that explicit consent is confirmed.

### Proof of Concept
1. Call `connectedOrigins.add({ origin: 'exodus.com', connectedAssetName: 'solana', assetNames: ['solana'], trusted: true })` — origin becomes trusted for `solana` only.
2. Call `connectedOrigins.add({ origin: 'exodus.com', assetNames: ['solana', 'ethereum'] })` (no `trusted` field, as exercised in the test at `features/connected-origins/module/__tests__/connections.test.js:129-158`).
3. Observe that `connectedAccountsAtom` (and thus `getConnectedAccounts()`) now returns Ethereum addresses for `exodus.com`, even though the user never explicitly approved sharing Ethereum accounts with that origin — the origin's original `trusted: true` decision was silently extended to cover the new asset.

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

**File:** features/connected-origins/module/connections.js (L198-207)
```javascript
  isTrusted = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) {
      return false
    }

    // backward compatibility
    return value.trusted === undefined || value.trusted
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

**File:** features/connected-origins/module/__tests__/connections.test.js (L129-158)
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
  })
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
