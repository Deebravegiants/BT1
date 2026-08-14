### Title
Unvalidated `seedId` accepted for non-`exodus` wallet accounts (`source: 'seed'`/`'passkey'`) allows binding accounts to unauthorized seeds - ([File: features/wallet-accounts/src/module/wallet-accounts.ts])

### Summary
`WalletAccounts#createMany` only validates/forces `data.seedId` to equal `primarySeedId` when `data.source === WalletAccount.EXODUS_SRC`. For any other software-seed source (`SEED_SRC`, `PASSKEY_SRC`), the attacker-supplied `seedId` is passed straight into `new WalletAccount(...)` and persisted with no check that it corresponds to a seed the user actually imported/registered via `wallet.addSeed()`/`keychain.addSeed()`. The persisted account's `seedId` is later used directly as the key-derivation/signing scope.

### Finding Description
In `createMany` [1](#0-0) , the seedId guard is scoped to `data.source === WalletAccount.EXODUS_SRC` only:
- If `source` is `EXODUS_SRC` (or omitted, since it defaults to `EXODUS_SRC`), the assert plus the forced `data.seedId = primarySeedId` on line 369 correctly prevents cross-seed binding.
- If `source` is `SEED_SRC` (or `PASSKEY_SRC`), this whole block is skipped entirely — `data.seedId` is used verbatim, with no comparison to `primarySeedId` or to any list of seeds actually registered in the keychain.

The `WalletAccount` constructor itself only asserts that a `seedId` is *present* for `SEED_SRC`/`PASSKEY_SRC` accounts [2](#0-1)  — it never validates that the value is a real, previously-imported seed.

Downstream, `walletAccount.seedId` is passed directly to the keychain for key operations, e.g. in `SeedBasedMessageSigner#getSigner`, which calls `this.#keychain.getPublicKey({ seedId, keyId })` and `this.#keychain.signBuffer({ seedId, keyId, ... })` using the wallet account's `seedId` verbatim [3](#0-2) . There is no re-validation at that layer that `seedId` belongs to an authorized/imported seed before it's used as the signing scope.

This means an attacker who can reach `walletAccounts.create`/`createMany` with `{ source: 'seed', seedId: 'attacker-seed', index: 0 }` can persist a `WalletAccount` bound to an arbitrary `seedId` string that was never authorized through `wallet.addSeed()`/`keychain.addSeed()`, violating the intended account/seed isolation invariant.

### Impact Explanation
This breaks account/seed isolation: a dapp/RPC caller can create wallet-account records scoped to a seed identifier the user never imported. Whether this becomes exploitable for actual key material theft depends on `keychain`'s internal handling of unknown `seedId`s (not fully verifiable from the reachable code in this pass) — if the keychain silently derives/creates keys for any `seedId` string, this becomes a path to signing with an attacker-influenced key namespace or corrupting per-seed account bookkeeping (analytics/index derivation, `getNextIndex`, balance/asset scoping); if the keychain instead throws for unregistered seeds, the impact is limited to persisted-but-inert malformed account state and denial-of-service/data-integrity issues (corrupted `walletAccounts` store, broken index derivation via `getNextIndex`).

### Likelihood Explanation
Feasibility hinges entirely on whether `walletAccounts.create`/`createMany` is reachable from untrusted dapp/RPC input with attacker-controlled `source`/`seedId` fields — this reachability (RPC surface exposing `walletAccountData` to a webpage/dapp) is asserted by the question's precondition but was not independently confirmed in this pass; the wallet-accounts module itself only enforces the invariant for `EXODUS_SRC`, so if the caller can supply arbitrary `WalletAccountsData`, the bypass is deterministic and repeatable (no auth/lock check on `seedId` for non-exodus sources beyond presence).

### Recommendation
Extend the seedId authorization check in `createMany` beyond the `EXODUS_SRC`-only branch: for any `SOFTWARE_SEED_SOURCES` (`EXODUS_SRC`, `SEED_SRC`, `PASSKEY_SRC`), validate `data.seedId` against the set of seeds actually registered in the keychain/wallet (e.g., via `keychain.getSeedIds()` or equivalent) before constructing/persisting the `WalletAccount`, rejecting any `seedId` not present in that authorized set.

### Proof of Concept
```ts
// features/wallet-accounts/src/module/__tests__/index.test.ts (new case)
it('rejects seedId not registered with the keychain for source: seed', async () => {
  const primarySeedId = await wallet.getPrimarySeedId()
  // attacker-controlled seedId, never added via wallet.addSeed()/keychain.addSeed()
  await expect(
    walletAccounts.createMany([
      { source: WalletAccount.SEED_SRC, seedId: 'attacker-seed', index: 0 },
    ])
  ).rejects.toThrow(/seedId/i) // expect an authorization/validation error

  // ensure no such account was persisted
  const all = await walletAccounts.getWalletAccounts()
  expect(Object.values(all).some((a) => a.seedId === 'attacker-seed')).toBe(false)
})
```
Expected today: this test fails (the account is created and persisted with `seedId: 'attacker-seed'`), demonstrating the bypass. After the fix, `createMany` should reject/sandbox unregistered seed IDs for all software-seed sources, not just `EXODUS_SRC`.

### Citations

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L359-374)
```typescript
      const created = walletAccountsData.map((_data) => {
        const data = { ..._data }
        if (!data.source) data.source = WalletAccount.EXODUS_SRC

        if (data.source === WalletAccount.EXODUS_SRC) {
          assert(
            !data.seedId || data.seedId === primarySeedId,
            'expected seedId to be the primarySeedId for "exodus" accounts'
          )

          data.seedId = primarySeedId
          // mirror compatibilityMode from default account unless we create it
          data.compatibilityMode = walletAccounts[WalletAccount.DEFAULT_NAME]
            ? walletAccounts[WalletAccount.DEFAULT_NAME].compatibilityMode
            : data.compatibilityMode
        }
```

**File:** libraries/models/src/wallet-account/index.ts (L161-162)
```typescript
    assert(source !== SEED_SRC || seedId, 'expected option "seedId" for seed wallet account')
    assert(source !== PASSKEY_SRC || seedId, 'expected option "seedId" for passkey wallet account')
```

**File:** features/message-signer/src/module/seed-signer.ts (L72-91)
```typescript
  #getSigner = ({ keyId, seedId }: { keyId: KeyIdentifier; seedId: WalletAccount['seedId'] }) => {
    return {
      getPublicKey: async () => this.#keychain.getPublicKey({ seedId, keyId }),

      sign: async ({
        data,
        signatureType,
        enc,
        tweak,
        extraEntropy,
      }: KeychainSignerParams): Promise<Buffer> =>
        this.#keychain.signBuffer({
          seedId,
          keyId,
          data,
          signatureType,
          enc,
          tweak,
          extraEntropy,
        }),
```
