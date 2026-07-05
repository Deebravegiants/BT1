I need to verify the exact flow for sub-tx treasury donation handling, particularly how `dijkstraSubTxProducedValue` interacts with `Conway.updateTreasuryDonation`, and whether the CBOR decoder gates key 22 by tx level.

### Title
Sub-Transaction Treasury Donation Destroys ADA: Counted in Value Conservation but Never Credited to Treasury - (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`)

---

### Summary

In the Dijkstra era, sub-transactions (`SubTx`) support a `treasuryDonationTxBodyL` field that is included in the produced-value calculation for value conservation but is never applied to the treasury state. `Conway.updateTreasuryDonation` is called only on the top-level transaction. Any ADA declared as a treasury donation in a sub-transaction is permanently destroyed.

---

### Finding Description

**1. The sub-tx treasury donation field is fully encodable/decodable.**

The CBOR decoder for `DijkstraTxBodyRaw` handles key 22 (treasury donation) without any `STopTx` level guard:

```haskell
22 ->
  Just $
    decodeAccA
      acc
      (treasuryDonationDijkstraTxBodyRawL .~)
      (pure <$> decodePositiveCoin (emptyFailure "Treasury Donation" "non-zero"))
``` [1](#0-0) 

Compare with fields that are correctly gated (e.g., key 13 collateral inputs, key 23 sub-transactions), which use `| STopTx <- sTxLevel ->`. Key 22 has no such guard, so it is accepted in sub-tx bodies. The encoder for `DijkstraSubTxBodyRaw` also emits key 22:

```haskell
!> Omit (== mempty) (Key 22 $ To dstbrTreasuryDonation)
``` [2](#0-1) 

**2. Sub-tx treasury donation IS counted in value conservation.**

`dijkstraSubTxProducedValue` explicitly adds `treasuryDonationTxBodyL` to the produced value for sub-transactions:

```haskell
dijkstraSubTxProducedValue pp isRegPoolId txBody =
  sumAllValue (txBody ^. outputsTxBodyL)
    <> inject (getTotalDepositsTxBody pp isRegPoolId txBody <> txBody ^. treasuryDonationTxBodyL)
    <> burnedMultiAssets txBody
``` [3](#0-2) 

`dijkstraProducedValue` aggregates this across all sub-transactions:

```haskell
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap'
      (getProducedValue pp isRegPoolId . view bodyTxL)
      (txBody ^. subTransactionsTxBodyL)
``` [4](#0-3) 

So `validateValueNotConservedUTxO` at line 381 of `Utxo.hs` passes when inputs cover the sub-tx donation. [5](#0-4) 

**3. Sub-tx treasury donation is NOT applied to the treasury.**

`Conway.updateTreasuryDonation` reads only the top-level transaction body:

```haskell
updateTreasuryDonation tx utxos =
  case tx ^. isValidTxL of
    IsValid True -> utxos & utxosDonationL <>~ tx ^. bodyTxL . treasuryDonationTxBodyL
    IsValid False -> utxos
``` [6](#0-5) 

It is called in `dijkstraUtxoTransition` as:

```haskell
Babbage.updateUTxOStateByTxValidity
  pp certState (utxosGovState utxos) tx
  (Conway.updateTreasuryDonation tx utxos)
``` [7](#0-6) 

There is no loop over sub-transactions to collect their donations. The sub-tx donation amount is consumed from UTxO inputs, satisfies value conservation as "produced", but is credited to no account — it vanishes.

---

### Impact Explanation

Any ADA declared as `treasuryDonationTxBodyL` in a sub-transaction is permanently destroyed. The amount is subtracted from the spender's UTxO inputs (required to balance value conservation) but is never added to `utxosDonationL` or any other ledger account. This constitutes direct, irreversible destruction of ADA, reducing the total circulating supply without any corresponding credit.

**Impact class: Critical** — Direct destruction of ADA through an invalid ledger state transition.

---

### Likelihood Explanation

Any unprivileged transaction author can exploit this. No governance majority, special key, or privileged role is required. The attacker simply constructs a batch transaction containing a sub-transaction with a non-zero `treasuryDonationTxBodyL`. The CBOR encoding and decoding infrastructure fully supports this field in sub-tx bodies. The exploit is deterministic and locally testable.

---

### Recommendation

Apply one of the following fixes:

1. **Reject sub-tx treasury donations at decode time**: Gate key 22 in the `DijkstraTxBodyRaw` decoder with `| STopTx <- sTxLevel ->`, mirroring the treatment of collateral inputs (key 13) and sub-transactions (key 23).

2. **Apply sub-tx donations to the treasury**: Extend `dijkstraUtxoTransition` to iterate over sub-transactions and accumulate their treasury donations into `utxosDonationL`, analogous to how `dijkstraProducedValue` aggregates them for value conservation.

Option 1 is simpler and eliminates the semantic ambiguity of sub-tx treasury donations entirely.

---

### Proof of Concept

1. Construct a top-level Dijkstra batch transaction with one sub-transaction whose `treasuryDonationTxBodyL` is set to, e.g., 1,000,000 lovelace. The sub-tx inputs must cover this amount.
2. Submit the batch. `validateValueNotConservedUTxO` passes because `dijkstraSubTxProducedValue` counts the donation in produced value.
3. Observe the treasury balance (`utxosDonationL`) before and after: it increases only by the top-level tx's donation (zero in this case), not by the sub-tx's 1,000,000 lovelace.
4. Observe the total UTxO balance: it has decreased by 1,000,000 lovelace with no corresponding credit anywhere in the ledger state.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L414-420)
```haskell
        22 ->
          -- plain field - initial accumulator already holds the omit-default
          Just $
            decodeAccA
              acc
              (treasuryDonationDijkstraTxBodyRawL .~)
              (pure <$> decodePositiveCoin (emptyFailure "Treasury Donation" "non-zero"))
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L513-513)
```haskell
        !> Omit (== mempty) (Key 22 $ To dstbrTreasuryDonation)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L102-106)
```haskell
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap'
      (getProducedValue pp isRegPoolId . view bodyTxL)
      (txBody ^. subTransactionsTxBodyL)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L258-261)
```haskell
dijkstraSubTxProducedValue pp isRegPoolId txBody =
  sumAllValue (txBody ^. outputsTxBodyL)
    <> inject (getTotalDepositsTxBody pp isRegPoolId txBody <> txBody ^. treasuryDonationTxBodyL)
    <> burnedMultiAssets txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L380-381)
```haskell
  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L421-426)
```haskell
  Babbage.updateUTxOStateByTxValidity
    pp
    certState
    (utxosGovState utxos)
    tx
    (Conway.updateTreasuryDonation tx utxos)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Utxo.hs (L206-209)
```haskell
updateTreasuryDonation tx utxos =
  case tx ^. isValidTxL of
    IsValid True -> utxos & utxosDonationL <>~ tx ^. bodyTxL . treasuryDonationTxBodyL
    IsValid False -> utxos
```
