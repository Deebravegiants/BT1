### Title
Disabled ("deauthorized") wallet accounts can still be used to sign transactions and messages - ([File: features/tx-signer/src/module/transaction-signer.ts], [File: features/tx-signer/src/api/index.ts], [File: features/message-signer/src/module/message-signer.ts])

### Summary
The external report describes an `AuthorizationModule.deauthorizeAccount` function that revokes a role but never validates/zeroes the account's remaining balance, letting a "deauthorized" account keep the asset it should have lost access to. The closest reachable analog in hydra is the wallet-accounts "disable" flow: `WalletAccounts.disable()`/`disableMany()` in `features/wallet-accounts/src/module/wallet-accounts.ts:416-448` merely flips `enabled: false` on the account record (it does not remove keys or revoke signing capability), and neither the transaction-signing path nor the message-signing path ever checks that flag before producing a signature.

### Finding Description
`disableMany` in `features/wallet-accounts/src/module/wallet-accounts.ts:420-448` calls `#disableWalletAccount`, which sets `{ enabled: false }` via `updateWalletAccount` — the account object (including its `seedId`/`index`/hardware `id`) stays in `walletAccountsAtom` (unless it is a hardware account, which is deleted outright at line 435-437). For software (`exodus`/`seed`) accounts, disabling is a soft, reversible flag flip only.

Both signing entry points resolve a `WalletAccount` purely from this same atom, with no authorization/enabled check:
- `features/tx-signer/src/api/index.ts:33-38` (`getWalletAccount`) looks the account up by name in `walletAccountsAtom` and asserts only that it exists — not that it is enabled. [1](#0-0) 
- `features/tx-signer/src/module/transaction-signer.ts:41-55` (`signTransaction`) dispatches straight to the seed-based or hardware signer based on `walletAccount.isSoftware`/`isHardware`, with no `enabled` check. [2](#0-1) 
- `features/message-signer/src/module/message-signer.ts:40-65` (`#normalizeWalletAccount`/`signMessage`) similarly resolves the account by name from `walletAccountsAtom` and asserts only that the instance exists. [3](#0-2) 

Grepping both `features/tx-signer/**` and `features/message-signer/**` for any reference to `enabled` returns no matches, confirming the enabled/disabled state is never consulted by the signing modules. The only place `enabled` is respected is the Redux `enabled` selector (`features/wallet-accounts/src/redux/selectors/enabled.ts`) and UI-facing `getEnabled()` (`wallet-accounts.ts:523-531`), which are used for display/filtering, not for gating cryptographic operations.

### Impact Explanation
This is the same bug class as the report: a "deauthorization"/revocation action (`disable`) does not fully cut off the account's ability to act — it leaves the underlying signing capability intact, exactly like a deauthorized MMF shareholder retaining shares. Concretely, once a wallet account is disabled (e.g., a user "removes" a compromised/loaned device account, or the app disables an account for policy reasons), any caller that still holds/derives that wallet account name or instance (e.g., a previously-connected dApp origin via `connected-origins`, which caches wallet-account names in `connectedAccountsAtom` and does not automatically prune them except via an explicit `updateConnectedAccounts()` call) can still invoke `transactionSignerApi.signTransaction` or `messageSigner.signMessage` for that account and obtain a valid signature. This is direct unauthorized signing on a supposedly de-authorized account — falling squarely within the "unauthorized signing / direct wallet-compromise impact" acceptance criteria.

### Likelihood Explanation
Likelihood is moderate: exploitation does not require a malicious node/peer, only an unprivileged caller (e.g., a connected web3 origin, or any RPC caller with access to the `transactionSignerApi`/`messageSigner` surface) that already knows the wallet-account identifier of a since-disabled account — which is trivial since it was legitimately obtained before disablement. No additional secret is required because the underlying seed/key material is untouched by `disable()`.

### Recommendation
**Short term**: Add an explicit `enabled` check in `transactionSigner.signTransaction` and `messageSigner.signMessage` (and in `transactionSignerApi.getWalletAccount`), rejecting requests for accounts where `walletAccount.enabled === false`. Additionally, ensure `connected-origins` proactively drops cached accounts/addresses for disabled accounts rather than relying on a separately-invoked `updateConnectedAccounts()`.

**Long term**: Document the wallet-account lifecycle/state machine (enabled → disabled → removed) and enforce invariants that no privileged operation (signing, address derivation for external consumption, connected-origin exposure) can be performed on a disabled account. Add tests/fuzzing asserting that once `disable()`/`disableMany()` is called, all downstream signing and connection paths are unreachable for that account.

### Proof of Concept
1. Create a software wallet account `exodus_1` and connect a dApp origin to it via `connectedOrigins.add(...)`, exposing its address through `getConnectedAccounts`.
2. Call `walletAccounts.disable('exodus_1')` (e.g., `features/wallet-accounts/src/module/wallet-accounts.ts:416-448`) — the account remains in `walletAccountsAtom` with `enabled: false`.
3. From the still-connected origin (or any code path still holding the `exodus_1` `WalletAccount`/name), call `transactionSignerApi.signTransaction({ walletAccount: 'exodus_1', ... })` (`features/tx-signer/src/api/index.ts:41-49`) or `messageSigner.signMessage({ walletAccount: 'exodus_1', ... })` (`features/message-signer/src/module/message-signer.ts:54-65`).
4. Observe that the signature is produced successfully — the disabled/"deauthorized" account still signs, because no code path in these two modules checks `enabled`.

### Citations

**File:** features/tx-signer/src/api/index.ts (L33-38)
```typescript
  const getWalletAccount = async (name: string): Promise<WalletAccount> => {
    const walletAccounts = await walletAccountsAtom.get()
    const walletAccount = walletAccounts[name]
    assert(walletAccount, `Unknown wallet account: ${name}`)
    return walletAccount
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

**File:** features/message-signer/src/module/message-signer.ts (L40-65)
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
