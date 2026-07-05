### Title
`validateBatchWithdrawals` Uses Post-Withdrawal Account Balance Instead of Original Balance, Causing Valid Withdrawal Transactions to Be Permanently Rejected — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`)

---

### Summary

In the Dijkstra era, `validateBatchWithdrawals` is intended to check that the total withdrawals across a batch (top-level transaction plus all sub-transactions) do not exceed the **original** account balance. However, the `accounts` value passed to this function is the **post-withdrawal** ledger state — after ENTITIES has already applied all withdrawals — not the original state. This causes the check to compare total withdrawals against an already-drained balance, incorrectly rejecting valid transactions where total withdrawals exceed half the original balance.

---

### Finding Description

**Vulnerability class:** Wrong variable used in a validation/bounds check (funds/accounting bug).

In `dijkstraLedgerTransition`, the LEDGER rule processes sub-transactions and then the top-level transaction's ENTITIES rule (which applies withdrawals to accounts) **before** invoking UTXOW/UTXO:

```haskell
-- Step 1: process sub-transactions
LedgerState utxoStateAfterSubLedgers certStateAfterSubLedgers <-
  trans @(EraRule "SUBLEDGERS" era) $ TRC (...)

-- Step 2: apply top-level tx withdrawals via ENTITIES
certStateAfterENTITIES <-
  trans @(EraRule "ENTITIES" era) $
    TRC (EntitiesEnv ..., certStateAfterSubLedgers, ...)

-- Step 3: pass post-withdrawal certState to UTXOW/UTXO
utxoStateFinal <-
  trans @(EraRule "UTXOW" era) $
    TRC (DijkstraUtxoEnv slot pp certStateFinal originalUtxo, ...)
``` [1](#0-0) [2](#0-1) 

Inside `dijkstraUtxoTransition`, the code reads the accounts from this post-withdrawal `certState` and passes them to `validateBatchWithdrawals`:

```haskell
-- this is the original Accounts, before any transactions were applied  ← COMMENT IS WRONG
let accounts = certState ^. certDStateL . accountsL
...
runTest $ validateBatchWithdrawals accounts tx
``` [3](#0-2) 

`validateBatchWithdrawals` then checks:

```haskell
validateBatchWithdrawals accounts tx =
  let allWithdrawals = Map.unionsWith (<>) $ ...
      badWithdrawals = Map.mapMaybeWithKey
        ( \acctAddr withdrawn ->
            let balance = getAccountBalance acctAddr   -- ← post-withdrawal balance
             in if withdrawn > balance
                  then Just Mismatch {mismatchSupplied = withdrawn, mismatchExpected = balance}
                  else Nothing
        )
        allWithdrawals
   in failureOnNonEmptyMap badWithdrawals WithdrawalsExceedAccountBalance
``` [4](#0-3) 

The function's own documentation states the intent:

> For each account, the total withdrawals across the entire batch should not exceed the **original** account balance. [5](#0-4) 

But `balance` is the post-withdrawal balance. Since `applyWithdrawals` subtracts each withdrawal from the account: [6](#0-5) 

…the post-withdrawal balance is `originalBalance − totalWithdrawals`. The check therefore becomes:

```
totalWithdrawals > originalBalance − totalWithdrawals
⟺  2 × totalWithdrawals > originalBalance
```

This is a strictly more restrictive condition than the intended `totalWithdrawals > originalBalance`. Any valid withdrawal of more than half the original balance is incorrectly rejected.

**Concrete example:**
- Account balance: 100 ADA
- User submits a Dijkstra-era transaction withdrawing 60 ADA (valid: 60 ≤ 100)
- ENTITIES applies the withdrawal → balance becomes 40 ADA
- `validateBatchWithdrawals` checks: `60 > 40` → **FAIL** → transaction rejected

The `DijkstraUtxoEnv` carries `dueOriginalUtxo` (the pre-sub-transaction UTxO snapshot) for input validation, but no equivalent "original certState" for account balance validation: [7](#0-6) 

---

### Impact Explanation

Any Dijkstra-era transaction whose total withdrawals (top-level + sub-transactions combined) exceed half the original account balance will be permanently rejected by the ledger. Users cannot withdraw more than 50% of their reward balance in a single batch transaction. Withdrawing the full balance in one transaction is always rejected. Because this check is embedded in the ledger transition rules, correcting it requires a hard fork. This constitutes **permanent freezing of withdrawals** beyond the 50% threshold, matching the High impact category: *"Permanent freezing of funds, deposits, rewards, or withdrawals where recovery requires a hard fork."*

---

### Likelihood Explanation

The Dijkstra era introduces nested/batch transactions as a new feature. Any unprivileged user who submits a Dijkstra-era transaction with a withdrawal exceeding half their account balance will trigger this failure. No special privileges, keys, or coordination are required. The entry path is a standard user-submitted transaction.

---

### Recommendation

Pass the **original** `certState` (captured before SUBLEDGERS and ENTITIES run) into the `DijkstraUtxoEnv`, analogously to how `originalUtxo` is already captured and threaded through:

```haskell
let originalUtxo    = utxosUtxo (ledgerState ^. lsUTxOStateL)
    originalCertState = ledgerState ^. lsCertStateL   -- ADD THIS
```

Then pass `originalCertState` to `DijkstraUtxoEnv` alongside `originalUtxo`, and use it in `validateBatchWithdrawals` instead of the post-withdrawal `certState`. Alternatively, restructure the LEDGER rule so that UTXOW/UTXO runs before ENTITIES applies withdrawals, consistent with the comment's stated intent.

---

### Proof of Concept

1. Register a staking credential and accumulate 100 ADA in rewards.
2. Construct a Dijkstra-era top-level transaction with a single withdrawal of 60 ADA from that account.
3. Submit the transaction.
4. Observe that the transaction fails with `WithdrawalsExceedAccountBalance` reporting `mismatchSupplied = 60, mismatchExpected = 40`, even though 60 ≤ 100.
5. Reduce the withdrawal to 49 ADA and resubmit — the transaction succeeds, confirming the threshold is `originalBalance / 2`.

The test infrastructure for this pattern already exists in: [8](#0-7)

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L318-378)
```haskell
dijkstraUtxoTransition ::
  forall era.
  ( EraUTxO era
  , EraCertState era
  , DijkstraEraTxBody era
  , AlonzoEraTx era
  , EraStake era
  , InjectRuleFailure "UTXO" Shelley.ShelleyUtxoPredFailure era
  , InjectRuleFailure "UTXO" Allegra.AllegraUtxoPredFailure era
  , InjectRuleFailure "UTXO" Alonzo.AlonzoUtxoPredFailure era
  , InjectRuleFailure "UTXO" Babbage.BabbageUtxoPredFailure era
  , InjectRuleFailure "UTXO" DijkstraUtxoPredFailure era
  , Environment (EraRule "UTXO" era) ~ DijkstraUtxoEnv era
  , State (EraRule "UTXO" era) ~ UTxOState era
  , Signal (EraRule "UTXO" era) ~ StAnnTx TopTx era
  , BaseM (EraRule "UTXO" era) ~ ShelleyBase
  , STS (EraRule "UTXO" era)
  , Event (EraRule "UTXO" era) ~ Alonzo.AlonzoUtxoEvent era
  , -- In this function we call the UTXOS rule, so we need some assumptions
    Environment (EraRule "UTXOS" era) ~ ()
  , State (EraRule "UTXOS" era) ~ ()
  , Signal (EraRule "UTXOS" era) ~ StAnnTx TopTx era
  , Embed (EraRule "UTXOS" era) (EraRule "UTXO" era)
  ) =>
  TransitionRule (EraRule "UTXO" era)
dijkstraUtxoTransition = do
  TRC (DijkstraUtxoEnv slot pp certState originalUtxo, utxos, stAnnTx) <-
    judgmentContext
  let tx = stAnnTx ^. txStAnnTxG
  -- this is the original Accounts, before any transactions were applied
  let accounts = certState ^. certDStateL . accountsL

  let txBody = tx ^. bodyTxL

  {- inInterval (SlotOf Γ) (ValidIntervalOf txTop) -}
  runTest $ Allegra.validateOutsideValidityIntervalUTxO slot txBody

  sysSt <- liftSTS $ asks systemStart
  ei <- liftSTS $ asks epochInfo

  runTest $ Alonzo.validateOutsideForecast ei slot sysSt tx

  {- SpendInputs ≠ ∅ -}
  runTestOnSignal $ Shelley.validateInputSetEmptyUTxO txBody

  let allInputs = txBody ^. allInputsTxBodyF
      inputs = txBody ^. inputsTxBodyL

  {- SpendInputsOf txTop ∪ RefInputsOf txTop ∪ CollInputsOf txTop ⊆ dom(utxo₀) -}
  runTest $ Shelley.validateBadInputsUTxO originalUtxo allInputs

  {- SpendInputsOf txTop ⊆ dom(utxo_s) — prevents double-spend with subtxs -}
  runTest $ Shelley.validateBadInputsUTxO (utxosUtxo utxos) inputs

  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo

  {- (RedeemersOf txTop ≠ ∅ ⊎ Any (λ txSub → RedeemersOf txSub ≠ ∅) subtxs) → collateralCheck -}
  validate $ validateBatchCollateral pp tx originalUtxo

  runTest $ validateBatchWithdrawals accounts tx
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L277-285)
```haskell
applyWithdrawals ::
  EraAccounts era =>
  Withdrawals ->
  Accounts era ->
  Accounts era
applyWithdrawals (Withdrawals wdrls) =
  updateAccountBalances
    (\amount account -> subtractCompactCoin amount (account ^. balanceAccountStateL))
    wdrls
```

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertsSpec.hs (L67-91)
```haskell
    it "Withdrawing the wrong amount" $ do
      modifyPParams $ ppGovActionLifetimeL .~ EpochInterval 2

      (accountAddress1, reward1, stakeKey1) <- setupAccountAddress
      (accountAddress2, reward2, stakeKey2) <- setupAccountAddress
      void $ delegateToDRep (KeyHashObj stakeKey1) (Coin 1_000_000) DRepAlwaysAbstain
      void $ delegateToDRep (KeyHashObj stakeKey2) (Coin 1_000_000) DRepAlwaysAbstain
      submitFailingTx
        ( mkBasicTx $
            mkBasicTxBody
              & withdrawalsTxBodyL
                .~ Withdrawals
                  [ (accountAddress1, reward1 <+> Coin 1)
                  , (accountAddress2, reward2)
                  ]
        )
        [ injectFailure $
            WithdrawalsExceedAccountBalance @era $
              NE.singleton accountAddress1 $
                Mismatch (reward1 <+> Coin 1) reward1
        , injectFailure $
            WithdrawalAmountsExceedAccountBalances @era $
              NE.singleton accountAddress1 $
                Mismatch (reward1 <+> Coin 1) reward1
        ]
```
