### Title
Lost-update race in `ConnectedOrigins` read-modify-write operations allows a concurrent `add()` to silently re-trust an origin the user just `untrust()`ed - ([File: features/connected-origins/module/connections.js])

### Summary
`connectedOriginsAtom`'s `isSoleWriter: true` + `dedupe` guarantee is enforced correctly at the atom level (writes are serialized via `makeConcurrent` in `enforceObservableRules`), so the underlying storage key itself cannot be corrupted by concurrent `atom.set()` calls. However, the higher-level `ConnectedOrigins` module composes each mutation (`add`, `untrust`, `setAttributes`) as a separate `get()` then `set()` pair with no cross-call locking, so two concurrent module calls can both read the same stale snapshot and the later `set()` silently clobbers the other's intended change.

### Finding Description
`ConnectedOrigins#add`, `#untrust`, and `#setAttributes` (in `features/connected-origins/module/connections.js`) all follow the same pattern: `await this.#getData()` (i.e. `connectedOriginsAtom.get()`), compute a new array based on that snapshot, then `await this.#setData(newData)` which calls `connectedOriginsAtom.set(data)` [1](#0-0) [2](#0-1) [3](#0-2) .

The atom itself only serializes calls to `set()` against each other (`makeConcurrent` with `concurrency: 1` in `enforceObservableRules`), and independently serializes `get()` only when `makeGetNonConcurrent` forces it [4](#0-3) [5](#0-4) . Nothing prevents `get()` calls made by two different in-flight module methods from interleaving with each other's `get`...`set` window - `isSoleWriter`/`dedupe` only protect the storage primitive, not the composite business-logic transaction built on top of it.

Concretely: if `untrust({origin})` and `add({origin, ...})` are both invoked for the same origin close together (e.g. user clicks "untrust" in the wallet UI while the still-open dapp tab fires another `connectedOrigins.add` reconnect call), both can call `#getData()`/`#getOrigin()` before either has called `#setData()`. `untrust` computes `newData` with the origin removed from the pre-race array, and `add`'s `#setAttributes` computes `newData` with the entry present and `trusted: true` (based on the stale pre-untrust `value.trusted`) from the *same* pre-race array. Whichever `set()` wins the race (there is no ordering guarantee between the two independent read-modify-write sequences) determines final state - if `add`'s write lands last, the origin is silently re-trusted despite the user's untrust action, and the untrust is lost.

### Impact Explanation
This is a wrong-origin-trust persistence bug: a dapp/origin that the user explicitly revoked can end up re-authorized/trusted without a corresponding fresh user approval, because a lost update silently restores a stale `trusted: true` attribute. Trusted origins gain increased capability (auto-approve eligibility, connected-account address exposure) via `isAutoApprove`/`getConnectedAccounts`, so this results in privilege persistence for a de-authorized origin [6](#0-5) [7](#0-6) .

### Likelihood Explanation
Exploitation requires precise timing: the attacker-controlled dapp origin must fire an `add`-triggering call (e.g. a reconnect/auto-connect flow) concurrently with the user's `untrust` action (or another `setAttributes`-based call) for the same origin, within the same JS microtask window before the first `set()` resolves. This is plausible for an origin the dapp keeps calling (auto-reconnect on focus/visibility events) but is not fully attacker-controlled on both sides - the user (or another legitimate flow) must trigger the competing write at just the right moment, making it a genuine but timing-dependent race rather than a trivially always-reproducible bug.

### Recommendation
Serialize the entire read-modify-write transaction in `ConnectedOrigins` (e.g., wrap `add`, `untrust`, `setAttributes`, `connect`, `disconnect`, `clearConnections` bodies in a per-module mutex/queue such as `make-concurrent` with `concurrency: 1`, or use the atom's functional `set(oldValue => newValue)` form if supported) instead of separate `get()` then `set()` calls, so concurrent module operations cannot interleave on stale reads.

### Proof of Concept
Integration test in `features/connected-origins/module/__tests__/`:
1. Create a `ConnectedOrigins` instance with an in-memory storage-backed `connectedOriginsAtom`, seed an origin already trusted.
2. Fire `connectedOrigins.add({ origin, trusted: true, ... })` and `connectedOrigins.untrust({ origin })` concurrently (without awaiting the first before starting the second), simulating a dapp reconnect racing a user's untrust click.
3. Await both promises, then read `connectedOriginsAtom.get()`.
4. Assert the final state matches the last authorized user intent (origin removed / `trusted: false`); demonstrate that under current code, depending on scheduling, the origin can still appear with `trusted: true`, proving the lost update.

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

**File:** features/connected-origins/module/connections.js (L150-185)
```javascript
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

**File:** libraries/atoms/src/factories/storage.ts (L83-92)
```typescript
    return enforceObservableRules({
      get,
      set,
      observe,
      defaultValue,
      // Making the "get" concurrent is a perf win on boot
      // since it prevents queueing up a flood of storage reads
      // and forces the usage of the in-memory cached value instead
      makeGetNonConcurrent: true,
    }) as Atom<T | D>
```
