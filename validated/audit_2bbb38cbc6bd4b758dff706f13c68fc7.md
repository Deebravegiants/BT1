### Title
Sub-Transactions Lack Value Conservation Enforcement, Enabling ADA Creation — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs`)

### Summary

In the Dijkstra era's nested-transaction design, the `SUBUTXO` rule processes each sub-transaction without ever checking value conservation (`validateValueNotConservedUTxO`). The top-level `UTXO` rule's value conservation check covers only the top-level transaction body against the original UTxO, leaving sub-transaction value flows entirely unaccounted for. An attacker can craft a sub-transaction whose outputs exceed its inputs, creating ADA or native assets from nothing.

### Finding Description

The Dijkstra era introduces nested ("batch") transactions. A top-level `TopTx` may embed one or more `SubTx` sub-transactions. Each sub-transaction is processed through the `SUBUTXO` rule (`dijkstraSubUtxoTransition`) before the top-level `UTXO` rule runs.

**In `dijkstraSubUtxoTransition`** the following checks are performed:

- Validity interval
- Forecast range
- Output size / too-big
- Non-empty input set
- Bad inputs (inputs must be in `originalUtxo`)
- Output boot-addr attrs
- Network IDs

**Critically absent** from `dijkstraSubUtxoTransition`:

- `validateValueNotConservedUTxO` — no value conservation check
- `validateFeeTooSmallUTxO` — no fee check
- `validateExUnitsTooBigUTxO` — no execution-unit cap
- `validateMaxTxSizeUTxO` — no size cap (the `SubMaxTxSizeUTxO` failure constructor exists but is never raised) [1](#0-0) 

The injection mapping for `SUBUTXO` explicitly marks these as unreachable:

```haskell
FeeTooSmallUTxO _       -> error "Impossible: `FeeTooSmallUTxO` for SUBUTXO"
ValueNotConservedUTxO _ -> error "Impossible: `ValueNotConservedUTxO` for SUBUTXO"
``` [2](#0-1) 

After passing all checks, the sub-transaction state is committed via `Shelley.updateUTxOStateNoFees`, which removes the sub-transaction's inputs from the UTxO and adds its outputs — with no value-conservation predicate guarding this update. [3](#0-2) 

The top-level `dijkstraUtxoTransition` does call `validateValueNotConservedUTxO`, but it does so against `originalUtxo` and the **top-level** `txBody` only:

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
``` [4](#0-3) 

`txBody` here is `tx ^. bodyTxL` — the top-level transaction body. The `consumed` computation sums only the top-level transaction's `inputsTxBodyL`, withdrawals, and refunds. Sub-transaction inputs and outputs are invisible to this check.

The top-level rule also enforces that the top-level transaction's inputs must reside in `originalUtxo`:

```haskell
runTest $ Shelley.validateBadInputsUTxO originalUtxo allInputs
``` [5](#0-4) 

Sub-transactions are similarly constrained to `originalUtxo` inputs. Therefore the complete value accounting across a batch is:

| Component | Consumed from UTxO | Added to UTxO |
|---|---|---|
| Sub-transactions | sub-tx inputs (checked ∈ originalUtxo) | sub-tx outputs (**unchecked**) |
| Top-level tx | top-level inputs (checked ∈ originalUtxo) | top-level outputs (conservation checked) |

The sub-transaction column has no conservation invariant. An attacker may set sub-tx outputs arbitrarily larger than sub-tx inputs.

### Impact Explanation

**Critical — Direct creation of ADA or native assets through an invalid ledger state transition.**

A single malicious sub-transaction can mint an unbounded quantity of ADA or any native asset by producing outputs whose total value exceeds the value of its consumed inputs. Because `updateUTxOStateNoFees` unconditionally commits the sub-transaction's outputs to the UTxO, and neither the `SUBUTXO` rule nor the top-level `UTXO` rule's conservation check covers the sub-transaction's value delta, the inflated outputs become spendable UTxO entries on the ledger. This constitutes a direct, permanent, invalid ledger state transition.

### Likelihood Explanation

The Dijkstra era is present in the production codebase and is the next planned era after Conway. Any node running Dijkstra-era validation would accept such a transaction. The attack requires only the ability to submit a transaction — no privileged access, no key compromise, no governance majority. The construction is straightforward: embed a sub-transaction that spends a 1-lovelace UTxO and produces a 1-billion-ADA output.

### Recommendation

Add a value conservation check inside `dijkstraSubUtxoTransition`, analogous to the check in `dijkstraUtxoTransition`:

```haskell
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

Alternatively, implement a batch-level value conservation check that sums consumed and produced values across all sub-transactions and the top-level transaction together, similar to how `validateBatchWithdrawals` aggregates withdrawals across the batch. [6](#0-5) 

Also remove or correct the `error "Impossible: ..."` branches for `FeeTooSmallUTxO` and `ValueNotConservedUTxO` in the `SUBUTXO` injection mapping, as these are not logically impossible — they are simply missing. [7](#0-6) 

### Proof of Concept

1. Construct a `TopTx` with `isValid = True`.
2. Embed one `SubTx` with:
   - `inputsTxBodyL` = `{utxo_entry_with_1_lovelace}`
   - `outputsTxBodyL` = `[TxOut attacker_addr (Value 1_000_000_000_ADA)]`
   - All other fields minimal/empty.
3. The top-level `UTXO` rule validates the top-level transaction body's conservation (which is satisfied independently).
4. `dijkstraSubUtxoTransition` validates the sub-transaction: inputs ∈ originalUtxo ✓, validity interval ✓, network IDs ✓ — no value conservation check is performed.
5. `updateUTxOStateNoFees` commits the sub-transaction: removes the 1-lovelace input, adds the 1-billion-ADA output.
6. The 1-billion-ADA output is now a valid, spendable UTxO entry. The ledger has accepted an invalid state transition creating ~1 billion ADA from 1 lovelace. [8](#0-7) [9](#0-8)

### Citations

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs (L324-351)
```haskell
dijkstraUtxoToDijkstraSubUtxoPredFailure ::
  DijkstraUtxoPredFailure era -> DijkstraSubUtxoPredFailure era
dijkstraUtxoToDijkstraSubUtxoPredFailure = \case
  UtxosFailure _ -> error "Impossible: `UtxosFailure` for SUBUTXO"
  BadInputsUTxO x -> SubBadInputsUTxO x
  OutsideValidityIntervalUTxO vi slotNo -> SubOutsideValidityIntervalUTxO vi slotNo
  MaxTxSizeUTxO m -> SubMaxTxSizeUTxO m
  InputSetEmptyUTxO -> SubInputSetEmptyUTxO
  FeeTooSmallUTxO _ -> error "Impossible: `FeeTooSmallUTxO` for SUBUTXO"
  ValueNotConservedUTxO _ -> error "Impossible: `ValueNotConservedUTxO` for SUBUTXO"
  WrongNetwork x y -> SubWrongNetwork x y
  WrongNetworkWithdrawal x y -> SubWrongNetworkWithdrawal x y
  OutputBootAddrAttrsTooBig xs -> SubOutputBootAddrAttrsTooBig xs
  OutputTooBigUTxO xs -> SubOutputTooBigUTxO xs
  InsufficientCollateral _ _ -> error "Impossible: `InsufficientCollateral` for SUBUTXO"
  ScriptsNotPaidUTxO _ -> error "Impossible: `ScriptsNotPaidUTxO` for SUBUTXO"
  ExUnitsTooBigUTxO _ -> error "Impossible: `ExUnitsTooBigUTxO` for SUBUTXO"
  CollateralContainsNonADA _ -> error "Impossible: `CollateralContainsNonADA` for SUBUTXO"
  WrongNetworkInTxBody m -> SubWrongNetworkInTxBody m
  OutsideForecast sno -> SubOutsideForecast sno
  TooManyCollateralInputs _ -> error "Impossible: `TooManyCollateralInputs` for SUBUTXO"
  NoCollateralInputs -> error "Impossible: `NoCollateralInputs` for SUBUTXO"
  IncorrectTotalCollateralField _ _ -> error "Impossible: `IncorrectTotalCollateralField` for SUBUTXO"
  BabbageOutputTooSmallUTxO outs -> SubBabbageOutputTooSmallUTxO outs
  BabbageNonDisjointRefInputs _ -> error "Impossible: `BabbageNonDisjointRefInputs` for SUBUTXO"
  PtrPresentInCollateralReturn _ -> error "Impossible: `PtrPresentInCollateralReturn` for SUBUTXO"
  WrongNetworkInDirectDeposit x y -> SubWrongNetworkInDirectDeposit x y
  WithdrawalsExceedAccountBalance _ -> error "Impossible: `WithdrawalsExceedAccountBalance` for SUBUTXO"
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L343-427)
```haskell
dijkstraUtxoTransition = do
  TRC (DijkstraUtxoEnv slot pp certState originalUtxo, utxos, stAnnTx) <-
    judgmentContext
  let tx = stAnnTx ^. txStAnnTxG
  -- this is the original Accounts, before any transactions were applied
  let accounts = certState ^. certDStateL . accountsL

  let txBody = tx ^. bodyTxL

  {- inInterval (SlotOf Γ) (ValidIntervalOf txTop) -}
  runTest $ Allegra.validateOutsideValidityIntervalUTxO slot txBody

  sysSt <- liftSTS $ asks systemStart
  ei <- liftSTS $ asks epochInfo

  runTest $ Alonzo.validateOutsideForecast ei slot sysSt tx

  {- SpendInputs ≠ ∅ -}
  runTestOnSignal $ Shelley.validateInputSetEmptyUTxO txBody

  let allInputs = txBody ^. allInputsTxBodyF
      inputs = txBody ^. inputsTxBodyL

  {- SpendInputsOf txTop ∪ RefInputsOf txTop ∪ CollInputsOf txTop ⊆ dom(utxo₀) -}
  runTest $ Shelley.validateBadInputsUTxO originalUtxo allInputs

  {- SpendInputsOf txTop ⊆ dom(utxo_s) — prevents double-spend with subtxs -}
  runTest $ Shelley.validateBadInputsUTxO (utxosUtxo utxos) inputs

  {- minfee pp txTop utxo₀ ≤ txfee txb -}
  runTest $ Shelley.validateFeeTooSmallUTxO pp tx originalUtxo

  {- (RedeemersOf txTop ≠ ∅ ⊎ Any (λ txSub → RedeemersOf txSub ≠ ∅) subtxs) → collateralCheck -}
  validate $ validateBatchCollateral pp tx originalUtxo

  runTest $ validateBatchWithdrawals accounts tx

  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody

  {- ∀ txout ∈ allOuts txb, getValue txout ≥ inject (serSize txout * coinsPerUTxOByte pp) -}
  let allSizedOutputs = txBody ^. allSizedOutputsTxBodyF
  runTest $ Babbage.validateOutputTooSmallUTxO pp allSizedOutputs

  let allOutputs = fmap sizedValue allSizedOutputs
  {- ∀ txout ∈ allOuts txb, serSize (getValue txout) ≤ maxValSize pp -}
  runTest $ Alonzo.validateOutputTooBigUTxO pp allOutputs

  {- ∀ ( _ ↦ (a,_)) ∈ allOuts txb, a ∈ Addrbootstrap → bootstrapAttrsSize a ≤ 64 -}
  runTestOnSignal $ Shelley.validateOutputBootAddrAttrsTooBig allOutputs

  netId <- liftSTS $ asks networkId

  {- ∀(_ → (a, _)) ∈ allOuts txb, netId a = NetworkId -}
  runTestOnSignal $ Shelley.validateWrongNetwork netId allOutputs

  {- ∀(a → ) ∈ txwdrls txb, netId a = NetworkId -}
  runTestOnSignal $ Shelley.validateWrongNetworkWithdrawal netId txBody

  {- (txnetworkid txb = NetworkId) ∨ (txnetworkid txb = ◇) -}
  runTestOnSignal $ Alonzo.validateWrongNetworkInTxBody netId txBody

  {- direct deposit network IDs -}
  runTestOnSignal $ validateWrongNetworkInDirectDeposit netId txBody

  {- no Ptr in collateral return -}
  validateNoPtrInCollateralReturn txBody

  {- txsize tx ≤ maxTxSize pp -}
  runTestOnSignal $ Shelley.validateMaxTxSizeUTxO pp tx

  {- totExunits tx ≤ maxTxExUnits pp -}
  runTest $ Alonzo.validateExUnitsTooBigUTxO pp tx

  {- ‖collateral tx‖ ≤ maxCollInputs pp -}
  runTest $ Alonzo.validateTooManyCollateralInputs pp txBody

  () <- trans @(EraRule "UTXOS" era) $ TRC ((), (), stAnnTx)
  Babbage.updateUTxOStateByTxValidity
    pp
    certState
    (utxosGovState utxos)
    tx
    (Conway.updateTreasuryDonation tx utxos)

```
