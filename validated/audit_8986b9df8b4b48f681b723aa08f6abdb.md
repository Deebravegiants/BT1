### Title
Race condition in `ConnectedOrigins` read-modify-write operations allows lost updates / dApp origin trust state corruption - (File: features/connected-origins/module/connections.js)

### Summary
The `ConnectedOrigins` module manages which websites (origins) are trusted/connected to the wallet, including sensitive `trusted` and `autoApprove` flags that gate whether a dApp can silently reconnect to a wallet account without user confirmation. Every mutating method (`add`, `#setAttributes`, `untrust`, `connect`, `disconnect`) follows an unguarded read-modify-write pattern: read the full origins array via `#getData()`, compute a new array, then write it back via `#setData()` — with no concurrency lock between the read and the write.

### Finding Description
`ConnectedOrigins#add`, `#setAttributes`, `connect`, `disconnect`, and `untrust` each call `#getOrigin`/`#getData` (an `await this.#connectedOriginsAtom.get()`), and only afterwards call `#setData` (an `await ... .set(data)`), with no mutex/lock in between: [1](#0-0) [2](#0-1) [3](#0-2) 

This is the same bug class as the reentrancy report: multiple invocations of a stateful mutator can interleave between the "read" and "write" steps (analogous to a callback re-entering `deposit()` before earlier state updates are committed), causing lost updates on shared state. Note that other stateful modules in this codebase (e.g. `wallet.create`, `PersonalNotes#update`, `AddressCache#update`, `WalletAccounts#replaceAll`) explicitly wrap their read-modify-write logic in `makeConcurrent`/`restrictConcurrency` to close exactly this class of race: [4](#0-3) [5](#0-4) 

`ConnectedOrigins` has no such guard, even though `add`, `connect`, `disconnect`, `untrust`, `setAutoApprove`, and `setFavorite` are all exposed publicly via `connectedOriginsApi`: [6](#0-5) 

The underlying storage atom itself only serializes individual `.set()` calls internally (`makeGetNonConcurrent`), but does not serialize the "get-then-computed-set" pattern used across two separate atom operations in `connections.js`: [7](#0-6) 

### Impact Explanation
Because the origins list is read, then later overwritten wholesale via `#setData` (which rewrites the *entire* array, not a single record), concurrent calls that race between the read and write can silently lose each other's updates. Concretely:
- Two concurrent `add()` calls for two different origins can both read the same "before" array, and whichever `#setData` finishes last wins, discarding the other origin's addition/trust update entirely.
- A `connect()`/`disconnect()` race (e.g., a dApp opening multiple simultaneous session/connection requests) can result in stale `activeConnections` lists — a disconnect being silently undone by an in-flight `connect`, or vice versa.
- A race between `setAutoApprove`/`untrust`(revoke) and a concurrent `add`/`connect` can leave the record with a `trusted`/`autoApprove` state the user did not intend, since `#setAttributes` re-reads and rewrites the whole array without any lock over the intervening `await`s.

This impacts the origin/account trust-isolation boundary between websites and the wallet: an attacker-controlled or malicious page that can trigger overlapping calls to this API (e.g., via rapid successive `connect`/`enable` calls or reconnect races during page load/reload storms) could cause the wallet to retain or restore a stale `trusted`/`autoApprove`/`activeConnections` state for an origin, undermining the intended per-origin consent model. This does not achieve unauthorized signing or secret disclosure by itself, but it is a genuine unauthorized state-mutation / lost-update bug in the origin isolation boundary, directly analogous to the reported reentrancy class (interleaved execution corrupting protocol state before prior state updates complete).

### Likelihood Explanation
Likelihood is moderate: this requires two or more calls into `ConnectedOrigins` methods to be in-flight concurrently for the same or overlapping origin state, which can plausibly occur from rapid/duplicate `connect`/`enable`/`disconnect` events fired by a webpage (e.g., a page issuing multiple provider `connect()` calls in quick succession, or connect/disconnect firing back-to-back on page navigation), or from parallel calls from UI and provider paths hitting the same shared `connectedOriginsAtom`. No special network or device access is needed — only crafted timing of standard, unprivileged API calls exposed through `connectedOriginsApi`.

### Recommendation
Wrap the mutating operations of `ConnectedOrigins` (`add`, `#setAttributes`, `connect`, `disconnect`, `untrust`, and anything else performing get-then-set on `#connectedOriginsAtom`/`#connectedAccountsAtom`) in a single-concurrency lock (e.g. `makeConcurrent(fn, { concurrency: 1 })`, as already used elsewhere in the codebase such as `features/personal-notes/module/index.js` and `features/wallet/module/wallet.js`), so that the read-modify-write cycle for the origins list is atomic with respect to other calls into the same module.

### Proof of Concept
Conceptual race (analogous pattern already demonstrated for other atoms' race conditions in this codebase, e.g. `features/wallet-accounts/src/module/__tests__/index.test.ts:1254-1267` shows the pattern used to test concurrent-create races):
1. Origin `evil.com` is already connected/trusted with `activeConnections: []`.
2. The page issues `connectedOrigins.connect({ id: 'a', origin: 'evil.com' })` and, before it resolves, the wallet or user issues `connectedOrigins.disconnect({ id: 'a', origin: 'evil.com' })` (or another `connect` call for a different id) concurrently.
3. Both methods independently call `#getOrigin` → `#getData` and read the same pre-state `activeConnections: []`.
4. Both then independently compute their "new" `activeConnections` arrays from that same stale base and call `#setAttributes` → `#setData`, with whichever finishes last overwriting the other's result.
5. Depending on ordering, either a `disconnect` is silently undone (a supposedly removed connection reappears) or a `connect` is silently dropped — with no error surfaced to the caller, since none of these methods coordinate via a shared lock. [2](#0-1)

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

**File:** features/personal-notes/module/index.js (L35-46)
```javascript
  #update = makeConcurrent(async (_personalNotesArray, { fromSync } = {}) => {
    const personalNotesArray = [_personalNotesArray]
      .flat()
      .map((personalNote) => pickBy(personalNote, (item) => item !== undefined))
    const personalNotesPre = await this.#personalNotesAtom.get()
    const personalNotesPost = personalNotesPre.update(personalNotesArray)
    if (personalNotesPre.equals(personalNotesPost)) {
      this.#logger.debug('skip personal notes update, they are the same as stored')
      return
    }

    await this.#personalNotesAtom.set(personalNotesPost)
```

**File:** features/wallet/module/wallet.js (L231-250)
```javascript
  create = makeConcurrent(
    async ({ mnemonic, passphrase } = {}) => {
      mnemonic = mnemonic || (await generateMnemonic({ bitsize: 128 }))

      const dateCreated = this.#clock.now()
      const seedBuffer = await mnemonicToSeed({ mnemonic, format: 'buffer', validate: false })
      const seed = { mnemonic, seed: seedBuffer, dateCreated }
      const seedId = await getSeedId(seedBuffer)

      await this.#setSeed({ seed, passphrase })

      this.#seedMetadataAtom.set((previous) => ({
        ...previous,
        [seedId]: { dateCreated },
      }))

      return { seedId }
    },
    { concurrency: 1 }
  )
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

**File:** libraries/atoms/src/factories/storage.ts (L26-59)
```typescript
const _createStorageAtomFactory = <T = unknown>({ storage }: { storage: Storage }) => {
  function createStorageAtom(opts: Omit<Params<unknown>, 'defaultValue'>): Atom<T | undefined>
  function createStorageAtom<D extends T>(opts: Params<D>): Atom<T | D>
  function createStorageAtom<D extends T>({ key, defaultValue }: Params<D>): Atom<T | D> {
    let version = 0
    const { notify, observe, listeners } = createSimpleObserver<T | undefined>({ enable: true })

    let canUseCached = false
    let cached: T | undefined
    let pendingWrite: Promise<void> | undefined

    // enforce-rules make it non concurrent
    const set = async (value: T | undefined) => {
      version++
      pendingWrite = (async () => {
        if (value === undefined) {
          await storage.delete(key)
          canUseCached = false
        } else {
          await storage.set(key, value)
          canUseCached = true
        }

        cached = value
        pendingWrite = undefined
      })()

      await pendingWrite
      await notify(value)

      if (!canUseCached && listeners.length > 0) {
        listeners.forEach((listener) => (listener as ResettableListener<T>).resetCallState())
      }
    }
```
