### Title
Global signing-request lock in `HardwareWallets` allows a single unresolved sign call to permanently deny hardware-wallet signing for all wallet accounts and dApps - ([File: features/hardware-wallets/src/module/hardware-wallets.ts])

### Summary
The reported PSM bug is a class of "shared limited resource exhausted by one unprivileged actor, denying service to everyone else within the reset window." The closest reachable analog in this codebase is the `HardwareWallets` module's `#signGeneric`, which wraps *all* hardware-wallet `signTransaction`/`signMessage` calls (from any dApp/origin/wallet account) behind a single `restrictConcurrency({ concurrency: 1 })` gate and a single shared `#signingRequest` slot. Unlike the PSM's rate limiter, which self-resets after a duration, this lock has **no timeout and no automatic reset** — it is only released by explicit UI action (retry/cancel) or a successful sign. A caller that drives the flow into the module's non-retriable "leave it dangling" error branch, or simply never triggers UI cancellation, holds this global slot indefinitely, blocking every other signing request app-wide.

### Finding Description
`#signGeneric` is declared once at the class level and shared by both `signTransaction` and `signMessage` for every asset and every wallet account: [1](#0-0) 

Because `restrictConcurrency` (aka `make-concurrent` with `concurrency: 1`) queues concurrent calls to the *same* wrapped function until the previous invocation's returned promise settles, and the wrapped function's completion is tied to `deferred.promise` (resolved/rejected only in `retrySigningRequest` or `cancelSigningRequest`), the “rate‑limit window” here is effectively unbounded: it does not reset on any clock, only on an explicit resolve/reject. [2](#0-1) 

`retrySigningRequest` deliberately leaves the request in a hung "error" state for any error that is neither a known disconnect condition nor a timeout/user-refusal: [3](#0-2) 

In that branch, `#updateSigningRequest` is called but `#deleteSigningRequest`/`deferred.resolve`/`deferred.reject` are not — the promise from the original `signTransaction`/`signMessage` call, and therefore the `restrictConcurrency` slot, stays open. The only paths out are:
- `cancelSigningRequest(id, fromUI)`, which is invoked by the wallet UI, or
- a subsequent successful `retrySigningRequest(id)`. [4](#0-3) 

Because the lock and the `#signingRequest` slot are single, global, per-`HardwareWallets`-instance state (not per wallet account, per asset, or per origin), any unprivileged caller that can trigger a `signTransaction`/`signMessage` request — e.g. a connected dApp calling `eth_sendTransaction`/`solana signTransaction` routed through this module for a hardware-wallet-backed account — can hold this shared slot open indefinitely by causing (or simply not resolving) such an error, or by keeping a request pending without user interaction. Every other signing request, from any other account/asset/origin, then queues behind it forever, since `make-concurrent` serializes calls and there is no timeout enforced at this layer.

This mirrors the reported bug class exactly: a single unprivileged action exhausts a shared, unbounded-duration gate that legitimate users depend on to complete a privileged (signing) operation, and there is no automatic reset.

### Impact Explanation
Any wallet account backed by a hardware wallet (Ledger/Trezor) becomes unable to sign any transaction or message — across all assets and all dApp connections — once the shared slot is stuck. This is a direct denial-of-service against the wallet's core signing capability, not merely a UX inconvenience: while stuck, users cannot approve any pending transfer, swap, or dApp interaction requiring hardware-wallet signature, and (depending on how a hung request is surfaced/cancellable from the UI) recovery may require restarting the application to reset in-memory `#signingRequest`/`#isRetrying` state.

### Likelihood Explanation
Reachability requires only a normal, unprivileged dApp interaction that a connected origin can already perform (requesting a signature) — no privileged key or elevated permission is needed. The trigger conditions (an error outside the known retry/cancel buckets, e.g., an unexpected device/transport error during `sign({ device })`) are plausible in real-world hardware-wallet usage and would be trivially reproducible by a malicious/careless dApp crafting a transaction payload known to fault a specific device/app combination, or simply by never surfacing a cancel action to the user while repeatedly re-triggering sign requests that queue behind the stuck one.

### Recommendation
Add a bounded timeout to the shared signing-request lock (e.g., wrap `#signGeneric`'s work with a hard timeout that force-rejects and clears `#signingRequest` if not resolved within N seconds), and/or scope the lock per wallet-account/asset instead of globally, so a single hung or adversarially-triggered request cannot block unrelated signing operations. Ensure every code path that leaves `#signingRequest` in the "error" state without deleting it still guarantees the underlying `deferred` promise/lock is eventually released (either automatically or by forcing a UI-visible dismiss action rather than a silent hang).

### Proof of Concept
1. Connect a hardware-wallet-backed account (`walletAccount.source` = ledger/trezor) to a dApp/origin.
2. From the dApp, invoke a signing operation (`signTransaction`/`signMessage`) whose underlying `sign({ device })` callback throws an error whose `name`/`message` is not `DisconnectedDevice(DuringOperation)`, does not include `timeout`, and is not `UserRefusedError` (e.g., an unexpected `TypeError` from a malformed but device-accepted payload, or any other uncategorized device error).
3. Observe in `retrySigningRequest` that execution falls into the final `else` branch: `#updateSigningRequest({..., scenario: 'error', ...})` is called, but `#signingRequest` is not cleared and `deferred` is not settled — see [5](#0-4) .
4. From any other wallet account/asset/origin, attempt another `signTransaction`/`signMessage`. Because `#signGeneric` is wrapped with `restrictConcurrency({ concurrency: 1 })` at the class level (shared instance), the new call queues behind the still-pending first call and never executes until the first is explicitly resolved via `cancelSigningRequest`/successful retry, demonstrating the global DoS.

Note: I was not able to execute this end-to-end in a live environment (no runtime/browser access here); the finding is based on static analysis of the exact control flow and the documented semantics of `make-concurrent`'s `concurrency: 1` mode as used elsewhere in this repo (e.g., [6](#0-5) , which relies on the same primitive to serialize wallet `create`/`import`).

### Citations

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L97-105)
```typescript
  #syncedKeysMap = new Map<SyncedKeysId, SyncedKeysData>()

  /** The currently active signing request */
  #signingRequest: SigningRequest | undefined

  /** Flag to prevent concurrent retry attempts */
  #isRetrying = false

  readonly events = new Emitter()
```

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L263-280)
```typescript
      // Errors for which we won't retry
      if (_error.message.includes('timeout') || _error.name === 'UserRefusedError') {
        // User refused the action on the device
        await this.cancelSigningRequest(id, false)
        return
      }

      // Allow the user to retry the signing request
      await this.#updateSigningRequest({
        id,
        scenario: 'error',
        error: _error,
        baseAssetName: this.#signingRequest.baseAssetName,
      })
    } finally {
      this.#isRetrying = false
    }
  }
```

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L282-306)
```typescript
  cancelSigningRequest = async (id: string, fromUI: boolean) => {
    const request = this.#signingRequest
    this.#logger.debug(`Cancelling signing request for id: ${id}, fromUI: ${fromUI}`)
    if (request?.id !== id) {
      this.#logger.warn(`No signing request found for id: ${id}`)
      return
    }

    await this.#deleteSigningRequest(id)

    // Ensure we cancel the action on the device
    if (fromUI) {
      this.#logger.debug(`Cancelling signing request on device for id: ${id}`)
      try {
        const { device } = await this.#getSelectedDevice(request.walletAccount)
        await device.cancelAction()
        this.#logger.debug(`Succesfully cancelled signing request on device for id: ${id}`)
      } catch (error: any) {
        this.#logger.error(`Failed to cancel signing request on device for id: ${id}`, error)
      }
    }

    // Now reject the promise returned to the asset caller
    request.reject(new UserRefusedError(!fromUI))
  }
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
