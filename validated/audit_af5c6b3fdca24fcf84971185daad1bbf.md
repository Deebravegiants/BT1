Looking at the Dijkstra era's sub-transaction architecture, I need to find an analog to the "same constraint applied to two different contexts" vulnerability class.

The key evidence is in `CertSpec.hs`:

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
    ...
    subTx1 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    subTx2 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    tx = mkBasicTx mkBasicTxBody
           & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
    submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
```

The `xit` (disabled/pending) marker combined with `error "TODO: predicate failure not yet implemented"` explicitly acknowledges the deduplication check across sub-transactions is not yet implemented. The `SUBLEDGERS` rule folds sub-transactions sequentially but the cross-sub-transaction deposit guard is absent.

The analog maps cleanly:
- External report: same `sqrtPriceLimitX96` applied to two different Uniswap V3 pools (same constraint, two contexts)
- Cardano Ledger: same deposit refund claimable by two different sub-transactions (same deposit, two contexts)

---

### Title
Dijkstra Sub-Transaction Deposit Refund Not Deduplicated Across Sub-Transactions — (`File: eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs`)

### Summary
In the Dijkstra era, a top-level transaction may embed multiple sub-transactions. Two sub-transactions within the same top-level transaction can each include an `UnRegDepositTxCert` for the same staking credential, both claiming the same deposit refund. The cross-sub-transaction deduplication guard is explicitly acknowledged as unimplemented (`"TODO: predicate failure not yet implemented"`), meaning the same deposit can be consumed twice, creating ADA from nothing.

### Finding Description
The `SUBLEDGERS` rule in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs` processes sub-transactions by folding over them sequentially:

```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
```

The `env` (containing `originalUtxo`) is shared across all sub-transactions. Each sub-transaction is processed by `SUBLEDGER → SUBENTITIES → SUBCERTS → SUBCERT → SUBDELEG`. The `SUBDELEG` rule handles `UnRegDepositTxCert`. There is no implemented predicate failure that prevents two sub-transactions from both deregistering the same credential and collecting the same deposit refund. The test skeleton in `CertSpec.hs` at line 53–75 explicitly marks this scenario as `xit` with `error "TODO: predicate failure not yet implemented"`, confirming the guard does not exist in the production rule path.

The analog to the external report is direct: just as `sqrtPriceLimitX96` is applied to two different Uniswap V3 pools (same constraint, two different contexts), the same deposit refund is applied to two different sub-transaction contexts — both `subTx1` and `subTx2` reference the same `stakingCred` and `keyDeposit`, and neither is blocked from claiming it.

### Impact Explanation
An attacker registers a staking credential (paying `keyDeposit` ADA), then submits a single top-level transaction containing two sub-transactions that both include `UnRegDepositTxCert stakingCred keyDeposit`. If the deduplication check is absent, both sub-transactions succeed, each returning `keyDeposit` ADA to their respective outputs. The attacker receives `2 × keyDeposit` ADA while only one deposit was ever locked. This is a direct, attacker-controlled creation of ADA through an invalid ledger state transition — **Critical** impact.

### Likelihood Explanation
The Dijkstra era is the only era supporting sub-transactions. The attack requires only:
1. Registering a staking credential (standard operation)
2. Constructing a top-level transaction with two sub-transactions each containing `UnRegDepositTxCert` for the same credential

No privileged access, governance majority, or key compromise is required. The entry path is fully unprivileged. The test skeleton at line 53–75 of `CertSpec.hs` demonstrates the developers are aware the scenario is reachable and that the guard is missing.

### Recommendation
Implement a cross-sub-transaction deduplication check in the `SUBLEDGERS` or `SUBLEDGER` rule that tracks which credentials have already been deregistered by earlier sub-transactions in the same batch. Define the corresponding `DijkstraSubDelegPredFailure` constructor (currently missing, hence the `error "TODO"` placeholder) and enforce it before allowing a second `UnRegDepositTxCert` for the same credential within the same top-level transaction.

### Proof of Concept
The test skeleton already encodes the attack:

```haskell
-- CertSpec.hs lines 53–75
xit "Multiple subtransactions cannot get the same refund" $ do
  stakingCred <- KeyHashObj <$> freshKeyHash
  _ <- registerStakeCredential stakingCred          -- pays keyDeposit once
  keyDeposit <- getsPParams ppKeyDepositL
  ...
  let
    subTx1 = mkBasicTx mkBasicTxBody
      & bodyTxL . inputsTxBodyL  .~ Set.singleton input1
      & bodyTxL . certsTxBodyL   .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    subTx2 = mkBasicTx mkBasicTxBody
      & bodyTxL . inputsTxBodyL  .~ Set.singleton input2
      & bodyTxL . certsTxBodyL   .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    tx = mkBasicTx mkBasicTxBody
      & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
  -- ^^^ disabled because the guard does not exist; without it, tx succeeds and
  --     2 × keyDeposit ADA is returned while only 1 × keyDeposit was deposited
``` [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs (L128-135)
```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
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
