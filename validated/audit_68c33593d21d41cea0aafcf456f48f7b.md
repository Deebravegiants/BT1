### Title
`getConnectedAccounts` throws uncaught `TypeError` when `activeWalletAccountAtom` is out of sync with `connectedAccountsAtom` cache - ([File: features/connected-origins/module/connections.js])

### Summary
`ConnectedOrigins.getConnectedAccounts` reads `accounts[activeWalletAccount].addresses` without checking that `accounts` (from `#connectedAccountsAtom`) actually contains an entry for the current `activeWalletAccount`. If the two atoms are momentarily out of sync (e.g. right after switching the active wallet account but before `updateConnectedAccounts` refreshes the cache), the lookup returns `undefined` and the subsequent `.addresses` access throws a `TypeError`.

### Finding Description
In `features/connected-origins/module/connections.js`:
```js
const activeWalletAccount = await this.#activeWalletAccountAtom.get()
const accounts = await this.#connectedAccountsAtom.get()
...
connectedAccounts.unshift({
  name: activeWalletAccount,
  addresses: pick(accounts[activeWalletAccount].addresses, assetNames),
})
``` [1](#0-0) 

`accounts` is populated by `#getAccounts`, which is only rebuilt from `enabledWalletAccountsAtom` inside `updateConnectedAccounts` (guarded by an `xor` diff check) or via `#setData` on `add`/`#setAttributes` calls [2](#0-1) . `activeWalletAccountAtom`, on the other hand, is a separate atom updated independently by the wallet-accounts module whenever the user switches accounts [3](#0-2) . There is no synchronization/locking between these two atoms, and `getConnectedAccounts` is exposed directly through the public API surface `connectedOriginsApi.getConnectedAccounts` [4](#0-3) , which is reachable from RPC/dapp bridge calls without requiring the wallet to be unlocked (per the function's own doc comment: "Can be used while the wallet is locked") [5](#0-4) .

If a caller queries `getConnectedAccounts({ origin })` in the window between an active-account switch and the completion of `updateConnectedAccounts()`'s cache rebuild, `accounts[activeWalletAccount]` is `undefined`, and `accounts[activeWalletAccount].addresses` throws an unhandled `TypeError: Cannot read properties of undefined (reading 'addresses')`. There is no try/catch or fallback path in this function, so the exception propagates up through the RPC/API bridge to the caller (the origin/dapp), which is against the "fail closed" invariant for RPC-exposed read paths.

### Impact Explanation
This is a denial-of-service / unhandled-exception issue: an unprivileged dapp origin can trigger a crash of the `getConnectedAccounts` RPC handler by calling it during the narrow race window after an account switch. Depending on how the RPC bridge/message-passing layer handles thrown errors, this could also propagate an internal stack trace or error message back to the origin, constituting a minor information leak (e.g., revealing internal atom/module names). No signing, secret material, or authorization state is affected — this is a robustness/availability bug in a read path, not a fund-loss or authentication-bypass bug.

### Likelihood Explanation
The bug requires only a normal user action (switching the active wallet account) followed immediately by a normal dapp RPC call to a trusted, already-connected origin. No privileged state, malicious peer, or special payload is needed. The race window depends on how quickly `updateConnectedAccounts()` re-syncs the cache relative to when `activeWalletAccountAtom` updates, so it is timing-dependent but plausible in real usage (e.g., a dapp polling connected accounts right after the user switches accounts). No existing guard in `getConnectedAccounts` prevents this.

### Recommendation
Add a defensive fallback in `getConnectedAccounts` (and analogously in `#getWalletAccountAddresses`) so that a missing `accounts[activeWalletAccount]` entry does not throw:
```js
const activeAccountData = accounts[activeWalletAccount]
connectedAccounts.unshift({
  name: activeWalletAccount,
  addresses: activeAccountData ? pick(activeAccountData.addresses, assetNames) : {},
})
```
Alternatively, call `updateConnectedAccounts()` (or otherwise ensure cache freshness for the active account) before reading `accounts[activeWalletAccount]`, or derive missing active-account addresses on the fly via `#addressProvider.getDefaultAddress`, mirroring the fallback already used in `#getWalletAccountAddresses` for other accounts [6](#0-5) .

### Proof of Concept
Add a test to `features/connected-origins/module/__tests__/connections.test.js`:
```js
test('getConnectedAccounts does not throw when activeWalletAccount is missing from connectedAccountsAtom cache', async () => {
  await connectedOrigins.add({
    origin: 'exodus.com',
    name: 'Exodus',
    icon: 'exodus_icon',
    connectedAssetName: 'solana',
    assetNames: ['solana'],
    trusted: true,
  })

  // Simulate account-switch race: activeWalletAccountAtom points to an account
  // not yet present in connectedAccountsAtom's cache.
  await activeWalletAccountAtom.set('exodus_new_not_cached')

  await expect(
    connectedOrigins.getConnectedAccounts({ origin: 'exodus.com' })
  ).resolves.not.toThrow()
})
```
Expected (current buggy) behavior: the promise rejects with `TypeError: Cannot read properties of undefined (reading 'addresses')` at `connections.js:269`, demonstrating the fail-open crash instead of the required fail-closed/graceful behavior.

### Citations

**File:** features/connected-origins/module/connections.js (L123-138)
```javascript
  #getWalletAccountAddresses = async (walletAccount, assetNames) => {
    const connectedAccounts = await this.#connectedAccountsAtom.get()
    const entries = await Promise.all(
      assetNames.map(async (assetName) => {
        const existingAddress = connectedAccounts[walletAccount]?.addresses[assetName]
        if (existingAddress) {
          return [assetName, existingAddress]
        }

        const address = await this.#addressProvider.getDefaultAddress({ assetName, walletAccount })
        return [assetName, address.toString()]
      })
    )

    return Object.fromEntries(entries)
  }
```

**File:** features/connected-origins/module/connections.js (L245-249)
```javascript
  /**
   * Returns the connected accounts for a given origin with the active wallet account sorted first. Can be used while
   * the wallet is locked
   */
  getConnectedAccounts = async ({ origin }) => {
```

**File:** features/connected-origins/module/connections.js (L258-270)
```javascript
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
```

**File:** features/connected-origins/module/connections.js (L299-314)
```javascript
  updateConnectedAccounts = async () => {
    const walletAccounts = await this.#enabledWalletAccountsAtom.get()
    const connectedAccounts = await this.#connectedAccountsAtom.get()

    const difference = xor(Object.keys(walletAccounts), Object.keys(connectedAccounts))
    if (difference.length === 0) {
      // up-to-date
      return
    }

    const connectedOrigins = await this.#connectedOriginsAtom.get()
    const assetNames = this.#getConnectedAssets(connectedOrigins)
    const updatedAccounts = await this.#getAccounts(assetNames)

    await this.#connectedAccountsAtom.set(updatedAccounts)
  }
```

**File:** features/wallet-accounts/src/plugins/lifecycle.ts (L1-6)
```typescript
import type { Atom } from '@exodus/atoms'
import { createAtomObserver } from '@exodus/atoms'
import { SEED_SRC } from '@exodus/models/lib/wallet-account/index.js'
import { WalletAccount } from '@exodus/models'
import { safeString } from '@exodus/safe-string'

```

**File:** features/connected-origins/api/index.js (L6-21)
```javascript
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
