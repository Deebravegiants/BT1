### Title
Race between `clear()` and concurrent `add()`/`#setData` can resurrect a supposedly-cleared origin's trust and account data - ([File: features/connected-origins/module/connections.js])

### Summary
`ConnectedOrigins#clear` writes `undefined` to `#connectedOriginsAtom` and `#connectedAccountsAtom` sequentially and unconditionally, with no locking against other in-flight mutators of the same module. If an `add()` call (or any `#setAttributes`/`#setData` path) is mid-flight when `clear()` runs, `add()`'s final `Promise.all([...set(data), ...set(accounts)])` can complete after `clear()`, overwriting both atoms with data computed from a pre-clear snapshot and re-persisting the previously-cleared origin's trust/connection entry.

### Finding Description
`clear()` performs two independent, unguarded atom writes: [1](#0-0) 

Meanwhile, `add()` reads the current state via `#getOrigin`/`#getData`, builds a merged `newData`, and calls `#setData`, which computes `assetNames`/`accounts` and only then writes both atoms via `Promise.all`: [2](#0-1) [3](#0-2) 

There is no version check, compare-and-swap, or mutex serializing `clear()` against `add()`/`#setAttributes`/`#addNewItem`. Each individual `createStorageAtomFactory` atom serializes its own `.set()` calls internally, but that only guarantees ordering per-atom, not across the multi-step `add()`/`clear()` module-level operations, which read-then-write across two atoms. Sequence: `add()` reads `#getOrigin`/`#getData` (pre-clear state) → `clear()` (triggered via `plugin/index.js` `onClear` on wallet delete/import) resolves, setting both atoms to `undefined` → `add()`'s `#setData` finishes afterward, calling `#connectedOriginsAtom.set(newData)` with the stale pre-clear list (merged with the new entry) and `#connectedAccountsAtom.set(accounts)`, re-populating the previously cleared origin's trust/connection record. [4](#0-3) 

This means `clear()` does not actually guarantee post-reset "no cleared data" if a connect/add flow is concurrently in progress, defeating the intent of `onClear` invoked during wallet delete or seed import.

### Impact Explanation
The scoped impact is privilege persistence of origin trust across a wallet reset/import boundary: an origin's `trusted`/`autoApprove`/`assetNames` metadata that should have been wiped by `clear()` can be resurrected into the freshly-reset wallet state, along with a `connectedAccountsAtom` entry mapping the (now different) wallet accounts. This is a data-integrity/authorization-boundary violation rather than key or secret disclosure — no private key material is exposed, but a dapp origin can retain trusted/auto-approve status it should have lost after wallet reset.

### Likelihood Explanation
Exploitation requires a narrow race window: the wallet owner must trigger `onClear` (wallet delete/reset or seed import) at essentially the same moment a `connect`/`add()` flow for some origin is mid-write. This is not purely attacker-controlled — the reset action is a wallet-owner-initiated event — so a malicious origin can only try to win the race by repeatedly issuing connect requests and hoping the timing aligns with a reset event, which is not fully reliable and typically requires many attempts or favorable timing in a specific client flow (e.g., import/switch-wallet UI actions). This lowers real-world likelihood substantially, though the underlying lack of synchronization is a genuine code defect.

### Recommendation
Serialize `clear()` against all other mutating module operations (`add`, `#setAttributes`, `#addNewItem`, `untrust`, `connect`/`disconnect`, `clearConnections`, `updateConnectedAccounts`) using a per-module async mutex/queue, or introduce a monotonically increasing "generation"/version token that is checked before the final `Promise.all` write in `#setData`, aborting the write if a `clear()` has occurred since the read. Alternatively, make `clear()` and `#setData` both go through a single serialized write queue keyed on the module instance.

### Proof of Concept
Integration test in `features/connected-origins/module/__tests__/connections.test.js` sequence:
1. Seed `connectedOriginsAtom`/`connectedAccountsAtom` with an entry for `origin: 'attacker.com'` and wallet-account addresses belonging to "wallet A".
2. Stub `#getAccounts`/`addressProvider.getDefaultAddress` with an artificial delay so `add()`'s `#setData` write resolves after a concurrently invoked `clear()`.
3. Fire `Promise.all([connectedOrigins.add({ origin: 'attacker.com', ... }), connectedOrigins.clear()])`, awaiting `clear()` to resolve first (via delay ordering), then let `add()`'s pending write flush.
4. Assert final state: `connectedOriginsAtom.get()` still contains `attacker.com` with `trusted`/`autoApprove` data despite `clear()` having run, and `connectedAccountsAtom.get()` is non-empty — demonstrating that `clear()` failed to leave the module in a fully cleared state.

### Citations

**File:** features/connected-origins/module/connections.js (L41-49)
```javascript
  #setData = async (data) => {
    const assetNames = this.#getConnectedAssets(data)
    const accounts = await this.#getAccounts(assetNames)

    return Promise.all([
      this.#connectedOriginsAtom.set(data),
      this.#connectedAccountsAtom.set(accounts),
    ])
  }
```

**File:** features/connected-origins/module/connections.js (L71-74)
```javascript
  clear = async () => {
    await this.#connectedOriginsAtom.set(undefined)
    await this.#connectedAccountsAtom.set(undefined)
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

**File:** features/connected-origins/plugin/index.js (L28-30)
```javascript
  const onClear = async () => {
    await connectedOrigins.clear()
  }
```
