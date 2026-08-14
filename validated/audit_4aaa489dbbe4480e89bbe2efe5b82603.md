### Title
Missing account-authorization check in `transactionSignerApi.signTransaction` allows signing for any wallet account - (File: `features/tx-signer/src/api/index.ts`)

### Summary
`transactionSignerApi.signTransaction`, the RPC-exposed entry point of `@exodus/tx-signer`, accepts a caller-supplied `walletAccount` (a plain string name or object) and resolves/signs with whatever account is found in `walletAccountsAtom`, with no check that the calling context (RPC caller / connected dApp origin) is actually entitled to use that wallet account.

### Finding Description
The API factory `createTransactionSignerApi` resolves the account purely from the parameters passed in the call, then immediately forwards it to the internal signer, which proceeds straight to key-derivation and signing: [1](#0-0) 

There is no origin/caller identity check anywhere in this path — contrast this with `@exodus/connected-origins`, which explicitly gates account exposure behind `isTrusted`/`isAutoApprove` checks before it will return account data to an origin: [2](#0-1) [3](#0-2) 

The `transactionSigner` feature module declares itself `public: true` and is documented as being wired 1:1 to the RPC-exposed `exodus.transactionSigner` API surface used by the SDK/RPC bridge: [4](#0-3) [5](#0-4) 

Once a `walletAccount` object/name reaches `TransactionSigner.signTransaction`, it dispatches purely on `walletAccount.isSoftware`/`isHardware` and signs without any reference to who is asking: [6](#0-5) 

For software accounts, `SeedBasedTransactionSigner.signTransaction` derives the signing key straight from `walletAccount.seedId`/`index` and signs, again with no caller-scoping: [7](#0-6) 

This is the analog of the reported `withdraw_collateral` bug: just as that CosmWasm entry point trusted a caller-supplied `borrower` address instead of verifying the caller was the authorized `overseer`, `transactionSignerApi.signTransaction` trusts a caller-supplied `walletAccount` instead of verifying the caller (RPC client / connected origin) is authorized to sign for that specific account.

### Impact Explanation
If any code path allows an untrusted or less-privileged caller (e.g., a connected dApp/RPC client that should only be scoped to one wallet account) to invoke `transactionSigner.signTransaction` with an arbitrary `walletAccount` name/object, it can obtain a valid signature for a transaction from any account managed by the wallet, not just the account it was granted access to. Since signing directly moves/authorizes funds, this is a direct wallet-compromise-class impact (unauthorized signing), not merely metadata leakage.

### Likelihood Explanation
The function is a `public: true` module/API meant to be exposed across process/RPC boundaries per `@exodus/sdk-rpc`'s design ("expose the methods of the SDK to be called over RPC"), and the README states the RPC surface corresponds 1:1 to `exodus.transactionSigner`. Likelihood of exploitation depends on whether any host application wires this API into a context reachable by less-trusted callers (e.g., a dApp-facing bridge) without adding its own origin-to-account authorization layer in front of it — I could not confirm from the indexed files whether such a layer always exists at every integration site, since the API module itself performs no such check.

### Recommendation
Add an explicit authorization check inside `transactionSignerApi.signTransaction` (or at the RPC exposure boundary) that verifies the requesting context/origin is permitted to use the specified `walletAccount` (e.g., cross-checking against `@exodus/connected-origins`'s trusted/connected accounts, analogous to how `getConnectedAccounts` gates on `isTrusted`) before delegating to the internal `transactionSigner`.

### Proof of Concept
Not applicable — full RPC-bridge wiring code (i.e., where `transactionSignerApi` is attached to a dApp-facing transport) was not found in the indexed portion of the repository, so a concrete unauthorized-signing call chain from an untrusted origin could not be fully traced end-to-end from the available files.

### Citations

**File:** features/tx-signer/src/api/index.ts (L29-52)
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
    },
  }
}
```

**File:** features/connected-origins/module/connections.js (L198-212)
```javascript
  isTrusted = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })

    if (!value) {
      return false
    }

    // backward compatibility
    return value.trusted === undefined || value.trusted
  }

  isAutoApprove = async ({ origin }) => {
    const value = await this.#getOrigin({ origin })
    return value?.autoApprove || false
  }
```

**File:** features/connected-origins/module/connections.js (L249-273)
```javascript
  getConnectedAccounts = async ({ origin }) => {
    const isTrusted = await this.isTrusted({ origin })
    if (!isTrusted) return []

    const value = await this.#getOrigin({ origin })
    const assetNames = [value.connectedAssetName, ...(value.assetNames ?? [])].filter(
      (name, index, ary) => Boolean(name) && ary.indexOf(name) === index
    )

    const activeWalletAccount = await this.#activeWalletAccountAtom.get()
    const accounts = await this.#connectedAccountsAtom.get()

    const connectedAccounts = []
    for (const name of Object.keys(accounts)) {
      if (name === activeWalletAccount) continue
      connectedAccounts.push({ name, addresses: pick(accounts[name].addresses, assetNames) })
    }

    connectedAccounts.unshift({
      name: activeWalletAccount,
      addresses: pick(accounts[activeWalletAccount].addresses, assetNames),
    })

    return connectedAccounts
  }
```

**File:** features/tx-signer/src/module/transaction-signer.ts (L20-55)
```typescript
class TransactionSigner implements ITransactionSigner {
  readonly #seedBasedTransactionSigner
  readonly #hardwareWallets

  constructor({ hardwareWallets, seedBasedTransactionSigner }: Dependencies) {
    this.#seedBasedTransactionSigner = seedBasedTransactionSigner
    this.#hardwareWallets = hardwareWallets
  }

  #getTransactionSigner = async (walletAccount: WalletAccount): Promise<InternalSigner> => {
    if (walletAccount.isSoftware) {
      return this.#seedBasedTransactionSigner
    }

    if (walletAccount.isHardware && this.#hardwareWallets) {
      return this.#hardwareWallets.requireDeviceFor(walletAccount)
    }

    throw new UnsupportedWalletAccountSource(walletAccount.source)
  }

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

**File:** features/tx-signer/src/module/transaction-signer.ts (L58-67)
```typescript
const createTransactionSigner = (opts: Dependencies) => new TransactionSigner(opts)

const transactionSignerDefinition = {
  id: MODULE_ID,
  type: 'module',
  factory: createTransactionSigner,
  dependencies: ['seedBasedTransactionSigner', 'hardwareWallets?'],
  public: true,
} as const satisfies Definition

```

**File:** features/tx-signer/README.md (L21-29)
```markdown
## Usage

This feature is designed to be used together with `@exodus/headless`. See [using the sdk](../../docs/development/using-the-sdk.md).

### Play with it

1. Open the playground https://exodus-hydra.pages.dev/features/tx-signer
2. Try out the some methods via the UI. These corresponds 1:1 with the `exodus.transactionSigner` API.

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
