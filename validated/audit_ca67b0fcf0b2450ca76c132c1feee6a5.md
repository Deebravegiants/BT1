### Title
Strict Equality Withdrawal Check Combined with Unpermissioned `DirectDeposits` Enables Withdrawal DoS in Legacy Mode — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs`)

---

### Summary

In the Dijkstra era, the `ENTITIES` rule validates withdrawals using a strict equality check (`withdrawalAmount == accountBalance`) when the transaction is in "legacy mode" (uses PlutusV2 or earlier scripts). Simultaneously, the Dijkstra era introduces a `DirectDeposits` field in the transaction body that allows any unprivileged transaction sender to add funds to any registered account without recipient authorization. An attacker can front-run a victim's legacy-mode withdrawal transaction by submitting a transaction with a 1-lovelace `directDeposit` to the victim's account, causing the victim's withdrawal to fail with `IncompleteWithdrawals` because the balance no longer exactly matches the declared withdrawal amount.

---

### Finding Description

**Root cause — strict equality check:**

`withdrawalsThatDoNotDrainAccounts` in `libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs` enforces that a withdrawal amount must **exactly equal** the account balance:

```haskell
withdrawalsThatDoNotDrainAccounts =
  categorizeWithdrawals
    ( \withdrawalAmount account ->
        withdrawalAmount == fromCompact (account ^. balanceAccountStateL)
    )
``` [1](#0-0) 

This function is called in the Dijkstra `ENTITIES` rule's `validateWithdrawals` when `legacyMode = True`:

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
        pure missingWithdrawals
      else do
        ...
        failOnNonEmptyMap exceededWithdrawals WithdrawalAmountsExceedAccountBalances
``` [2](#0-1) 

The `legacyMode` flag is `stAnnTx ^. plutusLegacyModeStAnnTxG`, set to `True` when the transaction uses PlutusV2 or earlier scripts, and is passed into `EntitiesEnv` from `dijkstraLedgerTransition`:

```haskell
certStateAfterENTITIES <-
  trans @(EraRule "ENTITIES" era) $
    TRC
      ( EntitiesEnv
          (stAnnTx ^. plutusLegacyModeStAnnTxG)
          ...
``` [3](#0-2) 

**Root cause — unpermissioned `DirectDeposits`:**

The Dijkstra era adds a `dtbrDirectDeposits :: !DirectDeposits` field to the top-level transaction body: [4](#0-3) 

In `dijkstraEntitiesTransition`, after certificates are processed, `directDeposits` from the transaction body are applied to accounts with **no recipient authorization check** — only a check that the target accounts exist:

```haskell
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
  injectFailure . DirectDepositsToMissingAccounts

pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
``` [5](#0-4) 

`applyDirectDeposits` simply adds the deposited amount to the target account balance:

```haskell
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
``` [6](#0-5) 

**The combined vulnerability:**

A victim constructs a withdrawal transaction in legacy mode specifying withdrawal amount = current balance `X`. An attacker front-runs by submitting a transaction with `directDeposit` of 1 lovelace to the victim's account. The victim's account balance becomes `X + 1`. When the victim's transaction is processed, `withdrawalAmount (X) ≠ balance (X + 1)`, so the rule fires `IncompleteWithdrawals` and the transaction is rejected.

---

### Impact Explanation

This falls under the **Medium** allowed impact: *"Attacker-controlled transactions... modify... withdrawals outside design parameters."*

An attacker can persistently prevent any legacy-mode withdrawal transaction from succeeding by repeatedly front-running with 1-lovelace direct deposits. The victim's funds are not permanently lost — they can re-query the balance and re-submit — but the attacker can sustain the DoS indefinitely at low cost (1 lovelace + fees per attack). Users with large reward balances who rely on legacy-mode scripts (PlutusV2 or earlier) are particularly affected.

---

### Likelihood Explanation

- The `DirectDeposits` feature is new in Dijkstra and requires no recipient authorization, making it trivially exploitable by any transaction sender.
- Legacy mode is triggered by any transaction that uses PlutusV2 or earlier Plutus scripts, which is a realistic scenario for wallets and dApps migrating from Conway.
- The attack requires only mempool observation and a small amount of ADA (1 lovelace + fees), making it economically viable.
- The non-legacy path already uses `withdrawalsThatExceedAccountBalance` (a `<=` check), confirming the protocol designers recognized the strict equality problem and fixed it for new-mode transactions — but the legacy path retains the vulnerable check.

---

### Recommendation

In `validateWithdrawals` within `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs`, replace the strict equality check in the legacy path with the same `<=` check used in the non-legacy path, or alternatively cap the withdrawal at `min(withdrawalAmount, balance)`. The non-legacy path already demonstrates the correct approach:

```haskell
-- Non-legacy (correct): uses <=
withdrawalAmount <= fromCompact (account ^. balanceAccountStateL)

-- Legacy (vulnerable): uses ==
withdrawalAmount == fromCompact (account ^. balanceAccountStateL)
``` [7](#0-6) 

Additionally, consider requiring recipient authorization (a witness from the staking credential) for `directDeposits` targeting an account, to prevent unsolicited balance manipulation.

---

### Proof of Concept

1. **Setup**: Register a staking credential `cred` and accumulate rewards `R` in its account. Construct a legacy-mode withdrawal transaction `txVictim` specifying `Withdrawals [(accountAddress cred, R)]` and including a PlutusV2 script input (triggering `legacyMode = True`).

2. **Attack**: Before `txVictim` is included in a block, submit `txAttacker` with:
   ```
   directDepositsTxBodyL .~ DirectDeposits [(accountAddress cred, Coin 1)]
   ```
   funded from the attacker's own UTxO.

3. **Result**: `txAttacker` is processed first. The victim's account balance becomes `R + 1`. When `txVictim` is processed, `validateWithdrawals True` calls `withdrawalsThatDoNotDrainAccounts`, finds `R ≠ R + 1`, and fires `IncompleteWithdrawals (NEM.singleton accountAddress (Mismatch R (R+1)))`. The withdrawal is rejected.

4. **Repeat**: The attacker repeats step 2 each time the victim re-submits, sustaining the DoS at a cost of 1 lovelace + fees per iteration.

This is directly analogous to the `TokenMigration.sol` report: a strict equality check on a balance that an unprivileged third party can increment by a minimal amount, causing the victim's transaction to revert.

### Citations

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L206-222)
```haskell
withdrawalsThatDoNotDrainAccounts =
  categorizeWithdrawals
    ( \withdrawalAmount account ->
        withdrawalAmount == fromCompact (account ^. balanceAccountStateL)
    )

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

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L295-298)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L225-241)
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
        pure missingWithdrawals
      else do
        let (missingWithdrawals, exceededWithdrawals) =
              case withdrawalsThatExceedAccountBalance withdrawals network accounts of
                Nothing -> (Map.empty, Map.empty)
                Just (missing, exceeded) -> (unWithdrawals missing, exceeded)
        failOnNonEmptyMap exceededWithdrawals WithdrawalAmountsExceedAccountBalances
        pure missingWithdrawals
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L185-186)
```haskell
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
```
