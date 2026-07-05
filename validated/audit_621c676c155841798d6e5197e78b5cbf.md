### Title
Plutus Guard Credential Datum Validation Bypass via Absent Script in `scriptsProvided` — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs`)

---

### Summary

In the Dijkstra era's `SUBUTXOW` rule, the `validateGuardDatums` function silently skips datum-presence enforcement for a `ScriptHashObj` guard credential when the referenced Plutus script is **not found** in `scriptsProvided`. An attacker-controlled subtransaction author can craft a `requiredTopLevelGuards` entry that references a Plutus script hash not present in the witness set, pair it with `SNothing` (no datum), and the check passes without error. This allows a subtransaction to declare a Plutus guard credential without supplying the required datum, bypassing the datum-consistency invariant that the guard mechanism is designed to enforce.

---

### Finding Description

The `validateGuardDatums` function in `SUBUTXOW` is responsible for enforcing that every entry in `requiredTopLevelGuards` carries a datum if and only if the credential is a Plutus script credential:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs:210-235
validateGuardDatums (ScriptsProvided scripts) txBody =
  failureOnNonEmptySet malformed SubMalformedGuardDatums
  where
    malformed =
      Map.foldlWithKey' accum mempty (txBody ^. requiredTopLevelGuardsL)
    accum acc cred mbDatum =
      case credScriptHash cred of
        Nothing ->
          -- Key hash: datum must be SNothing
          ...
        Just scriptHash ->
          case Map.lookup scriptHash scripts of
            Just script
              | isNativeScript script -> ...
              | otherwise ->
                  -- Plutus script: datum must be SJust
                  case mbDatum of
                    SJust _ -> acc
                    SNothing -> Set.insert cred acc
            Nothing -> acc   -- <-- BUG: silently accepts any datum value
```

The critical branch is `Nothing -> acc` at line 235. When `Map.lookup scriptHash scripts` returns `Nothing` — meaning the script is not present in `scriptsProvided` — the accumulator is returned unchanged regardless of whether `mbDatum` is `SNothing` or `SJust`. This means:

- A `ScriptHashObj` guard credential referencing a Plutus script that is absent from `scriptsProvided` is **never checked** for datum presence.
- An attacker can submit a subtransaction with `requiredTopLevelGuards = Map.singleton (ScriptHashObj plutusHash) SNothing` where `plutusHash` is not in the witness scripts, and `validateGuardDatums` will pass without flagging it.

The `scriptsProvided` for a subtransaction is computed by `getBabbageScriptsProvided` applied to the subtransaction alone (not the top-level transaction's scripts), as seen in `getDijkstraScriptsProvided`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs:153-164
getDijkstraScriptsProvided utxo tx =
  withBothTxLevels tx
    ( \topTx ->
        ScriptsProvided $ Map.unions $
          unScriptsProvided (getBabbageScriptsProvided utxo topTx)
            : [ unScriptsProvided (getBabbageScriptsProvided utxo subTx)
              | subTx <- OMap.elems (topTx ^. bodyTxL . subTransactionsTxBodyL) ]
    )
    (getBabbageScriptsProvided utxo)
```

For the `SUBUTXOW` rule, `scriptsProvided = scriptsProvidedStAnnTx stAnnTx` which for a subtransaction resolves to `dsastScriptsProvided` — the scripts provided by the subtransaction itself. If the Plutus script is not included in the subtransaction's witness set (e.g., it is only a reference script in the UTxO not referenced by the subtransaction's inputs), the `Map.lookup` returns `Nothing` and the datum check is skipped entirely.

The analog to the fingerprint bypass is direct: just as the Android app accepted `NULL` as a `CryptoObject` (the required cryptographic proof object) and bypassed authentication, this code accepts `SNothing` (the required datum — the cryptographic argument to the Plutus guard script) when the script is absent from the provided map, bypassing the datum-consistency check.

---

### Impact Explanation

The `requiredTopLevelGuards` field in a subtransaction body is the mechanism by which a subtransaction declares which top-level guard credentials must authorize it. The datum associated with a Plutus guard credential is the data argument passed to the Plutus script when it is evaluated as a guarding purpose. If a subtransaction can declare a Plutus guard credential with `SNothing` datum and pass phase-1 validation, the guard's Plutus script will be invoked without the datum it expects — or the datum-consistency invariant is violated, potentially causing deterministic disagreement between nodes about whether the subtransaction is valid.

Specifically: honest nodes that correctly implement the check would reject the transaction (if the check were enforced), while nodes with this code accept it. This constitutes a **deterministic disagreement between honest nodes from ledger rule evaluation**, matching the High impact category: *Deterministic disagreement between honest nodes from ledger rule evaluation, era transition, serialization, or script/witness validation*.

Additionally, if the guard Plutus script is evaluated with a missing datum (because the datum was not required to be present), the script may pass or fail in an unintended way, potentially allowing unauthorized subtransaction execution — which could affect funds locked by guard-protected scripts.

---

### Likelihood Explanation

The Dijkstra era is the newest era and nested transactions (`SubTx`) are a new feature. Any unprivileged transaction sender who constructs a subtransaction can craft `requiredTopLevelGuards` with a `ScriptHashObj` credential pointing to a Plutus script hash that is not included in the subtransaction's witness scripts. This requires no special privileges — only the ability to submit a transaction. The attacker controls the `requiredTopLevelGuards` map entirely as part of the subtransaction body they author.

Likelihood: **Medium** — requires knowledge of the Dijkstra subtransaction format and deliberate crafting, but no privileged access.

---

### Recommendation

The `Nothing -> acc` branch in `validateGuardDatums` should not silently pass. When a `ScriptHashObj` credential's script hash is not found in `scriptsProvided`, the function cannot determine whether it is a Plutus or native script. The correct behavior is one of:

1. **Treat the absent script as a Plutus script** (conservative): require `SJust` datum when the script is not found, since the script's absence from `scriptsProvided` is itself a separate error that will be caught by `babbageMissingScripts`. This ensures the datum check is not silently bypassed.

2. **Explicitly flag the credential as malformed** when the script is absent: add `Nothing -> Set.insert cred acc` to mark it as a validation failure.

The fix in `validateGuardDatums`:

```haskell
            Nothing -> Set.insert cred acc  -- was: Nothing -> acc
```

This ensures that a `ScriptHashObj` guard credential whose script is not in `scriptsProvided` is always flagged, preventing silent bypass of the datum-consistency check.

---

### Proof of Concept

An attacker constructs a Dijkstra subtransaction with:

```
requiredTopLevelGuards = Map.singleton
  (ScriptHashObj somePlutusScriptHash)  -- hash of a known Plutus script
  SNothing                               -- no datum supplied
```

where `somePlutusScriptHash` is **not** included in the subtransaction's `scriptTxWitsL` (witness scripts). The subtransaction is embedded in a top-level transaction that includes `somePlutusScriptHash` in its `guardsTxBodyL`.

When `dijkstraSubUtxowTransition` runs `validateGuardDatums scriptsProvided txBody` at line 289, `scriptsProvided` for the subtransaction does not contain `somePlutusScriptHash`. The `Map.lookup scriptHash scripts` at line 223 returns `Nothing`, and the `Nothing -> acc` branch at line 235 silently accepts the entry without checking `mbDatum`. The `SubMalformedGuardDatums` failure is never raised, and the subtransaction passes phase-1 validation with a Plutus guard credential that has no datum. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs (L210-235)
```haskell
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L153-164)
```haskell
getDijkstraScriptsProvided utxo tx =
  withBothTxLevels
    tx
    ( \topTx ->
        ScriptsProvided $
          Map.unions $
            unScriptsProvided (getBabbageScriptsProvided utxo topTx)
              : [ unScriptsProvided (getBabbageScriptsProvided utxo subTx)
                | subTx <- OMap.elems (topTx ^. bodyTxL . subTransactionsTxBodyL)
                ]
    )
    (getBabbageScriptsProvided utxo)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L205-205)
```haskell
    , dstbrRequiredTopLevelGuards :: !(Map (Credential Guard) (StrictMaybe (Data era)))
```
