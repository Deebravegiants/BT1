### Title
Lost-update race in `ConnectedOrigins` read-modify-write pattern can revert dApp connection/trust state - (File: features/connected-origins/module/connections.js)

### Summary
The external report's bug class is a classic TOCTOU/lost-update: a value is read into memory, an unrelated async operation intervenes, and the stale in-memory value is then written back, silently discarding the intervening change. In `hydra--014`, `ConnectedOrigins` (`features/connected-origins/module/connections.js`) implements every mutation (`add`, `#setAttributes`, `connect`, `disconnect`, `untrust`, `setAutoApprove`, `setFavorite`, `clearConnections`) with the same unguarded pattern: `await this.#getData()` → compute `newData` from that snapshot → `await this.#setData(newData)`. None of these public methods are serialized with each other at the module level.

### Finding Description
Each mutator independently calls `#getData()` (`connectedOriginsAtom.get()`), builds a new array from that snapshot, and calls `#setData()` (`connectedOriginsAtom.set(data)` plus `connectedAccountsAtom.set(accounts)`): [1](#0-0) [2](#0-1) [3](#0-2) 

`connect` and `disconnect` (used to track a dApp's active RPC connections/sessions per origin) both funnel through `#setAttributes`, which re-reads `#getData()` freshly but the *read* and *write* are two separate awaited storage round-trips with no mutual exclusion between concurrent calls to `connect`/`disconnect`/`setAutoApprove`/`untrust`/`add` for different or even the same origin: [3](#0-2) 

If two of these operations race (e.g., a dApp's RPC bridge fires a rapid `connect` for a new origin while the user concurrently calls `untrust`/`disconnect` on another origin, or the extension processes two RPC messages back-to-back), both read the same underlying array before either write lands. The second writer's `#setData(newData)` call overwrites the store with its own computed array, silently discarding the first writer's change (classic lost update). This mirrors the `withdraw_helper` root cause in the report: state computed from a stale read is written back after another state-mutating operation has already occurred, causing the intervening update to be lost.

The individual `connectedOriginsAtom` (and `connectedAccountsAtom`) `set()` calls are internally serialized via `makeConcurrent` inside the atom's `set` wrapper (only one write executes at a time), but that only prevents corruption of a single `set()` call — it does nothing to prevent the read-decide-write cycle across two separate `get()`+`set()` invocations from racing.

### Impact Explanation
Because `activeConnections` (session/connection state for RPC bridge access) and `trusted`/`autoApprove` (auto-approval flags controlling whether a connected dApp can silently sign/request actions) are all mutated via this same racy pattern, a lost update could:
- Cause a `disconnect` to be silently dropped, leaving a dApp's origin still "connected" in the accounts atom (`connectedAccountsAtom`) after the user believed they disconnected it — an origin/account isolation bleed.
- Cause an `untrust` (revoking a malicious/compromised origin) to be lost if it races with another origin's concurrent `add`/`connect`, leaving trust/autoApprove flags stale and effectively re-granting an origin the ability to auto-approve RPC signing requests it should no longer have.

This lands in the specified in-scope categories (origin/account isolation, RPC bridge trust boundary for unprivileged web-page dApp interactions).

### Likelihood Explanation
Likelihood is speculative rather than confirmed: I could not verify from available context whether callers of `ConnectedOrigins` (e.g., the RPC bridge/provider handling multiple concurrent tab/dApp requests) actually invoke these mutators concurrently in practice, nor whether an outer queue/lock (e.g., a per-origin or global `makeConcurrent` wrapper) exists at a layer I didn't inspect (e.g., the RPC message dispatcher). The `ConnectedOrigins` class itself has no such guard. Given multiple browser tabs/dApps can independently trigger `connect`, `disconnect`, `untrust`, or `setAutoApprove` around the same time, the race window is plausible but not proven to be reachable end-to-end without further tracing of the RPC bridge call sites.

### Recommendation
Serialize all `ConnectedOrigins` mutating operations (`add`, `#setAttributes`, `connect`, `disconnect`, `untrust`, `setAutoApprove`, `setFavorite`, `clearConnections`) behind a single `makeConcurrent`-style queue (concurrency: 1) at the module level, so that each read-modify-write cycle completes atomically relative to other mutators, analogous to fixing `withdraw_helper` by ensuring state is re-read (or the write is based on the latest state) immediately before the write, rather than on a snapshot that may be stale by the time the write executes.

### Proof of Concept
Conceptual reproduction (not run, since this is static-analysis-only access):
1. Call `connectedOrigins.connect({ id: 1, origin: 'a.com' })` and, before it resolves, call `connectedOrigins.untrust({ origin: 'b.com' })` concurrently (both `Promise.all([...])`).
2. Both operations call `#getData()` and receive the same array (containing both `a.com` and `b.com` entries).
3. `untrust` computes `newData` filtering out `b.com` from the snapshot and calls `#setData(newData)`.
4. `connect` computes `newData` by mapping `a.com`'s `activeConnections` from the *same* stale snapshot (which still contains `b.com`) and calls `#setData(newData)`.
5. Whichever `#setData` write lands last "wins," silently reverting the other operation — either `b.com` remains untrusted-but-still-present, or `a.com`'s new connection is lost — despite both operations having reported success to their callers.

### Citations

**File:** features/connected-origins/module/connections.js (L27-49)
```javascript
  #getData = async () => {
    return this.#connectedOriginsAtom.get()
  }

  #getConnectedAssets = (connectedOrigins) => {
    return [
      ...new Set(
        connectedOrigins.flatMap((connection) =>
          [connection.connectedAssetName, ...(connection.assetNames ?? [])].filter(Boolean)
        )
      ),
    ]
  }

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

**File:** features/connected-origins/module/connections.js (L222-243)
```javascript
  connect = async ({ id, origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) return

    const activeConnections = value.activeConnections || []
    const newConnection = { id, createdAt: Date.now() }
    const newConnections = uniqBy([...activeConnections, newConnection], 'id')

    await this.#setAttributes({ origin, attributes: { activeConnections: newConnections } })
  }

  disconnect = async ({ id, origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) return

    const activeConnections = value.activeConnections || []
    const newConnections = activeConnections.filter((connection) => connection.id !== id)

    await this.#setAttributes({ origin, attributes: { activeConnections: newConnections } })
  }
```
