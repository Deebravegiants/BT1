### Title
Double Deposit Refund via Duplicate Sub-Transaction Certificates in Dijkstra Era — (`eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs`, `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs`)

---

### Summary

The Dijkstra era introduces nested sub-transactions (`subTransactionsTxBodyL`). A transaction author can include multiple sub-transactions that each contain an `UnRegDepositTxCert` for the **same** stake credential, claiming the same deposit refund more than once. The predicate failure that should prevent this has not been implemented. An unprivileged transaction sender can exploit this to receive more ADA in refunds than they originally deposited, directly creating ADA from nothing.

---

### Finding Description

The Dijkstra era adds sub-transaction support. Each sub-transaction is processed independently through the `DELEG` rule. The function `dijkstraTotalRefundsTxCerts` in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs` computes the total refund for a set of certificates by simply summing all `UnRegDepositTxCert` and `UnRegDRepTxCert` deposit values:

```haskell
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit
  UnRegDRepTxCert _ deposit -> deposit
  _ -> zero
``` [1](#0-0) 

This function is used as the `getTotalRefundsTxCerts` implementation for `DijkstraEra`: [2](#0-1) 

There is no cross-sub-transaction deduplication check. The developers themselves have acknowledged this gap with a disabled (`xit`) test that explicitly states the predicate failure is not yet implemented:

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
  ...
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
``` [3](#0-2) 

The test constructs two sub-transactions (`subTx1`, `subTx2`) that both contain `UnRegDepositTxCert stakingCred keyDeposit` for the **same** credential, wraps them in a top-level transaction, and expects the transaction to be rejected — but the rejection logic does not exist yet. [4](#0-3) 

---

### Impact Explanation

**Critical — Direct creation of ADA through an invalid ledger state transition.**

An attacker who registers a stake credential (paying `keyDeposit`) can submit a top-level transaction containing N sub-transactions each claiming `UnRegDepositTxCert stakingCred keyDeposit`. Without the missing predicate check, the ledger would credit N × `keyDeposit` in refunds while only one deposit was ever paid. This constitutes direct ADA creation from nothing, violating the preservation-of-value invariant that is fundamental to the Cardano ledger.

The `returnProposalDeposits` and deposit accounting in the `EPOCH` rule rely on `utxosDepositedL` being accurate: [5](#0-4) 

Overclaiming refunds would cause `utxosDeposited` to go negative or diverge from the actual deposit pot, corrupting ledger accounting permanently.

---

### Likelihood Explanation

**High.** The attack requires no privileged access, no governance participation, no leaked keys, and no external dependencies. Any transaction sender who has registered a stake credential can construct the malicious transaction. The `xit` annotation and `TODO` comment confirm the developers are aware the protection is absent. The only current barrier is that the Dijkstra era has not yet been deployed on mainnet, but the production code is present in the repository and the check is missing.

---

### Recommendation

Before the Dijkstra era is deployed, implement a cross-sub-transaction deduplication check in the sub-transaction processing logic. Specifically:

1. Track which stake credentials and DRep credentials have been unregistered across all sub-transactions within a single top-level transaction.
2. Reject any top-level transaction where the same credential appears in `UnRegDepositTxCert` or `UnRegDRepTxCert` in more than one sub-transaction.
3. Implement the corresponding `PredicateFailure` constructor (as noted by the `TODO` in the test) and enable the `xit` test.

The fix should be applied in the sub-transaction validation path before `dijkstraTotalRefundsTxCerts` is used to compute the balance equation. [1](#0-0) 

---

### Proof of Concept

1. Register stake credential `stakingCred` (pays `keyDeposit`).
2. Construct `subTx1` containing `UnRegDepositTxCert stakingCred keyDeposit` spending `input1`.
3. Construct `subTx2` containing `UnRegDepositTxCert stakingCred keyDeposit` spending `input2`.
4. Submit top-level transaction:
   ```haskell
   tx = mkBasicTx mkBasicTxBody
     & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
   ```
5. Without the missing predicate check, the ledger credits `2 × keyDeposit` in refunds while only `1 × keyDeposit` was deposited.

This exact scenario is documented in the disabled test at: [3](#0-2)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs (L229-238)
```haskell
dijkstraTotalRefundsTxCerts ::
  ( Foldable f
  , ConwayEraTxCert era
  ) =>
  f (TxCert era) ->
  Coin
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit
  UnRegDRepTxCert _ deposit -> deposit
  _ -> zero
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs (L285-285)
```haskell
  getTotalRefundsTxCerts _ _ _ = dijkstraTotalRefundsTxCerts
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L351-353)
```haskell
    utxoState2 =
      utxoState1
        & utxosDepositedL .~ totalObligation certState2 govState1
```
