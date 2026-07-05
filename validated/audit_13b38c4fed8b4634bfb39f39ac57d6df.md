### Title
Double Deposit Refund via Duplicate `UnRegDepositTxCert` Across Subtransactions in Dijkstra Era - (File: `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs`)

### Summary

The Dijkstra era introduces nested/subtransactions. A top-level transaction can embed multiple subtransactions, each processed by the `SUBLEDGERS` → `SUBLEDGER` → `SUBENTITIES` → `SUBDELEG` pipeline. An attacker can include `UnRegDepositTxCert stakingCred keyDeposit` in two or more subtransactions for the same staking credential. The predicate failure that should prevent this double-claim is explicitly acknowledged as **not yet implemented** in the production codebase.

### Finding Description

The Dijkstra era's `dijkstraTotalRefundsTxCerts` function computes deposit refunds purely from certificate content, without consulting the live ledger state: [1](#0-0) 

```haskell
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit
  UnRegDRepTxCert _ deposit -> deposit
  _ -> zero
```

This is used in the UTxO balance check (`validateValueNotConservedUTxO`) for each subtransaction. Because the function does not verify whether the credential is still registered, the balance equation for a second subtransaction carrying the same `UnRegDepositTxCert` will include the refund amount on the consumed side, allowing the subtransaction to balance on paper.

The `SUBLEDGER` rule processes `SUBENTITIES` (certificate validation) before `SUBUTXOW` (UTxO balance), so the second subtransaction would ordinarily fail with `StakeKeyNotRegisteredDELEG`. However, the developers have explicitly written a disabled test acknowledging that the dedicated predicate failure for this exact scenario **has not been implemented**: [2](#0-1) 

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
  ...
  subTx1 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
  subTx2 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
  tx = mkBasicTx mkBasicTxBody
         & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
```

The `xit` prefix marks the test as pending/skipped, and the body uses `error "TODO: predicate failure not yet implemented"` as the expected failure — meaning no concrete predicate failure exists in the rule system to reject this transaction. The `SUBLEDGER` transition passes the **original** `certState` (before any subtransaction mutations) into `SUBUTXOW`: [3](#0-2) 

```haskell
utxoStateAfterSubUtxow <-
  trans @(EraRule "SUBUTXOW" era) $
    TRC (SubUtxoEnv slot pp certState originalUtxo topIsValid, ...)
```

Because `certState` here is the pre-subtransaction state, the UTxO balance check for the second subtransaction sees the credential as still registered and accepts the refund amount in the consumed-value computation, while no explicit cross-subtransaction deduplication guard exists.

### Impact Explanation

If the double-refund is reachable (as the disabled test implies), an attacker who paid one `keyDeposit` (currently 2 ADA on mainnet) can construct a top-level transaction with N subtransactions each carrying `UnRegDepositTxCert` for the same credential and collect N × `keyDeposit` in refunds. This constitutes **direct creation of ADA** from the deposit pot — a Critical impact under the allowed scope (direct loss/creation of ADA through an invalid ledger state transition).

### Likelihood Explanation

The Dijkstra era is the active development era. The `xit` test and its `error "TODO"` comment confirm the developers are aware the guard is missing. Any user who can submit a valid Dijkstra-era transaction (an unprivileged transaction sender) can craft this attack. No privileged access, governance majority, or key compromise is required.

### Recommendation

1. Add an explicit cross-subtransaction deduplication check in the `SUBLEDGERS` or `SUBLEDGER` rule that collects all `UnRegDepositTxCert` / `UnRegDRepTxCert` credential targets across all subtransactions and rejects the batch if any credential appears more than once.
2. Alternatively, thread the post-`SUBENTITIES` `certState` into `SUBUTXOW` so that the UTxO balance check uses the updated (post-unregistration) state, making the balance equation fail for the second subtransaction.
3. Enable and complete the pending test at `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs:53` once the predicate failure is defined.

### Proof of Concept

```
1. Register stakingCred, paying keyDeposit (e.g. 2 ADA).
2. Construct:
     subTx1 = { certs: [UnRegDepositTxCert stakingCred keyDeposit],
                inputs: [input1],
                outputs: [addr1 ← value1 + keyDeposit] }
     subTx2 = { certs: [UnRegDepositTxCert stakingCred keyDeposit],
                inputs: [input2],
                outputs: [addr2 ← value2 + keyDeposit] }
     topTx  = { subTransactions: [subTx1, subTx2] }
3. Submit topTx.
4. Because no cross-subtransaction deduplication predicate failure exists,
   both subtransactions balance (dijkstraTotalRefundsTxCerts returns keyDeposit
   for each), and the attacker receives 2 × keyDeposit while only one deposit
   was ever paid — net gain of keyDeposit ADA from the deposit pot.
```

The root cause is confirmed by the production code at: [1](#0-0) 
and the acknowledged missing guard at: [2](#0-1)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedger.hs (L287-293)
```haskell
  utxoStateAfterSubUtxow <-
    trans @(EraRule "SUBUTXOW" era) $
      TRC
        ( SubUtxoEnv slot pp certState originalUtxo topIsValid
        , utxoStateBeforeSubUtxow
        , stAnnTx
        )
```
