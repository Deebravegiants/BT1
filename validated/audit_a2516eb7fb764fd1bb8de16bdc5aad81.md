### Title
Sub-transaction ExUnits Bypass of `maxTxExUnits` Protocol Limit in Dijkstra Era SUBUTXO Rule — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs`)

---

### Summary

The Dijkstra era introduces nested ("sub") transactions embedded inside a top-level transaction batch. The `SUBUTXO` rule that validates each sub-transaction omits the `validateExUnitsTooBigUTxO` check. Simultaneously, the top-level `UTXO` rule's call to `Alonzo.validateExUnitsTooBigUTxO pp tx` only sums ExUnits from the top-level transaction's own redeemers via `totExUnits tx`, not from sub-transaction redeemers. Because sub-transactions support PlutusV4 scripts with their own redeemer/ExUnits declarations, an attacker can embed sub-transactions whose declared ExUnits exceed `maxTxExUnits` without any rejection, bypassing the protocol's per-transaction resource limit.

---

### Finding Description

The Dijkstra era's `dijkstraSubUtxoTransition` in `SubUtxo.hs` performs the following checks for each sub-transaction: [1](#0-0) 

Comparing this to the top-level `dijkstraUtxoTransition` in `Utxo.hs`, which includes:

```haskell
{- totExunits tx ≤ maxTxExUnits pp -}
runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
``` [2](#0-1) 

The sub-transaction rule has **no equivalent call**. The `validateExUnitsTooBigUTxO` function is defined as:

```haskell
validateExUnitsTooBigUTxO pp tx =
  failureUnless (pointWiseExUnits (<=) totalExUnits maxTxExUnits) $ ...
  where
    maxTxExUnits = pp ^. ppMaxTxExUnitsL
    -- This sums up the ExUnits for all embedded Plutus Scripts anywhere in the transaction:
    totalExUnits = totExUnits tx
``` [3](#0-2) 

`totExUnits tx` sums only the redeemers in the top-level transaction's own witness set (`tx ^. witsTxL . rdmrsTxWitsL`). Sub-transactions carry separate witness sets with their own redeemers and ExUnits declarations. These are never aggregated into the top-level ExUnits check.

The asymmetry is confirmed by `validateBatchCollateral`, which explicitly iterates over sub-transaction redeemers to determine whether collateral is required:

```haskell
hasAnyRedeemers t =
  hasRedeemers t || any hasRedeemers (t ^. bodyTxL . subTransactionsTxBodyL)
``` [4](#0-3) 

This shows the codebase is aware that sub-transactions can have redeemers, yet the ExUnits bound check does not aggregate them.

Sub-transactions support PlutusV4 scripts (PlutusV1–V3 are explicitly rejected via `UnsupportedScriptInSubTx`): [5](#0-4) 

The sub-transaction CDDL schema confirms that sub-transaction bodies carry a `script_data_hash` field (key 11), and the witness set carries redeemers (key 5): [6](#0-5) 

Additionally, the `DijkstraSubUtxoPredFailure` type includes a `SubMaxTxSizeUTxO` constructor that is **never triggered** in `dijkstraSubUtxoTransition`, indicating an incomplete implementation of per-sub-transaction resource limits: [7](#0-6) 

---

### Impact Explanation

An unprivileged transaction submitter can craft a top-level transaction whose top-level ExUnits are zero (or within the limit) but whose embedded sub-transactions each declare ExUnits up to or exceeding `maxTxExUnits`. Because the SUBUTXO rule never calls `validateExUnitsTooBigUTxO` and the top-level check only covers top-level redeemers, the batch is accepted. Nodes are then obligated to execute PlutusV4 scripts in sub-transactions with declared ExUnits that exceed the protocol's intended per-transaction ceiling, consuming CPU and memory beyond the design parameters. This matches the **Medium** allowed impact: *attacker-controlled transactions exceed intended validation limits*.

---

### Likelihood Explanation

Any transaction submitter can construct such a batch. No privileged access, governance majority, or key compromise is required. The Dijkstra era is experimental but the validation gap is structural and reachable through normal transaction submission. Likelihood is **Medium** given the era is not yet on mainnet, but the code path is fully reachable.

---

### Recommendation

1. **Short term:** Add `runTest $ Alonzo.validateExUnitsTooBigUTxO pp subTx` inside `dijkstraSubUtxoTransition` for each sub-transaction, analogous to the top-level check.
2. **Long term:** Define a batch-level ExUnits check that aggregates ExUnits across the top-level transaction and all sub-transactions and validates the total against `maxTxExUnits` (or a new `maxBatchExUnits` parameter). Activate the existing `SubMaxTxSizeUTxO` failure path for per-sub-transaction size enforcement as well.

---

### Proof of Concept

1. Obtain the current `maxTxExUnits` from protocol parameters (e.g., `ExUnits { exUnitsMem = M, exUnitsSteps = S }`).
2. Construct a PlutusV4 script that always succeeds and declare its redeemer with `ExUnits { exUnitsMem = M+1, exUnitsSteps = S+1 }` (exceeding the limit).
3. Place this script and redeemer in a sub-transaction's witness set.
4. Wrap the sub-transaction inside a top-level transaction whose own redeemers are empty (ExUnits = 0).
5. Submit the batch. The top-level `validateExUnitsTooBigUTxO pp tx` passes (top-level ExUnits = 0 ≤ maxTxExUnits). The `dijkstraSubUtxoTransition` never calls `validateExUnitsTooBigUTxO`, so the sub-transaction's over-limit ExUnits declaration is never rejected. The batch is accepted and nodes execute the script under an ExUnits budget exceeding the protocol limit.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L72-110)
```haskell
data DijkstraSubUtxoPredFailure era
  = -- | The bad transaction inputs
    SubBadInputsUTxO (NonEmptySet TxIn)
  | SubOutsideValidityIntervalUTxO
      -- | transaction's validity interval
      ValidityInterval
      -- | current slot
      SlotNo
  | SubMaxTxSizeUTxO (Mismatch RelLTEQ Word32)
  | SubInputSetEmptyUTxO
  | -- | the set of addresses with incorrect network IDs
    SubWrongNetwork
      -- | the expected network id
      Network
      -- | the set of addresses with incorrect network IDs
      (NonEmptySet Addr)
  | SubWrongNetworkWithdrawal
      -- | the expected network id
      Network
      -- | the set of reward addresses with incorrect network IDs
      (NonEmptySet AccountAddress)
  | -- | list of supplied bad transaction outputs
    SubOutputBootAddrAttrsTooBig (NonEmpty (TxOut era))
  | -- | list of supplied bad transaction output triples (actualSize,PParameterMaxValue,TxOut)
    SubOutputTooBigUTxO (NonEmpty (Int, Int, TxOut era))
  | -- | Wrong Network ID in body
    SubWrongNetworkInTxBody
      (Mismatch RelEQ Network)
  | -- | slot number outside consensus forecast range
    SubOutsideForecast SlotNo
  | -- | list of supplied transaction outputs that are too small,
    -- together with the minimum value for the given output.
    SubBabbageOutputTooSmallUTxO (NonEmpty (TxOut era, Coin))
  | SubWrongNetworkInDirectDeposit
      -- | the expected network id
      Network
      -- | the set of account addresses with incorrect network IDs
      (NonEmptySet AccountAddress)
  deriving (Generic)
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L300-302)
```haskell
    hasAnyRedeemers t =
      hasRedeemers t || any hasRedeemers (t ^. bodyTxL . subTransactionsTxBodyL)
    hasRedeemers = not . null . (^. witsTxL . rdmrsTxWitsL . unRedeemersL)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L414-415)
```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs (L451-465)
```haskell
validateExUnitsTooBigUTxO ::
  ( AlonzoEraTxWits era
  , EraTx era
  , AlonzoEraPParams era
  ) =>
  PParams era ->
  Tx l era ->
  Test (AlonzoUtxoPredFailure era)
validateExUnitsTooBigUTxO pp tx =
  failureUnless (pointWiseExUnits (<=) totalExUnits maxTxExUnits) $
    ExUnitsTooBigUTxO Mismatch {mismatchSupplied = totalExUnits, mismatchExpected = maxTxExUnits}
  where
    maxTxExUnits = pp ^. ppMaxTxExUnitsL
    -- This sums up the ExUnits for all embedded Plutus Scripts anywhere in the transaction:
    totalExUnits = totExUnits tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs (L96-109)
```haskell
data DijkstraContextError era
  = ConwayContextError (ConwayContextError era)
  | -- | Failure translating sub-transactions for Guarding purpose at the top level
    SubTxContextError TxId (ContextError era)
  | PointerPresentInOutput (NonEmpty (TxOut era))
  | -- | Attempt to use PlutusV1-V3 in a sub-transaction will result in this failure
    UnsupportedScriptInSubTx Language TxId
  | -- | Attempt to use PlutusV1-V3 with non-empty direct deposits will result in this failure
    DirectDepositsNotSupported DirectDeposits
  | -- | Attempt to use PlutusV1-V3 with non-empty account balance intervals will result in this failure
    AccountBalanceIntervalsNotSupported (AccountBalanceIntervals era)
  | -- | Attempt to use PlutusV1-V3 with script hashes in guards will result in this failure
    GuardScriptHashesNotSupported (NonEmpty ScriptHash)
  deriving (Generic)
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
