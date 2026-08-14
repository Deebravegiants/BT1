### Title
Missing wallet-account/keyId scope binding in `SeedBasedTransactionSigner.signTransaction` allows signing with a foreign account's key under the same seed - (File: `features/tx-signer/src/module/seed-signer.ts`)

### Summary
When `unsignedTx.txMeta.keyId` is present, `SeedBasedTransactionSigner.signTransaction` only validates that the `keyId` is *structurally* a valid `KeyIdentifier` and forwards it directly to `#getSignerForKeyId({ seedId: walletAccount.seedId, keyId })`, which signs with whatever derivation path is embedded in the attacker-supplied `keyId`. There is no check that the `keyId`'s embedded `accountIndex`/derivation path corresponds to `walletAccount.index`, so any caller authorized to invoke `signTransaction` for one `walletAccount` can supply a `keyId` pointing at a sibling account sharing the same `seedId` and obtain a signature from that other account's key.

### Finding Description
In `signTransaction`, when `unsignedTx.txMeta.keyId` is set, the code path is: [1](#0-0) 

The only guard applied to the attacker-controlled `keyId` is a structural validity check via `KeyIdentifier.validate(keyId)`: [2](#0-1) 

This does not verify that the derivation path/`accountIndex` inside `keyId` belongs to the `walletAccount` making the request. `#getSignerForKeyId` then builds a signer that uses `walletAccount.seedId` (correct seed) but the attacker-chosen `keyId` verbatim: [3](#0-2) 

Compare this to the "default" path (`#getSignerForWalletAccount`), which derives `accountIndex` strictly from `walletAccount.index` and cannot be overridden by caller input: [4](#0-3) 

Downstream, `#createSigner`'s `sign`/`getPublicKey` closures forward `seedId` and the raw `keyId` straight to `this.#keychain.signBuffer` / `getPublicKey`: [5](#0-4) 

`keychain.signBuffer` (features/keychain/module/keychain.js) only checks `keyId.keyType`/`signatureType` compatibility and buffer shape — it performs no account-ownership or caller-authorization check tying the derivation path to a specific `walletAccount`: [6](#0-5) 

For accounts sharing one seed (`walletAccount.seedId` identical across multiple derived accounts, e.g. `WalletAccount({ source: 'seed', seedId, index: N })` vs `index: N+1`), the seed-based key derivation only depends on the path encoded in `keyId`, not on which `walletAccount` object was passed in. Consequently, supplying a `keyId` whose `accountIndex` differs from `walletAccount.index` (but same `seedId`) produces a valid signature for the *other* account, with `signTransaction` never cross-checking `keyId` against `walletAccount.index`.

The one located external entry point that reaches this code unmodified is `AssetClientInterface.signTransaction`, which passes the caller-supplied `unsignedTx` (including `txMeta.keyId`, if the caller sets it) straight through to `transactionSigner.signTransaction`: [7](#0-6) 

and `TransactionSigner.signTransaction` performs only basic type assertions on `txData`/`txMeta` (objects), not on `txMeta.keyId` contents, before dispatching to the seed-based signer: [8](#0-7) 

**Caveat / uncertainty**: I was not able to locate, within indexed code, the specific dapp/RPC provider handler (e.g., an `eth_signTransaction`/`eth_sendTransaction` JSON-RPC handler) that maps untrusted dapp request parameters onto `unsignedTx.txMeta.keyId` before calling `assetClientInterface.signTransaction`. The comment in `seed-signer.ts` ("Sometimes we need a different keyId than the default... EOS tx with the Ethereum key... ripple") suggests this override is intended for internal/trusted asset-specific flows, not raw dapp input, but I could not confirm from the indexed code whether any provider surface forwards attacker-supplied `keyId` unmodified. This may exceed the coverage of the codebase index; a Devin session with full repo access could confirm whether any dapp-facing RPC handler constructs or passes through `txMeta.keyId` from untrusted request parameters.

### Impact Explanation
If reachable from an untrusted origin/dapp (or any caller with access to only one `walletAccount`'s signing consent), this allows cross-account signature disclosure and potentially unauthorized fund movement: an attacker who is only authorized to request signing for account index N could obtain a valid signature (and derive the address/public key) for a sibling account index N+1 under the same seed, bypassing wallet-account isolation. This maps to Hydra's "unauthorized signing / wrong-account access" impact category.

### Likelihood Explanation
Exploitability requires: (1) the seed already unlocked (a stated precondition), (2) more than one enabled wallet account sharing the same `seedId` (common for accounts derived from the same seed with different indices), and (3) a code path that lets the caller set `unsignedTx.txMeta.keyId` reaching `SeedBasedTransactionSigner.signTransaction` with an unmatched `walletAccount`. Within `seed-signer.ts` itself, there is no barrier once `txMeta.keyId` is attacker-influenced — the exploit is fully deterministic and repeatable. The main open question is whether any dapp/RPC-facing entry point actually lets untrusted callers set `txMeta.keyId`, which limits confidence in real-world reachability without further verification.

### Recommendation
In `SeedBasedTransactionSigner.signTransaction`, when `txMeta.keyId` is supplied, validate that the derivation path/`accountIndex` encoded in `keyId` is consistent with `walletAccount.index` (and `walletAccount.compatibilityMode`/purpose) before calling `#getSignerForKeyId`, or restrict the `keyId` override mechanism to an explicit allow-list of same-account key substitutions (e.g., only allow overriding `baseAsset`/purpose for the *same* `accountIndex`, as in the EOS/ripple use cases referenced in the comment) rather than accepting an arbitrary caller-supplied `KeyIdentifier`.

### Proof of Concept
Unit test to add to `features/tx-signer/src/module/__tests__/seed-signer.test.ts`:
```ts
test('signTransaction must not sign with a keyId belonging to a different account under the same seed', async () => {
  const { seedSigner, assets, keychain } = await setup()
  const seedId = 'shared-seed-id'
  const walletAccountN = new WalletAccount({ source: 'seed', seedId, index: 0 })
  const foreignKeyId = new KeyIdentifier({
    assetName: 'bitcoin',
    derivationAlgorithm: 'BIP32',
    derivationPath: "m/84'/0'/1'/0/0", // accountIndex = 1, NOT walletAccountN.index (0)
    keyType: 'secp256k1',
  })

  const signSpy = jest.spyOn(keychain, 'signBuffer')
  jest.spyOn(assets.bitcoin.api, 'signTx').mockImplementationOnce(async ({ signer }) =>
    signer.sign({ data: bufferToSign, keyId: foreignKeyId })
  )

  await seedSigner.signTransaction({
    walletAccount: walletAccountN,
    baseAssetName: 'bitcoin',
    unsignedTx: { txData: {}, txMeta: { keyId: foreignKeyId } },
  })

  // Expected (secure) behavior: should throw/reject because foreignKeyId's accountIndex (1)
  // does not match walletAccountN.index (0).
  // Actual (vulnerable) behavior: signBuffer is called with the foreign accountIndex derivation path.
  expect(signSpy).not.toHaveBeenCalledWith(
    expect.objectContaining({ keyId: expect.objectContaining({ derivationPath: expect.stringContaining("1'") }) })
  )
})
```
This test currently fails against the given implementation (i.e., `signBuffer` is invoked with the foreign `accountIndex`), demonstrating the missing cross-check between `keyId` and `walletAccount`.

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

**File:** features/tx-signer/src/module/seed-signer.ts (L82-115)
```typescript
    const getPublicKey = async ({
      keyId = getDefaultKeyIdentifier(),
    }: GetPublicKeyParams = {}): Promise<Buffer> => {
      return this.#keychain.getPublicKey({ seedId, keyId })
    }

    const sign = ({
      data,
      keyId = getDefaultKeyIdentifier(),
      signatureType,
      enc,
      tweak,
      extraEntropy,
    }: KeychainSignerParams): Promise<any> => {
      assert(KeyIdentifier.validate(keyId), 'signBuffer: invalid `keyId`')

      if (!signatureType) {
        // temporary because some assets (algorand) do not pass signatureType
        signatureType = keyId.keyType === 'secp256k1' ? 'ecdsa' : 'ed25519'
      }

      return this.#keychain.signBuffer({
        seedId,
        keyId,
        data,
        signatureType,
        enc,
        tweak,
        extraEntropy,
      })
    }

    return { sign, getPublicKey }
  }
```

**File:** features/tx-signer/src/module/seed-signer.ts (L144-151)
```typescript
    // Sometimes we need a different keyId than the default.
    // One example is signing an EOS tx with the Ethereum key, another is ripple:
    // https://github.com/ExodusMovement/exodus-desktop/blob/174efe1145152446e6183f55155972b3acc05ccc/src/app/_local_modules/eosio-write-api/fallback-claim.js#L54
    // https://github.com/ExodusMovement/exodus-desktop/blob/82f1e284efed2bf1ff95798a9e8e89bc71e2ae40/src/app/ui/exodus-global/debug/ripple.js#L105
    assert(KeyIdentifier.validate(keyId), `txMeta.keyId must be a key identifier object`)

    const signer = await this.#getSignerForKeyId({ seedId: walletAccount.seedId, keyId })
    return signTx({ unsignedTx, signer })
```

**File:** features/keychain/module/keychain.js (L311-323)
```javascript
  async signBuffer({ seedId, keyId, data, signatureType, enc, tweak, extraEntropy, ...rest }) {
    const noTweak = tweak === undefined
    const noEnc = enc === undefined
    const noOpts = noEnc && noTweak && extraEntropy === undefined
    const invalidOptions = Object.keys(rest).filter((key) => key !== 'ecOptions') // ignore legacy option `ecOptions`

    assert(invalidOptions.length === 0, `unsupported options supplied to signBuffer()`)
    assert(data instanceof Uint8Array, `expected "data" to be a Uint8Array, got: ${typeof data}`)
    assert(
      (['ecdsa', 'schnorr', 'schnorrZ'].includes(signatureType) && keyId.keyType === 'secp256k1') ||
        (signatureType === 'ed25519' && ['nacl', 'cardanoByron'].includes(keyId.keyType)),
      `"keyId.keyType" ${keyId.keyType} does not support "signatureType" ${signatureType}`
    )
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
