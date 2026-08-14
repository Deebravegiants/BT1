Based on the codebase, the closest structural analog to the reported `_msgSender()`/`trustedForwarder` impersonation issue is in hydra's signing APIs, where the caller supplies an arbitrary `walletAccount` identifier that is trusted at face value to select which private key signs, without any binding to the origin/dApp that is actually authorized to use that account.

### Title
Signer APIs (`messageSigner`/`transactionSigner`) trust caller-supplied `walletAccount` identifiers without binding to the authorized/connected account - (File: `features/message-signer/src/module/message-signer.ts`)

### Summary
The `_msgSender()` bug lets a trusted relayer specify any address as the transaction sender, letting it act as anyone. In hydra, `MessageSigner.signMessage` and the `transactionSigner` API accept a `walletAccount` (either a `WalletAccount` instance or a string name) supplied entirely by the caller. The module resolves this string directly against `walletAccountsAtom` and uses it to derive the signing key — with no verification that this account is the one the requesting context (e.g., a connected dApp/origin) is actually authorized to use.

### Finding Description
`MessageSigner#normalizeWalletAccount` looks up any wallet-account name in `walletAccountsAtom` and returns it for signing, with only an existence assertion, not an authorization check. [1](#0-0) 
The public API layer forwards `SignMessageParams` straight through to the module. [2](#0-1) 
The transaction-signer API does the same lookup-and-forward pattern for `signTransaction`. [3](#0-2) 
Meanwhile, the origin/dApp-connection layer (`connectedOrigins`) is the component that is supposed to restrict which wallet accounts a given origin can see/use, computing a per-origin list of connected accounts. [4](#0-3) 
However, this restriction lives in a separate module (`connectedOrigins`) and is not enforced inside `messageSigner`/`transactionSigner` themselves — any internal caller that can reach the signer module/API (both are marked `public: true` and exposed to the SDK bridge) can pass any wallet account name and obtain a signature from that account's key, regardless of which account is "connected" to the requesting origin. [5](#0-4) [6](#0-5) 

### Impact Explanation
If the RPC/provider bridge (the layer that turns dApp `eth_sign`/`signTransaction`/`signMessage` requests into calls to `messageSigner`/`transactionSigner`) fails to itself validate that the `walletAccount` parameter matches an account actually connected to/authorized for the requesting origin — mirroring the trustedForwarder impersonation pattern — a compromised or buggy bridge/relayer component could sign messages or transactions using any wallet account's private key, not just the one the user connected to that site. This is a direct wallet-compromise-class impact: unauthorized signing on behalf of any account held by the wallet.

### Likelihood Explanation
This requires the privileged bridge/provider code path (not shown in the indexed portion of the repo) to omit the connected-account check when constructing calls into these signer APIs. The `connectedOrigins.getConnectedAccounts` module and per-origin trust model exist specifically to gate this, suggesting the intended design already accounts for it elsewhere. Without visibility into every caller of `messageSignerApi`/`transactionSignerApi`, I cannot confirm whether such a validation gap is actually reachable from an untrusted dApp today — the signer modules themselves are the "trustedForwarder"-equivalent trust boundary and rely on callers to have already validated authorization.

### Recommendation
Move the authorization check (does the requesting origin/context own or have consented access to this specific `walletAccount`) into the `messageSigner`/`transactionSigner` module boundary itself, rather than relying entirely on upstream bridge code to pre-filter the `walletAccount` parameter. This closes the class of bug where a compromised or misconfigured "trusted" caller can impersonate arbitrary accounts, analogous to hardening `_msgSender()`'s trust in `trustedForwarder`.

### Proof of Concept
Not directly reproducible from the indexed code alone: reproduction would require tracing the concrete RPC-bridge/provider caller that turns a dApp request into a `messageSigner.signMessage({ walletAccount, ... })` or `transactionSigner.signTransaction({ walletAccount, ... })` call, and confirming whether that caller uses attacker/dApp-controlled input for `walletAccount` without cross-checking `connectedOrigins.getConnectedAccounts`. Due to index size limits, the concrete bridge/provider implementation files were not available in this search; a full Devin session with complete repo access would be needed to confirm concrete exploitability.

### Citations

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

**File:** features/message-signer/src/api/index.ts (L1-8)
```typescript
import type { IMessageSigner, SignMessageParams } from '../module/interfaces.js'
import type { Definition } from '@exodus/dependency-types'

const createMessageSignerApi = ({ messageSigner }: { messageSigner: IMessageSigner }) => ({
  messageSigner: {
    signMessage: (params: SignMessageParams) => messageSigner.signMessage(params),
  },
})
```

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
