### Title
`transactionSignerApi.signTransaction` / `messageSigner.signMessage` accept an arbitrary `walletAccount` name with no check that the caller (origin/dApp) is authorized for that account - ([File: features/tx-signer/src/api/index.ts])

### Summary
The Magnetar analog here is `@exodus/tx-signer`'s public API (and the equivalent `@exodus/message-signer` API), which is exposed over the SDK/RPC boundary (background↔UI / background↔dApp-provider process). Any caller of `transactionSigner.signTransaction({ walletAccount, ... })` can pass **any** wallet-account name as a plain string; the API resolves it directly from `walletAccountsAtom` and signs with that account's key material — without verifying that the requesting party (the connected origin, or whichever RPC caller invoked it) actually owns/is authorized to act as that wallet account.

### Finding Description
`createTransactionSignerApi` in [1](#0-0)  looks up whatever `walletAccount` string is supplied by the caller in `walletAccountsAtom` and passes it straight through to the internal `transactionSigner.signTransaction`, which ultimately fetches the seed/keychain signer for that specific wallet account and signs the transaction using its private key material — see `SeedBasedTransactionSigner#getSignerForWalletAccount` in [2](#0-1)  and the top-level dispatch in [3](#0-2) .

The only validation performed is that the account name exists (`assert(walletAccount, 'Unknown wallet account...')`), not that it belongs to / is authorized for the calling context. This mirrors the Magnetar `_processTapTokenOperation` bug: the batching/dispatch layer forwards a caller-supplied identifier (an oTAP/tOLP NFT id there, a `walletAccount` name here) straight to a privileged operation (exercising an option / signing a transaction) without checking that the caller is the legitimate owner/authorized party for that identifier.

Separately, `@exodus/connected-origins` (the module responsible for tracking which wallet accounts a given dApp origin is permitted to interact with, e.g. `ConnectedOrigins#getConnectedAccounts` in [4](#0-3) ) exists precisely to scope a dApp origin's access to specific accounts — but this enforcement lives in a separate module from `tx-signer`/`message-signer`, and the signer APIs themselves have no dependency on `connectedOrigins` or the requesting origin at all (dependencies are only `transactionSigner`, `walletAccountsAtom`, see the definition [5](#0-4) ). Whether the web3-provider layer (the code that turns `window.exodus.ethereum.request(...)` calls from a webpage into a `transactionSigner.signTransaction` call) actually cross-checks the requested `walletAccount` against `connectedOrigins.getConnectedAccounts({ origin })` before forwarding the request could not be confirmed — the provider-to-signer glue code was not found in the indexed portion of the codebase.

### Impact Explanation
If any code path that is reachable from a less-trusted context (a connected dApp origin, or a compromised/malicious UI process talking to the trusted background over the RPC bridge described in [6](#0-5) ) can invoke `transactionSigner.signTransaction` or `messageSigner.signMessage` with an arbitrary `walletAccount` name, it could obtain a signature/transaction signed by a wallet account it was never granted access to — e.g., a dApp connected only to `exodus_0` requesting a signature under `exodus_1`. That is a direct unauthorized-signing / account-isolation-bleed impact, analogous to exercising someone else's option in the original report.

### Likelihood Explanation
This is only exploitable if some caller that is not fully trusted (e.g., a browser-tab-facing provider, or a compromised renderer/UI in the multi-process split) is able to invoke these SDK API methods directly with a caller-chosen `walletAccount` argument, and if the origin-scoping enforcement (via `connectedOrigins`) is not applied before calling into `transactionSigner`/`messageSigner`. I was unable to trace the exact glue code that maps a `window.exodus.*` / `ethereum.request()` invocation to `transactionSigner.signTransaction`, so I cannot confirm whether an authorization check against the connected origin's account list is performed upstream. This is a genuine gap in my investigation, not a confirmed bypass.

### Recommendation
- In `transactionSignerApi.signTransaction` and the equivalent `messageSigner.signMessage` API, require and verify that the resolved `walletAccount` is one that the calling context (origin/session) is authorized to use — e.g., by threading through the requesting origin and checking it against `connectedOrigins.getConnectedAccounts({ origin })` before calling the internal signer, rather than trusting a bare wallet-account-name/string supplied by the caller.
- Audit every place in the codebase where a web3 provider (`window.exodus.ethereum`, `solana`, `bitcoin`, `cardano`, etc.) forwards a dApp request into `transactionSigner`/`messageSigner`, and confirm the account used is always derived from the origin's already-approved connection state, never from attacker-controlled request parameters.

### Proof of Concept
Not able to construct a concrete end-to-end PoC from the indexed files: I could not locate the specific provider/background code that bridges a `window.exodus.*` request to `transactionSigner.signTransaction`, so I cannot confirm the exact caller-controlled parameter path from an untrusted origin. Given index-size limitations, some of the provider-adapter files (e.g. under `features/application` or provider-specific background modules) may not be fully indexed; a Devin session with full filesystem access would be needed to trace this chain conclusively.

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

**File:** features/tx-signer/src/api/index.ts (L54-59)
```typescript
const transactionSignerApiDefinition = {
  id: 'transactionSignerApi',
  type: 'api',
  factory: createTransactionSignerApi,
  dependencies: ['transactionSigner', 'walletAccountsAtom'],
} as const satisfies Definition
```

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

**File:** libraries/sdk-rpc/src/rpc.ts (L1-47)
```typescript
import JsonRPC, { type Transport } from '@exodus/json-rpc'
import EventEmitter from 'eventemitter3'
import ms from 'ms'

import { SEPARATOR } from './constants.js'
import type { Fn, JsonRPCParams, Listener, Methods } from './types.js'

const serializePath = (path: string[]) => path.join(SEPARATOR)

export const flattenObject = <T>(obj: T, path: string[] = []): { [name: string]: Fn } => {
  if (typeof obj === 'function') {
    return { [serializePath(path)]: obj as Fn }
  }

  if (typeof obj !== 'object' || !obj) return {}

  return Object.keys(obj).reduce((acc, key) => {
    return { ...acc, ...flattenObject(obj[key as keyof T], [...path, key]) }
  }, {})
}

type ConstructorParams = {
  transport: Transport
  requestTimeout?: number
  serialize?: JsonRPCParams[0]['stringify']
  deserialize?: JsonRPCParams[0]['parse']
}

class RPC extends JsonRPC {
  _emitter = new EventEmitter()

  constructor({ transport, serialize, deserialize, requestTimeout = ms('5m') }: ConstructorParams) {
    super({
      transport,
      requestTimeout,
      parse: deserialize,
      stringify: serialize,
    })
  }

  // @ts-expect-error this overrides the parent method's signature with TS does not allow but which the original JS code did
  exposeMethods(methods: Methods) {
    const current = Object.fromEntries(this._methods)
    const flattenMethods = flattenObject(methods)

    return super.exposeMethods({ ...current, ...flattenMethods })
  }
```
