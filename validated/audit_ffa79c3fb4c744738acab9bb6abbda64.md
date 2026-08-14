Based on the code inspected, `signMessage` in `features/message-signer/src/module/message-signer.ts` performs no origin- or consent-based authorization check at all. It only:

1. Normalizes `walletAccount` (a string or `WalletAccount` instance) by looking it up in `#walletAccountsAtom` if it's a string [1](#0-0) .
2. Selects a signer based on `walletAccount.isSoftware`/`isHardware` [2](#0-1) .
3. Delegates directly to the signer with no caller/origin parameter anywhere in `SignMessageParams` or `InternalSignMessageParams` [3](#0-2) .

The public API wrapper `createMessageSignerApi` forwards `params` (including `walletAccount`) unconditionally to `messageSigner.signMessage` with no origin argument or scoping logic [4](#0-3) . The module is registered with `public: true` [5](#0-4) .

Separately, `@exodus/connected-origins` maintains per-origin trust/connection state and `getConnectedAccounts({ origin })` [6](#0-5) , but this is a wholly independent feature/module. `messageSigner`'s dependencies are only `seedBasedMessageSigner`, `hardwareMessageSigner`, `walletAccountsAtom` [7](#0-6)  — there is no dependency on `connectedOrigins`, and no `origin` parameter is threaded through `signMessage`'s call chain anywhere in this codebase. I found no RPC-bridge/gateway layer wrapping public APIs generically that injects/validates origin against `connectedOrigins` before invoking `messageSigner.signMessage`; the generic RPC dispatcher (`libraries/json-rpc/index.js`) and headless API composition (`sdks/headless/src/api/index.js`) just look up and invoke the method by name/namespace without any origin-scoping middleware [8](#0-7) [9](#0-8) .

However, I could not locate the actual dapp-bridge / injected-provider integration code (e.g., `window.exodus.ethereum` or `window.ethereum` provider implementation) that would show whether wallet-account resolution/consent enforcement happens at a layer above this — for example, whether the provider only ever passes the origin's already-connected/enabled account as `walletAccount` rather than accepting an arbitrary dapp-supplied value, or whether some UI/background-script layer intercepts `signMessage` calls to substitute/validate the account before it reaches this module. That provider/background-script wiring code was not found by search/index and its absence could be due to index coverage limits rather than confirmed non-existence.

### Title
Missing origin-to-account authorization check in `messageSigner.signMessage` allows signing for accounts never granted to the calling origin - (File: features/message-signer/src/module/message-signer.ts)

### Summary
`MessageSigner.signMessage` and the public `messageSigner.signMessage` API accept an arbitrary `walletAccount` (string ID or object) and use it directly to select and invoke a signer, without any check that the calling origin/session was authorized (connected) for that specific account. If the surrounding dapp-bridge/RPC layer that exposes this public API does not itself enforce that only the origin's connected `walletAccount` values can be forwarded, an origin previously granted access to account X could request signing for account Y.

### Finding Description
`signMessage` (features/message-signer/src/module/message-signer.ts:54-65) normalizes the `walletAccount` param — resolving a string into a `WalletAccount` instance via `#walletAccountsAtom` — and then picks a signer (`seedBasedMessageSigner`/`hardwareMessageSigner`) purely based on `walletAccount.isSoftware`/`isHardware`. There is no parameter for `origin`, no dependency on `connectedOrigins`, and no call anywhere to `isTrusted`/`getConnectedAccounts` to confirm the requesting origin is entitled to use that account. The public API (`features/message-signer/src/api/index.ts:4-8`) simply forwards `params` (including attacker-controlled `walletAccount`) to `messageSigner.signMessage` unconditionally. The `connectedOrigins` module (`features/connected-origins/module/connections.js`) does maintain per-origin connection/authorization state, but it is architecturally decoupled from `messageSigner` — neither module references the other, so the enforcement described by the invariant ("consent must stay scoped to the right origin and account") is not implemented inside this reachable code path.

### Impact Explanation
If reachable directly from a dapp/RPC bridge without an intermediate authorization layer, this allows signing arbitrary messages/typed-data on behalf of any wallet account known to the wallet instance (including accounts never exposed/connected to the requesting origin), which is a origin-to-account isolation bypass and unauthorized signing primitive.

### Likelihood Explanation
Feasibility depends entirely on code outside the scope I could verify: whether the actual RPC/dapp-bridge/provider implementation that exposes `exodus.messageSigner.signMessage` to web pages restricts the `walletAccount` value to the origin's connected set before calling this module, or passes through the caller-supplied value verbatim. I was unable to locate that provider/bridge integration code in the indexed codebase (only the generic, permission-agnostic JSON-RPC dispatcher and headless API composer were found, neither of which perform origin-account scoping). Because this critical linking code could not be confirmed present or absent, likelihood cannot be established with confidence from available evidence.

### Recommendation
Verify (and if missing, implement) an authorization layer between the dapp/RPC bridge and `messageSigner.signMessage` that: (1) resolves the calling origin, (2) fetches the origin's connected/enabled accounts via `connectedOrigins.getConnectedAccounts({ origin })`, and (3) rejects the request if the resolved `walletAccount` is not in that set. This check should be enforced inside `MessageSigner.signMessage` itself (accepting an `origin` argument) rather than relying solely on an external, possibly-missing bridge-layer check.

### Proof of Concept
Cannot be fully constructed without the missing dapp-bridge/provider integration code, since the vulnerability's exploitability hinges on that unverified layer. A conceptual integration test: instantiate the headless SDK with `connectedOrigins` configured such that origin A is connected only to account X; simulate an RPC bridge call attaching origin A's context and invoking `exodus.messageSigner.signMessage({ walletAccount: accountY, ... })`; assert the call is rejected. This test cannot be completed with the code found in this repository since no origin-checking code path exists to assert against within `message-signer`.

### Citations

**File:** features/message-signer/src/module/message-signer.ts (L11-15)
```typescript
export type Dependencies = {
  seedBasedMessageSigner: InternalSigner
  hardwareMessageSigner?: InternalSigner
  walletAccountsAtom: Atom<{ [name: string]: WalletAccount }>
}
```

**File:** features/message-signer/src/module/message-signer.ts (L28-38)
```typescript
  #getMessageSigner = async (walletAccount: WalletAccount): Promise<InternalSigner> => {
    if (walletAccount.isSoftware) {
      return this.#seedBasedMessageSigner
    }

    if (walletAccount.isHardware && this.#hardwareMessageSigner) {
      return this.#hardwareMessageSigner
    }

    throw new UnsupportedWalletAccountSource(walletAccount.source)
  }
```

**File:** features/message-signer/src/module/message-signer.ts (L40-52)
```typescript
  #normalizeWalletAccount = async (
    walletAccount: WalletAccount | string
  ): Promise<WalletAccount> => {
    if (typeof walletAccount === 'string') {
      const walletAccounts = await this.#walletAccountsAtom.get()
      const instance = walletAccounts[walletAccount]
      assert(instance, `wallet account ${walletAccount} not found`)

      return instance
    }

    return walletAccount
  }
```

**File:** features/message-signer/src/module/message-signer.ts (L70-76)
```typescript
const messageSignerDefinition = {
  id: MODULE_ID,
  type: 'module',
  factory: createMessageSigner,
  dependencies: ['seedBasedMessageSigner', 'hardwareMessageSigner?', 'walletAccountsAtom'],
  public: true,
} as const satisfies Definition
```

**File:** features/message-signer/src/module/interfaces.ts (L19-39)
```typescript
export interface InternalSignMessageParams {
  baseAssetName: string
  walletAccount: WalletAccount
  purpose?: Purpose
  message: IUnsignedMessage
}

export interface InternalSigner {
  signMessage: (params: InternalSignMessageParams) => Promise<ISignedMessage>
}

export interface HardwareSignerProvider {
  requireDeviceFor: (walletAccount: WalletAccount) => Promise<HardwareWalletDevice<any>>
}

export interface SignMessageParams {
  baseAssetName: string
  walletAccount: WalletAccount | string
  purpose?: Purpose
  message: IUnsignedMessage
}
```

**File:** features/message-signer/src/api/index.ts (L4-8)
```typescript
const createMessageSignerApi = ({ messageSigner }: { messageSigner: IMessageSigner }) => ({
  messageSigner: {
    signMessage: (params: SignMessageParams) => messageSigner.signMessage(params),
  },
})
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

**File:** libraries/json-rpc/index.js (L145-172)
```javascript
  async _processCallMethod(request) {
    const { method: methodName, params = [], id } = request
    const methodImplementation = this._methods.get(methodName)
    if (!methodImplementation) {
      this._sendError(
        {
          ...errors.METHOD_NOT_FOUND,
          methodName,
        },
        id
      )
    } else if (typeof methodImplementation === 'function') {
      // JSON-RPC allows to send "named parameters", where params is an object
      // In case params is not an array we pass it as a first parameter to method
      const paramsArray = Array.isArray(params) ? params : [params]

      try {
        const result = await Promise.resolve(methodImplementation.apply(this._methods, paramsArray))
        this._sendSuccess({
          result,
          id,
        })
      } catch (error) {
        this._sendError(error, id)
      }
    } else {
      this._sendError(errors.INTERNAL_ERROR, id)
    }
```

**File:** sdks/headless/src/api/index.js (L15-40)
```javascript
const createApi = ({ ioc, port, config, debug, logger }) => {
  const apis = ioc.getByType('api')
  const { application } = ioc.get('applicationApi')

  const featureApis = Object.create(null)
  for (const api of Object.values(apis)) {
    for (const [namespace, methods] of Object.entries(api)) {
      if (!(namespace in featureApis)) {
        // our RPC wrapped features use the proxy client which targets a function (https://github.com/ExodusMovement/exodus-hydra/blob/0e66207c3318051664e57e6b02627169eb7e10b5/libraries/sdk-rpc/src/client.ts#L41),
        // wrapping it further in an async function will break these features
        featureApis[namespace] =
          typeof methods === 'function' ? methods : mapValues(methods, asyncify)

        continue
      }

      for (const [method, implementation] of Object.entries(methods)) {
        assert(
          !(method in featureApis[namespace]),
          `duplicate definition of API method "${method}" in "${namespace}"`
        )

        featureApis[namespace][method] = asyncify(implementation)
      }
    }
  }
```
