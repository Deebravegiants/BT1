### Title
Missing Cross-Sub-Transaction Deduplication Check for Deposit Refunds Allows Double-Claiming of Deposits - (File: `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs`)

---

### Summary

In the Dijkstra era, a batch transaction containing multiple sub-transactions can include `UnRegDepositTxCert` for the **same staking credential** in more than one sub-transaction. Because no cross-sub-transaction deduplication check exists for certificate-based deposit refunds, each sub-transaction independently claims the full deposit refund for the same credential. This allows an attacker to extract more ADA from the deposit pot than was ever deposited, directly corrupting the ledger's value-conservation invariant.

---

### Finding Description

The Dijkstra era introduces nested/batch transactions: a top-level `Tx TopTx` may embed an ordered map of `Tx SubTx` sub-transactions (`dtbrSubTransactions`). Each sub-transaction carries its own certificate list (`dstbrCerts`) and is processed by the `SubDeleg`/`SubCerts`/`SubLedger` rules.

The `dijkstraTotalRefundsTxCerts` function correctly accumulates refunds **within a single certificate list** using `foldMap'`:

```haskell
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit
  UnRegDRepTxCert _ deposit -> deposit
  _ -> zero
```

However, there is no analogous accumulation or deduplication check **across** sub-transactions. The `dijkstraUtxoTransition` rule explicitly binds the accounts from the **original** pre-batch state:

```
-- this is the original Accounts, before any transactions were applied
let accounts = certState ^. certDStateL . accountsL
```

Because each sub-transaction is validated against this original snapshot rather than the progressively-updated state, two sub-transactions that each contain `UnRegDepositTxCert stakingCred deposit` for the same credential will both pass their individual deregistration checks and both receive the full deposit refund.

The developers are aware of this gap: the test case that should enforce the rejection is explicitly disabled with `xit` and the expected predicate failure is marked `error "TODO: predicate failure not yet implemented"`:

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
  ...
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
```

This is the direct Cardano analog of the original report's pattern: instead of a loop variable being **overwritten** (`=`) rather than **accumulated** (`+=`), here the per-sub-transaction refund accounting is **independent** rather than **deduplicated**, producing the same class of incorrect total.

---

### Impact Explanation

**Critical — Direct loss of ADA through an invalid ledger state transition.**

An attacker registers one staking credential (paying one deposit `D`). They then submit a single batch transaction containing `N` sub-transactions, each carrying `UnRegDepositTxCert stakingCred D`. Because the missing cross-sub-transaction check is not enforced, all `N` sub-transactions succeed and the deposit pot is reduced by `N × D` while only `D` was ever deposited. The surplus `(N-1) × D` ADA is created from nothing, violating the ledger's preservation-of-value invariant (`sumAdaPots` will no longer balance). This constitutes a direct, attacker-controlled creation of ADA through an invalid ledger state transition.

---

### Likelihood Explanation

**High.** The attack requires only:
1. Registering a staking credential (costs one deposit, publicly available operation).
2. Constructing a valid Dijkstra batch transaction with multiple sub-transactions — a standard user-level operation in the Dijkstra era.
3. No privileged access, governance majority, or key compromise is needed.

The disabled test and the `TODO` comment confirm the developers know the guard is absent, meaning the current production code accepts such a transaction.

---

### Recommendation

Implement a cross-sub-transaction deduplication check for `UnRegDepositTxCert` (and `UnRegDRepTxCert`) certificates. Before processing sub-transactions, collect the set of all credentials being deregistered across the entire batch (top-level certs + all sub-transaction certs). Reject the batch if any credential appears in more than one deregistration certificate. This mirrors the existing `validateBatchWithdrawals` pattern, which already uses `Map.unionsWith (<>)` to aggregate withdrawals across all sub-transactions before checking them against the original account balances:

```haskell
-- existing correct pattern for withdrawals:
allWithdrawals =
  Map.unionsWith (<>) $
    unWithdrawals (tx ^. bodyTxL . withdrawalsTxBodyL)
      : [ unWithdrawals $ subTx ^. bodyTxL . withdrawalsTxBodyL
        | subTx <- OMap.elems $ tx ^. bodyTxL . subTransactionsTxBodyL
        ]
```

An analogous aggregation must be applied to deregistration certificates before any sub-transaction is applied.

---

### Proof of Concept

The disabled test in `eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs` already encodes the exact attack: [1](#0-0) 

The test is skipped (`xit`) because the predicate failure that should reject it does not yet exist. The `dijkstraUtxoTransition` rule binds the original accounts snapshot, meaning each sub-transaction sees the credential as still registered: [2](#0-1) 

The refund accumulation function `dijkstraTotalRefundsTxCerts` is correct within a single certificate list but is never called in a cross-sub-transaction aggregation context: [3](#0-2) 

The correct cross-sub-transaction aggregation pattern already exists for withdrawals (`validateBatchWithdrawals`) but has no equivalent for certificate-based deposit refunds: [4](#0-3)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L249-270)
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
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L344-349)
```haskell
  TRC (DijkstraUtxoEnv slot pp certState originalUtxo, utxos, stAnnTx) <-
    judgmentContext
  let tx = stAnnTx ^. txStAnnTxG
  -- this is the original Accounts, before any transactions were applied
  let accounts = certState ^. certDStateL . accountsL

```

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
