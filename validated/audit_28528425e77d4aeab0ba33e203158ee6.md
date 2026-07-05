### Title
Sub-Transaction Plutus ExUnits Bypass of `maxTxExUnits` and `maxBlockExUnits` Limits — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`, `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs`)

---

### Summary

In the Dijkstra era, the `maxTxExUnits` and `maxBlockExUnits` protocol-parameter limits are enforced only against the top-level transaction's redeemer set. Sub-transactions embedded in a batch carry their own witness sets with independent redeemers, but no ExUnits limit check is ever applied to them. An unprivileged transaction author can therefore submit a batch whose top-level transaction declares zero ExUnits (passing the per-transaction check) while packing arbitrarily many sub-transactions each declaring up to `maxTxExUnits` ExUnits, causing the node to execute Plutus scripts far beyond the intended resource ceiling. The minimum-fee calculation has the same blind spot, so the excess script execution is also uncharged.

---

### Finding Description

**`totExUnits` only reads the top-level witness set.**

`validateExUnitsTooBigUTxO` is the sole ExUnits gate in `dijkstraUtxoTransition`:

```haskell
{- totExunits tx ≤ maxTxExUnits pp -}
runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx   -- line 415
```

`validateExUnitsTooBigUTxO` delegates to `totExUnits`:

```haskell
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

`tx ^. witsTxL` is the **top-level** transaction's witness set. Sub-transaction redeemers live in each sub-transaction's own `transaction_witness_set` (CDDL field `? 5 : redeemers`), which is a separate structure never touched by `totExUnits`.

**`SUBUTXO` has no ExUnits check at all.**

`dijkstraSubUtxoTransition` validates inputs, outputs, network IDs, validity intervals, and output sizes, but contains no call to `validateExUnitsTooBigUTxO` or any equivalent. The `DijkstraSubUtxoPredFailure` type has no `ExUnitsTooBigUTxO` constructor, and the injection mapping explicitly marks it as impossible:

```haskell
ExUnitsTooBigUTxO _ -> error "Impossible: `ExUnitsTooBigUTxO` for SUBUTXO"
```

**Block-level check is equally blind.**

`validateExUnits` in `alonzoBbodyTransition` sums `foldMap totExUnits txs` over all top-level transactions in the block. Because `totExUnits` ignores sub-transaction redeemers, the block-level `maxBlockExUnits` ceiling is also bypassed.

**Minimum fee does not cover sub-transaction script costs.**

`alonzoMinFeeTx` computes `txscriptfee (pp ^. ppPricesL) (totExUnits tx)`, again using only the top-level redeemers. Sub-transaction Plutus execution is therefore unpriced.

---

### Impact Explanation

**Allowed impact matched:** *Medium — Attacker-controlled transactions exceed intended validation limits or modify fees outside design parameters.*

A single batch transaction can cause nodes to execute an unbounded multiple of `maxTxExUnits` worth of Plutus computation (one full `maxTxExUnits` budget per sub-transaction, with no cap on the number of sub-transactions beyond the serialized transaction size). The attacker also pays zero script-execution fees for sub-transaction scripts, violating the fee-accounting invariant. If execution time varies across node implementations or hardware, this can additionally produce deterministic disagreement between honest nodes (High impact), but the Medium impact is already directly reachable.

---

### Likelihood Explanation

The Dijkstra era is the current development era and sub-transactions are its defining feature. Any transaction author (no privilege required) can craft a `TopTx` with an empty redeemer map and embed N sub-transactions each carrying a redeemer with `ExUnits { exUnitsMem = maxMem, exUnitsSteps = maxSteps }`. The only practical bound is the serialized transaction size (`maxTxSize`), which is a much weaker constraint than `maxTxExUnits`. The attack is fully deterministic and requires no key leakage, governance access, or external oracle.

---

### Recommendation

1. **Extend `validateExUnitsTooBigUTxO` to cover the whole batch.** Define a `totBatchExUnits` that sums redeemers across the top-level transaction and all sub-transactions, and check it against `maxTxExUnits` in `dijkstraUtxoTransition`.

2. **Add a per-sub-transaction ExUnits check in `SUBUTXO`.** Even if a batch-level check is added, each sub-transaction should independently be bounded so that a single sub-transaction cannot consume the entire budget.

3. **Include sub-transaction ExUnits in `minfee`.** `alonzoMinFeeTx` (or its Dijkstra override) must sum redeemers from all sub-transactions when computing the script-fee component.

4. **Include sub-transaction ExUnits in the block-level `validateExUnits` in `BBODY`.** `foldMap totExUnits txs` must be replaced with a function that recurses into sub-transactions.

---

### Proof of Concept

Construct a `DijkstraEra` top-level transaction with:
- Empty `rdmrsTxWitsL` (so `totExUnits tx = ExUnits 0 0`, passing `validateExUnitsTooBigUTxO`)
- `subTransactionsTxBodyL` containing K sub-transactions, each with a redeemer map declaring `ExUnits { exUnitsMem = maxMem pp, exUnitsSteps = maxSteps pp }`

The top-level UTXO rule passes at line 415 because `totExUnits tx = 0 ≤ maxTxExUnits`. Each sub-transaction passes through `dijkstraSubUtxoTransition` with no ExUnits check. The BBODY block check also passes because `foldMap totExUnits [tx] = 0`. The actual Plutus interpreter executes K × `maxTxExUnits` worth of computation, and the fee paid covers only the byte-size component of the top-level transaction.

---

**Key code references:**

`validateExUnitsTooBigUTxO` checks only `totExUnits tx` (top-level redeemers): [1](#0-0) 

`totExUnits` reads only the top-level witness set: [2](#0-1) 

`dijkstraUtxoTransition` calls `validateExUnitsTooBigUTxO` only for the top-level tx: [3](#0-2) 

`dijkstraSubUtxoTransition` has no ExUnits check: [4](#0-3) 

`ExUnitsTooBigUTxO` is explicitly marked impossible for SUBUTXO: [5](#0-4) 

Block-level check uses the same `totExUnits` that ignores sub-transactions: [6](#0-5) 

Sub-transaction CDDL confirms sub-transactions carry their own witness sets with redeemers: [7](#0-6)

### Citations

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs (L459-465)
```haskell
validateExUnitsTooBigUTxO pp tx =
  failureUnless (pointWiseExUnits (<=) totalExUnits maxTxExUnits) $
    ExUnitsTooBigUTxO Mismatch {mismatchSupplied = totalExUnits, mismatchExpected = maxTxExUnits}
  where
    maxTxExUnits = pp ^. ppMaxTxExUnitsL
    -- This sums up the ExUnits for all embedded Plutus Scripts anywhere in the transaction:
    totalExUnits = totExUnits tx
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Tx.hs (L390-394)
```haskell
totExUnits ::
  (EraTx era, AlonzoEraTxWits era) =>
  Tx l era ->
  ExUnits
totExUnits tx = foldMap snd $ tx ^. witsTxL . rdmrsTxWitsL . unRedeemersL
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L414-415)
```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L231-278)
```haskell
dijkstraSubUtxoTransition = do
  TRC (SubUtxoEnv slot pp certState originalUtxo (IsValid isValid), utxoState, stAnnTx) <-
    judgmentContext
  let tx = stAnnTx ^. txStAnnTxG

  let txBody = tx ^. bodyTxL

  runTest $ Allegra.validateOutsideValidityIntervalUTxO slot txBody

  sysSt <- liftSTS $ asks systemStart
  ei <- liftSTS $ asks epochInfo
  runTest $ Alonzo.validateOutsideForecast ei slot sysSt tx

  let allSizedOutputs = txBody ^. allSizedOutputsTxBodyF
  let allOutputs = fmap sizedValue allSizedOutputs
  runTest $ Alonzo.validateOutputTooBigUTxO pp allOutputs

  runTest $ Shelley.validateInputSetEmptyUTxO txBody

  let inputs = txBody ^. inputsTxBodyL
  let refInputs = txBody ^. referenceInputsTxBodyL
  runTest $ Shelley.validateBadInputsUTxO originalUtxo (inputs `Set.union` refInputs)
  runTest $ Shelley.validateBadInputsUTxO (utxosUtxo utxoState) inputs

  runTestOnSignal $ Shelley.validateOutputBootAddrAttrsTooBig allOutputs

  runTestOnSignal $ Babbage.validateOutputTooSmallUTxO pp allSizedOutputs

  netId <- liftSTS $ asks networkId
  runTestOnSignal $ Shelley.validateWrongNetwork netId allOutputs
  runTestOnSignal $ Shelley.validateWrongNetworkWithdrawal netId txBody
  runTestOnSignal $ validateWrongNetworkInDirectDeposit netId txBody
  runTestOnSignal $ Alonzo.validateWrongNetworkInTxBody netId txBody

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L340-340)
```haskell
  ExUnitsTooBigUTxO _ -> error "Impossible: `ExUnitsTooBigUTxO` for SUBUTXO"
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Bbody.hs (L158-160)
```haskell
validateExUnits txs ppMax =
  let txTotal = foldMap totExUnits txs
   in pointWiseExUnits (<=) txTotal ppMax
```

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L785-808)
```text
sub_transaction =
  [sub_transaction_body, transaction_witness_set, auxiliary_data/ nil]

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
