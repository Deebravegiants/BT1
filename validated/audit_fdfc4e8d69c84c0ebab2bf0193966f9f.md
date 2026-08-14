### Title
Overwriting the active hardware-wallet signing request without checking for an existing one - ([File: features/hardware-wallets/src/module/hardware-wallets.ts])

### Summary
`HardwareWallets#signGeneric` unconditionally creates and stores a new `#signingRequest` object every time `signTransaction`/`signMessage` is invoked, without first checking whether a signing request is already in flight. This mirrors the reported analog: `createReserveAuction` created a second auction without checking `nftContractToTokenIdToAuctionId[nftContract][tokenId]` already pointed at an active auction, silently orphaning the first one. Here, a second sign call silently orphans the first pending signing request instead of rejecting it or queueing behind it.

### Finding Description
`#signGeneric` is defined as: [1](#0-0) 

Note that unlike every other usage of `make-concurrent`/`restrictConcurrency` in this codebase (which explicitly pass `{ concurrency: 1 }`, e.g. [2](#0-1)  and [3](#0-2) ), `#signGeneric` calls `restrictConcurrency` with **no options object at all**: [4](#0-3) 

There is no check such as `if (this.#signingRequest) throw ...` before assigning `this.#signingRequest = { id, baseAssetName, walletAccount, sign, resolve, reject }` at line 318. Whatever value was previously stored in the private `#signingRequest` field (and its associated `deferred` promise created via `pDefer()` at line 314) is silently replaced.

`cancelSigningRequest` and `retrySigningRequest` only ever operate on the single, most-recently-set `this.#signingRequest`: [5](#0-4) [6](#0-5) 

If a second `signTransaction`/`signMessage` call starts before the first one completes, the earlier `SigningRequest`'s `resolve`/`reject` (its caller's `deferred.promise`) is orphaned — nothing in the class ever calls `reject`/`resolve` for it again, and the UI-facing `hardwareWalletSigningRequestsAtom` (single-value atom, not a map/list) is also overwritten with the second request's state: [7](#0-6) [8](#0-7) 

This is architecturally the same root cause as the reported issue: a resource-creation function (`createReserveAuction` / `#signGeneric`) fails to verify "is there already an active instance of this resource?" before creating a new one, and the tracking/lookup mechanism (`nftContractToTokenIdToAuctionId` / `#signingRequest`) is single-slotted, so the newest instance silently displaces the old one instead of being rejected or queued.

### Impact Explanation
- The caller awaiting the first `signTransaction`/`signMessage` promise (e.g. a dApp-facing tx-signer/message-signer API call) hangs indefinitely — it is never resolved nor rejected, since only the current `#signingRequest.id` can be cancelled/resolved going forward. This is a direct functional/DoS parallel to "permanently locks funds" in the original report (a pending signing operation that can never complete or be cancelled by the caller).
- Because the device itself is asynchronously driven per-request (`device.ensureDeviceReady`, `sign({ device })`), overlapping requests risk a race between the device state and the UI-displayed `baseAssetName`/`scenario`, which is a signing/trust-boundary concern (what is confirmed on-device vs. what is shown to the user) rather than a simple UI glitch.
- Exploitability requires the ability to trigger two rapid, overlapping calls to `signTransaction`/`signMessage` — e.g., from an integrating feature or a connected dApp path invoking the hardware signer, which is unprivileged-reachable through the SDK's asset-signing surface rather than requiring any elevated privileges.

### Likelihood Explanation
Moderate-to-uncertain. I could not fully verify from the index whether `restrictConcurrency`/`make-concurrent`, when called with no explicit `{ concurrency: 1 }` option (as done here, in contrast to every other call site in the repo), truly allows two invocations of `#signGeneric` to execute concurrently, or whether the library defaults to `concurrency: 1` and thus queues the second call until the first's `deferred.promise` settles. This is the key open question determining actual exploitability, and I was unable to confirm the `make-concurrent` package's default behavior within this session (the package source was not present in the indexed files). If the default is not 1, the race described above is directly triggerable; if the default is 1, the practical impact is reduced to a benign serialization (though a stuck/unresponsive first request due to a device disconnect could still starve subsequent calls).

### Recommendation
- Explicitly pass `{ concurrency: 1 }` (or equivalent single-flight/queueing behavior) to `restrictConcurrency` in `#signGeneric`, consistent with every other usage in the codebase.
- Before assigning a new `#signingRequest`, check for and explicitly reject/cancel any existing pending request (mirroring the upstream fix's "must check before creating a new instance" pattern), rather than silently overwriting it.
- Consider tracking signing requests in a keyed structure (map/array) if concurrent requests are intentionally supported, so that no request is ever silently dropped/orphaned.

### Proof of Concept
Conceptual PoC (exact reachability depends on the unresolved `make-concurrent` default-concurrency question noted above):
1. Caller A invokes `hardwareWallets.signTransaction({...})`, which enters `#signGeneric`, creates `deferred_A`, sets `this.#signingRequest = requestA`, and calls `retrySigningRequest(idA)` (not awaited) before returning `deferred_A.promise`.
2. Before the user confirms on the hardware device (device interaction is slow / user is mid-approval), a second call, `hardwareWallets.signMessage({...})` (from another queued request in the same feature, or a re-entrant call), enters `#signGeneric` again, creating `deferred_B` and overwriting `this.#signingRequest = requestB`.
3. `deferred_A.promise` (returned to Caller A) is now unreachable from any future `resolve`/`reject` call, since `cancelSigningRequest`/`retrySigningRequest` only ever match `this.#signingRequest.id` (now `idB`). Caller A's promise hangs forever.
4. If Caller A cancels via UI, it cannot: `cancelSigningRequest(idA, ...)` checks `request?.id !== id` (line 285) against the current `#signingRequest` (now `requestB`), logs "No signing request found for id: idA", and returns without ever rejecting `deferred_A`. [6](#0-5)

### Citations

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L197-202)
```typescript
  #updateSigningRequest = async (state: SigningRequestState): Promise<void> => {
    // Update the internal map
    this.#logger.debug(`Updating signing request state: ${JSON.stringify(state)}`)
    await this.#signingRequestAtom.set(state)
    this.#logger.debug(`Finished updating signing request state: ${JSON.stringify(state)}`)
  }
```

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L218-228)
```typescript
  retrySigningRequest = async (id: string) => {
    const request = this.#signingRequest
    if (request?.id !== id) {
      this.#logger.warn(`No signing request found for id: ${id}`)
      return
    }

    if (this.#isRetrying) {
      this.#logger.debug(`Retry already in progress for id: ${id}, ignoring duplicate call`)
      return
    }
```

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L282-290)
```typescript
  cancelSigningRequest = async (id: string, fromUI: boolean) => {
    const request = this.#signingRequest
    this.#logger.debug(`Cancelling signing request for id: ${id}, fromUI: ${fromUI}`)
    if (request?.id !== id) {
      this.#logger.warn(`No signing request found for id: ${id}`)
      return
    }

    await this.#deleteSigningRequest(id)
```

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L308-343)
```typescript
  #signGeneric = restrictConcurrency(
    async ({ baseAssetName, scenario, sign, walletAccount }: GenericSignParams) => {
      const id = randomBytes(16).toString('hex')
      this.#logger.debug(
        `Starting signing request for ${baseAssetName} with scenario: ${scenario} and id: ${id}`
      )
      const deferred = pDefer()

      // Track the signing request in the internal map
      // so the UI can retry & cancel if needed.
      this.#signingRequest = {
        id,
        baseAssetName,
        walletAccount,
        sign: async ({ device }) => {
          // Kick off the signing request to the UI
          await this.#updateSigningRequest({
            id,
            baseAssetName,
            scenario,
          })

          await device.ensureDeviceReady({ baseAssetName, walletAccount })
          return sign({ device })
        },
        resolve: deferred.resolve,
        reject: deferred.reject,
      }

      // We don't await for the signing request to complete here,
      // as the UI will handle it asynchronously.
      void this.retrySigningRequest(id)

      return deferred.promise
    }
  )
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L348-349)
```typescript
  createMany = makeConcurrent(
    async (
```

**File:** features/personal-notes/module/index.js (L35-35)
```javascript
  #update = makeConcurrent(async (_personalNotesArray, { fromSync } = {}) => {
```

**File:** features/hardware-wallets/src/atoms/hardwareWalletSigningRequestsAtom.ts (L1-14)
```typescript
import { createInMemoryAtom } from '@exodus/atoms'
import type { Definition } from '@exodus/dependency-types'
import type { SigningRequestState } from '../module/interfaces.js'

export const hardwareWalletSigningRequestsAtomDefinition = {
  id: 'hardwareWalletSigningRequestsAtom',
  type: 'atom',
  factory: () =>
    createInMemoryAtom<SigningRequestState>({
      defaultValue: Object.create(null) as SigningRequestState,
    }),
  dependencies: [],
  public: false,
} as const satisfies Definition
```
