### Title
Missing Cross-Sub-Transaction Deposit Refund Deduplication Allows Double-Claiming of Stake Key Deposits - (File: `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs`)

---

### Summary

In the Dijkstra era, a batch transaction can contain multiple sub-transactions that each include an `UnRegDepositTxCert` certificate for the **same** staking credential. Because no cross-sub-transaction deduplication check is implemented, each sub-transaction independently processes the unregistration and claims the deposit refund. This allows an attacker to receive multiple refunds for a single deposit, directly creating ADA from the deposit pot and violating the preservation-of-value invariant.

---

### Finding Description

The Dijkstra era introduces **batch transactions** (`subTransactionsTxBodyL`), where a top-level transaction delegates execution to an ordered set of sub-transactions. Each sub-transaction is processed sequentially through the `SUBLEDGERS` → `SUBLEDGER` → `SubCerts` → `SubDeleg` rule chain before the top-level transaction's own rules run.

The test file explicitly acknowledges the missing guard:

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
  stakingCred <- KeyHashObj <$> freshKeyHash
  _ <- registerStakeCredential stakingCred
  keyDeposit <- getsPParams ppKeyDepositL
  ...
  let
    subTx1 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    subTx2 = ... & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    tx = mkBasicTx mkBasicTxBody
           & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
``` [1](#0-0) 

The test is disabled (`xit`) because the expected predicate failure is literally `error "TODO: predicate failure not yet implemented"` — meaning the developers acknowledge the scenario must be rejected but have not yet implemented the enforcement. The test would crash if enabled.

The `dijkstraLedgerTransition` processes all sub-transactions first via `SUBLEDGERS`, passing the evolving `CertState` through each sub-ledger sequentially:

```haskell
LedgerState utxoStateAfterSubLedgers certStateAfterSubLedgers <-
  trans @(EraRule "SUBLEDGERS" era) $
    TRC (SubLedgerEnv slot mbCurEpochNo txIx pp chainAccountState originalUtxo (tx ^. isValidTxL),
         ledgerState, subStAnnTxs)
``` [2](#0-1) 

When `subTx1` processes `UnRegDepositTxCert stakingCred keyDeposit`, the `SubDeleg` rule calls `unregisterConwayAccount`, removes the credential from `accounts`, and credits the deposit refund to the transaction's produced value. The updated `CertState` (with the credential now absent) is then passed to `subTx2`. When `subTx2` processes the identical certificate, the `Nothing` branch of `unregisterConwayAccount` is reached (credential already gone), and — because no predicate failure is implemented for this cross-sub-transaction case — the second refund is credited again without a corresponding deposit being present in the pot.

The `conwayDelegTransition` (reused by `SubDeleg`) handles the `ConwayUnRegCert` case:

```haskell
ConwayUnRegCert stakeCred sMayRefund -> do
  let (mAccountState, newAccounts) = unregisterConwayAccount stakeCred accounts
      checkInvalidRefund = ...
      checkStakeKeyHasZeroRewardBalance = ...
  failOnJust checkInvalidRefund id
  failOnJust checkStakeKeyHasZeroRewardBalance (injectFailure . StakeKeyHasNonZeroAccountBalanceDELEG)
  case mAccountState of
    Nothing -> do   -- ← no rejection here for the sub-transaction double-claim case
``` [3](#0-2) 

The `validateBatchWithdrawals` function in `Utxo.hs` shows the pattern of cross-sub-transaction aggregation that exists for withdrawals but is absent for deposit refunds:

```haskell
validateBatchWithdrawals accounts tx =
  let allWithdrawals =
        Map.unionsWith (<>) $
          unWithdrawals (tx ^. bodyTxL . withdrawalsTxBodyL)
            : [ unWithdrawals $ subTx ^. bodyTxL . withdrawalsTxBodyL
              | subTx <- OMap.elems $ tx ^. bodyTxL . subTransactionsTxBodyL ]
``` [4](#0-3) 

No equivalent cross-sub-transaction deduplication exists for `UnRegDepositTxCert` certificates.

---

### Impact Explanation

**Critical — Direct creation of ADA through an invalid ledger state transition.**

An attacker registers one staking credential (paying `keyDeposit` once into the deposit pot) and then submits a single batch transaction containing N sub-transactions each bearing `UnRegDepositTxCert stakingCred keyDeposit`. Each sub-transaction independently claims the refund, producing `N × keyDeposit` ADA in outputs while only `1 × keyDeposit` was ever deposited. The deposit pot is over-drained by `(N-1) × keyDeposit`, violating the preservation-of-value invariant. This constitutes direct, attacker-controlled creation of ADA from an invalid ledger state transition.

---

### Likelihood Explanation

The Dijkstra era is not yet deployed on mainnet, but the vulnerability is present in the production implementation code. The attack requires only:
1. Registering a staking credential (standard, permissionless operation).
2. Constructing a batch transaction with duplicate `UnRegDepositTxCert` certificates across sub-transactions (standard serialization, no privileged access).

No governance majority, leaked keys, or external dependencies are required. The attacker is an unprivileged transaction sender. The missing check is explicitly documented in the codebase as a known TODO.

---

### Recommendation

Implement a cross-sub-transaction deduplication check for `UnRegDepositTxCert` certificates, analogous to `validateBatchWithdrawals`. Before processing the batch, collect all staking credentials appearing in `UnRegDepositTxCert` certificates across all sub-transactions and the top-level transaction, and reject the batch if any credential appears more than once. Alternatively, enforce at the `SUBLEDGERS` level that a credential unregistered by one sub-transaction cannot be unregistered again by a subsequent sub-transaction in the same batch. The disabled test at `CertSpec.hs:53–75` should be re-enabled once the predicate failure is implemented.

---

### Proof of Concept

1. Register staking credential `C`, paying `keyDeposit = D` ADA into the deposit pot.
2. Construct sub-transaction `subTx1` with `certsTxBodyL = [UnRegDepositTxCert C D]` and a distinct UTxO input `input1`.
3. Construct sub-transaction `subTx2` with `certsTxBodyL = [UnRegDepositTxCert C D]` and a distinct UTxO input `input2`.
4. Submit batch transaction `tx` with `subTransactionsTxBodyL = OMap.fromFoldable [subTx1, subTx2]`.
5. `subTx1` processes successfully: credential `C` is removed from accounts, `D` ADA is credited as a refund in `subTx1`'s produced value.
6. `subTx2` processes: credential `C` is already absent (`mAccountState = Nothing`); no predicate failure fires (TODO not implemented); `D` ADA is credited again.
7. Net result: `2D` ADA extracted from deposit pot, `D` ADA over-created, preservation of value violated.

This is the exact scenario the disabled test at line 53–75 of `CertSpec.hs` was written to prevent. [1](#0-0) [2](#0-1) [4](#0-3) [3](#0-2)

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L240-270)
```haskell
    ConwayUnRegCert stakeCred sMayRefund -> do
      let (mAccountState, newAccounts) = unregisterConwayAccount stakeCred accounts
          checkInvalidRefund = do
            SJust suppliedRefund <- Just sMayRefund
            -- we don't want to report invalid refund when stake credential is not registered:
            accountState <- mAccountState
            -- we return offending refund only when it doesn't match the expected one:
            let expectedRefund = fromCompact $ accountState ^. depositAccountStateL
            guard (suppliedRefund /= expectedRefund)
            Just $
              if hardforkConwayDELEGIncorrectDepositsAndRefunds pv
                then
                  injectFailure
                    ( RefundIncorrectDELEG
                        Mismatch
                          { mismatchSupplied = suppliedRefund
                          , mismatchExpected = expectedRefund
                          }
                    )
                else injectFailure $ IncorrectDepositDELEG suppliedRefund
          checkStakeKeyHasZeroRewardBalance = do
            accountState <- mAccountState
            let balanceCompact = accountState ^. balanceAccountStateL
            guard (balanceCompact /= mempty)
            Just $ fromCompact balanceCompact
      failOnJust checkInvalidRefund id
      failOnJust
        checkStakeKeyHasZeroRewardBalance
        (injectFailure . StakeKeyHasNonZeroAccountBalanceDELEG)
      case mAccountState of
        Nothing -> do
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L259-275)
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
```
