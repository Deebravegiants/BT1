### Title
`validateBatchWithdrawals` ignores sub-transaction direct deposits when checking batch withdrawal limits — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`)

---

### Summary

In the Dijkstra era, the `validateBatchWithdrawals` function checks the sum of all withdrawals across a transaction batch against the **original** account balance (before any sub-transaction processing). However, sub-transactions can include `directDeposits` that increase account balances. Because sub-transactions are executed sequentially in `SUBLEDGERS` before the top-level `UTXO` validation runs, the actual available balance for withdrawal may be higher than the original balance. The batch-level check does not account for this, causing valid transaction batches to be incorrectly rejected.

---

### Finding Description

**Root cause — `validateBatchWithdrawals` uses the pre-sub-ledger account state:**

In `dijkstraUtxoTransition`, the `accounts` snapshot used for the batch withdrawal check is taken from the `certState` field of `DijkstraUtxoEnv`:

```haskell
-- this is the original Accounts, before any transactions were applied
let accounts = certState ^. certDStateL . accountsL
``` [1](#0-0) 

This `certState` is supplied by `dijkstraLedgerTransition` as `lsCertState ledgerState` — the **original** cert state before any sub-ledger processing:

```haskell
-- Call UTXOW with DijkstraUtxoEnv, passing the original UTxO and original certState
utxoStateFinal <-
  trans @(EraRule "UTXOW" era) $
    TRC
      ( DijkstraUtxoEnv slot pp (lsCertState ledgerState) originalUtxo
      , ...
      )
``` [2](#0-1) 

**The check itself:**

`validateBatchWithdrawals` aggregates all withdrawals from the top-level tx and every sub-transaction, then checks each against `getAccountBalance`, which reads from the original (pre-sub-ledger) `accounts`:

```haskell
validateBatchWithdrawals accounts tx =
  let allWithdrawals =
        Map.unionsWith (<>) $
          unWithdrawals (tx ^. bodyTxL . withdrawalsTxBodyL)
            : [ unWithdrawals $ subTx ^. bodyTxL . withdrawalsTxBodyL
              | subTx <- OMap.elems $ tx ^. bodyTxL . subTransactionsTxBodyL
              ]
      badWithdrawals =
        Map.mapMaybeWithKey
          ( \acctAddr withdrawn ->
              let balance = getAccountBalance acctAddr
               in if withdrawn > balance
                    then Just Mismatch {mismatchSupplied = withdrawn, mismatchExpected = balance}
                    else Nothing
          )
          allWithdrawals
   in failureOnNonEmptyMap badWithdrawals WithdrawalsExceedAccountBalance
``` [3](#0-2) 

**The inconsistency with actual execution:**

Sub-transactions are processed first in `SUBLEDGERS` (before `UTXOW` is called):

```haskell
-- Process all subtransactions first
LedgerState utxoStateAfterSubLedgers certStateAfterSubLedgers <-
  trans @(EraRule "SUBLEDGERS" era) $ TRC (...)
``` [4](#0-3) 

Within each sub-transaction, `dijkstraSubEntitiesTransition` applies withdrawals first, then applies direct deposits, updating the `certState` that is passed to the next sub-transaction:

```haskell
& certDStateL . accountsL %~ applyWithdrawals withdrawals
-- ...
pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
``` [5](#0-4) 

This means that in the **actual execution**, a direct deposit made by sub-tx N is visible to sub-tx N+1's withdrawal check (via the updated `certState`). But `validateBatchWithdrawals` never sees these updated balances — it always checks against the original balance.

---

### Impact Explanation

**Medium.** The withdrawal validation in `validateBatchWithdrawals` is more restrictive than the actual execution semantics. Any transaction batch where a sub-transaction makes a direct deposit to an account and a subsequent sub-transaction (or the top-level transaction) withdraws from that same account will be incorrectly rejected if the total withdrawal exceeds the original balance — even though the post-deposit balance would be sufficient. This modifies the effective withdrawal limits outside design parameters, preventing users from using valid transaction patterns that the ledger's own execution model would otherwise permit.

---

### Likelihood Explanation

**Medium.** The Dijkstra era introduces both sub-transactions and direct deposits as new primitives. Any transaction author who constructs a batch where a sub-transaction funds an account via `directDeposits` and a later sub-transaction withdraws from that account will trigger this rejection. The pattern is a natural use case for atomic multi-step operations (e.g., fund-then-withdraw in a single batch), making accidental triggering likely as adoption grows.

---

### Recommendation

`validateBatchWithdrawals` should compute the effective available balance for each account by adding the direct deposits from all sub-transactions (in execution order) to the original balance before checking withdrawal limits. Concretely, the function should accumulate the `directDepositsTxBodyL` from each sub-transaction in the same order as `SUBLEDGERS` processes them, and add those amounts to `getAccountBalance` before comparing against the aggregated withdrawals.

---

### Proof of Concept

**Setup:** Account A has an original balance of 100 ADA.

**Transaction batch:**
- Sub-tx 1: `directDeposits = { AccountA → 50 ADA }`, no withdrawals
- Sub-tx 2: `withdrawals = { AccountA → 120 ADA }`, no direct deposits

**Actual execution path (SUBLEDGERS):**
1. Sub-tx 1 `SUBENTITIES`: applies direct deposit → Account A balance = 150 ADA
2. Sub-tx 2 `SUBENTITIES`: checks 120 ≤ 150 → **passes**, applies withdrawal → Account A balance = 30 ADA

**Batch validation path (UTXO):**
- `validateBatchWithdrawals` aggregates: `allWithdrawals = { AccountA → 120 ADA }`
- `getAccountBalance AccountA` = 100 ADA (original, pre-sub-ledger)
- 120 > 100 → emits `WithdrawalsExceedAccountBalance` → **entire batch rejected**

The transaction is rejected despite the sub-transaction execution being individually valid, because `validateBatchWithdrawals` checks against the original balance at: [6](#0-5) 

using accounts sourced from the original cert state at: [7](#0-6) 

rather than the post-sub-ledger cert state (`certStateAfterSubLedgers`) that reflects the direct deposits applied by `applyDirectDeposits` in: [8](#0-7)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L249-280)
```haskell
-- | For each account, the total withdrawals across the entire batch should not exceed the original account balance.
-- Unregistered accounts are treated as having 0 balance.
validateBatchWithdrawals ::
  ( EraTx era
  , EraAccounts era
  , DijkstraEraTxBody era
  ) =>
  Accounts era ->
  Tx TopTx era ->
  Test (DijkstraUtxoPredFailure era)
validateBatchWithdrawals accounts tx =
  let allWithdrawals =
        Map.unionsWith (<>) $
          unWithdrawals (tx ^. bodyTxL . withdrawalsTxBodyL)
            : [ unWithdrawals $ subTx ^. bodyTxL . withdrawalsTxBodyL
              | subTx <- OMap.elems $ tx ^. bodyTxL . subTransactionsTxBodyL
              ]
      badWithdrawals =
        Map.mapMaybeWithKey
          ( \acctAddr withdrawn ->
              let balance = getAccountBalance acctAddr
               in if withdrawn > balance
                    then Just Mismatch {mismatchSupplied = withdrawn, mismatchExpected = balance}
                    else Nothing
          )
          allWithdrawals
   in failureOnNonEmptyMap badWithdrawals WithdrawalsExceedAccountBalance
  where
    getAccountBalance (AccountAddress _ (AccountId cred)) =
      case lookupAccountState cred accounts of
        Nothing -> mempty -- unregistered account, 0 balance
        Just accountState -> fromCompact $ accountState ^. balanceAccountStateL
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L347-348)
```haskell
  -- this is the original Accounts, before any transactions were applied
  let accounts = certState ^. certDStateL . accountsL
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L369-383)
```haskell
  -- Process all subtransactions first
  LedgerState utxoStateAfterSubLedgers certStateAfterSubLedgers <-
    trans @(EraRule "SUBLEDGERS" era) $
      TRC
        ( SubLedgerEnv
            slot
            mbCurEpochNo
            txIx
            pp
            chainAccountState
            originalUtxo
            (tx ^. isValidTxL)
        , ledgerState
        , subStAnnTxs
        )
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L435-442)
```haskell
  -- Call UTXOW with DijkstraUtxoEnv, passing the original UTxO and original certState
  utxoStateFinal <-
    trans @(EraRule "UTXOW" era) $
      TRC
        ( DijkstraUtxoEnv slot pp (lsCertState ledgerState) originalUtxo
        , utxoStateBeforeUtxow
        , stAnnTx
        )
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L174-187)
```haskell
  let certStateBeforeSubCerts =
        certState
          & Conway.updateDormantDRepExpiries tx curEpoch
          & Conway.updateVotingDRepExpiries tx curEpoch (pp ^. ppDRepActivityL)
          & certDStateL . accountsL %~ applyWithdrawals withdrawals
  certStateAfterSubCerts <-
    trans @(EraRule "SUBCERTS" era) $ TRC (subCertsEnv, certStateBeforeSubCerts, certificates)

  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
    injectFailure . SubDirectDepositsToMissingAccounts

  pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```
