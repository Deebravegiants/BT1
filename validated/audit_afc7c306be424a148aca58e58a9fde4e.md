Confirmed: `LedgerDevice` has no `getWalletId` implementation, unlike `TrezorDevice` which implements `getWalletId`/`ensureDeviceReady` walletId verification.

### Title
Ledger device selection ignores `walletAccount.id`, allowing signing under a different physical device without a fresh confirmation - ([File: features/hardware-wallets/src/module/hardware-wallets.ts])

### Summary
`TransactionSigner.signTransaction` delegates to `HardwareWallets.requireDeviceFor(walletAccount)`, which routes to `#getSelectedDevice` and eventually `device.ensureDeviceReady({ baseAssetName, walletAccount })` before signing. For Trezor, `ensureDeviceReady` verifies the connected device's `getWalletId()` against `walletAccount.id` and throws `WrongWalletSelectedError` on mismatch, but for Ledger, `ensureDeviceReady` only opens the correct asset application and never checks `walletAccount.id`/device identity at all.

### Finding Description
`TransactionSigner.#getTransactionSigner` (`features/tx-signer/src/module/transaction-signer.ts:34-36`) calls `this.#hardwareWallets.requireDeviceFor(walletAccount)` for any `walletAccount.isHardware` account. `HardwareWallets.requireDeviceFor` (`features/hardware-wallets/src/module/hardware-wallets.ts:826-841`) just binds the given `walletAccount` into `signTransaction`/`signMessage` calls without any device-matching step of its own.

Actual device selection happens in `#getSelectedDevice` (`hardware-wallets.ts:170-195`): it filters connected descriptors only by **manufacturer** (`walletAccount.source`, e.g. `'ledger'` vs `'trezor'`) and then unconditionally picks `descriptors[0]` — the first connected device of that manufacturer. It never compares the descriptor/device identity to `walletAccount.id`.

The only remaining safety net is `device.ensureDeviceReady({ baseAssetName, walletAccount })`, invoked in `#signGeneric`'s `sign` callback (`hardware-wallets.ts:330`). For Trezor (`features/hw-trezor/src/module/device.ts:100-127`), this method explicitly derives the wallet fingerprint via `getWalletId()` and compares it against `walletAccount.id`, throwing `WrongWalletSelectedError` if they don't match — providing exactly the re-confirmation guard the question is probing for. For Ledger (`features/hw-ledger/src/module/device.ts:178-180`), `ensureDeviceReady` only calls `#ensureApplicationIsOpened(baseAssetName)` and does not use `walletAccount` at all; `LedgerDevice` has no `getWalletId` implementation (confirmed absent from the class, unlike `TrezorDevice`).

Consequently, if a user has two different paired Ledger-sourced `WalletAccount`s (different `id`s, e.g. from two distinct physical Ledgers, or a `WalletAccount` referencing an id belonging to another Ledger) and only one Ledger is currently connected, a signing request for the *other* account's `WalletAccount` (chosen by a caller through the RPC-facing `transactionSigner.signTransaction({ walletAccount })` API, `features/tx-signer/src/api/index.ts:42-49`) will silently be routed to whichever Ledger happens to be plugged in. The signature is produced using `accountIndex = walletAccount.index` (`hardware-wallets.ts:352,358`) against the physically connected device's seed — not the seed originally used to create/approve that `walletAccount`. No error, no re-confirmation, and no mismatch is surfaced; the device-approval prompt only asks the user to approve the tx on-device, without confirming the device matches the intended `walletAccount.id`.

### Impact Explanation
This can cause signing under an unintended key/account: a transaction the user believes is being signed from `walletAccount` (tied to a specific physical Ledger and its `id`) may be silently signed using a different connected Ledger's key for the same `index`, producing a signature/address the user did not intend to use. This matches a "wrong-account signing" / "unauthorized signing" impact class, though it requires the user to actually own/have paired multiple distinct Ledger devices and have only the wrong one connected at signing time — it does not allow an attacker to forge signatures from a device they don't physically possess or bypass on-device transaction approval.

### Likelihood Explanation
Requires: (1) the user has multiple `WalletAccount`s of `source: 'ledger'` with different `id`s (multiple paired Ledger devices), (2) only one (the "wrong" one) is connected when a dApp/RPC caller requests signing for a `walletAccount` corresponding to the other device, and (3) the RPC/API layer permits selecting an arbitrary existing `walletAccount` (by name or object) for signing rather than restricting to a single connected/approved account. Given the `transactionSigner` API resolves `walletAccount` by name from `walletAccountsAtom` without cross-checking currently connected device identity, this path is reachable for any already-paired Ledger account name known to the caller. This is a real, reproducible gap in the Ledger path specifically (Trezor already has the equivalent protection).

### Recommendation
Implement a Ledger-equivalent of Trezor's wallet-identity check: add a `getWalletId`-style fingerprint derivation for `LedgerDevice` (e.g., derived from a fixed path public key/xpub) and enforce it inside `ensureDeviceReady` by comparing against `walletAccount.id`, throwing a `WrongWalletSelectedError` (or similar) on mismatch, mirroring `features/hw-trezor/src/module/device.ts:100-127`. Additionally, `#getSelectedDevice` in `hardware-wallets.ts` should ideally match descriptors against `walletAccount.id`/device identity rather than blindly picking the first connected device of the correct manufacturer.

### Proof of Concept
Integration test in `features/hardware-wallets/src/module/__tests__/hardware-wallets.test.ts`:
1. Mock `ledgerDiscovery.list()` to return a single connected descriptor representing "Device A" (`mockDevice.ensureDeviceReady` is a spy that does nothing, no `getWalletId`).
2. Construct `walletAccountB = new WalletAccount({ source: 'ledger', id: 'device-B-id', index: 0 })` (representing an account belonging to a different, currently-disconnected Ledger "Device B").
3. Call `hardwareWallets.signTransaction({ baseAssetName, unsignedTx, walletAccount: walletAccountB })`.
4. Assert current (vulnerable) behavior: the call succeeds and `mockDevice` (Device A) is used to sign, with `mockDevice.ensureDeviceReady` called but performing no `walletAccount.id` verification — i.e., `baseAsset.api.signHardware` is invoked with Device A's session despite `walletAccount.id !== 'device-A-id'`.
5. Expected/fixed behavior: `ensureDeviceReady`/`#getSelectedDevice` should detect the identity mismatch (via a Ledger wallet-fingerprint check analogous to Trezor's) and reject with a `WrongWalletSelectedError`-type exception instead of silently signing. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

### Citations

**File:** features/tx-signer/src/module/transaction-signer.ts (L29-39)
```typescript
  #getTransactionSigner = async (walletAccount: WalletAccount): Promise<InternalSigner> => {
    if (walletAccount.isSoftware) {
      return this.#seedBasedTransactionSigner
    }

    if (walletAccount.isHardware && this.#hardwareWallets) {
      return this.#hardwareWallets.requireDeviceFor(walletAccount)
    }

    throw new UnsupportedWalletAccountSource(walletAccount.source)
  }
```

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L170-195)
```typescript
  #getSelectedDevice = async (
    walletAccount?: WalletAccount
  ): Promise<{
    device: HardwareWalletDevice
  }> => {
    let descriptors: HardwareWalletDescriptor[]
    const manufacturer = walletAccount?.source as HardwareWalletManufacturer | undefined

    if (manufacturer === 'ledger') {
      descriptors = await this.#listLedgerDevicesOrEmpty()
    } else if (manufacturer === 'trezor') {
      descriptors = await this.#listTrezorDevicesOrEmpty()
    } else {
      const [trezors, ledgers] = await Promise.all([
        this.#listTrezorDevicesOrEmpty(),
        this.#listLedgerDevicesOrEmpty(),
      ])
      descriptors = [...trezors, ...ledgers]
    }

    if (descriptors[0]) {
      return { device: await descriptors[0].get() }
    }

    throw new NoDeviceFoundError()
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

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L826-841)
```typescript
  requireDeviceFor = async (walletAccount: WalletAccount) => {
    return {
      signTransaction: ({
        baseAssetName,
        unsignedTx,
        multisigData,
      }: Omit<SignTransactionParams, 'walletAccount'> & { walletAccount?: WalletAccount }) =>
        this.signTransaction({ baseAssetName, unsignedTx, multisigData, walletAccount }),
      signMessage: ({
        assetName,
        derivationPath,
        message,
      }: Omit<SignMessageParams, 'walletAccount'>) =>
        this.signMessage({ assetName, derivationPath, message, walletAccount }),
    }
  }
```

**File:** features/hw-trezor/src/module/device.ts (L100-127)
```typescript
  ensureDeviceReady = async ({ walletAccount }: EnsureDeviceReadyParams): Promise<void> => {
    const walletId = String(walletAccount.id ?? '')

    // Legacy accounts may have id === <deviceId> (no walletId persisted).
    // In that case, treat as standard and avoid triggering a passphrase prompt.
    if (!/^[\da-f]{32}$/iu.test(walletId)) {
      if (this.#events.getPassphraseMode() !== 'standard') {
        await this.setPassphraseMode('standard')
      }

      return
    }

    // Attempt 1: check current session first (avoids resets/prompts when already correct).
    const walletIdCurrent = await this.getWalletId()
    if (walletIdCurrent === walletId) return

    // Attempt 2: reset to standard wallet context (no passphrase prompt) and re-check.
    await this.setPassphraseMode('standard')
    const walletIdStandard = await this.getWalletId()
    if (walletIdStandard === walletId) return

    // Attempt 3: reset to hidden wallet context and prompt for passphrase on-device, then re-check.
    await this.setPassphraseMode('hidden')
    const walletIdHidden = await this.getWalletId()
    if (walletIdHidden === walletId) return

    throw new WrongWalletSelectedError()
```

**File:** features/hw-ledger/src/module/device.ts (L178-180)
```typescript
  ensureDeviceReady = async ({ baseAssetName }: EnsureDeviceReadyParams) => {
    await this.#ensureApplicationIsOpened(baseAssetName)
  }
```

**File:** features/tx-signer/src/api/index.ts (L29-49)
```typescript
const createTransactionSignerApi = ({
  transactionSigner,
  walletAccountsAtom,
}: Dependencies): TransactionSignerApi => {
  const getWalletAccount = async (name: string): Promise<WalletAccount> => {
    const walletAccounts = await walletAccountsAtom.get()
    const walletAccount = walletAccounts[name]
    assert(walletAccount, `Unknown wallet account: ${name}`)
    return walletAccount
  }

  return {
    transactionSigner: {
      signTransaction: async (params: SignTransactionApiParams) => {
        const walletAccount =
          typeof params.walletAccount === 'string'
            ? await getWalletAccount(params.walletAccount)
            : params.walletAccount

        return transactionSigner.signTransaction({ ...params, walletAccount })
      },
```
