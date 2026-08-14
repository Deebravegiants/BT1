### Title
Delegated-account asset restriction is enforced only in a UI display selector, not in the transaction/message signing path - (File: `features/asset-sources/atoms/available-asset-names-by-wallet-account.ts`)

### Summary
The `delegated` `WalletAccount` flag is meant to restrict a wallet account to signing only a specific, allow-listed subset of assets (by default `solana` and `usdcoin_solana`, configurable via `delegatedAllowedAssetNames`). However, this allow-list check exists only inside `createDelegatedAvailableAssetsSelector`, a Redux/atoms selector that computes which asset names to *display* per wallet account for UI purposes. The actual authorization/execution paths that perform signing — `TransactionSigner.signTransaction` and the seed/message signers — never inspect `walletAccount.delegated` or any allow-list, so a delegated account can be used to sign transactions/messages for any asset, not just the intended restricted subset.

### Finding Description
`WalletAccount.delegated` is a boolean flag added specifically to mark accounts that should be constrained to a narrow set of assets: [1](#0-0) [2](#0-1) 

The only place this restriction is implemented is `available-asset-names-by-wallet-account.ts`, which filters the list of asset names surfaced to the UI: [3](#0-2) 

with the default allow-list defined here: [4](#0-3) 

This is analogous to `GuardCM.checkTransaction()`, which restricts privileged `schedule`/`scheduleBatch` calls only when `to == owner` (the timelock), but fails to apply any check when the same privileged capability (arbitrary code execution) is reached via `delegatecall` to any other address — the restriction is checked at one entry point but not at the actual point where the sensitive capability is exercised.

Here, the sensitive capability is *signing*. The actual signing entry points — `TransactionSigner.signTransaction()`, `SeedBasedTransactionSigner.signTransaction()`, `HardwareWallets.signTransaction()`, and the analogous message-signing modules — take `baseAssetName` and `walletAccount` directly and never reference `walletAccount.delegated` or any asset allow-list: [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

The `transactionSignerApi` similarly only resolves the `WalletAccount` object and forwards to `transactionSigner.signTransaction`, again with no `delegated` check: [9](#0-8) 

The delegated-account restriction tests confirm the intended access-control semantics apply only to what asset names are returned by the atom, not to whether signing is actually possible for other assets: [10](#0-9) 

### Impact Explanation
If a `delegated` wallet account is used in a context where the caller (e.g. an integrating dApp, a partner-facing wallet API, or any code that invokes `transactionSigner.signTransaction`/`messageSigner.signMessage` directly with a `baseAssetName` outside the allow-list) does not itself re-derive the allowed asset list from the `available-asset-names-by-wallet-account` atom, the delegated account will happily sign for any supported asset. Since `delegated` accounts are explicitly modeled as reduced-trust/limited-scope accounts (restricted by design to `solana`/`usdcoin_solana`), this is a privilege-escalation / scope-bypass: a party that should only be able to obtain signatures for a narrow asset set can obtain unauthorized signatures (and thus unauthorized asset movement) for any other asset held by that account, because the enforcement point (a UI filter atom) is decoupled from the actual signing authorization logic.

### Likelihood Explanation
Likelihood depends on whether any caller of the signing APIs actually relies on `available-asset-names-by-wallet-account` as an authorization gate rather than purely a UI-population helper. Given the flag's name (`delegated`) and its introduction specifically to scope down what a delegated account can do, and given that this atom is the sole place referencing `delegated`/`delegatedAllowedAssetNames` outside of models/tests, it is reasonable to conclude this selector is intended as the enforcement mechanism, but it is architecturally only wired into a display/selection atom, not into the transaction/message signing modules. I could not find any additional runtime guard (e.g., in `tx-signer`, `message-signer`, `hardware-wallets`, or `keychain`) that consults `walletAccount.delegated`, so the gap appears real within the indexed code, though I cannot rule out an enforcement point elsewhere (e.g. in a consuming application repo not indexed here, such as `exodus-mobile`/`exodus-desktop`) that wraps the signer APIs with the allow-list check before calling them.

### Recommendation
Enforce the `delegated` asset restriction at the actual authorization boundary, not just in the UI-facing atom:
- In `TransactionSigner.signTransaction` (`features/tx-signer/src/module/transaction-signer.ts`) and `IMessageSigner.signMessage` (`features/message-signer/...`), assert that if `walletAccount.delegated` is true, `baseAssetName` (or its underlying asset) is a member of the configured `delegatedAllowedAssetNames` set, throwing an authorization error otherwise.
- Thread the same `delegatedAllowedAssetNames` configuration used by `features/asset-sources` into `tx-signer`/`message-signer`/`hardware-wallets` so there is a single source of truth, rather than duplicating the allow-list only in a display selector.
- Add tests asserting that `signTransaction`/`signMessage` reject disallowed assets for delegated accounts even when called directly (i.e., bypassing the UI atom).

### Proof of Concept
Conceptual PoC (cannot be executed against this index, but demonstrates the gap using existing test scaffolding):
1. Create a `WalletAccount` with `{ source: 'exodus', index: 0, delegated: true }`, as used in `features/asset-sources/atoms/__tests__/available-asset-names-by-wallet-account.test.ts` (lines 519-549) — this account is only supposed to be usable for `solana`/`usdcoin_solana`.
2. Instead of going through `available-asset-names-by-wallet-account` atom, call `transactionSignerDefinition`'s `signTransaction({ baseAssetName: 'ethereum', unsignedTx, walletAccount })` directly (mirroring the test setup in `features/tx-signer/src/module/__tests__/index.test.ts`, lines 19-78) with the delegated account.
3. Observe that `TransactionSigner.signTransaction` (`features/tx-signer/src/module/transaction-signer.ts`, lines 41-55) proceeds to sign the Ethereum transaction with no error, despite `ethereum` not being in `delegatedAllowedAssetNames`, because no code path checks `walletAccount.delegated` before dispatching to the underlying signer.

### Citations

**File:** libraries/models/src/wallet-account/index.ts (L123-125)
```typescript
  compatibilityMode?: string
  isMultisig?: boolean
  delegated?: boolean
```

**File:** libraries/models/CHANGELOG.md (L34-38)
```markdown
## [12.18.0](https://github.com/ExodusMovement/exodus-hydra/compare/@exodus/models@12.17.1...@exodus/models@12.18.0) (2025-10-27)

### Features

- feat: add delegated field on WalletAccount (#14195)
```

**File:** features/asset-sources/atoms/available-asset-names-by-wallet-account.ts (L136-168)
```typescript
const createDelegatedAvailableAssetsSelector = (delegatedAllowedAssetNames: string[]) =>
  createSelector(
    (state: DelegatedSelectorState) => state.availableAssetNames,
    (availableAssetNames) => {
      const allowedAssets = new Set(delegatedAllowedAssetNames)
      return availableAssetNames.filter((name) => allowedAssets.has(name))
    }
  )

const createAvailableAssetNamesByWalletAccountAtom = ({
  assetsAtom,
  availableAssetNamesAtom,
  enabledWalletAccountsAtom,
  config = { delegatedAllowedAssetNames: ['solana', 'usdcoin_solana'] },
}: Dependencies): ReadonlyAtom<AvailableAssetNamesByWalletAccount> => {
  const delegatedAvailableAssetsSelector = createDelegatedAvailableAssetsSelector(
    config.delegatedAllowedAssetNames
  )

  return dedupe(
    compute({
      atom: <Atom<CombinedAtomResult>>combine({
        walletAccounts: enabledWalletAccountsAtom,
        availableAssetNames: availableAssetNamesAtom,
        assets: assetsAtom,
      }),
      selector: ({ assets, walletAccounts, availableAssetNames }: CombinedAtomResult) => {
        return mapValues(walletAccounts, ({ source, model, delegated }: WalletAccount) => {
          if (delegated) {
            return delegatedAvailableAssetsSelector({
              availableAssetNames,
            })
          }
```

**File:** features/asset-sources/default-config.ts (L1-4)
```typescript
const config = {
  delegatedAllowedAssetNames: ['solana', 'usdcoin_solana'],
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

**File:** features/message-signer/src/module/seed-signer.ts (L95-111)
```typescript
  signMessage = async (opts: InternalSignMessageParams) => {
    const { baseAssetName, message, walletAccount } = opts
    const baseAsset = this.#assetsModule.getAsset(baseAssetName)

    assert(baseAsset, `baseAsset not found`)
    assert(
      baseAsset.api.features.signMessageWithSigner,
      `asset ${baseAssetName} does not support message signing`
    )

    const keyId = await this.#getKeyId(opts)

    return baseAsset.api.signMessage!({
      signer: this.#getSigner({ keyId, seedId: walletAccount.seedId }),
      message,
    })
  }
```

**File:** features/tx-signer/src/api/index.ts (L40-52)
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
}
```

**File:** features/asset-sources/atoms/__tests__/available-asset-names-by-wallet-account.test.ts (L519-549)
```typescript
  describe('Delegated wallet accounts', () => {
    it('should return only SOL and USDC for delegated accounts', async () => {
      const delegatedAccount = new WalletAccount({
        source: WalletAccount.EXODUS_SRC,
        index: 0,
        delegated: true,
      })

      const enabledWalletAccountsAtom = createInMemoryAtom({
        defaultValue: {
          [delegatedAccount.toString()]: delegatedAccount,
        },
      })

      const atom = availableAssetNamesByWalletAccountAtomDefinition.factory({
        assetsAtom: createInMemoryAtom({ defaultValue: { value: assets } }),
        availableAssetNamesAtom: createInMemoryAtom({
          defaultValue: ['bitcoin', 'ethereum', 'solana', 'usdcoin_solana', 'cardano'],
        }),
        enabledWalletAccountsAtom,
        config: defaultConfig,
      })

      const result = await atom.get()
      const delegatedAssets = result[delegatedAccount.toString()]

      expect(delegatedAssets).toEqual(['solana', 'usdcoin_solana'])
      expect(delegatedAssets).not.toContain('bitcoin')
      expect(delegatedAssets).not.toContain('ethereum')
      expect(delegatedAssets).not.toContain('cardano')
    })
```
