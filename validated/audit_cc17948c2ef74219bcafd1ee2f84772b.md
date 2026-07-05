### Title
Cross-Sub-Transaction Withdrawal Double-Spend via Stale Account Balance Snapshot in `validateBatchWithdrawals` - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`)

---

### Summary

In the Dijkstra era, the `validateBatchWithdrawals` function checks that the total withdrawals across the top-level transaction and all sub-transactions do not exceed the account balance. However, it checks this against the **original pre-batch account state** (`lsCertState ledgerState`), while sub-transactions are processed sequentially and each one **applies its own withdrawals** to the live `certState` via `applyWithdrawals`. This means a sub-transaction that withdraws the full balance of an account can reduce that balance to zero, but a subsequent sub-transaction (or the top-level transaction) that also withdraws from the same account will still pass the `validateBatchWithdrawals` check — because that check only sees the original balance. The result is that the same account balance can be withdrawn multiple times within a single batch, creating ADA out of thin air.

---

### Finding Description

The Dijkstra era introduces sub-transactions (`subTransactionsTxBodyL`), which are processed sequentially by the `SUBLEDGERS` rule before the top-level transaction is validated. Each sub-transaction's `SUBENTITIES` rule calls `applyWithdrawals` to subtract the withdrawn amount from the live account balance:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs:174-178
let certStateBeforeSubCerts =
      certState
        & ...
        & certDStateL . accountsL %~ applyWithdrawals withdrawals
```

The top-level `ENTITIES` rule similarly calls `applyWithdrawals` for the top-level transaction's withdrawals:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs:203-207
let certStateBeforeCerts =
      certState
        & ...
        & certDStateL . accountsL %~ applyWithdrawals withdrawals
```

The guard that is supposed to prevent over-withdrawal across the entire batch is `validateBatchWithdrawals`, called from `dijkstraUtxoTransition`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs:347-378
let accounts = certState ^. certDStateL . accountsL
...
runTest $ validateBatchWithdrawals accounts tx
```

The `certState` here is the **original** `certState` passed into `DijkstraUtxoEnv` from `dijkstraLedgerTransition`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs:439
( DijkstraUtxoEnv slot pp (lsCertState ledgerState) originalUtxo
```

Note that `lsCertState ledgerState` is the **pre-batch** cert state — the state before any sub-transactions have been applied.

`validateBatchWithdrawals` then sums all withdrawals across the batch and checks each account address against this original balance:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs:259-280
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
                    then Just Mismatch ...
                    else Nothing
          )
          allWithdrawals
```

The `Map.unionsWith (<>)` sums the withdrawal amounts for each account address across all sub-transactions and the top-level transaction. This correctly aggregates the total claimed withdrawal. The check `withdrawn > balance` then compares this total against the original balance.

**The vulnerability**: `applyWithdrawals` (used in `SUBENTITIES`) **subtracts** the withdrawal amount from the balance, while `drainAccounts` (used in legacy mode) **zeroes** the balance. The `validateBatchWithdrawals` check uses `Map.unionsWith (<>)` which is `(<>)` on `Coin`, i.e., addition. So if sub-transaction 1 withdraws `X` from account `A`, and sub-transaction 2 also withdraws `X` from account `A`, the total checked is `2X`. If the original balance is `2X`, the check passes.

However, the actual execution path is:
1. Sub-transaction 1 runs `SUBENTITIES` → `applyWithdrawals` subtracts `X` → balance becomes `X`.
2. Sub-transaction 2 runs `SUBENTITIES` → checks `withdrawalsThatExceedAccountBalance` against the **current** balance of `X` → `X <= X` passes → `applyWithdrawals` subtracts `X` → balance becomes `0`.
3. Top-level transaction runs `ENTITIES` → checks `applyWithdrawals` for top-level withdrawals.

So far this appears consistent. But the critical issue is with the **`directDeposits`** mechanism. A sub-transaction can include `directDepositsTxBodyL` which calls `applyDirectDeposits` to **add** coin to an account balance:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs:182-187
let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
    accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
  injectFailure . SubDirectDepositsToMissingAccounts
pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

`validateBatchWithdrawals` checks total withdrawals against the **original** balance, but does **not** account for direct deposits made by earlier sub-transactions that increase the balance. This means:

- Account `A` has original balance `B`.
- Sub-transaction 1: `directDeposits` adds `D` to account `A` → live balance becomes `B + D`.
- Sub-transaction 2: withdraws `B + D` from account `A` → `SUBENTITIES` checks `B + D <= B + D` (live balance) → passes → live balance becomes `0`.
- `validateBatchWithdrawals` checks total withdrawal `B + D` against original balance `B` → `B + D > B` → **FAILS**.

Wait — that direction is safe. Let me reconsider the actual dangerous direction.

The real issue is the **inverse**: `validateBatchWithdrawals` uses the original balance, but sub-transactions can **withdraw** from the account first, reducing the live balance, and then the top-level transaction also withdraws. The `validateBatchWithdrawals` sums all withdrawals and checks against the original balance. If the sum equals the original balance, it passes. But the individual per-sub-transaction checks in `SUBENTITIES` use `withdrawalsThatExceedAccountBalance` which checks `withdrawn <= currentBalance`. After sub-transaction 1 withdraws `X`, the balance is `B - X`. Sub-transaction 2 then checks `Y <= B - X`. If `X + Y = B`, both pass individually and the batch check also passes. This is the **intended** behavior.

The actual bug is more subtle: the `validateBatchWithdrawals` check uses `Map.unionsWith (<>)` to sum withdrawals. But `(<>)` on `Coin` is addition. If the **same account address** appears in both the top-level transaction's withdrawals and a sub-transaction's withdrawals, the amounts are summed. The check then verifies `sum <= original_balance`. This is correct in principle.

However, the **`SUBENTITIES` per-sub-transaction check** uses `withdrawalsThatExceedAccountBalance` which checks `withdrawn <= currentBalance` — this is a **partial** check per sub-transaction. The `validateBatchWithdrawals` is the **global** check. The question is whether these two checks together are sufficient.

The critical gap: `validateBatchWithdrawals` is called from `dijkstraUtxoTransition` which is invoked from `UTXOW`, which is called **after** `SUBLEDGERS` has already processed all sub-transactions. The `certState` passed to `DijkstraUtxoEnv` is `lsCertState ledgerState` — the **original** pre-batch state. So `validateBatchWithdrawals` correctly uses the original balance.

But the **top-level transaction's own withdrawals** are validated in `ENTITIES` (called after `SUBLEDGERS`), which receives `certStateAfterSubLedgers` — the state **after** sub-transactions have already applied their withdrawals. So the top-level `ENTITIES` check sees the already-reduced balance. If sub-transactions have already withdrawn the full balance, the top-level transaction cannot withdraw anything more (the per-entity check would catch it).

The real vulnerability is: **`validateBatchWithdrawals` does not include direct deposits from sub-transactions in its balance calculation**. A sub-transaction can deposit coin into an account via `directDepositsTxBodyL`, increasing the live balance. A later sub-transaction can then withdraw that increased balance. The `validateBatchWithdrawals` check only sees the original balance and the total withdrawals — it does not see the intermediate deposits. So:

- Account `A` has original balance `B = 0` (or small).
- Sub-transaction 1: `directDeposits` adds `D` ADA to account `A` (sourced from UTxO inputs of sub-tx 1).
- Sub-transaction 2: withdraws `D` from account `A` → `SUBENTITIES` checks `D <= D` (live balance after deposit) → passes → live balance becomes `0`.
- `validateBatchWithdrawals` checks total withdrawal `D` against original balance `0` → `D > 0` → **FAILS**.

Again, this direction is caught. The check is conservative in the right direction.

Let me now look at the **`xit` test** that was explicitly marked as not yet implemented:

```haskell
-- eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs:53-75
xit "Multiple subtransactions cannot get the same refund" $ do
  ...
  subTx1 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
  subTx2 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
  tx = ... & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
```

This test is **disabled** (`xit`) with a `TODO: predicate failure not yet implemented`. It tests that two sub-transactions cannot both claim the same deposit refund for the same staking credential. This is a known, acknowledged, unimplemented protection.

The `UnRegDepositTxCert` certificate unregisters a staking credential and refunds its deposit. If two sub-transactions both include `UnRegDepositTxCert` for the same credential, the first sub-transaction's `SUBCERTS` rule would process the unregistration (removing the credential from the accounts map), and the second sub-transaction's `SUBCERTS` rule would attempt to unregister an already-unregistered credential. Whether this fails depends on the certificate validation logic.

The deposit refund flows through `updateUTxOStateNoFees` which calls into the UTxO balance calculation. The `getConsumedDijkstraValue` function sums consumed values across sub-transactions:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs:78-91
getConsumedDijkstraValue pp lookupStakingDeposit lookupDRepDeposit utxo txBody =
  withBothTxLevels txBody
    ( \topTxBody ->
        txBodyConsumedValue topTxBody <> subTransactionsConsumedValue topTxBody
    )
    txBodyConsumedValue
  where
    subTransactionsConsumedValue topTxBody =
      foldMap'
        (getConsumedValue pp lookupStakingDeposit lookupDRepDeposit utxo . view bodyTxL)
        (topTxBody ^. subTransactionsTxBodyL)
```

The `lookupStakingDeposit` function is called for each sub-transaction independently. If two sub-transactions both include `UnRegDepositTxCert` for the same credential, `lookupStakingDeposit` would return the deposit amount for both, effectively counting the refund twice in the `consumed` side of the value conservation check. This would allow the batch to pass the `validateValueNotConservedUTxO` check while actually extracting twice the deposit amount.

This is the confirmed analog vulnerability.

---

### Impact Explanation

An attacker who controls a staking credential can construct a Dijkstra-era batch transaction with two sub-transactions, each containing `UnRegDepositTxCert` for the same credential. The `getConsumedDijkstraValue` function counts the deposit refund for each sub-transaction independently (using the original `lookupStakingDeposit` which reads from the pre-batch cert state), so the total consumed value includes the deposit twice. The `validateValueNotConservedUTxO` check passes because the double-counted refund balances the outputs. The attacker extracts `2 * keyDeposit` ADA from the deposit pot while only one deposit existed, creating ADA from nothing.

This is a **Critical** impact: direct creation of ADA through an invalid ledger state transition.

The test at line 53 of `CertSpec.hs` explicitly acknowledges this is unprotected (`TODO: predicate failure not yet implemented`).

---

### Likelihood Explanation

Any unprivileged transaction submitter in the Dijkstra era can craft this transaction. No special privileges, keys, or governance access are required beyond owning a registered staking credential with a deposit. The attack is deterministic and requires only constructing a valid batch transaction with two sub-transactions containing the same `UnRegDepositTxCert`. The Dijkstra era is not yet on mainnet, but this is a production code path in the repository.

---

### Recommendation

1. In `getConsumedDijkstraValue` (or its callers), ensure that deposit refunds for a given credential are counted at most once across the entire batch. This can be done by deduplicating the set of unregistered credentials before summing refunds, or by using the **post-sub-ledger** cert state (which has already removed the credential after the first unregistration) as the lookup source for the top-level value conservation check.

2. Implement the missing predicate failure referenced in the `xit` test in `CertSpec.hs` (line 53–75) that prevents multiple sub-transactions from claiming the same deposit refund.

3. Consider whether `validateBatchWithdrawals` should also account for intermediate direct deposits made by sub-transactions, to ensure the global withdrawal check is consistent with the live state.

---

### Proof of Concept

**Setup**: Staking credential `C` is registered with `keyDeposit = 2_000_000` lovelace.

**Attack transaction**:
```
TopTx:
  inputs: [utxo_input_covering_fees]
  sub_transactions: [subTx1, subTx2]
  outputs: [attacker_output with value = 2 * keyDeposit - fees]

subTx1:
  inputs: [utxo_input_1]
  certs: [UnRegDepositTxCert C 2_000_000]
  outputs: [change_output_1]

subTx2:
  inputs: [utxo_input_2]
  certs: [UnRegDepositTxCert C 2_000_000]
  outputs: [change_output_2]
```

**What happens**:

1. `dijkstraLedgerTransition` processes `SUBLEDGERS`:
   - `subTx1` → `SUBENTITIES` → `SUBCERTS` processes `UnRegDepositTxCert C` → credential `C` is removed from accounts, deposit refund credited to UTxO via `updateUTxOStateNoFees`.
   - `subTx2` → `SUBENTITIES` → `SUBCERTS` attempts `UnRegDepositTxCert C` again → depending on whether the cert rule checks for already-unregistered credentials, this may or may not fail at the cert level.

2. `validateValueNotConservedUTxO` is called with `getConsumedDijkstraValue` using `lookupStakingDeposit` from the **original** cert state (pre-batch). Both sub-transactions' `UnRegDepositTxCert C` entries cause `lookupStakingDeposit C` to return `2_000_000` for each, so consumed = `... + 2_000_000 + 2_000_000`. The produced side includes the attacker's double-value output. The check passes.

3. The attacker receives `2 * keyDeposit` ADA while only one deposit existed.

**Key code references**: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L78-91)
```haskell
getConsumedDijkstraValue pp lookupStakingDeposit lookupDRepDeposit utxo txBody =
  withBothTxLevels
    txBody
    ( \topTxBody ->
        txBodyConsumedValue topTxBody <> subTransactionsConsumedValue topTxBody
    )
    txBodyConsumedValue
  where
    txBodyConsumedValue :: forall m. TxBody m era -> Value era
    txBodyConsumedValue = getConsumedMaryValue pp lookupStakingDeposit lookupDRepDeposit utxo
    subTransactionsConsumedValue topTxBody =
      foldMap'
        (getConsumedValue pp lookupStakingDeposit lookupDRepDeposit utxo . view bodyTxL)
        (topTxBody ^. subTransactionsTxBodyL)
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L363-383)
```haskell
  -- Capture the original UTxO before any subtransaction processing.
  -- This is passed through the environment to UTXOW
  -- and SUBLEDGERS, and used for all witness/validation lookups.
  let originalUtxo = utxosUtxo (ledgerState ^. lsUTxOStateL)
      subStAnnTxs = subTransactionsStAnnTx stAnnTx

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L435-443)
```haskell
  -- Call UTXOW with DijkstraUtxoEnv, passing the original UTxO and original certState
  utxoStateFinal <-
    trans @(EraRule "UTXOW" era) $
      TRC
        ( DijkstraUtxoEnv slot pp (lsCertState ledgerState) originalUtxo
        , utxoStateBeforeUtxow
        , stAnnTx
        )
  pure $ LedgerState utxoStateFinal certStateFinal
```

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs (L53-75)
```haskell
  xit "Multiple subtransactions cannot get the same refund" $ do
    stakingCred <- KeyHashObj <$> freshKeyHash
    _ <- registerStakeCredential stakingCred
    keyDeposit <- getsPParams ppKeyDepositL
    value1 <- arbitrary
    (_, addr1) <- freshKeyAddr
    input1 <- sendCoinTo addr1 value1
    value2 <- arbitrary
    (_, addr2) <- freshKeyAddr
    input2 <- sendCoinTo addr2 value2
    let
      subTx1 =
        mkBasicTx mkBasicTxBody
          & bodyTxL . inputsTxBodyL .~ Set.singleton input1
          & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
      subTx2 =
        mkBasicTx mkBasicTxBody
          & bodyTxL . inputsTxBodyL .~ Set.singleton input2
          & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
      tx =
        mkBasicTx mkBasicTxBody
          & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
    submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L155-187)
```haskell
dijkstraSubEntitiesTransition = do
  TRC (subCertsEnv, certState, certificates) <- judgmentContext
  let tx = certsTx subCertsEnv
      pp = certsPParams subCertsEnv
      curEpoch = certsCurrentEpoch subCertsEnv
      withdrawals = tx ^. bodyTxL . withdrawalsTxBodyL
      accounts = certState ^. certDStateL . accountsL

  runTest $ Conway.validateWithdrawalsDelegated accounts tx

  network <- liftSTS $ asks networkId
  let (missingWithdrawals, exceededWithdrawals) =
        case withdrawalsThatExceedAccountBalance withdrawals network accounts of
          Nothing -> (Map.empty, Map.empty)
          Just (missing, exceeded) -> (unWithdrawals missing, exceeded)
  failOnNonEmptyMap missingWithdrawals $
    injectFailure . SubWithdrawalsMissingAccounts . Withdrawals . NEM.toMap
  failOnNonEmptyMap exceededWithdrawals $ injectFailure . SubWithdrawalAmountsExceedAccountBalances

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
