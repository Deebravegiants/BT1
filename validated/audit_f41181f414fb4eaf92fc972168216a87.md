### Title
Silent Bypass of Plutus Guard Datum Consistency Check When Script Not in Provided Scripts - (File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs)

### Summary
In the Dijkstra era's `SUBUTXOW` rule, the `validateGuardDatums` function is responsible for enforcing that every `ScriptHashObj` credential listed in a sub-transaction's `requiredTopLevelGuards` map that resolves to a Plutus script must carry a datum (`SJust`). When the script hash is not found in `scriptsProvided`, the function silently returns the accumulator unchanged (`Nothing -> acc`, line 235) instead of flagging the entry as malformed. This is the direct analog of the reported whitelist bug: a guard that should reject an unresolvable credential instead silently passes it, allowing a sub-transaction author to submit a Plutus-script guard credential with no datum and have it accepted at phase-1.

### Finding Description
`validateGuardDatums` in `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs` iterates over every entry in `requiredTopLevelGuards` and classifies each credential:

```
accum acc cred mbDatum =
  case credScriptHash cred of
    Nothing ->                          -- key hash: datum must be SNothing
      ...
    Just scriptHash ->
      case Map.lookup scriptHash scripts of
        Just script
          | isNativeScript script -> ... -- native: datum must be SNothing
          | otherwise ->                 -- Plutus: datum must be SJust
              case mbDatum of
                SJust _ -> acc
                SNothing -> Set.insert cred acc
        Nothing -> acc                  -- ← BUG: script absent, check silently skipped
``` [1](#0-0) 

The function's own doc-comment states: *"Plutus script credentials must have a datum, key/native script credentials must not."* The `Nothing -> acc` branch at line 235 violates this invariant: when `Map.lookup scriptHash scripts` returns `Nothing` (the script is absent from `scriptsProvided`), the credential is silently accepted regardless of whether `mbDatum` is `SNothing` or `SJust`.

**Attacker-controlled entry path:**

1. An unprivileged sub-transaction author constructs a `DijkstraSubTxBody` whose `requiredTopLevelGuards` field contains a `ScriptHashObj sh` credential mapped to `SNothing`, where `sh` is the hash of a Plutus script that is **not** included in the sub-transaction's witness set and is not reachable as a reference script from the sub-transaction's inputs.
2. Because the script is absent from `scriptsProvided`, `Map.lookup sh scripts` returns `Nothing`, and `validateGuardDatums` adds nothing to `malformed`. The `SubMalformedGuardDatums` predicate failure is never raised.
3. The sub-transaction passes phase-1 (`SUBUTXOW`) validation and is accepted into a block.
4. The top-level transaction that embeds this sub-transaction must now honour the declared guard credential. When the top-level UTXOW rule evaluates the guard, it attempts to invoke the Plutus script without the datum that the script requires, producing a phase-2 failure and consuming the top-level submitter's collateral. [2](#0-1) 

The `babbageMissingScripts` check that runs earlier in `dijkstraSubUtxowTransition` does **not** cover this case: guard scripts declared in `requiredTopLevelGuards` are executed at the top-level, not the sub-transaction level, so they are absent from the sub-transaction's `scriptsNeeded` set and are invisible to the missing-scripts check. [3](#0-2) 

### Impact Explanation
The bypass allows an attacker-controlled sub-transaction to exceed the intended phase-1 validation limit: a `ScriptHashObj` guard credential with `SNothing` datum is accepted when it should be rejected. The malformed `requiredTopLevelGuards` entry propagates into a committed block. Any top-level transaction that embeds the sub-transaction will attempt to invoke the Plutus guard script without its required datum, causing a deterministic phase-2 failure and collateral loss for the top-level submitter. This matches the **Medium** allowed impact: *"Attacker-controlled transactions … exceed intended validation limits."*

### Likelihood Explanation
The exploit requires only that the sub-transaction author reference a script hash not present in the sub-transaction's `scriptsProvided`. This is trivially achievable by any unprivileged transaction sender who can author a sub-transaction body. No privileged access, key compromise, or consensus majority is needed. The Dijkstra era is experimental/upcoming, but the code path is live in the repository and will be exercised once the era activates.

### Recommendation
Replace the silent `Nothing -> acc` branch with a failure that adds the credential to `malformed`:

```haskell
Nothing ->
  -- Script not provided: cannot confirm it is native; treat as malformed
  -- (a missing Plutus guard script credential must still carry a datum)
  Set.insert cred acc
```

Alternatively, if the design intent is that unresolvable script hashes are caught by a separate check, that separate check must be made to cover guard credentials in `requiredTopLevelGuards` explicitly, and the current silent pass must be documented with a proof that no datum-less Plutus guard can reach the top-level execution path.

### Proof of Concept
Construct a `DijkstraSubTxBody` with:
```
requiredTopLevelGuards = { ScriptHashObj phantomHash ↦ SNothing }
```
where `phantomHash` is the hash of any Plutus script that is **not** in the sub-transaction's witness scripts and not reachable via reference inputs. Submit this sub-transaction embedded in a top-level Dijkstra transaction. Observe that `validateGuardDatums` raises no `SubMalformedGuardDatums` failure (the `Nothing -> acc` branch is taken), the sub-transaction is accepted at phase-1, and the top-level transaction subsequently fails at phase-2 when it attempts to invoke the Plutus guard without a datum. [4](#0-3)

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs (L237-291)
```haskell
dijkstraSubUtxowTransition ::
  forall era.
  ( AlonzoEraTx era
  , AlonzoEraUTxO era
  , DijkstraEraTxBody era
  , EraRule "SUBUTXO" era ~ SUBUTXO era
  , EraRule "SUBUTXOW" era ~ SUBUTXOW era
  , Embed (EraRule "SUBUTXO" era) (SUBUTXOW era)
  , InjectRuleFailure "SUBUTXOW" Alonzo.AlonzoUtxowPredFailure era
  , InjectRuleFailure "SUBUTXOW" Shelley.ShelleyUtxowPredFailure era
  , InjectRuleFailure "SUBUTXOW" Babbage.BabbageUtxowPredFailure era
  , InjectRuleFailure "SUBUTXOW" DijkstraSubUtxowPredFailure era
  , ScriptsNeeded era ~ AlonzoScriptsNeeded era
  ) =>
  TransitionRule (EraRule "SUBUTXOW" era)
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
