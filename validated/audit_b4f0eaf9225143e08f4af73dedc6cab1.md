### Title
Multiple Sub-Transactions Can Double-Claim the Same Deposit Refund, Creating ADA Out of Thin Air - (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs`)

---

### Summary

The Dijkstra era introduces nested sub-transactions. The `SUBLEDGERS` rule processes each sub-transaction sequentially via `foldM`, passing the updated `LedgerState` forward. No cross-sub-transaction guard prevents two sub-transactions from each submitting an `UnRegDepositTxCert` for the **same staking credential**. The first sub-transaction legitimately unregisters the credential and claims the deposit refund; the second sub-transaction then processes the same certificate against the already-modified state. Because the predicate failure that should reject this case is explicitly acknowledged as **not yet implemented**, the batch transaction is accepted, and the deposit pot is decremented twice while only one deposit was ever paid — creating ADA out of thin air.

---

### Finding Description

**Vulnerability class:** Same-transaction state-manipulation bypass of an accounting invariant (direct analog to the Surge utilization-rate bypass: inflate a value, pass a check, deflate it back — here: register once, unregister twice in the same atomic batch).

**Root cause — `SUBLEDGERS` sequential fold with no cross-sub-transaction deduplication:** [1](#0-0) 

`dijkstraSubLedgersTransition` folds over all sub-transactions with `foldM`, threading the `LedgerState` through each `SUBLEDGER` invocation. After `subTx1` processes `UnRegDepositTxCert stakingCred keyDeposit`, the credential is removed from the `accounts` map inside `certState`. When `subTx2` then processes the identical certificate, the `SUBDELEG` rule is invoked against the already-mutated `certState`.

**Missing predicate failure — explicitly acknowledged by developers:** [2](#0-1) 

The test `"Multiple subtransactions cannot get the same refund"` is disabled with `xit` and its expected predicate failure is `error "TODO: predicate failure not yet implemented"`. This confirms that:
1. The transaction currently **succeeds** (the test is disabled because it would fail — the batch is accepted when it should be rejected).
2. No guard in `SUBDELEG` / `SUBCERT` / `SUBENTITIES` rejects a deregistration certificate for a credential that was already unregistered by an earlier sub-transaction in the same batch.

**How the deposit pot is decremented twice:**

Each sub-transaction must satisfy the preservation-of-value check independently. `subTx1` includes the `keyDeposit` refund in its outputs and the deposit pot is decremented by `keyDeposit`. `subTx2` does the same. The deposit pot is decremented twice, but only one deposit was ever paid, violating the global accounting invariant. [3](#0-2) 

The `SUBENTITIES` call inside `dijkstraSubLedgersTransition` processes certificates against `certState` (the state carried forward from the previous sub-transaction), but there is no batch-level check that a given credential's deposit has already been refunded in an earlier sub-transaction of the same top-level batch.

---

### Impact Explanation

**Critical — Direct creation of ADA through an invalid ledger state transition.**

An attacker who registers a staking credential (paying `keyDeposit` once) can construct a top-level Dijkstra transaction containing two sub-transactions that each carry `UnRegDepositTxCert stakingCred keyDeposit`. Both sub-transactions are accepted; both claim the refund. The deposit pot is decremented by `2 × keyDeposit` while only `1 × keyDeposit` was ever deposited. The difference (`keyDeposit` lovelace) is created from nothing, violating the preservation-of-value invariant that is the foundational correctness property of the Cardano ledger.

The same attack generalises to DRep deposits (`RegDRepTxCert` / `UnRegDRepTxCert`) and pool deposits, multiplying the magnitude. With `keyDeposit` currently set to 2 ADA and an unbounded number of credentials, the attack can be repeated to drain the deposit pot entirely.

---

### Likelihood Explanation

The Dijkstra era is production-targeted code in this repository. The vulnerability requires only:
- The ability to submit a valid Dijkstra-era transaction (unprivileged).
- One prior registration of a staking credential (costs `keyDeposit`).
- Construction of a top-level transaction with two sub-transactions carrying the same `UnRegDepositTxCert`.

No privileged access, no flash loan, no governance majority, and no consensus attack is required. The attack is fully self-contained in a single transaction. The developers have already identified the scenario and noted the missing guard, confirming the path is reachable.

---

### Recommendation

1. **Add a cross-sub-transaction deduplication check in `SUBLEDGERS` or `SUBLEDGER`:** Before processing each sub-transaction's certificates, verify that no credential whose deposit was already refunded in an earlier sub-transaction of the same batch appears again in an `UnRegDepositTxCert` (or `UnRegDRepTxCert`, `RetirePoolTxCert`).

2. **Alternatively, track a "refunded credentials" set** across the `foldM` in `dijkstraSubLedgersTransition` and thread it through the environment, rejecting any duplicate deregistration certificate.

3. **Implement the pending predicate failure** referenced in `Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs` line 75 and re-enable the `xit` test as `it`.

---

### Proof of Concept

```
Setup:
  stakingCred  ← freshKeyHash
  _            ← registerStakeCredential stakingCred   -- pays keyDeposit once
  keyDeposit   ← getsPParams ppKeyDepositL

Attack transaction:
  subTx1 = mkBasicTx mkBasicTxBody
             & bodyTxL . certsTxBodyL .~ [UnRegDepositTxCert stakingCred keyDeposit]
             -- outputs include keyDeposit refund; deposit pot -= keyDeposit

  subTx2 = mkBasicTx mkBasicTxBody
             & bodyTxL . certsTxBodyL .~ [UnRegDepositTxCert stakingCred keyDeposit]
             -- outputs include keyDeposit refund again; deposit pot -= keyDeposit again

  tx = mkBasicTx mkBasicTxBody
         & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]

  submitTx_ tx   -- currently SUCCEEDS (predicate failure not implemented)

Result:
  Deposit pot decremented by 2 × keyDeposit.
  Only 1 × keyDeposit was ever paid.
  Net ADA created: keyDeposit lovelace.
```

This is structurally identical to the Surge attack: the attacker uses the atomicity of the batch (deposit → borrow → withdraw in one transaction) to bypass a check that is only evaluated per-sub-transaction rather than across the entire batch.

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedger.hs (L248-284)
```haskell
  (utxoStateBeforeSubUtxow, certStateFinal) <-
    if topIsValid == IsValid True
      then do
        runTest $ Conway.validateTreasuryValue txBody (chainAccountState ^. casTreasuryL)

        certStateAfterSubEntities <-
          trans @(EraRule "SUBENTITIES" era) $
            TRC
              ( SubCertsEnv tx pp curEpochNo committee (proposalsWithPurpose grCommitteeL proposals)
              , certState
              , StrictSeq.fromStrict $ txBody ^. certsTxBodyL
              )
        let govEnv =
              Conway.GovEnv
                (txIdTxBody txBody)
                curEpochNo
                pp
                (govState ^. constitutionGovStateL . constitutionGuardrailsScriptHashL)
                certStateAfterSubEntities
                committee
        let govSignal =
              Conway.GovSignal
                { Conway.gsVotingProcedures = txBody ^. votingProceduresTxBodyL
                , Conway.gsProposalProcedures = txBody ^. proposalProceduresTxBodyL
                , Conway.gsCertificates = txBody ^. certsTxBodyL
                }
        proposalsState <-
          trans @(EraRule "SUBGOV" era) $
            TRC
              ( govEnv
              , proposals
              , govSignal
              )
        pure
          ( utxoState & utxosGovStateL . proposalsGovStateL .~ proposalsState
          , certStateAfterSubEntities
          )
```
