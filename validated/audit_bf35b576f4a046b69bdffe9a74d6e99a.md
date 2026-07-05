### Title
Sub-transactions in Dijkstra Era Bypass Value Conservation Check, Enabling Direct ADA Creation — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs`)

---

### Summary

The Dijkstra era introduces nested ("batch") transactions where a top-level transaction carries one or more sub-transactions. The top-level UTXO rule (`dijkstraUtxoTransition`) enforces `validateValueNotConservedUTxO` against the top-level transaction body only. The sub-transaction UTXO rule (`dijkstraSubUtxoTransition`) applies `updateUTxOStateNoFees` — which removes inputs and adds outputs to the UTxO — without any value-conservation predicate. An unprivileged transaction author can therefore craft a sub-transaction whose outputs exceed its inputs in ADA value, minting arbitrary ADA into the ledger state with no corresponding destruction of existing funds.

---

### Finding Description

**Top-level path (correct):**

In `dijkstraUtxoTransition`, value conservation is enforced before the UTxO state is mutated:

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

`txBody` here is the top-level transaction body; `originalUtxo` is the UTxO snapshot captured before any sub-transaction processing. The check verifies that the sum of values consumed by the top-level transaction's own inputs equals the sum of its outputs plus fees and deposits.

**Sub-transaction path (missing check):**

`dijkstraSubUtxoTransition` performs no equivalent check. It calls `updateUTxOStateNoFees` directly:

```haskell
if isValid
  then do
    newState <-
      Shelley.updateUTxOStateNoFees
        pp utxoState txBody certState
        (utxosGovState utxoState)
        (tellEvent . TotalDeposits (hashAnnotated txBody))
        (\a b -> tellEvent $ TxUTxODiff a b)
    pure $ newState & utxosDonationL <>~ txBody ^. treasuryDonationTxBodyL
  else pure utxoState
```

`updateUTxOStateNoFees` removes the sub-transaction's inputs from the UTxO and inserts its outputs. It contains no internal value-conservation assertion; that invariant is the caller's responsibility. Because `dijkstraSubUtxoTransition` never calls `validateValueNotConservedUTxO`, the sub-transaction's outputs can be arbitrarily larger than its inputs.

**Why the top-level check does not cover sub-transactions:**

The top-level check uses `originalUtxo` and the top-level `txBody`. The `consumed` function reads `txBody ^. inputsTxBodyL` — the top-level transaction's own spend inputs — and the `produced` function reads `txBody ^. outputsTxBodyL` — the top-level transaction's own outputs. Sub-transaction bodies are carried in `txBody ^. subTransactionsTxBodyL` and are never passed to `validateValueNotConservedUTxO`. The top-level check is therefore blind to any value imbalance inside sub-transactions.

The `dijkstraLedgerTransition` captures `originalUtxo` before sub-transactions run, processes all sub-transactions via `SUBLEDGERS`, and then passes `originalUtxo` into the top-level `UTXOW` environment. The top-level value-conservation predicate therefore sees only the top-level transaction's own inputs and outputs, regardless of what sub-transactions created or destroyed.

---

### Impact Explanation

**Severity: Critical — Direct creation of ADA through an invalid ledger state transition.**

An attacker who controls any UTxO entry (even a dust output) can include a sub-transaction that spends that entry and produces an output of arbitrary ADA value. After the batch transaction is accepted, the attacker's address holds the inflated output. The total ADA supply in the ledger increases by the difference between the sub-transaction's output value and its input value. This is an unbounded, attacker-controlled inflation of the native asset, constituting a direct invalid ledger state transition.

---

### Likelihood Explanation

Any user who can submit a Dijkstra-era transaction can trigger this. No privileged key, governance majority, or special role is required. The attacker needs only a single UTxO entry to use as the sub-transaction's input. The attack is deterministic and reproducible: every honest node running the Dijkstra ledger rules will accept the transaction and apply the inflated UTxO update identically, so there is no divergence — all nodes agree on the invalid (inflated) state.

---

### Recommendation

Add a `validateValueNotConservedUTxO` call inside `dijkstraSubUtxoTransition`, analogous to the check in `dijkstraUtxoTransition`. The sub-transaction's consumed value (inputs from `originalUtxo` or the current UTxO state) must equal its produced value (outputs + treasury donation + deposit changes). Alternatively, aggregate all sub-transaction inputs and outputs into the top-level `validateValueNotConservedUTxO` call so that the single check covers the entire batch.

---

### Proof of Concept

1. Attacker owns UTxO entry `txIn_A` worth 2 ADA.
2. Attacker constructs sub-transaction `subTx`:
   - `inputsTxBodyL = {txIn_A}` (2 ADA)
   - `outputsTxBodyL = [TxOut attacker_addr 1_000_000_ADA]`
3. Attacker constructs top-level transaction `topTx`:
   - `inputsTxBodyL = {txIn_B}` (some separate 5 ADA entry)
   - `outputsTxBodyL = [TxOut attacker_addr 5_ADA]` (fee-adjusted)
   - `subTransactionsTxBodyL = OMap.singleton subTx`
4. Ledger processing:
   - `SUBLEDGERS` processes `subTx` via `dijkstraSubUtxoTransition` → `updateUTxOStateNoFees` removes `txIn_A`, inserts `(attacker_addr, 1_000_000_ADA)` — **no value check**.
   - `UTXOW` → `dijkstraUtxoTransition` runs `validateValueNotConservedUTxO pp originalUtxo certState topTxBody`: consumed = 5 ADA (from `txIn_B`), produced = 5 ADA (output + fee) → **passes**.
5. Final UTxO contains `(attacker_addr, 1_000_000_ADA)` created from a 2 ADA input. Net ADA inflation: **999,998 ADA**.

**Relevant code locations:**

Top-level check (present): [1](#0-0) 

Sub-transaction UTxO update (missing check): [2](#0-1) 

`updateUTxOStateNoFees` called without prior value conservation predicate: [3](#0-2) 

Top-level check uses only `originalUtxo` and top-level `txBody`, not sub-transaction bodies: [1](#0-0) 

Sub-transaction error mapping confirms `ValueNotConservedUTxO` is explicitly marked impossible for `SUBUTXO`: [4](#0-3)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L380-382)
```haskell
  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody

```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L265-278)
```haskell
  if isValid
    then do
      newState <-
        Shelley.updateUTxOStateNoFees
          pp
          utxoState
          txBody
          certState
          (utxosGovState utxoState)
          (tellEvent . TotalDeposits (hashAnnotated txBody))
          (\a b -> tellEvent $ TxUTxODiff a b)
      pure $ newState & utxosDonationL <>~ txBody ^. treasuryDonationTxBodyL
    else
      pure utxoState
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L333-333)
```haskell
  ValueNotConservedUTxO _ -> error "Impossible: `ValueNotConservedUTxO` for SUBUTXO"
```
