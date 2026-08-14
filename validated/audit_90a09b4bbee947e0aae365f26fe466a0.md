### Title
Lost-update race between `ConnectedOrigins#add` and `#updateConnectedAccounts` can leave stale/removed wallet-account addresses in `connectedAccountsAtom` - (File: features/connected-origins/module/connections.js)

### Summary
`ConnectedOrigins#add()` (via `#setData`) and `ConnectedOrigins#updateConnectedAccounts()` both independently read `enabledWalletAccountsAtom`/`connectedAccountsAtom`, compute a full replacement value, and then unconditionally overwrite `connectedAccountsAtom` with no compare-and-swap or version check tying the write to the snapshot it was computed from. If a wallet-account removal/rename (which fires `updateConnectedAccounts`) races with an in-flight `add()` call (e.g. a dapp connection approval), the operation that started first but finishes last can clobber the freshly-corrected state with a stale computation that still contains the removed account's addresses.

### Finding Description
`#setData` (features/connected-origins/module/connections.js:41-49) recomputes accounts from scratch via `#getAccounts(assetNames)`, which calls `this.#enabledWalletAccountsAtom.get()` [1](#0-0)  at the moment it executes — not at the moment `add()` was invoked. `updateConnectedAccounts()` performs the same kind of read-diff-recompute-write sequence independently [2](#0-1) .

Both paths ultimately call `this.#connectedAccountsAtom.set(...)`. The underlying atom's `set` is wrapped with `makeConcurrent` in `enforceObservableRules` [3](#0-2) , which only guarantees that individual `set` invocations run to completion one at a time (serialized queue) — it provides no compare-and-swap, no versioning, and no rejection of "stale" writes based on the snapshot used to compute them. Whichever call reaches `.set()` last simply replaces the atom's entire value.

Because `add()`'s computation path involves multiple awaited steps (`#getAccounts` → `#getWalletAccountAddresses` → `addressProvider.getDefaultAddress` per asset) [4](#0-3) , it can take meaningfully longer to reach its `.set()` call than `updateConnectedAccounts()`, which is a comparatively short synchronous-ish chain once triggered by an `enabledWalletAccountsAtom` change. If `add()` began (and read `enabledWalletAccountsAtom`) before a wallet account was removed, but its `connectedAccountsAtom.set()` call lands after `updateConnectedAccounts()` has already written the corrected (removed-account-excluded) state, `add()`'s write reintroduces the removed account's key/addresses into `connectedAccountsAtom`.

`getConnectedAccounts({ origin })` then iterates `Object.keys(accounts)` from `connectedAccountsAtom` unconditionally (not scoped to only the wallet accounts currently enabled) and returns their addresses filtered by the origin's asset names [5](#0-4) . If a stale/removed wallet account entry has been reintroduced by the race, any origin calling `getConnectedAccounts` will receive that removed account's addresses until the next `updateConnectedAccounts()` invocation corrects it.

### Impact Explanation
The result is that `connectedAccountsAtom` can transiently (until the next enabled-wallet-accounts change) diverge from the true set of enabled wallet accounts, exposing a removed or renamed wallet account's addresses to a connected dapp origin via `getConnectedAccounts`. This is a persisted-state integrity/authenticity violation (lost update) rather than a memory-safety bug, and the disclosed data is limited to public receive addresses of the affected wallet account (not keys or signing capability).

### Likelihood Explanation
This requires precise timing: a wallet-account removal/rename must occur while an `add()` (dapp connect/approve) operation is in flight and reach its `connectedAccountsAtom.set()` after `updateConnectedAccounts()`'s write. This is not attacker-controlled from the dapp/origin side alone — it depends on the wallet user coincidentally removing/renaming an account during a connection approval — so real-world exploitation is low-probability and requires favorable scheduling, though it is reproducible deterministically in a controlled test by manually interleaving promise resolution order.

### Recommendation
Introduce optimistic-concurrency protection for `connectedAccountsAtom` writes: attach a version/generation counter (or use the `enabledWalletAccountsAtom`'s own version) to each computed snapshot, and reject/retry a `set()` if the target version has changed since the read that produced it. Alternatively, serialize `add()`/`#setData()`/`updateConnectedAccounts()` behind a single mutex (e.g. `make-concurrent` at the `ConnectedOrigins` method level) so that read-compute-write for these two operations cannot interleave, and have `#getAccounts` always recompute against the freshest `enabledWalletAccountsAtom` snapshot taken at write time rather than at call start.

### Proof of Concept
Integration/invariant test plan (Jest, similar to existing tests in `features/connected-origins/module/__tests__/connections.test.js`):
1. Set up `ConnectedOrigins` with mock atoms where `enabledWalletAccountsAtom.get()` and `addressProvider.getDefaultAddress()` are deferred (`pDefer`) to control resolution order.
2. Seed `enabledWalletAccountsAtom` with accounts `{A, B}` and add an origin via `connectedOrigins.add({...})`, but delay the `addressProvider.getDefaultAddress` promise so `add()`'s internal `#getAccounts` is still pending.
3. While `add()` is pending, remove account `B` from `enabledWalletAccountsAtom` and immediately await `connectedOrigins.updateConnectedAccounts()` to completion (asserting `connectedAccountsAtom` now only has key `A`).
4. Resolve the deferred `addressProvider` promise so the original `add()` call's `#setData` finally completes and calls `connectedAccountsAtom.set()`.
5. Assert: `connectedAccountsAtom.get()` incorrectly contains stale key `B` again (demonstrating the lost update), and `connectedOrigins.getConnectedAccounts({ origin })` returns an entry for the removed account `B`.
6. Expected (fixed) behavior: `connectedAccountsAtom` keys must always equal `Object.keys(enabledWalletAccountsAtom)` after both operations settle, regardless of interleaving — a fuzz harness firing `add()` and `updateConnectedAccounts()` many times with randomized delays should assert this invariant on every run.

### Citations

**File:** features/connected-origins/module/connections.js (L108-121)
```javascript
  #getAccounts = async (assetNames) => {
    const walletAccounts = Object.values(await this.#enabledWalletAccountsAtom.get())

    const entries = await Promise.all(
      walletAccounts.map(async (walletAccount) => [
        walletAccount.toString(),
        {
          addresses: await this.#getWalletAccountAddresses(walletAccount, assetNames),
        },
      ])
    )

    return Object.fromEntries(entries)
  }
```

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

**File:** libraries/atoms/src/enforce-rules.ts (L96-106)
```typescript
  const set = makeConcurrent(async (value: T | ((value: T) => T)) => {
    // support a function a la React's setState(oldState => newState)
    if (isSetter(value)) {
      const current = getInitialized() ? await get() : defaultValue
      value = await value(current)

      if (current === value) return
    }

    await atom.set(value)
  })
```
