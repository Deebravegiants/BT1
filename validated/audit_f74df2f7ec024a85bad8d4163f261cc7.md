### Title
Unvalidated `txMeta.keyId` in `SeedBasedTransactionSigner.signTransaction` allows signing arbitrary data with an unintended key - (File: `features/tx-signer/src/module/seed-signer.ts`)

### Summary
`SeedBasedTransactionSigner.signTransaction` accepts an optional `keyId` inside `unsignedTx.txMeta` and, if present, uses it to derive the signer instead of deriving the key from the declared `baseAssetName`/`walletAccount` pair. The only validation performed is a structural check (`KeyIdentifier.validate(keyId)`) and that the `seedId` matches the wallet account's seed — there is no check that the supplied `keyId` is actually compatible with (i.e., belongs to the same asset/derivation purpose as) `baseAssetName`. This mirrors the `VoterProxy.deposit` pattern of accepting `_token`/`_gauge` pairs without validating their compatibility, letting a caller mix an unrelated but valid credential/identifier with an unrelated payload.

### Finding Description
In `features/tx-signer/src/module/seed-signer.ts`: [1](#0-0) 

`signTransaction` derives the base asset purely from `baseAssetName`, but if `unsignedTx.txMeta.keyId` is present, it bypasses `#getSignerForWalletAccount` (which derives the key deterministically from `baseAsset` + `walletAccount`) and instead calls `#getSignerForKeyId`, which only enforces that the `keyId` is well-formed and scoped to the same `seedId`: [2](#0-1) [3](#0-2) 

There is no assertion that `keyId`'s asset/purpose/derivation path corresponds to `baseAssetName`. The public-facing `transaction-signer.ts` module wrapper also does not add this check — it only validates types of `baseAssetName`, `txData`, and `txMeta`, not their mutual compatibility: [4](#0-3) 

The API layer (`features/tx-signer/src/api/index.ts`) simply forwards caller-supplied params to `transactionSigner.signTransaction` after resolving `walletAccount` by name — it performs no additional validation of `unsignedTx.txMeta`: [5](#0-4) 

And `AssetClientInterface.signTransaction` similarly passes the caller-provided `unsignedTx` straight through without sanitizing `txMeta`: [6](#0-5) 

This is the direct analog of the reported bug class: `VoterProxy.deposit` accepted arbitrary `(_token, _gauge)` pairs without verifying they were compatible, enabling misuse. Here, `signTransaction` accepts an arbitrary `(baseAssetName, txMeta.keyId)` pairing without verifying the `keyId` actually corresponds to `baseAssetName`'s expected derivation, allowing a caller to request that data intended to look like one asset's transaction actually be signed with a key identifier belonging to a different asset/derivation path in the same seed.

### Impact Explanation
If any caller upstream of `transactionSigner.signTransaction` (an asset plugin, an SDK consumer, or a compromised/malicious UI/dApp integration path) can influence `unsignedTx.txMeta.keyId` independently of `baseAssetName`, this becomes a signing oracle: attacker-controlled byte data (`txData`) can be signed under an arbitrary key from the user's seed (subject only to structural `KeyIdentifier` validation), rather than the key that is legitimately associated with the declared asset/account context. This is a concrete unauthorized-signing primitive — the wallet could be tricked into producing a valid signature over attacker-chosen data using a key different from the one the user believes/intends they are authorizing, undermining the authorization/compatibility boundary between "what asset the user thinks they're signing for" and "which of the wallet's private keys actually signs."

### Likelihood Explanation
The code comments acknowledge that `txMeta.keyId` is intentionally used in some legitimate internal flows (EOS/Ripple key-derivation-mismatch cases), meaning the field is a recognized, exercised code path rather than dead code. However, I could not fully confirm from the indexed files whether externally-supplied/dApp-supplied `unsignedTx` objects can reach this path with attacker-controlled `txMeta.keyId` untouched by sanitization in the UI or provider layers (`AssetClientInterface.signTransaction` forwards `unsignedTx` as received at line 364, but the earlier construction of `unsignedTx` by asset-specific transaction builders was not traceable within the indexed context). Given index size limits, some of the UI/provider-level call sites that construct `unsignedTx` before reaching this API were not available for review, so full end-to-end reachability by an untrusted/dApp actor is not proven, only the missing compatibility check at the signer layer is proven.

### Recommendation
In `SeedBasedTransactionSigner.signTransaction`, when a `keyId` is supplied via `unsignedTx.txMeta.keyId`, validate that it is compatible with `baseAssetName` (e.g., assert `keyId.keyType`/purpose corresponds to an asset/purpose combination permitted for `baseAssetName`, similar to how `VoterProxy` is recommended to check `ICurveGauge(_gauge).withdraw()` returns the expected `_token`). At minimum, maintain an explicit allowlist of asset pairs permitted to use cross-asset `keyId` overrides (matching the existing EOS/Ripple use cases) and reject any `keyId` outside that allowlist.

### Proof of Concept
Conceptual PoC (pending confirmation of external reachability, given indexing limits):
1. A caller invokes `transactionSigner.signTransaction({ baseAssetName: 'ethereum', unsignedTx: { txData: <arbitrary bytes>, txMeta: { keyId: <valid KeyIdentifier for a different asset/purpose, e.g. bitcoin> } }, walletAccount })`.
2. `seed-signer.ts` line 148 only checks `KeyIdentifier.validate(keyId)` (structural validity), and line 150 derives the signer using that `keyId` scoped to the same `seedId`.
3. `signTx` on the `ethereum` asset API signs `txData` using the Bitcoin-purpose key rather than the Ethereum key, producing a signature under an unintended key for attacker-supplied data — never verifying `keyId` corresponds to `baseAssetName`. [7](#0-6)

### Citations

**File:** features/tx-signer/src/module/seed-signer.ts (L71-73)
```typescript
  async #getSignerForKeyId({ seedId, keyId }: { seedId?: string; keyId: KeyIdentifier }) {
    return this.#createSigner({ seedId, getDefaultKeyIdentifier: () => new KeyIdentifier(keyId) })
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

**File:** features/assets-feature/client/asset-client-interface.js (L361-365)
```javascript
  signTransaction = async ({ assetName, unsignedTx, walletAccount: walletAccountName }) => {
    const baseAssetName = this.#assetsModule.getAsset(assetName).baseAsset.name
    const walletAccount = await this.#getWalletAccount(walletAccountName)
    return this.#transactionSigner.signTransaction({ baseAssetName, unsignedTx, walletAccount })
  }
```
