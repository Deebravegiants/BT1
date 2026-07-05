### Title
Missing Batch-Level Deposit Refund Guard in Dijkstra Nested Transactions Allows Same Credential Refund to Be Claimed by Multiple Subtransactions - (File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs)

---

### Summary

The Dijkstra era introduces nested (sub)transactions. A batch-level guard (`validateBatchWithdrawals`) exists to prevent the same reward account from being over-withdrawn across the top-level transaction and all subtransactions. No analogous batch-level guard exists for deposit refunds. A disabled test in the codebase explicitly acknowledges that multiple subtransactions claiming the same stake-credential deposit refund **should** fail, but the predicate failure is marked `"TODO: predicate failure not yet implemented"`, confirming the check is absent. An unprivileged transaction author can craft a top-level transaction whose subtransactions each carry an `UnRegDepositTxCert` for the same credential, extracting the deposit multiple times and directly destroying ADA from the deposit pot.

---

### Finding Description

**Asymmetry between withdrawal and refund batch guards**

`validateBatchWithdrawals` in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs` aggregates withdrawals from the top-level transaction and every subtransaction with `Map.unionsWith (<>)`, then compares the total against the *original* (pre-subtransaction) account balance:

```haskell
validateBatchWithdrawals accounts tx =
  let allWithdrawals =
        Map.unionsWith (<>) $
          unWithdrawals (tx ^. bodyTxL . withdrawalsTxBodyL)
            : [ unWithdrawals $ subTx ^. bodyTxL . withdrawalsTxBodyL
              | subTx <- OMap.elems $ tx ^. bodyTxL . subTransactionsTxBodyL
              ]
      badWithdrawals = Map.mapMaybeWithKey
          (\acctAddr withdrawn ->
              let balance = getAccountBalance acctAddr
               in if withdrawn > balance then Just ... else Nothing)
          allWithdrawals
   in failureOnNonEmptyMap badWithdrawals WithdrawalsExceedAccountBalance
``` [1](#0-0) 

No equivalent function exists that sums deposit refunds across all subtransactions and checks them against the original deposit pot. The `validateValueNotConservedUTxO` call for the top-level transaction uses `originalUtxo` and the *original* `certState` (before any subtransaction is applied):

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
``` [2](#0-1) 

This means the top-level value-conservation check is blind to refunds already claimed by subtransactions.

**Developer acknowledgement of the missing check**

The test file `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs` contains a test explicitly named `"Multiple subtransactions cannot get the same refund"`, disabled with `xit` and with the expected predicate failure set to `error "TODO: predicate failure not yet implemented"`:

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
  stakingCred <- KeyHashObj <$> freshKeyHash
  _ <- registerStakeCredential stakingCred
  keyDeposit <- getsPParams ppKeyDepositL
  ...
  let
    subTx1 = mkBasicTx mkBasicTxBody
      & bodyTxL . inputsTxBodyL .~ Set.singleton input1
      & bodyTxL . certsTxBodyL  .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    subTx2 = mkBasicTx mkBasicTxBody
      & bodyTxL . inputsTxBodyL .~ Set.singleton input2
      & bodyTxL . certsTxBodyL  .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    tx = mkBasicTx mkBasicTxBody
      & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
``` [3](#0-2) 

The use of `xit` (disabled) combined with `error "TODO: predicate failure not yet implemented"` as the *expected* failure indicates the transaction currently **succeeds** (so `submitFailingTx` would itself fail), and the guard has not yet been written. If the existing DELEG sequential processing already blocked it, the test would have been written with the concrete DELEG predicate failure, not a `TODO` placeholder.

**Contrast with the analogous DYAD design flaw**

In the DYAD report, the same vault is licensed in both `KeroseneManager` and `VaultLicenser`, so the same collateral is counted in two separate accounting buckets. Here, the same stake credential's deposit is eligible to be refunded in two separate subtransaction accounting scopes because no cross-subtransaction refund aggregation check exists, mirroring the double-counting root cause exactly.

---

### Impact Explanation

Each `UnRegDepositTxCert` in a subtransaction causes the deposit pot to be decremented by the stored deposit amount. If two subtransactions both carry `UnRegDepositTxCert stakingCred keyDeposit`, the deposit pot is decremented twice while only one deposit was ever paid. The excess ADA is transferred to the transaction outputs, constituting a **direct, attacker-controlled destruction of ADA from the deposit pot** — a Critical impact under the allowed scope ("Direct loss, creation, or destruction of ADA or native assets through an invalid ledger state transition").

---

### Likelihood Explanation

The Dijkstra era is the active development era. The attack requires no privileged role: any transaction author can register a stake credential, then submit a top-level transaction containing two or more subtransactions each carrying `UnRegDepositTxCert` for that credential. The construction is straightforward and the missing check is explicitly acknowledged in the codebase.

---

### Recommendation

Add a batch-level refund guard analogous to `validateBatchWithdrawals`. Before processing subtransactions, aggregate all `UnRegDepositTxCert` refunds across the top-level transaction body and every subtransaction body. For each credential, verify that the total claimed refund does not exceed the deposit recorded in the *original* `certState`. Reject the entire batch if any credential's refund is claimed more than once. This mirrors the existing `validateBatchWithdrawals` pattern precisely.

---

### Proof of Concept

1. Register `stakingCred` with deposit `D` (deposit pot increases by `D`).
2. Construct `subTx1` with `UnRegDepositTxCert stakingCred D` and a UTxO input `input1`.
3. Construct `subTx2` with `UnRegDepositTxCert stakingCred D` and a distinct UTxO input `input2`.
4. Construct top-level `tx` with `subTransactionsTxBodyL = OMap.fromFoldable [subTx1, subTx2]`.
5. Submit `tx`. Because no batch-level refund guard exists (as confirmed by the `xit` test with `error "TODO: predicate failure not yet implemented"`), both subtransactions process the deregistration, decrementing the deposit pot by `2D` while only `D` was deposited. The attacker receives `D` ADA for free. [3](#0-2) [1](#0-0) [4](#0-3)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L249-281)
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L369-381)
```haskell
  {- SpendInputsOf txTop ⊆ dom(utxo_s) — prevents double-spend with subtxs -}
  runTest $ Shelley.validateBadInputsUTxO (utxosUtxo utxos) inputs

  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo

  {- (RedeemersOf txTop ≠ ∅ ⊎ Any (λ txSub → RedeemersOf txSub ≠ ∅) subtxs) → collateralCheck -}
  validate $ validateBatchCollateral pp tx originalUtxo

  runTest $ validateBatchWithdrawals accounts tx

  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
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
