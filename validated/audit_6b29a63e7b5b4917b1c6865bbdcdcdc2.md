### Title
Transaction signer accepts an attacker/caller-supplied `keyId` in `txMeta` without scoping it to the requested asset/wallet account, enabling signing with an unintended key - ([File: features/tx-signer/src/module/seed-signer.ts])

### Summary
The external report describes `recoverAsset` accepting an arbitrary address parameter without validating it against a protected value (TRSY), letting a privileged caller act on an asset it should never be able to touch, with no compensating accounting update. The closest reachable analog in this Exodus Hydra wallet SDK is `SeedBasedTransactionSigner.signTransaction` in [1](#0-0) , which lets the caller override the key used to sign a transaction by supplying an arbitrary `txMeta.keyId`, with only a structural (not scope/ownership) validation.

### Finding Description
`signTransaction` normally derives the signing key deterministically from the requested `baseAssetName` and `walletAccount` via `#getSignerForWalletAccount`, which calls `baseAsset.api.getKeyIdentifier(...)` scoped to that asset/account/purpose [2](#0-1) .

However, if the caller-supplied `unsignedTx.txMeta.keyId` is present, the function takes a different path: it only checks that the value is a *structurally* valid `KeyIdentifier` object (`KeyIdentifier.validate(keyId)`), and never verifies that this `keyId` actually corresponds to the `baseAssetName` being signed for, or that it's an allowed key for the calling asset/account context: [3](#0-2) 

`KeyIdentifier.validate` merely checks that fields like `derivationAlgorithm`, `derivationPath`, `keyType`, `assetName` are well-formed — it performs no cross-check against `baseAssetName` or `walletAccount` [4](#0-3) . `#getSignerForKeyId` then builds a signer directly from the supplied `keyId` and the walletAccount's `seedId`, bypassing the intended per-asset key derivation entirely [5](#0-4) .

This is directly analogous to the `recoverAsset` bug: a function meant to operate within a restricted scope (asset-specific signing) accepts an arbitrary caller-controlled identifier (`keyId`) instead of validating it belongs to the expected/allowed scope, allowing the operation to reach into a domain it should not (a different asset's or account's derivation path).

The `TransactionSigner` wrapper that calls into this code performs only generic type assertions (`typeof txMeta === 'object'`) and does not sanitize or restrict `txMeta.keyId` [6](#0-5) . The changelog confirms this "custom keyId" capability was added as a first-class, intentional feature (`feat: allow custom keyId in transaction signing (#11002)`), not test-only scaffolding.

### Impact Explanation
If a caller (e.g. a compromised/malicious internal integration, or any code path that can construct `unsignedTx.txMeta`) can influence `keyId`, it can force the wallet to sign data with a key derived from a different derivation path/asset than the one the user believes they are authorizing (e.g., sign an "EOS-labeled" transaction with the Ethereum key, or point at an arbitrary path under the same seed). Because the check is purely structural, there is no guarantee the resulting signature is scoped to the intended asset/account, which is a form of unauthorized signing with an unintended key. This maps to the "concrete unauthorized signing" impact category.

### Likelihood Explanation
Likelihood is limited because reaching this path requires control over `unsignedTx.txMeta.keyId`, which in the standard call graph is constructed by asset library code, not directly by external dApp/web3 provider input based on what is indexed. This bounds exploitability to callers with the ability to shape `txMeta` (e.g. custom/duplicate asset integration code, or any internal caller reusing this API in a non-standard way), rather than an arbitrary unprivileged web page. Full confirmation of whether an external web3 provider request can set `txMeta.keyId` would require deeper tracing of each asset's `signTx` param construction, which was not fully observable in the indexed code.

### Recommendation
In `seed-signer.ts`, when `txMeta.keyId` is supplied, validate that the `keyId.assetName` (or equivalent scope) matches `baseAssetName`/the asset family explicitly permitted for override (per the documented EOS/ripple exception), rather than accepting any structurally valid `KeyIdentifier`. Maintain an explicit allow-list of asset pairs permitted to use a foreign `keyId`, and reject/assert otherwise, mirroring the recommendation to reconcile `cumulativeFees`/restrict `recoverAsset` in the original report: restrict the override to only its intended narrow use case rather than allowing an arbitrary key from the same seed.

### Proof of Concept
Not independently reproducible from the indexed code alone. Based on the code path, the following pseudo-call demonstrates the vulnerable pattern:
```js
// baseAssetName: 'ethereum', but caller supplies keyId for a different derivation path
await seedBasedTransactionSigner.signTransaction({
  baseAssetName: 'ethereum',
  walletAccount,
  unsignedTx: {
    txData: { /* ethereum tx */ },
    txMeta: {
      keyId: new KeyIdentifier({
        assetName: 'bitcoin',
        derivationAlgorithm: 'BIP32',
        derivationPath: "m/44'/0'/0'/0/0",
      }),
    },
  },
})
```
`KeyIdentifier.validate` passes because the object is well-formed, and `#getSignerForKeyId` signs using the Bitcoin-derived key instead of the Ethereum key implied by `baseAssetName`, with no cross-check enforced in `signTransaction` [3](#0-2) .

### Citations

**File:** features/tx-signer/src/module/seed-signer.ts (L38-69)
```typescript
  async #getSignerForWalletAccount({
    baseAsset,
    walletAccount,
  }: {
    baseAsset: Asset
    walletAccount: WalletAccount
  }): Promise<Signer> {
    const { seedId } = walletAccount
    const defaultPurpose = await this.#assetSources.getDefaultPurpose({
      walletAccount: walletAccount.toString(),
      assetName: baseAsset.name,
    })
    const { chainIndex, addressIndex } = getDefaultPathIndexes({
      asset: baseAsset,
      walletAccount,
      compatibilityMode: walletAccount.compatibilityMode,
    })

    const getDefaultKeyIdentifier = () => {
      return new KeyIdentifier(
        baseAsset.api.getKeyIdentifier({
          compatibilityMode: walletAccount.compatibilityMode,
          purpose: defaultPurpose,
          accountIndex: walletAccount.index!,
          chainIndex,
          addressIndex,
        })
      )
    }

    return this.#createSigner({ seedId, getDefaultKeyIdentifier })
  }
```

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

**File:** libraries/key-identifier/src/key-identifier.js (L82-90)
```javascript
  static validate = (potentialKeyIdentifier) => {
    try {
      // eslint-disable-next-line no-new
      new KeyIdentifier(potentialKeyIdentifier)
      return true
    } catch {
      return false
    }
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
