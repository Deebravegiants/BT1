### Title
Missing `validateTooManyCollateralInputs` Enforcement in Alonzo UTXO Transition Rule - (File: `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs`)

---

### Summary

The Alonzo UTXO transition rule (`utxoTransition`) contains a comment stub for the `maxCollateralInputs` check but never calls the corresponding validation function. An attacker can submit an Alonzo-era transaction with an unbounded number of collateral inputs, bypassing the `ppMaxCollateralInputsL` protocol parameter limit that is supposed to cap the number of additional VKey signature verifications per transaction.

---

### Finding Description

In `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs`, the `utxoTransition` function lists every required predicate from the formal spec as a Haskell comment and then calls the corresponding validator. At lines 567–574, after enforcing `totExunits ≤ maxTxExUnits`, the code contains the comment:

```haskell
  {-   totExunits tx ≤ maxTxExUnits pp    -}
  runTest $ validateExUnitsTooBigUTxO pp tx

  {-   ‖collateral tx‖  ≤  maxCollInputs pp   -}

  updatedGovState <-
    trans @(EraRule "UTXOS" era) $ ...
```

The comment `{- ‖collateral tx‖ ≤ maxCollInputs pp -}` is present but the corresponding `runTest $ validateTooManyCollateralInputs pp txBody` call is entirely absent. The function `validateTooManyCollateralInputs` is defined in the same file (lines 467–481) and correctly enforces `numColl <= maxColl` via `ppMaxCollateralInputsL`, but it is never invoked inside `utxoTransition`.

Every successor era correctly enforces this check. In `eras/babbage/impl/src/Cardano/Ledger/Babbage/Rules/Utxo.hs` (lines 411–412):

```haskell
  {-   ‖collateral tx‖  ≤  maxCollInputs pp   -}
  runTest $ Alonzo.validateTooManyCollateralInputs pp txBody
```

And in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs` (lines 417–418):

```haskell
  {- ‖collateral tx‖ ≤ maxCollInputs pp -}
  runTest $ Alonzo.validateTooManyCollateralInputs pp txBody
```

The `grep_search` confirms `validateTooManyCollateralInputs` appears 6 times in the Alonzo file (definition + exports + re-exports) but zero times as a call inside `utxoTransition`, while Babbage and Dijkstra each call it once.

---

### Impact Explanation

The `maxCollateralInputs` protocol parameter exists specifically to bound the number of VKey witness verifications a validator node must perform for collateral inputs. Without this check in the Alonzo UTXO rule, a transaction author can include an arbitrarily large collateral input set. Each collateral input requires an independent VKey signature check. This allows an attacker to craft Alonzo-era transactions that exceed the intended per-transaction validation cost ceiling, constituting a resource-limit bypass outside design parameters.

This matches the allowed Medium impact: *"Attacker-controlled transactions exceed intended validation limits."*

---

### Likelihood Explanation

Alonzo is no longer the active era on Cardano mainnet (the chain is in Conway/Dijkstra). However:

1. The Alonzo `utxoTransition` is still compiled into production node binaries and is invoked when re-validating historical Alonzo-era blocks or when running nodes in Alonzo-era test environments.
2. The `AtMostEra "Babbage" era` constraint on `utxoTransition` means the function is the canonical UTXO rule for the Alonzo era instance; no override exists for Alonzo itself.
3. Any test harness or private network still running at Alonzo protocol version is fully exposed.

Likelihood is **low** on mainnet but **medium** in test/staging environments.

---

### Recommendation

Add the missing enforcement call immediately after the comment at line 570 of `eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs`:

```haskell
  {-   ‖collateral tx‖  ≤  maxCollInputs pp   -}
  runTest $ validateTooManyCollateralInputs pp txBody
```

This mirrors the pattern already used in Babbage and Dijkstra and matches the formal Alonzo specification requirement `‖collateral tx‖ ≤ maxCollateralInputs pp`.

---

### Proof of Concept

**Alonzo `utxoTransition` — missing call** (`eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs`, lines 567–574): [1](#0-0) 

The comment stub is present but no `runTest` call follows it. Execution falls directly into the `UTXOS` sub-transition.

**`validateTooManyCollateralInputs` — defined but uncalled in Alonzo** (`eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Rules/Utxo.hs`, lines 467–481): [2](#0-1) 

**Babbage correctly enforces the same check** (`eras/babbage/impl/src/Cardano/Ledger/Babbage/Rules/Utxo.hs`, lines 411–412): [3](#0-2) 

**Dijkstra also enforces it** (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs`, lines 417–418): [4](#0-3) 

An attacker targeting an Alonzo-era node submits a transaction with `collateralInputsTxBodyL` containing far more entries than `ppMaxCollateralInputsL` permits. The Alonzo UTXO rule accepts the transaction without error, forcing the node to verify every collateral VKey signature beyond the protocol-intended ceiling.

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
