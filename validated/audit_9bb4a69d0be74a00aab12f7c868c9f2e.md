### Title
Premature clearing of signing-request state before device cancellation is confirmed allows a "cancelled" signature to still resolve - (File: features/hardware-wallets/src/module/hardware-wallets.ts)

### Summary
This is a direct structural analog of the Rubicon `outstandingAmount` bug: bookkeeping state is cleared as soon as a cancellation is *initiated*, rather than after the underlying operation is *confirmed reversed*. In `hardware-wallets.ts`, `cancelSigningRequest()` deletes the in-memory/atom-tracked signing request (and thus tells the UI "no signing request pending") **before** the hardware device's cancellation is confirmed, and any failure to actually cancel on-device is silently swallowed. A concurrently in-flight `retrySigningRequest()` call can still complete the original `sign()` and resolve the original deferred promise with a valid signature after the UI has already reported the request as cancelled.

### Finding Description
`cancelSigningRequest` performs the following sequence [1](#0-0) :

1. `await this.#deleteSigningRequest(id)` — immediately clears `this.#signingRequest` and resets the `signingRequestAtom`, which is what the UI observes to know a request is no longer pending.
2. Only afterward does it attempt `device.cancelAction()` to actually stop the hardware device from continuing the operation — wrapped in a `try/catch` that just logs and swallows any failure [2](#0-1) .
3. Only at the very end does it call `request.reject(new UserRefusedError(...))` on the deferred promise that was originally returned to the asset caller (e.g. `signTransaction`/`signMessage`).

Meanwhile, `retrySigningRequest` may already be mid-flight, awaiting `await request.sign({ device })` using a **local reference to the same `request` object and the same `deferred.resolve`/`reject`** [3](#0-2) . Because `#deleteSigningRequest` only clears the shared `this.#signingRequest` field but does not abort or invalidate the closures already capturing `request`/`deferred`, if the on-device cancellation in step 2 fails or does not actually interrupt the pending device operation (e.g. `#getSelectedDevice` throws `NoDeviceFoundError` because the device list is momentarily empty, or `device.cancelAction()` errors for any transport reason), the original `sign()` call can still complete successfully. When it does, `retrySigningRequest` calls `request.resolve(result)` [4](#0-3) , settling the very deferred promise that `cancelSigningRequest` is racing to reject with `UserRefusedError`. A JS promise only honors the first settlement — whichever of `resolve(result)` / `reject(UserRefusedError)` executes first wins. Since `cancelSigningRequest`'s reject happens only after two `await`s (`#deleteSigningRequest`, `getSelectedDevice`+`cancelAction`), there is a real window in which the legitimate signature resolution from `retrySigningRequest` wins the race despite the user having clicked "Cancel."

This exactly mirrors the root cause pattern in the report: internal accounting/state (`outstandingAmount` / `this.#signingRequest`) is cleared optimistically on the "cancel" path before the underlying effect (WETH repayment / actual device cancellation) is verified, and the error/failure path of the "clean up" step is not fail-safe (in Rubicon: no repayment check; here: swallowed `catch` on `device.cancelAction()`).

### Impact Explanation
If this race is won by the in-flight sign operation, a transaction or message the user explicitly cancelled in the UI can still be signed and delivered to the calling code as a resolved, valid signature — a concrete case of unauthorized/uncontrolled signing that bypasses the user's cancellation intent. Depending on the caller (e.g. a dApp-initiated `signTransaction`), this could result in a transaction being broadcast or a message being signed against the user's explicit "cancel" action, i.e. a direct wallet-compromise-adjacent impact (unauthorized signing).

### Likelihood Explanation
The race requires a normal, unprivileged user interaction: initiating a hardware-wallet signing request and then pressing "Cancel" while the device operation is in flight. The window is opened whenever `#getSelectedDevice`/`device.cancelAction()` fails to reach or interrupt the exact device session performing the operation (e.g., transient device-list/discovery gaps, BLE/USB hiccups, or `NoDeviceFoundError`) — conditions plausible in real hardware-wallet usage, especially over Bluetooth. It requires no malicious peer/operator and no privileged access; it is triggerable purely by an ordinary user's cancel action combined with an already-known-flaky hardware transport layer. I was not able to fully confirm (due to iteration limits) whether `#getSelectedDevice`/discovery always returns the exact same in-memory `LedgerDevice`/`TrezorDevice` instance handling the pending session, which would determine how often `device.cancelAction()` truly no-ops versus succeeds; this affects exact likelihood but not the fundamental ordering flaw.

### Recommendation
Do not clear `this.#signingRequest` / reset the atom until the on-device cancellation is confirmed successful, or otherwise make the deferred settlement order deterministic: reject the deferred `request` (and mark it as cancelled) atomically before any awaited device call, and have `retrySigningRequest`/`#signGeneric`'s success path check a "cancelled" flag immediately after `await request.sign(...)` resolves, before calling `resolve()`. Additionally, `device.cancelAction()` failures must not be silently swallowed — if cancellation cannot be confirmed, the system should treat the request as still pending/unsafe rather than reporting it as cleared to the UI.

### Proof of Concept
1. Initiate `signTransaction`/`signMessage` via `hardware-wallets.ts`, which calls `#signGeneric` → `retrySigningRequest(id)`, which starts `await request.sign({ device })` on the actual connected device (long-running, e.g. waiting for physical device button confirmation).
2. While step 1's `sign()` call is still pending, call `cancelSigningRequest(id, true)` from the UI.
3. `cancelSigningRequest` immediately clears `this.#signingRequest` via `#deleteSigningRequest`, updating the atom the UI reads (UI now shows no pending request).
4. `cancelSigningRequest` calls `#getSelectedDevice` then `device.cancelAction()`; simulate transient failure (e.g. mock `#listLedgerDevicesOrEmpty`/`#listTrezorDevicesOrEmpty` to return `[]` momentarily, causing `NoDeviceFoundError`), which is caught and only logged [5](#0-4) .
5. Meanwhile the user actually approves on the physical device (unaware software marked it cancelled); the original `sign()` promise from step 1 resolves with a valid signature.
6. `retrySigningRequest`'s success path executes `request.resolve(result)` [4](#0-3)  before `cancelSigningRequest` reaches its own `request.reject(...)` call, so the original caller's promise resolves with the signature despite the UI reporting cancellation.

### Citations

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L218-238)
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

    this.#isRetrying = true

    try {
      this.#logger.debug(`Attempting to get selected device for signing request with id: ${id}`)
      const { device } = await this.#getSelectedDevice(request.walletAccount)
      this.#logger.debug(`Attempting to sign for signing request with id: ${id}`)
      const result = await request.sign({ device })
      await this.#deleteSigningRequest(id)
      request.resolve(result)
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
