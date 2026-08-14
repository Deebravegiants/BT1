### Title
Cross-account message signing due to missing origin/account binding in `MessageSigner.signMessage` - ([File: features/message-signer/src/module/message-signer.ts])

### Finding Description
`MessageSigner.signMessage` accepts a `SignMessageParams` object whose `walletAccount` field can be either a `WalletAccount` instance or a raw string identifier [1](#0-0) . When a string is passed, `#normalizeWalletAccount` looks it up directly in `walletAccountsAtom` — the global map of *all* wallet accounts known to the wallet, not an origin-scoped subset — and returns whatever `WalletAccount` instance matches, with no check of which origin/dapp is making the call [2](#0-1) . `signMessage` then resolves the appropriate signer (`seedBasedMessageSigner` or `hardwareMessageSigner`) and signs unconditionally with that account's key [3](#0-2) . Neither `SignMessageParams` nor `InternalSignMessageParams` contain an `origin`/`dappId` field, so there is no way for the module to bind a request to the origin that issued it [4](#0-3) . The thin API wrapper (`messageSignerApiDefinition`) forwards `params` verbatim with no additional checks [5](#0-4) , and this module is registered with `public: true`, meaning it is exposed through the generic IOC-based API surface [6](#0-5) . The generic SDK API builder (`sdks/headless/src/api/index.js`) iterates every module of type `'api'` and flattens all of their methods into a single `featureApis` object with no per-origin partitioning [7](#0-6) .

Separately, the `connected-origins` feature does maintain a per-origin notion of "connected accounts" (`connectedAccountsAtom`, `getConnectedAccounts`) [8](#0-7) , but nothing in `message-signer` or its API wrapper consults `connectedOrigins`/`connectedAccountsAtom` to restrict which accounts a caller may reference. The two modules are entirely independent — no import, no dependency wiring, no shared middleware was found connecting them.

### Impact Explanation
If a consumer surface (e.g., a dapp-facing bridge/content script) exposes `exodus.messageSigner.signMessage` directly to third-party origins without itself enforcing per-origin account scoping, an origin approved only for `account_0` could pass `walletAccount: 'account_1'` and obtain a valid signature from `account_1`'s key — a cross-account signing/authorization bypass. This would let a malicious or compromised dapp forge signed messages (e.g., off-chain authentication, order signing, SIWE-style login) impersonating a wallet account it was never granted access to.

### Likelihood Explanation
Exploitability depends entirely on an unverified precondition explicitly called out in the question: "assuming the RPC bridge does not itself enforce per-origin account scoping upstream of this module." Within this repository, I could not find any code that performs such upstream scoping for `exodus.messageSigner.signMessage` specifically — the only observed call sites are the headless SDK integration test and internal playground/README usage, both of which invoke the method directly with an explicit `walletAccount`, not via a dapp-provider abstraction (unlike `BitcoinProvider`, `window.exodus.solana`, etc., which are documented as separate, asset-specific provider surfaces) [9](#0-8) [10](#0-9) . I was unable to locate the actual browser-extension content-script/provider bridge code that decides which methods are exposed to which origins and whether it wraps `messageSigner` with account-scoping logic before forwarding to the background SDK; this could exist outside of what the index covers, or in a repo/module not surfaced by search. Given index size limits, some file contents (e.g., the content-script/provider injection layer) may not be fully available — I recommend a Devin session with full filesystem access to confirm whether such a scoping wrapper exists elsewhere before treating this as a confirmed, currently-exploitable vulnerability end-to-end.

### Recommendation
Add explicit origin/account binding to the message-signer module's public surface: thread the calling origin through `SignMessageParams`, and before resolving/signing, validate that the requested `walletAccount` is in the set of accounts that origin has been granted (e.g., cross-check against `connectedOrigins.getConnectedAccounts({ origin })`). Reject the request (throw, e.g., `UnauthorizedWalletAccountAccess`) if the account is not in the origin's granted set. This check should live either directly in `MessageSigner.signMessage` (requiring an `origin` dependency) or in a wrapping authorization middleware applied to the `messageSignerApi` before it is exposed to dapp-facing RPC transports.

### Proof of Concept
Integration test plan (extending `features/message-signer/src/module/__tests__/index.test.ts` and wiring `connectedOrigins`):
1. Set up `walletAccountsAtom` with two accounts: `account_0` and `account_1`.
2. Set up `connectedOriginsAtom`/`connectedAccountsAtom` such that `originA` is connected/approved only for `account_0` (via `connectedOrigins.add({ origin: 'originA', ... })` followed by connecting only `account_0`).
3. Simulate `originA` calling `messageSigner.signMessage({ walletAccount: 'account_1', baseAssetName: 'ethereum', message: { rawMessage: ... } })` through whatever API surface is exposed to origins (currently just `messageSignerApiDefinition.signMessage`, which has no `origin` parameter at all).
4. Assert: expected behavior is a thrown authorization error (e.g., `UnauthorizedWalletAccountAccess`) because `account_1` is not in `originA`'s granted set.
5. Current actual behavior: `messageSigner.signMessage` resolves `account_1` via `#normalizeWalletAccount` and returns a valid signature from `account_1`'s key, with no error — demonstrating the missing origin/account isolation.

### Citations

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

**File:** features/message-signer/src/module/message-signer.ts (L54-65)
```typescript
  signMessage = async (opts: SignMessageParams) => {
    const { baseAssetName, message, purpose } = opts
    const walletAccount = await this.#normalizeWalletAccount(opts.walletAccount)

    const signer = await this.#getMessageSigner(walletAccount)
    return signer.signMessage({
      baseAssetName,
      walletAccount,
      purpose,
      message,
    })
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

**File:** features/message-signer/src/api/index.ts (L4-8)
```typescript
const createMessageSignerApi = ({ messageSigner }: { messageSigner: IMessageSigner }) => ({
  messageSigner: {
    signMessage: (params: SignMessageParams) => messageSigner.signMessage(params),
  },
})
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

**File:** features/message-signer/README.md (L21-28)
```markdown
```js
await exodus.messageSigner.signMessage({
  walletAccount: 'exodus_0',
  baseAssetName: 'ethereum',
  purpose: 44,
  message: { rawMessage: Buffer.from('hello world') },
})
```
```

**File:** sdks/headless/__tests__/message-signer.test.js (L30-39)
```javascript
  test('signs message', async () => {
    await exodus.application.unlock({ passphrase })

    const signature = await exodus.messageSigner.signMessage({
      baseAssetName: 'ethereum',
      walletAccount: new WalletAccount({ ...WalletAccount.DEFAULT, seedId }),
      message: {
        rawMessage: Buffer.from('hello world'),
      },
    })
```
