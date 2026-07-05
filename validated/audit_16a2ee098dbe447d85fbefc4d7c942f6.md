### Title
Strict Equality Withdrawal Check Enables Permissionless DoS via `directDeposits` in Dijkstra Era Legacy Mode — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs`)

---

### Summary

In the Dijkstra era, when a transaction is processed in **legacy mode** (i.e., it spends a Plutus V1–V3 script input), `validateWithdrawals` enforces a **strict equality** check between the declared withdrawal amount and the on-chain account balance. Simultaneously, the Dijkstra era introduces `directDeposits` — a **permissionless** mechanism that allows any transaction sender to add ADA to any registered staking account. An attacker can front-run a victim's legacy-mode withdrawal transaction by depositing a small amount to the victim's account, causing the strict equality check to fail and the transaction to be permanently rejected until the victim resubmits with the updated amount. The attacker can repeat this indefinitely.

---

### Finding Description

**Root cause — strict equality in `withdrawalsThatDoNotDrainAccounts`:** [1](#0-0) 

```haskell
withdrawalsThatDoNotDrainAccounts =
  categorizeWithdrawals
    ( \withdrawalAmount account ->
        withdrawalAmount == fromCompact (account ^. balanceAccountStateL)
    )
```

This function returns a failure for any withdrawal whose declared amount does not **exactly equal** the current account balance.

**Where it is called in Dijkstra legacy mode:** [2](#0-1) 

```haskell
validateWithdrawals legacyMode network withdrawals accounts = do
  missingWithdrawals <-
    if legacyMode
      then do
        let (missingWithdrawals, incompleteWithdrawals) =
              case withdrawalsThatDoNotDrainAccounts withdrawals network accounts of
                Nothing -> (Map.empty, Map.empty)
                Just (missing, incomplete) -> (unWithdrawals missing, incomplete)
        failOnNonEmptyMap incompleteWithdrawals IncompleteWithdrawals
        ...
```

`legacyMode` is set to `True` when the top-level transaction spends a Plutus V1–V3 script input (`stAnnTx ^. plutusLegacyModeStAnnTxG`). [3](#0-2) 

**The permissionless `directDeposits` mechanism:**

The Dijkstra era introduces `directDepositsTxBodyL`, which allows any transaction to add ADA to any registered staking account. The only validation is that the target accounts are registered — there is no authorization check on who may deposit: [4](#0-3) 

```haskell
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts
pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

`applyDirectDeposits` unconditionally adds the deposited amount to the account balance: [5](#0-4) 

```haskell
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
```

**Contrast with non-legacy mode:** When `legacyMode = False`, the check uses `withdrawalsThatExceedAccountBalance` (`<=`), which correctly allows withdrawals of any amount up to the balance: [6](#0-5) 

---

### Impact Explanation

An attacker can cause any victim's legacy-mode withdrawal transaction to fail by depositing 1 lovelace to the victim's staking account immediately before the victim's transaction is processed. The victim's transaction is rejected with `IncompleteWithdrawals`. The attacker can repeat this for every resubmission attempt, creating a persistent denial-of-service against reward withdrawals. If the victim is a Plutus script with a hardcoded withdrawal amount (e.g., a script that asserts `withdrawalAmount == expectedBalance`), the attack can permanently prevent the script from executing its withdrawal logic, effectively freezing the rewards in the account.

This matches the **Medium** allowed impact: *attacker-controlled transactions modify withdrawals outside design parameters*.

---

### Likelihood Explanation

- The Dijkstra era is the current experimental era in this repository.
- `directDeposits` is a new, permissionless feature with no authorization gate.
- Any transaction that spends a Plutus V1/V2/V3 script input is in legacy mode and subject to the strict equality check.
- Front-running is realistic on Cardano since mempool contents are observable.
- The cost to the attacker is only the minimum ADA required for the deposit (1 lovelace + fees).

---

### Recommendation

In `validateWithdrawals`, replace the strict equality check in legacy mode with a `>=` (greater-than-or-equal) check, consistent with the non-legacy path. The withdrawal should be valid as long as the declared amount does not **exceed** the balance, not only when it **exactly equals** it:

```haskell
-- Replace:
withdrawalAmount == fromCompact (account ^. balanceAccountStateL)
-- With:
withdrawalAmount <= fromCompact (account ^. balanceAccountStateL)
```

Alternatively, if the protocol requirement is that withdrawals must drain the full balance (which is the Shelley/Conway design intent), then `directDeposits` targeting an account that has a pending withdrawal in the mempool should be considered carefully, or the strict-equality check should be removed from legacy mode entirely and replaced with the `<=` check used in non-legacy mode. [7](#0-6) 

---

### Proof of Concept

1. Victim registers a staking credential and accumulates rewards (balance = `R` lovelace).
2. Victim constructs a Dijkstra-era transaction that:
   - Spends a Plutus V2 script input (triggering `legacyMode = True`).
   - Declares a withdrawal of exactly `R` lovelace from their account.
3. Attacker observes the victim's transaction in the mempool.
4. Attacker submits a transaction with `directDeposits = [(victimAccountAddress, 1)]`, depositing 1 lovelace to the victim's account. This transaction is processed first (e.g., via higher fee).
5. Victim's account balance is now `R + 1`.
6. Victim's transaction is evaluated: `withdrawalsThatDoNotDrainAccounts` checks `R == R + 1` → `False` → `IncompleteWithdrawals` failure. Transaction is rejected.
7. Attacker repeats step 4 for every resubmission attempt by the victim. [8](#0-7) [9](#0-8)

### Citations

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L196-210)
```haskell
withdrawalsThatDoNotDrainAccounts ::
  EraAccounts era =>
  Withdrawals ->
  Network ->
  Accounts era ->
  -- | invalid withdrawal = that which does not have an account address or is in
  -- the wrong network.
  -- incomplete withdrawal = that which does not withdraw the exact account
  -- balance.
  Maybe (Withdrawals, Map AccountAddress (Mismatch RelEQ Coin))
withdrawalsThatDoNotDrainAccounts =
  categorizeWithdrawals
    ( \withdrawalAmount account ->
        withdrawalAmount == fromCompact (account ^. balanceAccountStateL)
    )
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L212-222)
```haskell
withdrawalsThatExceedAccountBalance ::
  EraAccounts era =>
  Withdrawals ->
  Network ->
  Accounts era ->
  Maybe (Withdrawals, Map AccountAddress (Mismatch RelLTEQ Coin))
withdrawalsThatExceedAccountBalance =
  categorizeWithdrawals
    ( \withdrawalAmount account ->
        withdrawalAmount <= fromCompact (account ^. balanceAccountStateL)
    )
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L287-298)
```haskell
-- | Add each direct-deposit amount to the matching account balance.
--
-- /Note/ - There are no checks that direct deposits mention only registered accounts.
applyDirectDeposits ::
  EraAccounts era =>
  DirectDeposits ->
  Accounts era ->
  Accounts era
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L211-216)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
    injectFailure . DirectDepositsToMissingAccounts

  pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L218-244)
```haskell
validateWithdrawals ::
  EraAccounts era =>
  Bool ->
  Network ->
  Withdrawals ->
  Accounts era ->
  Rule (ENTITIES era) ctx ()
validateWithdrawals legacyMode network withdrawals accounts = do
  missingWithdrawals <-
    if legacyMode
      then do
        let (missingWithdrawals, incompleteWithdrawals) =
              case withdrawalsThatDoNotDrainAccounts withdrawals network accounts of
                Nothing -> (Map.empty, Map.empty)
                Just (missing, incomplete) -> (unWithdrawals missing, incomplete)
        failOnNonEmptyMap incompleteWithdrawals IncompleteWithdrawals
        pure missingWithdrawals
      else do
        let (missingWithdrawals, exceededWithdrawals) =
              case withdrawalsThatExceedAccountBalance withdrawals network accounts of
                Nothing -> (Map.empty, Map.empty)
                Just (missing, exceeded) -> (unWithdrawals missing, exceeded)
        failOnNonEmptyMap exceededWithdrawals WithdrawalAmountsExceedAccountBalances
        pure missingWithdrawals
  failOnNonEmptyMap missingWithdrawals $
    WithdrawalsMissingAccounts . Withdrawals . NEM.toMap

```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L399-407)
```haskell
        certStateAfterENTITIES <-
          trans @(EraRule "ENTITIES" era) $
            TRC
              ( EntitiesEnv
                  (stAnnTx ^. plutusLegacyModeStAnnTxG)
                  (Conway.CertsEnv tx pp curEpochNo committee committeeProposals)
              , certStateAfterSubLedgers
              , StrictSeq.fromStrict $ txBody ^. certsTxBodyL
              )
```
