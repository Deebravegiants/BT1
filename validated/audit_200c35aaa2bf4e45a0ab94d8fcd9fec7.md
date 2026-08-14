### Title
`AssetClientInterface.signTransaction` allows signing/dApp-driven transactions for assets that are not in the available-asset allowlist - ([File: features/assets-feature/client/asset-client-interface.js])

### Summary
The Sherlock report describes a class of bug where a "delisting" restriction is enforced at one entry point (`deposit`) but not at the actual state-mutating/authorization path (direct transfer + health check), so an account that already holds the delisted asset can keep using it. The analogous pattern in this repo is the asset-availability gate (`availableAssetNamesAtom`) that is enforced in read/listing paths of `AssetClientInterface` but not enforced in the signing path, `signTransaction`.

### Finding Description
`AssetClientInterface` consistently filters or asserts against the `availableAssetNamesAtom`/asset registry for informational/listing endpoints, e.g. `getAssetsForNetwork` explicitly intersects with `availableAssetNames`: [1](#0-0) 

and `getAssetConfig` asserts the asset is a known/supported asset: [2](#0-1) 

However, `signTransaction` — the method that actually authorizes a cryptographic signature to be produced for a given `assetName`/`walletAccount` — performs no check against `#availableAssetNamesAtom` (or any "is this asset still supported/listed" gate) before delegating straight to `#transactionSigner.signTransaction`: [3](#0-2) 

It only resolves `baseAssetName` via `assetsModule.getAsset(assetName).baseAsset.name` and forwards to the signer. The downstream signer (`seed-signer.ts`) likewise only checks `baseAsset.api.features.signWithSigner`, not whether the asset is currently available/enabled: [4](#0-3) 

This mirrors the reported bug class exactly: a restriction ("asset X is delisted/unsupported, block new usage") is enforced in the "front door" (listing/config APIs used to populate UI, dApp connect flows, `getAssetsForNetwork`) but not in the actual privileged action (signing), because the signing path assumes any asset object retrievable from `assetsModule.getAsset()` is fine to sign for, regardless of its availability/lifecycle status. Since `assetsModule.getAsset()` continues to return delisted/disabled asset definitions (they are only removed from the `availableAssetNamesAtom` set, not from the module's registry — confirmed by the `#isSupportedAsset` pattern used elsewhere: `this.#availableAssetNames.includes(assetName) && !this.#getAsset(assetName).isCombined`, in `features/balances/module/index.js:293-294`), a dApp (via a web3 provider such as `window.ethereum`/`window.solana`/`window.exodus.cardano` that ultimately calls into `assetClientInterface.signTransaction`) or any internal caller can still request and obtain a valid signature for an asset that has been intentionally delisted/blocked at the availability layer.

### Impact Explanation
If an asset is delisted for security reasons (e.g. a broken/malicious token contract, a chain fork, a compromised bridge), the wallet's availability/enabled-asset layer is supposed to stop new interactions with it. Because `signTransaction` bypasses this check, an unprivileged website (dApp) connected to the wallet can still get the wallet to produce valid signatures for transactions involving the delisted asset, defeating the purpose of the delisting and potentially causing loss of funds or continued exposure to the exact vulnerability that triggered the delisting.

### Likelihood Explanation
Any dApp that already knows (or can guess/enumerate) the internal `assetName` string for a delisted-but-still-defined asset can call the standard signing RPC surface exposed through `AssetClientInterface`/web3 providers. No special privilege beyond a normal connected-origin/dApp session is required, and no user-facing UI check (which only reads from the filtered "available assets" list) would flag the request, since the block only exists in listing/UI-facing code paths, not the signer.

### Recommendation
Add an explicit availability/support check in `AssetClientInterface.signTransaction` (and ideally in `signMessage`/other privileged action methods) before delegating to `#transactionSigner`, e.g. assert `(await this.#availableAssetNamesAtom.get()).includes(assetName)` (or reuse the `#isSupportedAsset`-style guard used in `features/balances/module/index.js`) and throw if the asset is not currently available. This should also be enforced at the lower-level `seed-signer.ts`/`hardware-wallets.ts` signing entry points as defense in depth, so that no caller can bypass the gate by invoking the signer directly.

### Proof of Concept
1. Wallet has asset `X` registered in `assetsModule` (so `assetsModule.getAsset('X')` still resolves) but `X` has been removed from `availableAssetNamesAtom` (delisted), e.g. via the same mechanism shown in `features/available-assets/module/index.js` / `features/enabled-assets/module/index.js`.
2. `getAssetsForNetwork({ baseAssetName: 'X' })` correctly returns an empty result because it intersects with `availableAssetNames` (`features/assets-feature/client/asset-client-interface.js:165-171`), so UI surfaces correctly hide asset `X`.
3. A connected dApp (or any caller with access to the asset-client/transaction-signer API) nonetheless calls:
   ```js
   assetClientInterface.signTransaction({ assetName: 'X', unsignedTx, walletAccount: 'exodus_0' })
   ```
4. `signTransaction` performs no availability check (`features/assets-feature/client/asset-client-interface.js:361-365`), resolves `baseAssetName`, and forwards to `#transactionSigner.signTransaction`, which likewise only checks `baseAsset.api.features.signWithSigner` (`features/tx-signer/src/module/seed-signer.ts:117-141`) — a valid signature for the delisted asset `X` is produced despite the asset being blocked everywhere else in the UI/listing layer.

Note: I was unable to fully trace every call site into `AssetClientInterface.signTransaction` (e.g., the exact web3-provider-to-asset-client wiring) due to index/tool limitations in this final pass, so I cannot 100% confirm there isn't an additional gate injected further upstream in a specific provider's RPC handler. If such a gate exists in some providers but not others, the finding still stands for any code path that reaches `AssetClientInterface.signTransaction` directly (e.g., internal SDK consumers, or providers that don't add this check).

### Citations

**File:** features/assets-feature/client/asset-client-interface.js (L165-171)
```javascript
  getAssetsForNetwork = async ({ baseAssetName }) => {
    const availableAssetNames = new Set(await this.#availableAssetNamesAtom.get())
    return pickBy(
      this.#assetsModule.getAssets(),
      (asset) => asset.baseAsset.name === baseAssetName && availableAssetNames.has(asset.name)
    )
  }
```

**File:** features/assets-feature/client/asset-client-interface.js (L175-179)
```javascript
  getAssetConfig = async ({ assetName, walletAccount }) => {
    const walletAccountInstance = await this.#getWalletAccount(walletAccount)
    const asset = this.#assetsModule.getAsset(assetName)
    assert(asset, `assetName ${assetName} is not supported`)
    assert(walletAccountInstance, `walletAccountInstance ${walletAccount} is not available`)
```

**File:** features/assets-feature/client/asset-client-interface.js (L361-365)
```javascript
  signTransaction = async ({ assetName, unsignedTx, walletAccount: walletAccountName }) => {
    const baseAssetName = this.#assetsModule.getAsset(assetName).baseAsset.name
    const walletAccount = await this.#getWalletAccount(walletAccountName)
    return this.#transactionSigner.signTransaction({ baseAssetName, unsignedTx, walletAccount })
  }
```

**File:** features/tx-signer/src/module/seed-signer.ts (L117-141)
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
```
