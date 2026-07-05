### Title
Missing `validateExUnitsTooBigUTxO` Check in Sub-Transaction UTXO Rule Allows Per-Transaction Execution Unit Limit Bypass - (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs`)

---

### Summary

The Dijkstra era introduces nested sub-transactions (`Tx SubTx era`) embedded inside a top-level transaction. The top-level UTXO rule (`dijkstraUtxoTransition`) enforces the `maxTxExUnits` protocol parameter via `Alonzo.validateExUnitsTooBigUTxO`. The sub-transaction UTXO rule (`dijkstraSubUtxoTransition`) omits this check entirely. Because sub-transactions carry their own independent redeemer sets with their own declared execution units, an unprivileged transaction author can craft a top-level transaction whose sub-transactions each declare execution units just below `maxTxExUnits`, causing the aggregate execution unit consumption of the batch to far exceed the intended per-transaction limit.

---

### Finding Description

**Top-level UTXO rule** (`dijkstraUtxoTransition`) enforces the execution unit cap:

```haskell
{- totExunits tx ≤ maxTxExUnits pp -}
runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
``` [1](#0-0) 

**Sub-transaction UTXO rule** (`dijkstraSubUtxoTransition`) applies no equivalent check. The full transition rule runs validity-interval, forecast, output-size, input-set, bad-inputs, output-boot-attrs, output-too-small, and network-ID checks — but never calls `validateExUnitsTooBigUTxO`: [2](#0-1) 

Sub-transactions carry their own `TxWits` including their own `Redeemers` map, so `totExunits subTx` is entirely independent of `totExunits topTx`. The top-level check operates only on the top-level transaction's redeemers: [3](#0-2) 

The design is aware that sub-transactions can carry redeemers — `validateBatchCollateral` explicitly checks whether *any* transaction in the batch (top or sub) has redeemers and triggers collateral validation accordingly: [4](#0-3) 

Yet no analogous "batch execution unit" check exists. The `validateExUnitsTooBigUTxO` check is a hard `runTest` (not `runTestOnSignal`) in the top-level rule, confirming it is a mandatory protocol invariant — not an optional signal-only check.

---

### Impact Explanation

**Allowed impact matched:** *Medium — Attacker-controlled transactions exceed intended validation limits.*

`maxTxExUnits` is a protocol parameter that bounds the computational work a single transaction may demand from block-producing nodes. By embedding N sub-transactions each declaring `maxTxExUnits - 1` execution units, an attacker causes the ledger to accept a single logical transaction that consumes `N × (maxTxExUnits - 1)` execution units — an unbounded multiple of the intended cap. This:

1. Allows a single transaction to monopolize block execution resources beyond the per-transaction design limit.
2. Undermines the fee model: the minimum-fee calculation for the top-level transaction (`validateFeeTooSmallUTxO`) is applied only to the top-level tx; if sub-transaction execution units are not included in the fee computation, the attacker obtains excess computation below the intended cost.
3. Constitutes a direct violation of the `maxTxExUnits` protocol parameter, which is an "intended validation limit" in the allowed impact scope. [5](#0-4) 

---

### Likelihood Explanation

Any unprivileged transaction author can exploit this. No special keys, governance majority, or privileged role is required. The attacker only needs to:
- Construct a valid top-level transaction body with a `subTransactionsTxBodyL` field containing multiple sub-transactions.
- Populate each sub-transaction's `Redeemers` with declared execution units approaching `maxTxExUnits`.
- Provide valid witnesses for the top-level transaction.

The CDDL schema confirms sub-transactions are a standard, user-controlled field in the transaction body: [6](#0-5) 

---

### Recommendation

Add `validateExUnitsTooBigUTxO` to `dijkstraSubUtxoTransition` in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs`, mirroring the check present in the top-level rule:

```haskell
-- In dijkstraSubUtxoTransition, after existing checks:
{- totExunits subTx ≤ maxTxExUnits pp -}
runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

This ensures the execution unit cap is enforced uniformly for every transaction in the batch, consistent with the pattern already established for collateral (`validateBatchCollateral`) and withdrawal balance (`validateBatchWithdrawals`). [7](#0-6) 

---

### Proof of Concept

1. Obtain `maxTxExUnits = ExUnits { exUnitsMem = M, exUnitsSteps = S }` from current protocol parameters.
2. Craft a top-level `Tx TopTx DijkstraEra` with:
   - Empty top-level redeemers (0 execution units at top level → passes `validateExUnitsTooBigUTxO`).
   - `subTransactionsTxBodyL` containing N sub-transactions, each with a Plutus V3 redeemer declaring `ExUnits (M-1) (S-1)`.
3. Submit the transaction. The ledger accepts it because:
   - Top-level UTXO: `totExunits topTx = 0 ≤ maxTxExUnits` → **passes**.
   - Sub-level SUBUTXO: no `validateExUnitsTooBigUTxO` call → **no check performed**.
4. Total execution units consumed by the batch: `N × (M-1, S-1)`, which for N ≥ 2 exceeds `maxTxExUnits` — the protocol parameter is bypassed. [1](#0-0) [2](#0-1)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L282-302)
```haskell
-- | Validate collateral if any transaction in the batch has redeemers.
validateBatchCollateral ::
  forall era rule.
  ( AlonzoEraTx era
  , DijkstraEraTxBody era
  , InjectRuleFailure rule Alonzo.AlonzoUtxoPredFailure era
  , InjectRuleFailure rule Babbage.BabbageUtxoPredFailure era
  ) =>
  PParams era ->
  Tx TopTx era ->
  UTxO era ->
  Test (EraRuleFailure rule era)
validateBatchCollateral pp tx (UTxO utxo) =
  -- TODO OPTIMIZATION: Rewrite in a way that doesn't require this check when rules are executed without validation
  when (hasAnyRedeemers tx) $
    Babbage.validateTotalCollateral pp (tx ^. bodyTxL) utxoCollateral
  where
    utxoCollateral = Map.restrictKeys utxo (tx ^. bodyTxL . collateralInputsTxBodyL)
    hasAnyRedeemers t =
      hasRedeemers t || any hasRedeemers (t ^. bodyTxL . subTransactionsTxBodyL)
    hasRedeemers = not . null . (^. witsTxL . rdmrsTxWitsL . unRedeemersL)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L372-373)
```haskell
  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L414-415)
```haskell
  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx
```

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L215-278)
```haskell
dijkstraSubUtxoTransition ::
  forall era.
  ( EraTx era
  , EraStake era
  , EraCertState era
  , DijkstraEraTxBody era
  , AlonzoEraTxWits era
  , STS (EraRule "SUBUTXO" era)
  , EraRule "SUBUTXO" era ~ SUBUTXO era
  , InjectRuleFailure "SUBUTXO" Shelley.ShelleyUtxoPredFailure era
  , InjectRuleFailure "SUBUTXO" Allegra.AllegraUtxoPredFailure era
  , InjectRuleFailure "SUBUTXO" Alonzo.AlonzoUtxoPredFailure era
  , InjectRuleFailure "SUBUTXO" Babbage.BabbageUtxoPredFailure era
  , InjectRuleFailure "SUBUTXO" DijkstraUtxoPredFailure era
  ) =>
  TransitionRule (EraRule "SUBUTXO" era)
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

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L783-808)
```text
sub_transactions = nonempty_oset<sub_transaction>

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
