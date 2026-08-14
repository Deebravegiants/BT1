### Title
Non-atomic read-modify-write in `ConnectedOrigins#setData`/`#setAttributes`/`#addNewItem` allows a lost-update race that can re-persist `trusted`/`autoApprove` after `untrust()` - (`features/connected-origins/module/connections.js`)

### Summary
`add()`, `untrust()`, and `setAutoApprove()` all follow a read-then-write pattern (`#getOrigin`/`#getData` → compute new array → `#setData`) over the same shared `connectedOriginsAtom`, with no per-origin locking or version check between read and write. Because `#setData` performs extra async work (`#getConnectedAssets`, `#getAccounts`) before actually calling `atom.set()`, two concurrent RPC calls that both start from the same snapshot can have their writes complete in either order, letting a `trusted:true` write from `add()` overwrite a subsequent (in wall-clock terms) `untrust()` removal, or vice versa - a classic lost update.

### Finding Description
Every mutation in `ConnectedOrigins` goes through the same pattern: [1](#0-0) [2](#0-1) [3](#0-2) 

`#setData` is not a single atomic transaction: it first computes `assetNames`/`accounts` via `await this.#getAccounts(...)` and only afterward calls `this.#connectedOriginsAtom.set(data)`. This means the time between the initial `#getData()` read and the final `atom.set()` write is non-trivial and variable per call.

If `add({ origin, trusted: true })` and `untrust({ origin })` are both dispatched by the same origin without awaiting the first, both may call `#getOrigin`/`#getData` before either write lands, so both read the *same* pre-mutation array snapshot (`D0`). `add()`'s `#setAttributes` computes `newData1` = `D0` with the origin's `trusted` flag set to `true`; `untrust()` computes `newData2` = `D0` with the origin entry filtered out entirely. Each then independently proceeds through `#setData`'s async pre-work and eventually calls `#connectedOriginsAtom.set(...)`. The underlying atom's `set` is serialized by `enforceObservableRules`'s `makeConcurrent` wrapper (queued, not truly parallel), [4](#0-3)  but the *order in which each caller's `set()` invocation is enqueued* is determined by whichever `#getAccounts`/`#getConnectedAssets` resolves first - not by the true call order or by any re-validation against the freshest data. Whichever write is enqueued last wins entirely, discarding the other. There is no compare-and-swap, no version check, and no re-read of the current atom value inside `#setData` before writing the full replacement array.

Consequently, if `add()`'s write happens to be enqueued after `untrust()`'s write, the origin's `trusted: true` entry (added via `newData1`) silently overwrites the removal performed by `untrust()`, even though `untrust()` was logically issued (or resolved) afterward. The same lost-update pattern applies to `setAutoApprove()` racing with `untrust()`, since `setAutoApprove` also goes through `#setAttributes` → `#setData` on the same shared array. No auth/lock/origin-scoping check in this module protects against this because the vulnerability is purely a concurrency defect in the data layer, not a check that can be bypassed by validation alone - the guards (`isTrusted`, `#getOrigin`) all read from the same racy, un-versioned atom.

### Impact Explanation
This allows an unprivileged dapp origin to defeat a legitimate `untrust()`/revocation call by racing it with a concurrent `add({trusted:true})`/`setAutoApprove(true)` call, causing the origin's elevated trust (`trusted: true` and/or `autoApprove: true`) to persist in `connectedOriginsAtom` even though the user/wallet believes the origin was revoked. Since `isTrusted`/`isAutoApprove`/`getConnectedAccounts` gate address/account disclosure and auto-approval of connect/sign flows for that origin, a resurrected `trusted`/`autoApprove` entry effectively grants unrevocable, persistent unauthorized access/auto-approval to an origin the user attempted to de-authorize - a privilege-persistence bug that violates the "consent must stay scoped and revocable" invariant.

### Likelihood Explanation
Exploitability requires only that the malicious dapp fire two RPC calls (`add()` and `untrust()`/`setAutoApprove()`) back-to-back without awaiting the first - fully within reach of an ordinary unprivileged dapp using the exposed `connectedOrigins` API (`features/connected-origins/api/index.js`). No wallet lock bypass, no privileged state, and no additional social engineering is needed. The race window is small but real, since `#setData` performs multiple `await`s (`#getConnectedAssets`, `#getAccounts`, and `Promise.all`) between reading and writing, and the outcome ordering is determined by microtask/async scheduling rather than call order, making it non-deterministic and repeatable under load/fuzzing (i.e., reliably reproducible by repeatedly firing the two calls in a tight loop until a bad interleaving occurs).

### Recommendation
Make the read-modify-write in `#setData`/`#setAttributes`/`#addNewItem`/`untrust` atomic with respect to concurrent calls on the same `ConnectedOrigins` instance - e.g., serialize all mutating operations (`add`, `untrust`, `setAutoApprove`, `setFavorite`, `connect`, `disconnect`, `updateConnection`, `clearConnections`) through a single-origin (or global) mutex/queue (such as `make-concurrent` with `concurrency: 1`), or switch `#setData` to use the atom's functional-setter form (`atom.set(currentValue => nextValue)`) so the read and write happen atomically inside the atom's own serialized `set`, instead of reading via `#getData()` outside of the `set` call and writing a stale, externally-computed full array.

### Proof of Concept
Integration test (Jest) plan:
1. Instantiate `ConnectedOrigins` with in-memory/mock atoms (`connectedOriginsAtom`, `connectedAccountsAtom`, `enabledWalletAccountsAtom`, `addressProvider`) mirroring the existing test setup in `features/connected-origins/module/__tests__/connections.test.js`.
2. Seed the atom so `origin: 'https://evil.dapp'` already exists with `trusted: false`.
3. Fire, without awaiting the first:
   - `const p1 = connectedOrigins.add({ origin: 'https://evil.dapp', trusted: true })`
   - `const p2 = connectedOrigins.untrust({ origin: 'https://evil.dapp' })`
4. `await Promise.all([p1, p2])`.
5. Assert deterministically: `const data = await connectedOriginsAtom.get(); expect(data.find(c => c.origin === 'https://evil.dapp')).toBeUndefined()` (or, if the desired semantic is "last requested wins," assert the origin is not left `trusted: true` after an `untrust()` call was issued).
6. To make the race reliably observable, inject artificial delays into the mocked `#getAccounts`/`addressProvider.getDefaultAddress` (e.g., `delay(Math.random() * 10)`) so that `add()`'s `#setData` pre-processing sometimes resolves after `untrust()`'s, and run the test in a loop (e.g., 100 iterations) to show the final state is non-deterministic - sometimes the `trusted: true` entry survives despite `untrust()` having been called, demonstrating the lost update.

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
