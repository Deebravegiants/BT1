### Title
Chain-ID selection in Ledger Ethereum hardware signing trusts caller-supplied `assetName` instead of the actual serialized transaction content - (File: features/hw-ledger/src/module/assets/ethereum.ts)

### Summary
The reported Cally bug is a classic "declared type vs. actual type" confusion: `createVault()` trusts a caller-supplied `tokenType` label instead of verifying it against the real type of `token`, and downstream code (`exercise()`/`withdraw()`) blindly branches on that unverified label, leading to stuck/mishandled assets. The closest reachable analog in this repo is in the hardware-wallet Ethereum signing handler, where the chain that a transaction gets signed for is likewise selected from an unverified, caller-supplied label (`assetName`) rather than being derived from or validated against the actual transaction bytes being signed.

### Finding Description
In `createHandler` for Ledger's Ethereum asset app, `signTransaction` deserializes the raw bytes the caller wants signed (`params.signableTransaction`) and then decides which EVM chain ID to stamp onto the transaction purely by switching on the separately-supplied `params.assetName` string: [1](#0-0) 

```
switch (params.assetName) {
  case 'ethereum': { deserializedTransaction.chainId = 1; break }
  case 'matic': { deserializedTransaction.chainId = 137; break }
  case 'basemainnet': { deserializedTransaction.chainId = 8453; break }
  // No default
}
```

There is no assertion that `deserializedTransaction.chainId` (if already present in `signableTransaction`) matches `params.assetName`, nor any check that the two "types" — the declared asset (`assetName`) and the actual transaction payload (`signableTransaction`) — refer to the same chain. This is structurally identical to Cally's bug: two independent fields (`tokenType` vs. `token`, here `assetName` vs. `signableTransaction`'s embedded chain data) are supposed to agree, but only one of them (the declared label) drives the security-relevant branch, and the code comment itself flags this as a known shortcut: `/** TODO: retrieve from meta or bubble this up to the asset library "signHardware" */`.

The call chain that reaches this code is:
- `AssetClientInterface.signTransaction` takes an `assetName` and forwards a derived `baseAssetName` to the transaction signer [2](#0-1) .
- `TransactionSigner.signTransaction` only asserts that `baseAssetName` is a string and that `unsignedTx.txData`/`txMeta` are objects — it does not cross-validate content vs. label [3](#0-2) .
- `HardwareWallets.signTransaction` passes `baseAssetName` straight through to `baseAsset.api.signHardware` [4](#0-3) .
- `LedgerDevice.signTransaction` opens the app keyed by `params.assetName` and hands the raw params to the per-asset `handler.signTransaction` [5](#0-4) , which lands in the vulnerable `switch` above.

### Impact Explanation
If any caller in this chain (e.g., a wallet-account/asset selection bug, a compromised or malicious dApp/RPC-connected feature, or simply a mismatched call from application code) supplies an `assetName`/`baseAssetName` that doesn't match the chain actually encoded in `signableTransaction`, the Ledger device will sign the transaction for the wrong `chainId` (e.g., relabeling a Polygon or Base transaction as Ethereum mainnet, or vice versa). Because EIP-155 chain ID is part of the signed payload and is used to prevent cross-chain replay, this produces a validly-signed transaction for a chain the user never intended to interact with, and the amount/destination shown to the user during on-device approval may not correspond to the actual network that ultimately processes the transaction. This is a direct wallet-compromise-adjacent impact (unauthorized signing for the wrong chain), analogous to the frozen/mismatched-asset impact in the Cally finding, though the severity depends on what upstream caller can actually control `assetName` independently of the transaction bytes — which was not fully verifiable from the indexed code alone.

### Likelihood Explanation
Likelihood is moderate-to-low in a "normal" operation, since in the primary EVM apps flow `assetName` and `signableTransaction` are typically produced together by the same asset library and should agree. However, the finding is reachable through several layers of internal APIs (`AssetClientInterface` → `TransactionSigner` → `HardwareWallets` → Ledger `device.ts` → per-asset handler) none of which cross-validate the two fields, and the author's own TODO comment acknowledges this is a fragile, ad-hoc mapping rather than an authoritative source of truth. Any bug or drift in an upstream feature that computes `assetName` separately from `unsignedTx`/`signableTransaction` (e.g., combined/multi-network assets such as `basemainnet`/`matic` sharing infrastructure with `ethereum`, as seen in `features/available-assets`) could trigger this silently, without an explicit malicious actor.

### Recommendation
Do not derive `chainId` (or any other chain-identifying signing parameter) from a separately-supplied `assetName` string. Instead, require that the chain ID be explicit and authoritative on the transaction data (`txMeta`/`signableTransaction`) itself, and assert equality between the chain ID embedded in the deserialized transaction and the chain ID expected for `assetName` before signing — rejecting the request if they disagree, similar to how `SeedBasedTransactionSigner.signTransaction` asserts on `txMeta.accountIndex` and `keyId` validity today [6](#0-5) .

### Proof of Concept
Conceptual PoC (not confirmed end-to-end due to index limitations on the exact caller that supplies both fields):
1. Construct an `unsignedTx`/`signableTransaction` payload encoding a Base-mainnet transaction (chainId 8453) but invoke the signing flow with `assetName`/`baseAssetName` set to `'ethereum'`.
2. Trace through `AssetClientInterface.signTransaction` → `TransactionSigner.signTransaction` → `HardwareWallets.signTransaction` → `LedgerDevice.signTransaction` → the Ethereum `createHandler.signTransaction` switch statement.
3. Observe that `deserializedTransaction.chainId` gets forcibly overwritten to `1` (Ethereum mainnet) regardless of the transaction's original chain, per the `switch (params.assetName)` logic at [7](#0-6) , and the device signs a chain ID that does not match the transaction's true intended network.

### Citations

**File:** features/hw-ledger/src/module/assets/ethereum.ts (L102-131)
```typescript
    signTransaction: async (params: SignTransactionParams) => {
      assert(
        Array.isArray(params.derivationPaths) && params.derivationPaths.length === 1,
        'derivationsPath array must be one element long'
      )
      assert(Buffer.isBuffer(params.signableTransaction), 'signableTransaction must be Buffer')

      const deserializedTransaction = ethers.parse(params.signableTransaction)

      /** TODO: retrieve from meta or bubble this up to the asset library "signHardware" */
      switch (params.assetName) {
        case 'ethereum': {
          deserializedTransaction.chainId = 1

          break
        }

        case 'matic': {
          deserializedTransaction.chainId = 137

          break
        }

        case 'basemainnet': {
          deserializedTransaction.chainId = 8453

          break
        }
        // No default
      }
```

**File:** features/assets-feature/client/asset-client-interface.js (L361-365)
```javascript
  signTransaction = async ({ assetName, unsignedTx, walletAccount: walletAccountName }) => {
    const baseAssetName = this.#assetsModule.getAsset(assetName).baseAsset.name
    const walletAccount = await this.#getWalletAccount(walletAccountName)
    return this.#transactionSigner.signTransaction({ baseAssetName, unsignedTx, walletAccount })
  }
```

**File:** features/tx-signer/src/module/transaction-signer.ts (L41-55)
```typescript
  signTransaction = async (opts: SignTransactionParams) => {
    assert(typeof opts === 'object', `signTransaction expected parameters`)
    const { baseAssetName, unsignedTx, walletAccount } = opts
    assert(typeof baseAssetName === 'string', `baseAssetName must be string`)
    assert(typeof unsignedTx === 'object', `unsignedTx must be object`)
    const { txData, txMeta } = unsignedTx
    assert(typeof txData === 'object' && txData !== null, `txData must be object`)
    assert(typeof txMeta === 'object' && txMeta !== null, `txMeta must be object`)
    const signer = await this.#getTransactionSigner(walletAccount)
    return signer.signTransaction({
      baseAssetName,
      unsignedTx,
      walletAccount,
    })
  }
```

**File:** features/hardware-wallets/src/module/hardware-wallets.ts (L345-369)
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
```

**File:** features/hw-ledger/src/module/device.ts (L239-248)
```typescript
  signTransaction = async (params: SignTransactionParams) => {
    await this.#ensureApplicationIsOpened(params.assetName)
    return this.#runInSession(async (transport) => {
      const handler = await this.#getAssetApplication(params.assetName).handler(
        transport,
        this.#walletPolicyAtom
      )
      return handler.signTransaction(params)
    })
  }
```

**File:** features/tx-signer/src/module/seed-signer.ts (L117-152)
```typescript
  signTransaction = async (opts: InternalSignTransactionParams) => {
    const { baseAssetName, unsignedTx, walletAccount } = opts
    const baseAsset = this.#assetsModule.getAsset(baseAssetName)

    if (!('compatibilityMode' in unsignedTx.txMeta)) {
      unsignedTx.txMeta.compatibilityMode = walletAccount.compatibilityMode
    }

    if (!('accountIndex' in unsignedTx.txMeta)) {
      unsignedTx.txMeta.accountIndex = walletAccount.index
    }

    assert(
      Number.isInteger(unsignedTx.txMeta?.accountIndex),
      `txMeta.accountIndex was not a valid integer`
    )

    assert(baseAsset.api.features.signWithSigner, `asset ${baseAssetName} does not support signing`)

    const keyId = unsignedTx.txMeta?.keyId
    const signTx = baseAsset.api.signTx!

    if (!keyId) {
      const signer = await this.#getSignerForWalletAccount({ walletAccount, baseAsset })
      return signTx({ unsignedTx, signer })
    }

    // Sometimes we need a different keyId than the default.
    // One example is signing an EOS tx with the Ethereum key, another is ripple:
    // https://github.com/ExodusMovement/exodus-desktop/blob/174efe1145152446e6183f55155972b3acc05ccc/src/app/_local_modules/eosio-write-api/fallback-claim.js#L54
    // https://github.com/ExodusMovement/exodus-desktop/blob/82f1e284efed2bf1ff95798a9e8e89bc71e2ae40/src/app/ui/exodus-global/debug/ripple.js#L105
    assert(KeyIdentifier.validate(keyId), `txMeta.keyId must be a key identifier object`)

    const signer = await this.#getSignerForKeyId({ seedId: walletAccount.seedId, keyId })
    return signTx({ unsignedTx, signer })
  }
```
