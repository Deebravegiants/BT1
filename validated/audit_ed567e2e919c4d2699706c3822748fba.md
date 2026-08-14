### Title
Single-slot hardware wallet signing request lets any dApp/site DOS all other signing (transactions/messages) for that device - ([File: features/hardware-wallets/src/module/hardware-wallets.ts])

### Summary
`HardwareWallets` stores exactly one active signing request in a private field, and its entry point (`#signGeneric`) is wrapped with `restrictConcurrency` (concurrency 1). Any caller (including a connected dApp via `window.exodus.ethereum.request` → `eth_sendTransaction`/message signing) that triggers a hardware-wallet `signTransaction`/`signMessage` call occupies this single slot until the user (or the request itself) explicitly cancels/resolves it. There is no automatic timeout. Because there's only one slot, and only the party who initiated the request or the UI (`cancelSigningRequest`) can clear it, a hung or intentionally-never-approved request from one origin blocks every other legitimate signing request from being processed, exactly analogous to the bonding mechanism in the external report where a single "bond" slot froze all further settlement until manually cleared.

### Finding Description
`HardwareWallets` keeps a module-level singleton `#signingRequest`, populated by `#signGeneric`: [1](#0-0) 

`#signGeneric` is rate-limited to a single concurrent execution via `restrictConcurrency` (i.e. `make-concurrent`), and it creates a deferred promise that is only resolved/rejected by `retrySigningRequest` (on success) or `cancelSigningRequest` (on explicit cancel): [2](#0-1) 

`signTransaction` and `signMessage` — both reachable indirectly from untrusted dApp input via the web3 provider RPC surface (`eth_sendTransaction`, message-signing RPC methods) — funnel into this same shared `#signGeneric` gate: [3](#0-2) 

Crucially, the only way to release the slot is:
1. `retrySigningRequest` completing successfully (requires physical device interaction to actually sign), or
2. `cancelSigningRequest`, called either from the UI (`fromUI = true`, requiring the *user* to press cancel) or from an internal timeout/`UserRefusedError` path triggered by the device itself: [4](#0-3) 

There is no automatic expiry of `#signingRequest` if the request is simply left pending (e.g., a dApp fires `eth_sendTransaction`, the wallet surfaces a device-approval prompt, and the user is not immediately present, or the calling site deliberately never causes a device error/rejection). While that pending request exists, every subsequent call to `signTransaction`/`signMessage` — for *any* asset, from *any* origin, hardware account — queues behind `restrictConcurrency`'s concurrency-1 gate and cannot proceed. This is the same class of bug as the bonding report: a single shared, exclusive resource slot that any unprivileged caller can occupy and that only a manual, out-of-band action (user cancel or device response) can release, resulting in denial of service for all other legitimate operations relying on that resource.

### Impact Explanation
Any website/dApp connected to the wallet (an unprivileged, untrusted origin under the Web3 Provider RPC trust boundary documented in `docs/web3-providers/ethereum-provider-api.md`) can call `ethereum.request({ method: 'eth_sendTransaction', ... })` (or an equivalent message-sign RPC) targeting a hardware-wallet account, and simply not resolve the interaction (e.g., keep the tab in background, or exploit any code path that doesn't reach `cancelSigningRequest`/`retrySigningRequest`'s reject/resolve branches). Because only one `#signingRequest` can exist at a time and `#signGeneric` restricts concurrency to 1, this locks out signing for every other dApp/tab and even the user's own subsequent, legitimate signing attempts on that hardware wallet account until the pending request is manually cleared. This matches the "denial of service, holding functionality hostage" impact described in the source report, applied here to wallet signing availability rather than fund freezing directly, but it can still block a user from completing time-sensitive transactions.

### Likelihood Explanation
Likelihood is moderate-to-high for hardware-wallet users interacting with dApps: triggering the vulnerable code path only requires normal `window.exodus.ethereum.request` calls that any web page can make once connected, with no special privileges needed. The severity depends on whether any hidden/automatic timeout exists elsewhere in the call stack (e.g., a transport-level timeout in `LedgerDevice`/`TrezorDevice`) that would eventually reject a truly abandoned request — I did not find explicit evidence of a bounded timeout guarding the full end-to-end flow within `hardware-wallets.ts` itself (only device-transport level errors like `DisconnectedDevice` are handled, which depend on the underlying hardware transport actually erroring out).

### Recommendation
- Scope the signing-request lock per wallet-account/device (or per origin) rather than as a single wallet-wide singleton, so one pending request cannot block unrelated signing operations.
- Add a hard timeout on pending signing requests (auto-cancel via `cancelSigningRequest` after N seconds/minutes of inactivity) so an abandoned or intentionally-stalled request cannot indefinitely occupy the slot.
- Consider allowing new signing requests to supersede/cancel a stale pending request automatically (with an explicit "another connection wants to sign — cancel current request?" UX) similar to Alex's suggestion in the original report to de-prioritize the exclusive lock in favor of allowing concurrent handling.

### Proof of Concept
1. Connect a malicious dApp to Exodus with a hardware-wallet account selected.
2. From the dApp, call `window.exodus.ethereum.request({ method: 'eth_sendTransaction', params: [tx] })`, which resolves to `HardwareWallets.signTransaction` → `#signGeneric`, populating `#signingRequest` and awaiting `retrySigningRequest`/UI action [2](#0-1) .
3. Do not respond to the device prompt (e.g., background the tab, or keep the device disconnected/idle so no `DisconnectedDevice`/`UserRefusedError` fires).
4. From a second (legitimate) dApp or the wallet UI itself, attempt another `signTransaction`/`signMessage` call for the same or a different asset on the same hardware wallet — the call queues indefinitely behind `restrictConcurrency`'s concurrency-1 gate and never executes until the first request is cancelled, demonstrating the DOS of the signing subsystem.

### Citations

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L99-105)
```typescript
  /** The currently active signing request */
  #signingRequest: SigningRequest | undefined

  /** Flag to prevent concurrent retry attempts */
  #isRetrying = false

  readonly events = new Emitter()
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

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L345-388)
```typescript
  signTransaction = async ({
    baseAssetName,
    unsignedTx,
    walletAccount,
    multisigData,
  }: SignTransactionParams) => {
    const baseAsset = this.#assetsModule.getAsset(baseAssetName)
    const accountIndex = walletAccount.index

    const sign: GenericSignCallback = async ({ device }) => {
      return baseAsset.api.signHardware({
        unsignedTx,
        hardwareDevice: device,
        accountIndex,
        multisigData,
      })
    }

    return this.#signGeneric({
      baseAssetName,
      scenario: 'signTransaction',
      sign,
      walletAccount,
    })
  }

  signMessage = async ({
    assetName,
    derivationPath,
    message,
    walletAccount,
  }: SignMessageParams) => {
    const baseAssetName = this.#assetsModule.getAsset(assetName).baseAsset.name

    const sign: GenericSignCallback = async ({ device }) => {
      return device.signMessage({
        assetName: baseAssetName,
        derivationPath,
        message,
      })
    }

    return this.#signGeneric({ baseAssetName, scenario: 'signMessage', sign, walletAccount })
  }
```
