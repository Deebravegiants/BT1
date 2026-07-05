### Title
Silent Skip of Datum-Presence Check for Nonexistent Plutus Guard Scripts in `validateGuardDatums` - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs`)

---

### Summary

In the Dijkstra era's `SUBUTXOW` rule, the `validateGuardDatums` function silently skips the datum-presence check for a Plutus script credential listed in a sub-transaction's `requiredTopLevelGuards` map when the corresponding script is not found in `scriptsProvided`. This is the direct Cardano Ledger analog of the "lack of contract existence check" vulnerability: when the referenced entity (the script) does not exist in the provided set, the validation returns success instead of a predicate failure.

---

### Finding Description

The `validateGuardDatums` function in `dijkstraSubUtxowTransition` is responsible for enforcing the invariant that every Plutus script credential listed in a sub-transaction's `requiredTopLevelGuards` map must carry a datum (`SJust`), while key-hash and native-script credentials must not carry one (`SNothing`). The datum is the argument that will be passed to the Plutus guard script during execution.

The function iterates over the `requiredTopLevelGuards` map and, for each `ScriptHashObj` credential, looks up the script in `scriptsProvided`:

```haskell
accum acc cred mbDatum =
  case credScriptHash cred of
    Nothing ->
      -- Key hash: datum must be SNothing
      ...
    Just scriptHash ->
      case Map.lookup scriptHash scripts of
        Just script
          | isNativeScript script ->
              -- Native script: datum must be SNothing
              ...
          | otherwise ->
              -- Plutus script: datum must be SJust
              case mbDatum of
                SJust _ -> acc
                SNothing -> Set.insert cred acc
        Nothing -> acc   -- ← silent pass when script not found
```

The `Nothing -> acc` branch at line 235 means: if the script hash is absent from `scriptsProvided`, the credential is not added to the `malformed` set, and no predicate failure is raised. An attacker-controlled sub-transaction can therefore include `ScriptHashObj sh -> SNothing` in `requiredTopLevelGuards` (a Plutus script credential with no datum) while ensuring `sh` is absent from `scriptsProvided`, and `validateGuardDatums` will pass without error. [1](#0-0) 

The check is invoked unconditionally in `dijkstraSubUtxowTransition`: [2](#0-1) 

The top-level `UTXOW` rule only verifies that every credential listed in sub-transaction `requiredTopLevelGuards` is present in the top-level `guards` set; it does not re-validate datum presence: [3](#0-2) 

The `requiredTopLevelGuards` field is defined as `Map (Credential Guard) (StrictMaybe (Data era))`, where the `Data` value is the datum argument for the Plutus guard script: [4](#0-3) 

---

### Impact Explanation

The `validateGuardDatums` check enforces a well-formedness invariant: every Plutus script credential in `requiredTopLevelGuards` must carry a datum. This datum is the argument passed to the guard Plutus script during execution. Bypassing this check allows a sub-transaction to declare a Plutus script guard without a datum, violating the intended authorization model.

Concretely:

1. A sub-transaction author lists `ScriptHashObj sh -> SNothing` in `requiredTopLevelGuards` while keeping `sh` out of `scriptsProvided`.
2. `validateGuardDatums` passes silently (the `Nothing -> acc` branch).
3. The top-level transaction includes `ScriptHashObj sh` in its `guards` and the guard script is validated at the top level — but the datum that was supposed to constrain the guard's execution context for this sub-transaction is absent.
4. The guard Plutus script executes without the expected datum argument, potentially passing when it should fail (if the script's logic depends on the datum to enforce a condition).

This maps to the allowed impact: **Medium — attacker-controlled sub-transactions exceed intended validation limits**, specifically by bypassing the datum-presence requirement for Plutus guard scripts, which modifies the effective authorization constraints on sub-transaction execution outside design parameters.

---

### Likelihood Explanation

The entry path is fully attacker-controlled. Any party who can submit a Dijkstra-era transaction with sub-transactions can craft a sub-transaction body with an arbitrary `requiredTopLevelGuards` map. No privileged access, governance majority, or key compromise is required. The attacker only needs to:

- Include a `ScriptHashObj sh -> SNothing` entry in the sub-transaction's `requiredTopLevelGuards`.
- Ensure `sh` is not present in the sub-transaction's `scriptsProvided` (i.e., not in the witness set and not reachable via reference inputs for the sub-tx).
- Include `ScriptHashObj sh` in the top-level `guards` (which the attacker controls as the transaction author).

The Dijkstra era is new, so the attack surface is not yet widely exercised, but the code path is reachable by any unprivileged transaction sender.

---

### Recommendation

In `validateGuardDatums`, the `Nothing -> acc` branch should be replaced with a failure. When a `ScriptHashObj` credential appears in `requiredTopLevelGuards` but the script is not found in `scriptsProvided`, the credential should be treated as malformed (added to the `malformed` set), because the script type cannot be determined and the datum-presence invariant cannot be verified:

```haskell
Nothing -> Set.insert cred acc  -- flag as malformed when script not found
```

This mirrors the design principle stated in the Alonzo ADR: silently ignoring missing data leads to surprising and unfortunate mistakes by script authors. The same principle applies here — a missing script should be a hard phase-1 failure, not a silent pass. [5](#0-4) 

---

### Proof of Concept

1. Construct a Dijkstra-era top-level transaction `txTop` with:
   - A sub-transaction `subTx` whose `requiredTopLevelGuards` contains `{ ScriptHashObj sh -> SNothing }` where `sh` is the hash of a Plutus V4 script.
   - `subTx`'s witness set and reference inputs do **not** include the script `sh`.
   - `txTop`'s `guards` field contains `ScriptHashObj sh`.
   - `txTop`'s witness set includes the script `sh` (so the top-level guard validation passes).

2. Submit `txTop`. The `dijkstraSubUtxowTransition` rule calls `validateGuardDatums` on `subTx`. Because `sh` is absent from `subTx`'s `scriptsProvided`, the `Nothing -> acc` branch fires and no `SubMalformedGuardDatums` failure is raised.

3. The sub-transaction is accepted with a Plutus script guard credential carrying no datum, violating the invariant enforced by `validateGuardDatums` for all other cases. [6](#0-5) [7](#0-6)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs (L202-235)
```haskell
-- | Validate that requiredTopLevelGuards datums are consistent with the credential type:
-- Plutus script credentials must have a datum, key/native script credentials must not.
validateGuardDatums ::
  forall era.
  DijkstraEraTxBody era =>
  ScriptsProvided era ->
  TxBody SubTx era ->
  Test (DijkstraSubUtxowPredFailure era)
validateGuardDatums (ScriptsProvided scripts) txBody =
  failureOnNonEmptySet malformed SubMalformedGuardDatums
  where
    malformed =
      Map.foldlWithKey' accum mempty (txBody ^. requiredTopLevelGuardsL)
    accum acc cred mbDatum =
      case credScriptHash cred of
        Nothing ->
          -- Key hash: datum must be SNothing
          case mbDatum of
            SNothing -> acc
            SJust _ -> Set.insert cred acc
        Just scriptHash ->
          case Map.lookup scriptHash scripts of
            Just script
              | isNativeScript script ->
                  -- Native script: datum must be SNothing
                  case mbDatum of
                    SNothing -> acc
                    SJust _ -> Set.insert cred acc
              | otherwise ->
                  -- Plutus script: datum must be SJust
                  case mbDatum of
                    SJust _ -> acc
                    SNothing -> Set.insert cred acc
            Nothing -> acc
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs (L252-291)
```haskell
dijkstraSubUtxowTransition = do
  TRC (env@(SubUtxoEnv _ pp certState originalUtxo _), utxoState, stAnnTx) <-
    judgmentContext
  let tx = stAnnTx ^. txStAnnTxG
      txBody = tx ^. bodyTxL
      witsKeyHashes = keyHashWitnessesTxWits (tx ^. witsTxL)
      scriptsProvided = scriptsProvidedStAnnTx stAnnTx

  {- ∀[ (vk , σ) ∈ vKeySigs ] isSigned vk (txidBytes txId) σ -}
  runTestOnSignal $ Shelley.validateVerifiedWits tx

  let scriptsNeeded = scriptsNeededStAnnTx stAnnTx
      scriptHashesNeeded = getScriptsHashesNeeded scriptsNeeded

  {- ∀[ s ∈ p1ScriptsNeeded ] validP1Script vKeyHashesProvided txVldt s -}
  runTest $ Babbage.validateFailedBabbageScripts tx scriptsProvided scriptHashesNeeded

  {- vKeyHashesNeeded ⊆ vKeyHashesProvided -}
  runTest $ Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody

  {- dataHashesNeeded ⊆ mapˢ hash dataProvided -}
  runTest $ Alonzo.missingRequiredDatums scriptsProvided originalUtxo tx

  {- txADhash ≡ map hash txAuxData -}
  runTestOnSignal $ Shelley.validateMetadata pp tx

  let scriptIntegrity = mkScriptIntegrity pp tx (plutusLanguagesUsedStAnnTx stAnnTx)
  runTest $ Alonzo.checkScriptIntegrityHash tx pp scriptIntegrity

  runTest $ Alonzo.hasExactSetOfRedeemers tx scriptsProvided scriptsNeeded

  runTest $
    Babbage.validateScriptsWellFormedTxOuts
      pp
      (tx ^. witsTxL . scriptTxWitsL)
      (tx ^. bodyTxL . outputsTxBodyL)

  runTest $ validateGuardDatums scriptsProvided txBody

  trans @(EraRule "SUBUTXO" era) $ TRC (env, utxoState, stAnnTx)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs (L292-297)
```haskell
  {- concatMapˡ (λ txSub → mapˢ proj₁ (TopLevelGuardsOf txSub)) (SubTransactionsOf txTop) ⊆ GuardsOf txTop -}
  let requiredGuardsBySubTxs =
        foldMap (Map.keysSet . (^. bodyTxL . requiredTopLevelGuardsL)) subTxs
      topLevelGuards = OSet.toSet (txBody ^. guardsTxBodyL)
      missingGuards = requiredGuardsBySubTxs `Set.difference` topLevelGuards
  runTestOnSignal $ failureOnNonEmptySet missingGuards MissingRequiredGuards
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L1316-1317)
```haskell
  requiredTopLevelGuardsL ::
    Lens' (TxBody SubTx era) (Map (Credential Guard) (StrictMaybe (Data era)))
```
