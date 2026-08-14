### Title
`WalletAccounts#createMany` silently overwrites `seedId` on collision for `passkey`-source accounts, bypassing `updateWalletAccount` immutability checks - ([File: features/wallet-accounts/src/module/wallet-accounts.ts])

### Summary
`createMany` decides whether an incoming `WalletAccount` is "new" or "existing" purely by comparing `walletAccount.toString()` keys, then unconditionally overwrites `walletAccounts[key]` for the "existing" case without ever running the `source`/`id`/`index`/`seedId` immutability assertions that `updateWalletAccount` enforces. Because `WalletAccount#toString()` deliberately omits `seedId` for every source except `SEED_SRC` [1](#0-0) , a `passkey`-source account (which requires `seedId` at construction time [2](#0-1) ) can collide on the same key (`passkey_<index>`) while carrying a different `seedId`, letting the second `create`/`createMany` call silently replace the stored account's `seedId`.

### Finding Description
In `createMany`, existence is determined solely by string-key collision: `const exists = Boolean(walletAccounts[walletAccount.toString()])` [3](#0-2) . When `exists` is true and `fillIndexGapsOnCreation` is enabled, no error is thrown, the secondary uniqueness guard (`getUniqueTagForWalletAccount`, which does check `id`/`seedId`/`index`) is explicitly skipped because it's gated by `if (!exists)` [4](#0-3) , and the code falls straight through to `walletAccounts[walletAccount.toString()] = walletAccount` [5](#0-4) . This is a direct object replacement, not a call to `updateWalletAccount`, so none of `updateWalletAccount`'s immutability asserts (`source`/`id`/`index` unchanged, `seedId` "can only be set if previously undefined") run at all [6](#0-5) .

For most sources this is not exploitable, because `toString()` is itself derived from `source`+`index`+`id` (hardware/custodial) or `source`+`index`+`seedId`+`compatibilityMode` (`SEED_SRC`) [1](#0-0)  — two accounts cannot share the same key while differing in those fields, so the "overwrite" is a no-op with respect to identity fields. However, `PASSKEY_SRC` is the exception: its constructor requires `seedId` (`assert(source !== PASSKEY_SRC || seedId, ...)`) but `toString()` only appends `seedId` when `source === SEED_SRC`, not for `PASSKEY_SRC`. Consequently two `passkey` accounts with the same `index` but different `seedId` produce an identical key (`passkey_<index>`), triggering the collision/overwrite path and letting a second `create`/`createMany` call silently reassign `seedId` on the stored account.

### Impact Explanation
An entity able to invoke `create`/`createMany` with a `passkey`-source payload (attacker-controlled `seedId`, matching `index` of an existing passkey account) can silently swap the `seedId` associated with that wallet account entry, bypassing the explicit immutability guarantee ("seedId can only be set if previously undefined") that `updateWalletAccount` enforces everywhere else. Since `seedId` determines derivation context for the account, this could redirect subsequent operations against that account name to a different seed's key material context — a real identity/derivation-context confusion, though scoped to the `passkey` source only (not a generic source/id/index takeover, since those fields are inherently protected by being part of the collision key itself).

### Likelihood Explanation
This requires: (1) `fillIndexGapsOnCreation: true` in module config, (2) the caller being able to invoke `create`/`createMany` with `source: 'passkey'` and an attacker-chosen `seedId`/`index`, and (3) an existing passkey account already present at that index. Whether `create`/`createMany` is reachable from untrusted/unprivileged surfaces (dapp RPC, deeplink, etc.) without an unlock/lock-state gate could not be confirmed from the indexed code — the `features/wallet-accounts/src/api/index.ts` layer that would expose this to RPC was not available in the retrieved context, so this precondition is assumed per the question rather than independently verified.

### Recommendation
In `createMany`, when `exists` is true, route the update through `updateWalletAccount` (or an equivalent explicit immutability check covering `source`/`id`/`index`/`seedId`) instead of directly overwriting `walletAccounts[walletAccount.toString()]`. Additionally, fix `WalletAccount#toString()` (or add a dedicated identity-tag helper used for collision detection) so that `seedId` is included in the uniqueness key for any source that requires `seedId` (not just `SEED_SRC`), e.g. `PASSKEY_SRC`.

### Proof of Concept
Integration test in `features/wallet-accounts/src/module/__tests__/index.test.ts` style:
1. Configure `walletAccounts` with `fillIndexGapsOnCreation: true`.
2. Call `walletAccounts.create({ source: 'passkey', index: 0, seedId: 'seedA' })`.
3. Call `walletAccounts.create({ source: 'passkey', index: 0, seedId: 'seedB' })`.
4. Assert the second call throws (matching the rejection behavior of `updateWalletAccount`'s `'seedId can only be set if previously undefined'` assert) — currently it does not throw, and `walletAccounts.get('passkey_0')` returns an account with `seedId === 'seedB'`, proving the silent overwrite.

### Citations

**File:** libraries/models/src/wallet-account/index.ts (L161-162)
```typescript
    assert(source !== SEED_SRC || seedId, 'expected option "seedId" for seed wallet account')
    assert(source !== PASSKEY_SRC || seedId, 'expected option "seedId" for passkey wallet account')
```

**File:** libraries/models/src/wallet-account/index.ts (L217-225)
```typescript
  toString() {
    return [
      this.source,
      this.index,
      ...(this.source === SEED_SRC ? [this.seedId, this.compatibilityMode] : [this.id]),
    ]
      .filter((v) => v != null)
      .join('_')
  }
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L63-74)
```typescript
  for (const key of ['source', 'id', 'index']) {
    assert(
      (before as unknown as Record<string, unknown>)[key] ===
        (after as unknown as Record<string, unknown>)[key],
      `cannot change account ${key}`
    )
  }

  assert(
    !before.seedId || before.seedId === after.seedId,
    'seedId can only be set if previously undefined'
  )
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L386-390)
```typescript
        const walletAccount = new WalletAccount(data as WalletAccountParams)
        const exists = Boolean(walletAccounts[walletAccount.toString()])
        if (exists && !this.#fillIndexGapsOnCreation) {
          throw new Error(`WalletAccount already exists: ${walletAccount.toString()}`)
        }
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L392-403)
```typescript
        // allow updating existing ones
        if (!exists) {
          const tag = getUniqueTagForWalletAccount(walletAccount)
          const match = byUniqueFields[tag]?.[0]
          if (match) {
            throw new Error(
              `Already have walletAccount with same .source, .id, .seedId, and .index: ${JSON.stringify(
                match.toJSON()
              )}`
            )
          }
        }
```

**File:** features/wallet-accounts/src/module/wallet-accounts.ts (L405-405)
```typescript
        walletAccounts[walletAccount.toString()] = walletAccount
```
