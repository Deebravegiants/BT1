### Title
Missing concurrency guard allows race-condition privilege bleed in `ConnectedOrigins` trust/permission state - (File: `features/connected-origins/module/connections.js`)

### Summary
The external report describes a reentrancy issue in an NFT minting contract where an unguarded external call (`safeMint`) occurs before critical state (mint count) is finalized, allowing state to be manipulated mid-call. The closest reachable analog in this hydra repository is the `ConnectedOrigins` module, which manages dApp origin trust/permission state (`trusted`, `autoApprove`, `activeConnections`) using an unguarded read-modify-write pattern across multiple `await` boundaries, with no concurrency lock like the one used elsewhere in the codebase (e.g. `makeConcurrent` in `wallet-accounts.ts`).

### Finding Description
`ConnectedOrigins` (`features/connected-origins/module/connections.js`) exposes methods such as `add`, `connect`, `disconnect`, `untrust`, `setAutoApprove`, `setFavorite`, and `updateConnection` that are called directly in response to dApp/web-page-originated actions (exposed via `connectedOriginsApi` in `features/connected-origins/api/index.js`).

Each of these methods follows a "check-then-act" pattern spanning multiple `await` points without any mutual-exclusion mechanism: [1](#0-0) [2](#0-1) [3](#0-2) 

Each of `#setAttributes`, `untrust`, `add`, and `connect` first reads the current origin record via `#getOrigin`/`isTrusted` (an async atom `.get()`), then—after an await gap where another concurrent invocation can interleave—reads `#getData()` again and writes back a full array via `#setData`, which itself performs further async work (`#getAccounts`, `getDefaultAddress`) before finally calling `.set()` on the atom: [4](#0-3) 

Unlike other modules in the same codebase (e.g. `WalletAccounts.createMany`/`#replaceAll`, which explicitly wrap read-modify-write sequences in `makeConcurrent({ concurrency: 1 })` and document the hazard: "Warning: the following code between reading from currentWalletAccounts and writing back to it needs to remain sync ... or may lead to concurrency issues"), `ConnectedOrigins` has no such guard: [5](#0-4) 

This is directly analogous to the reported bug class: an external, attacker-influenced call sequence (multiple back-to-back RPC calls from a connected/malicious website, e.g. rapid `connect`/`disconnect`/`add` calls) can interleave with the read-modify-write cycle before the final state (trust/auto-approve/connection list) is persisted, causing a lost update. For example, a website could race `untrust`/revocation with a nearly-simultaneous `add`/`connect` call so that a stale, pre-revocation snapshot (still containing `trusted: true` or an already-approved `activeConnections` entry) is written back after the user's revocation is supposed to have taken effect, restoring privileges that should have been removed.

### Impact Explanation
If exploited, this race allows a connected origin's trust or auto-approve state to be reinstated or connection state corrupted after the user has explicitly revoked access (via `untrust`), effectively bypassing the origin-trust boundary that gates dApp/website access to wallet account addresses and future auto-approved signing flows (`isAutoApprove`/`isTrusted` gate transaction/message signing UX in the Web3 providers). This is a cross-origin/account privilege-bleed condition consistent with the "unauthorized access/privilege bypass" impact class called for in the validation rules.

### Likelihood Explanation
Likelihood is constrained by the need for tight timing: a malicious or compromised website would need to fire concurrent RPC calls (e.g., `connect`/`add`) in a narrow window around a user-initiated `untrust`/revoke action, or race two of its own `connect`/`disconnect` calls. Since all `ConnectedOrigins` methods are exposed to be called repeatedly and asynchronously with no `makeConcurrent` guard, and JS `await` on atom I/O provides real interleaving opportunity, this is plausible but not trivially deterministic — it depends on the underlying atom/storage latency and how quickly the host application dispatches origin requests.

### Recommendation
Wrap the read-modify-write sequences in `ConnectedOrigins` (`#setAttributes`, `add`, `#addNewItem`, `untrust`, `connect`, `disconnect`, `clearConnections`) in a per-origin (or global) concurrency guard, mirroring the `makeConcurrent({ concurrency: 1 })` pattern already used in `features/wallet-accounts/src/module/wallet-accounts.ts`, so that origin trust/connection state mutations are serialized and cannot be lost or reordered due to concurrent async calls.

### Proof of Concept
Not independently verified with a running exploit in this ask-only session; the race condition is inferred from the code structure (multiple unguarded `await this.#getData()`/`await this.#getOrigin()` reads followed by `await this.#setData()` writes with no lock, contrasted with the explicitly-guarded pattern in `wallet-accounts.ts`). Confirming actual exploitability (e.g. that the host RPC bridge permits back-to-back concurrent dispatch of `connectedOrigins.*` calls from a single origin without serialization at a higher layer) would require dynamic testing, which is out of scope for this static analysis.

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

**File:** features/connected-origins/module/connections.js (L222-232)
```javascript
  connect = async ({ id, origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) return

    const activeConnections = value.activeConnections || []
    const newConnection = { id, createdAt: Date.now() }
    const newConnections = uniqBy([...activeConnections, newConnection], 'id')

    await this.#setAttributes({ origin, attributes: { activeConnections: newConnections } })
  }
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L246-268)
```typescript
  #replaceAll = makeConcurrent(
    async ({
      walletAccounts,
      accounts,
    }: {
      walletAccounts: Record<string, Record<string, unknown>>
      accounts?: HardwareWalletPublicKeys
    }) => {
      // This will replace all the locally stored hardware wallet public keys
      // with the ones provided by fusion without any attempt to merge inconsistent states.
      this.#hardwareWalletPublicKeys = accounts || createEmptyAccounts()

      await this.#loaded.promise
      const primarySeedId = await this.#wallet.getPrimarySeedId()

      const currentWalletAccounts = (await this.#getInternalWalletAccountsWithFallback()) as Record<
        string,
        WalletAccount
      >
      // Warning: the following code between reading from currentWalletAccounts and writing back to it
      // needs to remain sync until this.#save or may lead to concurrency issues. "await" yields execution
      // and may allow .update(), .create(), etc to execute before
      // fusion syncing is done.
```
