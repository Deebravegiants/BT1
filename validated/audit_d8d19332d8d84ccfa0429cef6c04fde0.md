Based on the investigation, I found a concrete structural analog of this bug class in the Exodus Hydra software-signing pipeline.

### Title
Arbitrary `txMeta.keyId` accepted without validating it belongs to the requested `walletAccount`, allowing signature generation with an unintended key - (`features/tx-signer/src/module/seed-signer.ts`)

### Summary
The Wonderland Prophet report describes modules that accept a `_request`/dispute payload without validating that it actually corresponds to the `requestId` context being processed, letting a caller substitute arbitrary parameters to bypass the validation that should be scoped to that specific request. The same class of bug exists in Hydra's software transaction signer: `SeedBasedTransactionSigner.signTransaction` accepts a caller-supplied `unsignedTx.txMeta.keyId` and only checks that it is *structurally* a valid `KeyIdentifier` — it never checks that the `keyId` is *the* key that corresponds to the `walletAccount`/`baseAssetName` context that was supposedly authorized for this signing operation.

### Finding Description
`signTransaction` in `SeedBasedTransactionSigner` resolves which key to use as follows: [1](#0-0) 

If `unsignedTx.txMeta.keyId` is absent, the signer correctly derives the key deterministically from the trusted `walletAccount` and `baseAsset` (via `#getSignerForWalletAccount`). But if `txMeta.keyId` is present, the code takes a completely different path: it only asserts that the value is a syntactically valid `KeyIdentifier` object (`KeyIdentifier.validate(keyId)`), then builds a signer bound to `walletAccount.seedId` but with the caller-supplied `keyId` — i.e., an arbitrary derivation path/purpose/key type chosen by the caller, unrelated to the `walletAccount`/`baseAssetName` that were supposed to define which key gets used.

This mirrors the report's root cause exactly: a value taken from the "request" payload (`txMeta.keyId`) that should be *derived from* / *validated against* the trusted context (`walletAccount`) is instead accepted and trusted directly, with only a shallow shape check rather than a consistency/ownership check.

The public API surface for this is: [2](#0-1) 
which is exposed as `public: true` through the SDK's dependency-injection container and can be reached over `@exodus/sdk-rpc`/`@exodus/json-rpc` bridges used for multi-process communication (e.g., extension UI ↔ background process), as described in the sdk-rpc docs: [3](#0-2) 

### Impact Explanation
Any caller able to invoke `transactionSigner.signTransaction` (e.g., a compromised/malicious extension UI/renderer process, or any other less-trusted component communicating over the RPC bridge) can pass an arbitrary `txMeta.keyId` while supplying an unrelated `walletAccount` for display/authorization purposes. Because `KeyIdentifier.validate` only checks shape, not ownership relative to the account being authorized, this allows the caller to obtain a signature over attacker-chosen `txData` using *any* key derivable from the seed (any asset, purpose, account/address index) rather than the key that the surrounding authorization/UI flow indicates. Depending on what higher layers assume about "the key used matches the approved account," this can be leveraged to produce signatures/transactions from unintended addresses/accounts under the same seed — a direct wallet-compromise-adjacent impact (unauthorized signing with an unintended key).

### Likelihood Explanation
Likelihood is Low-to-Medium: it requires a caller with access to the `transactionSigner` API (a "less-trusted process" in Hydra's multi-process model, or any code path that can influence `unsignedTx.txMeta.keyId`) rather than an arbitrary unauthenticated remote attacker. The code comments themselves confirm `keyId` override is an intentionally supported feature ("Sometimes we need a different keyId than the default... EOS tx with the Ethereum key... ripple"), showing this is a real, exercised code path rather than dead code, which increases the realistic attack surface if any caller in the trust chain is compromised or if `txMeta` can be influenced from a less privileged boundary.

### Recommendation
- Short term: When `txMeta.keyId` is supplied, validate that it is consistent with `walletAccount`/`baseAssetName` (e.g., verify the `keyId`'s `derivationAlgorithm`/purpose/accountIndex either matches an explicit allow-list for known cross-asset signing scenarios — EOS/Ripple — or is derived server-side from a trusted mapping, not accepted verbatim from the caller).
- Long term: Replace ad-hoc `keyId` overrides with an explicit, enumerated set of "alternate key" scenarios resolved internally (as already done for the default path via `#getSignerForWalletAccount`), and add tests that attempt to sign with a `keyId` belonging to a different `walletAccount`/asset than the one passed in, asserting rejection.

### Proof of Concept
1. Obtain the ability to call `exodus.transactionSigner.signTransaction` (e.g., from the RPC-connected process as shown in `sdks/headless/__tests__/utils/rpc.js` / `libraries/sdk-rpc`).
2. Call it with:
```ts
await transactionSigner.signTransaction({
  baseAssetName: 'bitcoin',
  walletAccount: someLegitimateWalletAccount, // used only for seedId + UI context
  unsignedTx: {
    txData: attackerChosenData,
    txMeta: {
      keyId: new KeyIdentifier({
        assetName: 'ethereum',
        derivationAlgorithm: 'BIP32',
        derivationPath: "m/44'/60'/0'/0/0", // unrelated to walletAccount/baseAssetName
        keyType: 'secp256k1',
      }),
    },
  },
})
```
3. `KeyIdentifier.validate(keyId)` passes because the object is well-formed, and `#getSignerForKeyId` signs `attackerChosenData` using the Ethereum key at index 0 for the seed, even though the `walletAccount`/`baseAssetName` context indicated Bitcoin — confirming the caller-controlled `keyId` is trusted without cross-checking it against the authorized context. [4](#0-3)

### Citations

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

**File:** features/tx-signer/src/api/index.ts (L40-51)
```typescript
  return {
    transactionSigner: {
      signTransaction: async (params: SignTransactionApiParams) => {
        const walletAccount =
          typeof params.walletAccount === 'string'
            ? await getWalletAccount(params.walletAccount)
            : params.walletAccount

        return transactionSigner.signTransaction({ ...params, walletAccount })
      },
    },
  }
```

**File:** libraries/sdk-rpc/README.md (L15-29)
```markdown
```ts
// in the process that instantiates the RPC server
import createWalletSdk from '@exodus/wallet-sdk'
import { RPC } from '@exodus/sdk-rpc'

const rpc = new RPC({
  transport: windowTransport,
})

const walletSdkApi = createWalletSdk({
  // ...deps
}).resolve()

rpc.exposeMethods(walletSdkApi)
```
```
