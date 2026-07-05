### Title
Missing `maxCollateralInputs` Enforcement in Alonzo UTXO Transition Rule - (File: `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs`)

---

### Summary
The `utxoTransition` function in the Alonzo UTXO STS rule contains a comment indicating the `maxCollateralInputs` check should be enforced, but the corresponding `runTest` call is absent. The `validateTooManyCollateralInputs` function is defined but never invoked in this transition, meaning the `maxCollateralInputs` protocol parameter is not enforced in the Alonzo era. An unprivileged transaction sender can submit a transaction with an unbounded number of collateral inputs, forcing validators to perform more VKey signature verifications than the protocol parameter was designed to permit.

---

### Finding Description

In `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs`, the `utxoTransition` function (lines 505–595) applies a sequence of validation checks. Every other check in the function is followed by a `runTest` or `runTestOnSignal` call. At line 570, a comment marks where the collateral count check should appear:

```haskell
  {-   ‖collateral tx‖  ≤  maxCollInputs pp   -}

  updatedGovState <-
    trans @(EraRule "UTXOS" era) $
``` [1](#0-0) 

There is no `runTest $ validateTooManyCollateralInputs pp txBody` call between the comment and the `trans` invocation. The function `validateTooManyCollateralInputs` is fully implemented at lines 467–481:

```haskell
validateTooManyCollateralInputs pp txBody =
  failureUnless (numColl <= maxColl) $
    TooManyCollateralInputs Mismatch {mismatchSupplied = numColl, mismatchExpected = maxColl}
  where
    maxColl = pp ^. ppMaxCollateralInputsL
    numColl = fromIntegral . Set.size $ txBody ^. collateralInputsTxBodyL
``` [2](#0-1) 

By contrast, the Babbage era's `babbageUtxoValidation` (which is also used by Conway via `Babbage.babbageUtxoValidation`) correctly enforces the limit:

```haskell
  {-   ‖collateral tx‖  ≤  maxCollInputs pp   -}
  runTest $ Alonzo.validateTooManyCollateralInputs pp txBody
``` [3](#0-2) 

The Dijkstra era also enforces it independently: [4](#0-3) 

The Alonzo `utxoTransition` carries the `AtMostEra "Babbage" era` constraint, scoping it to the Alonzo era only (Babbage and later eras use their own transition rules that include the check). [5](#0-4) 

The formal specification explicitly states the purpose of `maxCollateralInputs`: *"The parameter maxCollateralInputs is used to limit, additionally, the total number of collateral inputs, and thus the total number of additional signatures that must be checked during validation."* [6](#0-5) 

---

### Impact Explanation

Each collateral input must be a VKey address (enforced by `validateScriptsNotPaidUTxO` inside `feesOK`). Each such input requires a signature witness and a corresponding signature verification. The `maxCollateralInputs` parameter was introduced precisely to bound the number of these verifications per transaction. Without the enforcement call in `utxoTransition`, an attacker can include as many collateral inputs as the `maxTxSize` byte limit allows — far more than `maxCollateralInputs` permits — forcing every validating node to perform unbounded signature verification work per transaction. This directly exceeds the intended per-transaction validation resource limit set by the protocol parameter, matching the **Medium** impact: *attacker-controlled transactions exceed intended validation limits*.

---

### Likelihood Explanation

The Alonzo era is no longer the active era on mainnet (Conway/Dijkstra is current). However, the Alonzo UTXO rule is still present in the production codebase and is exercised during historical block replay. Any node replaying Alonzo-era blocks, or any private/test network running in the Alonzo era, is subject to this missing check. An unprivileged transaction sender requires no special keys or privileges — only the ability to submit a transaction with many collateral inputs. The attack is straightforward to construct.

---

### Recommendation

Add the missing enforcement call in `utxoTransition` in `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs`, immediately after the existing comment at line 570:

```haskell
  {-   ‖collateral tx‖  ≤  maxCollInputs pp   -}
  runTest $ validateTooManyCollateralInputs pp txBody
```

This mirrors the correct pattern already present in `babbageUtxoValidation` and the Dijkstra UTXO rule.

---

### Proof of Concept

1. Construct an Alonzo-era transaction with `N > maxCollateralInputs` collateral inputs, each referencing a distinct VKey UTxO with a corresponding signature witness. Keep total serialized size within `maxTxSize`.
2. Submit the transaction to a node running in the Alonzo era (or replay an Alonzo-era block containing such a transaction).
3. Observe that `utxoTransition` accepts the transaction: the comment at line 570 is present but no `runTest` call follows it, so `validateTooManyCollateralInputs` is never invoked and the `TooManyCollateralInputs` predicate failure is never raised.
4. The node performs `N` VKey signature verifications — exceeding the `maxCollateralInputs` bound — for a single transaction, violating the resource limit the protocol parameter was designed to enforce.

### Citations

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs (L467-481)
```haskell
-- | Ensure that number of collaterals does not exceed the allowed @maxCollInputs@ parameter.
--
-- > ‖collateral tx‖  ≤  maxCollInputs pp
validateTooManyCollateralInputs ::
  AlonzoEraTxBody era =>
  PParams era ->
  TxBody TopTx era ->
  Test (AlonzoUtxoPredFailure era)
validateTooManyCollateralInputs pp txBody =
  failureUnless (numColl <= maxColl) $
    TooManyCollateralInputs Mismatch {mismatchSupplied = numColl, mismatchExpected = maxColl}
  where
    maxColl, numColl :: Word16
    maxColl = pp ^. ppMaxCollateralInputsL
    numColl = fromIntegral . Set.size $ txBody ^. collateralInputsTxBodyL
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs (L486-504)
```haskell
utxoTransition ::
  forall era.
  ( EraUTxO era
  , AlonzoEraTx era
  , AtMostEra "Babbage" era
  , EraRule "UTXO" era ~ UTXO era
  , InjectRuleFailure "UTXO" Shelley.ShelleyUtxoPredFailure era
  , InjectRuleFailure "UTXO" AlonzoUtxoPredFailure era
  , InjectRuleFailure "UTXO" Allegra.AllegraUtxoPredFailure era
  , Embed (EraRule "UTXOS" era) (UTXO era)
  , Environment (EraRule "UTXOS" era) ~ UtxosEnv era
  , State (EraRule "UTXOS" era) ~ ShelleyGovState era
  , Signal (EraRule "UTXOS" era) ~ StAnnTx TopTx era
  , EraCertState era
  , EraStake era
  , SafeToHash (TxWits era)
  , GovState era ~ ShelleyGovState era
  ) =>
  TransitionRule (EraRule "UTXO" era)
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs (L567-574)
```haskell
  {-   totExunits tx ≤ maxTxExUnits pp    -}
  runTest $ validateExUnitsTooBigUTxO pp tx

  {-   ‖collateral tx‖  ≤  maxCollInputs pp   -}

  updatedGovState <-
    trans @(EraRule "UTXOS" era) $
      TRC (UtxosEnv slot pp certState, utxosGovState utxos, stAnnTx)
```

**File:** eras/babbage/impl/src/Cardano/Ledger/Babbage/Rules/Utxo.hs (L411-412)
```haskell
  {-   ‖collateral tx‖  ≤  maxCollInputs pp   -}
  runTest $ Alonzo.validateTooManyCollateralInputs pp txBody
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L417-418)
```haskell
  {- ‖collateral tx‖ ≤ maxCollInputs pp -}
  runTest $ Alonzo.validateTooManyCollateralInputs pp txBody
```

**File:** eras/alonzo/formal-spec/protocol-parameters.tex (L115-120)
```tex
The parameter $\var{collateralPercent}$ is used to specify the percentage of
the total transaction fee its collateral must (at minimum) cover. The
collateral inputs must not themselves be locked by a script. That is, they must
be VKey inputs. The parameter $\var{maxCollateralInputs}$ is used to limit, additionally,
the total number of collateral inputs, and thus the total number of additional
signatures that must be checked during validation.
```
