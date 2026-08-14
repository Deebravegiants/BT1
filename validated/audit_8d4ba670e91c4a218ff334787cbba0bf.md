### Title
Concurrent `untrust`/`setAutoApprove` calls cause lost-update race that can re-grant auto-approve trust after revocation - ([File: features/connected-origins/module/connections.js])

### Summary
`untrust` and `#setAttributes` (used by `setAutoApprove`, `add`, `connect`, etc.) each perform a non-atomic read-modify-write cycle against `#connectedOriginsAtom` via `#getData()`/`#setData()`, with no version check or compare-and-swap. If two calls race against the same origin, the writer that reads stale data last can overwrite an in-flight `untrust` and resurrect the origin entry with `autoApprove: true`.

### Finding Description
`untrust` reads `isTrusted` then `#getData()`, filters out the origin, and writes via `#setData` [1](#0-0) . `setAutoApprove` calls `#setAttributes`, which independently reads `#getOrigin` then `#getData()`, merges `{ ...connection, ...attributes }` for the matching origin, and writes via `#setData` [2](#0-1) [3](#0-2) . Neither method locks on `origin`, checks a version/token from its read, nor validates that the entry still exists at write time. The underlying atom (`createStorageAtomFactory`, wrapped by `enforceObservableRules`) does serialize individual `atom.set()` calls via `makeConcurrent(concurrency:1)` [4](#0-3) , but this only guarantees writes don't tear each other — it does not make the higher-level read→compute→write sequence in `connections.js` atomic. If a `setAutoApprove` call's `#getData()` read resolves with the origin still present (because it interleaved before `untrust`'s write committed), and its subsequent `#setData` write executes after `untrust`'s write, the merge `{ ...connection, ...attributes }` re-inserts the full origin object (including stale `trusted` value) with `autoApprove: true`, undoing the revocation.

### Impact Explanation
An origin whose access was just explicitly revoked via `untrust` can end up back in `connectedOriginsAtom` with `autoApprove: true` (and its prior `trusted` flag intact), meaning it regains the ability to have future signing requests silently auto-approved without new user consent — a persisted, unauthorized signing-trust escalation for a specific origin, reachable purely through ordinary connection/dapp interaction flows that call these two module methods concurrently.

### Likelihood Explanation
This requires the wallet/dapp integration layer to actually invoke `untrust({origin})` and `setAutoApprove({origin, value:true})` (or `add`) concurrently for the same origin without external serialization. `connections.js` itself provides no `origin`-scoped mutex, so exploitability depends entirely on whether any calling code (extension RPC handlers, UI actions) can trigger overlapping calls — e.g. a revoke UI action racing with an in-flight approve/auto-approve request from a still-open dapp session. I could not find call sites in `plugin/index.js` or `api/index.js` that add locking around these calls [5](#0-4) , so nothing in this module prevents the race if the caller allows it. This is a logic/concurrency bug rather than input-validated attacker-controlled data, so likelihood depends on external orchestration outside this file, which I could not fully verify was reachable from an untrusted dapp on its own (a dapp cannot itself directly invoke `untrust`; that's typically a user/UI action) — reducing confidence that this is remotely attacker-triggerable without some cooperating internal call pattern.

### Recommendation
Make `#setAttributes` and `untrust` atomic with respect to a given `origin`: use a per-origin (or global) async mutex around the read-modify-write sequence, or have `#setData`/the atom's `set` accept an updater function keyed on the freshest state (similar to the setter-function support already in `enforce-rules.ts`) so that `untrust` and `setAutoApprove` operate on the same consistent snapshot. At minimum, `#setAttributes` should re-check that the origin is still present/trusted immediately before merging, and `untrust` should be treated as authoritative by having subsequent grant operations no-op if the origin was removed after their read began.

### Proof of Concept
Integration/invariant test in `features/connected-origins/module/__tests__/connections.test.js` style:
1. Seed `connectedOriginsAtom` with a trusted origin (`{ origin, trusted: true, autoApprove: false }`).
2. Monkey-patch/stub `connectedOriginsAtom.get` to introduce a controlled delay/ordering so that `setAutoApprove`'s second `#getData()` read resolves with the pre-untrust array, and its `#setData` write is scheduled to run after `untrust`'s write (e.g. via manual `Promise` resolution ordering or fake timers around the internal awaits).
3. Run `await Promise.all([connectedOrigins.untrust({ origin }), connectedOrigins.setAutoApprove({ origin, value: true })])`.
4. Assert final state: `await connectedOrigins.isTrusted({ origin })` and `await connectedOrigins.isAutoApprove({ origin })` — expected `false`/`false` after `untrust` resolves, but the race produces `origin` reappearing with `autoApprove: true`, violating the revocation invariant.

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

**File:** features/connected-origins/module/connections.js (L214-216)
```javascript
  setAutoApprove = async ({ origin, value }) => {
    return this.#setAttributes({ origin, attributes: { autoApprove: value } })
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
