### Title
Unbounded Plutus Execution Units in Sub-Transactions Bypass `maxTxExUnits` in Dijkstra Era `SUBLEDGERS` Rule - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs`)

---

### Summary

The Dijkstra era introduces sub-transactions (`subTransactionsTxBodyL`) processed by the `SUBLEDGERS` rule via an unbounded `foldM` loop. Each sub-transaction can carry Plutus scripts with redeemers that specify execution unit budgets. However, `validateExUnitsTooBigUTxO` is applied only to the top-level transaction's redeemers; sub-transaction redeemers are never checked against `maxTxExUnits`. An unprivileged transaction submitter can craft a top-level transaction whose sub-transactions collectively declare execution unit budgets far exceeding `maxTxExUnits`, causing every validating node to run the Plutus evaluator for an arbitrarily large budget on a single transaction.

---

### Finding Description

**Root cause — `SUBLEDGERS` iterates without an execution-unit budget check:**

`dijkstraSubLedgersTransition` folds over every sub-transaction, invoking the full `SUBLEDGER` rule (→ `SUBUTXOW` → `SUBUTXO` → Plutus evaluation) for each one:

```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
``` [1](#0-0) 

There is no protocol parameter bounding the number of sub-transactions; a grep for `maxSubTx`, `maxSubTransactions`, `SubTxCount`, etc. returns zero results across the entire codebase. The CDDL only enforces a lower bound:

```
sub_transactions = nonempty_oset<sub_transaction>
``` [2](#0-1) 

**`validateExUnitsTooBigUTxO` is applied only to the top-level transaction:**

In `dijkstraUtxoTransition`, the execution-unit check uses the top-level `tx` object:

```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
``` [3](#0-2) 

`Alonzo.validateExUnitsTooBigUTxO` calls `totExunits`, which sums execution units from `tx ^. witsTxL . rdmrsTxWitsL` — the top-level transaction's redeemer map only. Sub-transaction redeemers live in each `subTx ^. witsTxL . rdmrsTxWitsL` and are never aggregated into this check.

**`ExUnitsTooBigUTxO` is explicitly absent from the sub-transaction UTxO rule:**

`DijkstraSubUtxoPredFailure` has no `ExUnitsTooBigUTxO` constructor, and the injection mapping treats it as impossible:

```haskell
  ExUnitsTooBigUTxO _ -> error "Impossible: `ExUnitsTooBigUTxO` for SUBUTXO"
``` [4](#0-3) 

**Sub-transactions do execute Plutus scripts:**

The CDDL includes `? 11 : script_data_hash` in `sub_transaction_body`, and `DijkstraStAnnSubTx` carries `dsastPlutusScriptsWithContext`, confirming that Plutus scripts are collected and evaluated per sub-transaction. [5](#0-4) [6](#0-5) 

**`maxTxSize` does not adequately bound Plutus work:**

`validateMaxTxSizeUTxO` bounds the total serialized bytes of the transaction including sub-transactions. However, a redeemer specifying `(maxBound :: Word64, maxBound :: Word64)` execution units serializes to only ~20 bytes while instructing the Plutus evaluator to run for an astronomically large budget. Serialized size and Plutus CPU/memory cost are decoupled. [7](#0-6) 

---

### Impact Explanation

**Medium — Attacker-controlled transactions exceed intended validation limits.**

An attacker submits a single valid top-level transaction containing N sub-transactions, each with a Plutus script redeemer declaring the maximum execution unit budget. Every honest node must evaluate all N Plutus scripts to their declared budget before it can reject or accept the transaction. Because the Plutus evaluator is bounded by the declared budget (not by `maxTxExUnits`), nodes can be forced to spend orders of magnitude more CPU/memory per transaction than the protocol intends. This can cause block-producing nodes to miss their slot leadership window and cause relay nodes to fall behind in chain synchronization, degrading liveness of the network.

---

### Likelihood Explanation

**Medium.** The Dijkstra era is not yet deployed on mainnet, but the vulnerability is reachable by any unprivileged transaction submitter once the era activates. No special keys, governance majority, or privileged access is required. Constructing the malicious transaction requires only knowledge of the sub-transaction format and the ability to include a Plutus script (e.g., `alwaysSucceeds`) with an inflated execution unit declaration.

---

### Recommendation

1. **Add a batch-level execution unit check** analogous to `validateAllRefScriptSize` in `dijkstraLedgerTransition`. Sum `totExunits` across the top-level transaction and all sub-transactions and enforce the aggregate against `maxTxExUnits pp`.
2. **Alternatively, add a per-sub-transaction `ExUnitsTooBigUTxO` check** inside `SUBUTXO` so each sub-transaction is individually bounded.
3. **Consider a hard protocol-parameter cap** on the number of sub-transactions per top-level transaction, analogous to `maxCollInputs`, to bound the multiplicative validation cost.

---

### Proof of Concept

1. Obtain a Plutus V3 script that always succeeds (e.g., `alwaysSucceeds`).
2. Construct a top-level Dijkstra transaction with N sub-transactions (N chosen so total serialized size ≤ `maxTxSize`).
3. Each sub-transaction spends a UTxO locked by the always-succeeds script and includes a redeemer with `ExUnits { exUnitsMem = maxBound, exUnitsSteps = maxBound }`.
4. The top-level transaction's `totExunits` is 0 (no top-level redeemers), so `validateExUnitsTooBigUTxO` passes.
5. `SUBLEDGERS` iterates over all N sub-transactions; for each, `SUBUTXOW` collects and evaluates the Plutus script against the declared budget.
6. Nodes spend N × `maxBound` execution steps evaluating scripts for a single transaction, far exceeding the intended per-transaction limit. [1](#0-0) [3](#0-2) [4](#0-3) [8](#0-7)

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

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L783-783)
```text
sub_transactions = nonempty_oset<sub_transaction>
```

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L788-808)
```text
sub_transaction_body =
  {   0  : set<transaction_input>
  ,   1  : [* transaction_output]
  , ? 3  : slot
  , ? 4  : certificates
  , ? 5  : withdrawals
  , ? 7  : auxiliary_data_hash
  , ? 8  : slot
  , ? 9  : mint
  , ? 11 : script_data_hash
  , ? 14 : guards
  , ? 15 : network_id
  , ? 18 : nonempty_set<transaction_input>
  , ? 19 : voting_procedures
  , ? 20 : proposal_procedures
  , ? 21 : coin
  , ? 22 : positive_coin
  , ? 24 : required_top_level_guards
  , ? 25 : direct_deposits
  , ? 26 : account_balance_intervals
  }
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L411-412)
```haskell
  {- txsize tx ≤ maxTxSize pp -}
  runTestOnSignal $ Shelley.validateMaxTxSizeUTxO pp tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L414-415)
```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L340-340)
```haskell
  ExUnitsTooBigUTxO _ -> error "Impossible: `ExUnitsTooBigUTxO` for SUBUTXO"
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra.hs (L120-148)
```haskell
    stAnnSubTxs =
      map
        (mkDijkstraStAnnSubTx ei sysStart pp utxo scriptsProvided)
        (toList (txBody ^. subTransactionsTxBodyL))
    ledgerTxInfo =
      LedgerTxInfo
        { ltiProtVer = pp ^. ppProtocolVersionL
        , ltiEpochInfo = ei
        , ltiSystemStart = sysStart
        , ltiUTxO = utxo
        , ltiTx = tx
        , ltiMemoizedSubTransactions =
            Map.fromList
              [ (txIdTx dsastTx, dsastTxInfoResult)
              | DijkstraStAnnSubTx {dsastTx, dsastTxInfoResult} <- stAnnSubTxs
              ]
        }
    languagesUsed = Set.fromList [plutusScriptLanguage s | (_, _, s) <- plutusScriptsUsed]
   in
    DijkstraStAnnTopTx
      { dsattTx = tx
      , dsattScriptsNeeded = scriptsNeeded
      , dsattScriptsProvided = scriptsProvided
      , dsattPlutusLegacyMode = not $ Set.null $ Set.filter (<= PlutusV3) languagesUsed
      , dsattPlutusLanguagesUsed = languagesUsed
      , dsattPlutusScriptsWithContext =
          scriptsWithContextFromLedgerTxInfo ledgerTxInfo (pp ^. ppCostModelsL) plutusScriptsUsed
      , dsattSubTransactions = stAnnSubTxs
      }
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L313-329)
```haskell
validateAllRefScriptSize ::
  ( EraTx era
  , DijkstraEraTxBody era
  ) =>
  PParams era ->
  UTxO era ->
  Tx TopTx era ->
  Test (DijkstraLedgerPredFailure era)
validateAllRefScriptSize pp utxo tx =
  let totalRefScriptSize = batchNonDistinctRefScriptsSize utxo tx
      maxRefScriptSizePerTx = fromIntegral @Word32 @Int $ pp ^. ppMaxRefScriptSizePerTxG
   in failureUnless (totalRefScriptSize <= maxRefScriptSizePerTx) $
        DijkstraTxRefScriptsSizeTooBig
          Mismatch
            { mismatchSupplied = totalRefScriptSize
            , mismatchExpected = maxRefScriptSizePerTx
            }
```
