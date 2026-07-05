### Title
PlutusV4 Scripts Excluded from Era Language Validation Due to Incorrect `eraMaxLanguage` - (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs`)

### Summary

The `DijkstraEra` declares `eraMaxLanguage = PlutusV3` while simultaneously providing full PlutusV4 infrastructure (constructors, `mkPlutusScript`, `mkSupportedLanguage`, `TxInfoResult` field). This is the direct analog of the DAI permit mismatch: a specific variant (PlutusV4) is fully wired in at one level but silently excluded from the interface that governs era-wide language enumeration, causing PlutusV4 scripts to fall outside the `eraLanguages`-based validation path.

### Finding Description

In `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs`, the `AlonzoEraScript DijkstraEra` instance sets:

```haskell
eraMaxLanguage = PlutusV3
``` [1](#0-0) 

Yet the same instance defines a `DijkstraPlutusV4` constructor, accepts PlutusV4 in `mkPlutusScript`, and the `EraPlutusContext DijkstraEra` instance returns `Just (SupportedLanguage SPlutusV4)` from `mkSupportedLanguage` and includes a `PlutusV4` slot in `DijkstraTxInfoResult`: [2](#0-1) [3](#0-2) 

The CDDL specification for Dijkstra explicitly lists PlutusV4 as script type `4` and cost model index `3`: [4](#0-3) 

The core ledger derives `eraLanguages` directly from `eraMaxLanguage`:

```haskell
eraLanguages :: forall era. AlonzoEraScript era => [Language]
eraLanguages = [minBound .. eraMaxLanguage @era]
``` [5](#0-4) 

And `supportedLanguages`, which drives the script integrity hash computation, enumerates only up to `eraMaxLanguage`:

```haskell
supportedLanguages =
  let langs = [ errorFail (mkSupportedLanguageM lang)
              | lang <- [minBound .. eraMaxLanguage @era] ]
``` [6](#0-5) 

Because `eraMaxLanguage = PlutusV3`, `eraLanguages` for `DijkstraEra` is `[PlutusV1, PlutusV2, PlutusV3]`. PlutusV4 is absent. Any validation path that iterates `eraLanguages` — including the script integrity hash (`ScriptIntegrity`) computation that commits the cost model for each language used in a transaction — will silently omit the PlutusV4 cost model.

The script integrity hash is the ledger's mechanism to ensure that the cost model used during script execution is the same one the transaction author committed to. If PlutusV4 is excluded from this commitment, a transaction carrying a PlutusV4 script can be submitted without binding to the PlutusV4 cost model. A subsequent protocol-parameter update that changes the PlutusV4 cost model would alter the execution budget consumed by that script without invalidating the transaction's integrity hash, breaking the determinism guarantee.

### Impact Explanation

**High — Deterministic disagreement between honest nodes from ledger rule evaluation.**

A transaction with a PlutusV4 script submitted under one PlutusV4 cost model and included in a block under a different one (after a `ParameterChange` governance action) will be evaluated with a different resource budget than the author committed to. Nodes that apply the transaction at different protocol-parameter snapshots may reach different conclusions about whether the script execution stays within the declared `ExUnits`, producing divergent ledger states. This constitutes a deterministic disagreement from ledger rule evaluation that cannot be resolved without a hard fork.

Additionally, because the PlutusV4 cost model is not committed to in the transaction body, an attacker who can time a `ParameterChange` enactment can cause a previously-valid PlutusV4 transaction to consume more execution units than declared, effectively manipulating fees and execution limits outside design parameters.

### Likelihood Explanation

PlutusV4 is gated behind protocol version 12 (`guardPlutus` in `Language.hs`): [7](#0-6) 

Once the Dijkstra era activates at protocol version 12, any unprivileged transaction sender can submit a transaction with a PlutusV4 script. The `mkPlutusScript` path for `DijkstraEra` accepts `SPlutusV4` without restriction. The triggering condition (a `ParameterChange` governance action altering the PlutusV4 cost model) is a normal on-chain governance operation, not an exotic attack. The window between transaction submission and block inclusion is sufficient for a governance action to be enacted, particularly given the mempool's typical depth.

### Recommendation

Change `eraMaxLanguage` for `DijkstraEra` from `PlutusV3` to `PlutusV4`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs
eraMaxLanguage = PlutusV4   -- was PlutusV3
```

This ensures `eraLanguages`, `supportedLanguages`, and all downstream script integrity hash computations include the PlutusV4 cost model, restoring the determinism guarantee for PlutusV4 scripts.

### Proof of Concept

1. `eraMaxLanguage = PlutusV3` for `DijkstraEra`: [1](#0-0) 

2. `eraLanguages` is derived directly from `eraMaxLanguage`, so PlutusV4 is absent: [5](#0-4) 

3. `supportedLanguages` (used in script integrity hash) enumerates only up to `eraMaxLanguage`, excluding PlutusV4: [8](#0-7) 

4. Yet `mkSupportedLanguage` for `DijkstraEra` returns `Just` for PlutusV4, and `mkPlutusScript` accepts it — confirming PlutusV4 is intended to be fully supported: [9](#0-8) 

5. The Dijkstra CDDL spec and cost model definitions confirm PlutusV4 is a first-class language in this era: [10](#0-9)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L436-453)
```haskell
instance AlonzoEraScript DijkstraEra where
  data PlutusScript DijkstraEra
    = DijkstraPlutusV1 !(Plutus 'PlutusV1)
    | DijkstraPlutusV2 !(Plutus 'PlutusV2)
    | DijkstraPlutusV3 !(Plutus 'PlutusV3)
    | DijkstraPlutusV4 !(Plutus 'PlutusV4)
    deriving (Eq, Ord, Show, Generic)

  type PlutusPurpose f DijkstraEra = DijkstraPlutusPurpose f DijkstraEra

  eraMaxLanguage = PlutusV3

  mkPlutusScript plutus =
    case plutusSLanguage plutus of
      SPlutusV1 -> pure $ DijkstraPlutusV1 plutus
      SPlutusV2 -> pure $ DijkstraPlutusV2 plutus
      SPlutusV3 -> pure $ DijkstraPlutusV3 plutus
      SPlutusV4 -> pure $ DijkstraPlutusV4 plutus
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs (L221-232)
```haskell
  data TxInfoResult DijkstraEra
    = DijkstraTxInfoResult -- Fields must be kept lazy
        (PlutusTxInfoResult 'PlutusV1 DijkstraEra)
        (PlutusTxInfoResult 'PlutusV2 DijkstraEra)
        (PlutusTxInfoResult 'PlutusV3 DijkstraEra)
        (PlutusTxInfoResult 'PlutusV4 DijkstraEra)

  mkSupportedLanguage = \case
    PlutusV1 -> Just $ SupportedLanguage SPlutusV1
    PlutusV2 -> Just $ SupportedLanguage SPlutusV2
    PlutusV3 -> Just $ SupportedLanguage SPlutusV3
    PlutusV4 -> Just $ SupportedLanguage SPlutusV4
```

**File:** eras/dijkstra/impl/cddl/lib/Cardano/Ledger/Dijkstra/HuddleSpec.hs (L339-353)
```haskell
dijkstraScriptRule pname p =
  comment
    [str| Dijkstra supports five script types:
        |   0: Native scripts with guard support (7 variants)
        |   1: Plutus V1 scripts
        |   2: Plutus V2 scripts
        |   3: Plutus V3 scripts
        |   4: Plutus V4 scripts (NEW)
        |]
    $ pname
      =.= arr [0, a (huddleRule @"native_script" p)]
      / arr [1, a (huddleRule @"plutus_v1_script" p)]
      / arr [2, a (huddleRule @"plutus_v2_script" p)]
      / arr [3, a (huddleRule @"plutus_v3_script" p)]
      / arr [4, a (huddleRule @"plutus_v4_script" p)]
```

**File:** eras/dijkstra/impl/cddl/lib/Cardano/Ledger/Dijkstra/HuddleSpec.hs (L1145-1165)
```haskell
instance HuddleRule "cost_models" DijkstraEra where
  huddleRuleNamed pname p =
    comment
      [str| The format for cost_models is flexible enough to allow adding
          | Plutus built-ins and language versions in the future.
          |
          | Plutus v1: only 166 integers are used, but more are accepted (and ignored)
          | Plutus v2: only 175 integers are used, but more are accepted (and ignored)
          | Plutus v3: only 223 integers are used, but more are accepted (and ignored)
          | Plutus v4: TBD integers are used (NEW)
          |
          | Any 8-bit unsigned number can be used as a key.
          |]
      $ withCBORGen (conwayCostModelsGenerator @DijkstraEra)
      $ pname
        =.= mp
          [ opt $ idx 0 ==> arr [0 <+ a (huddleRule @"int64" p)]
          , opt $ idx 1 ==> arr [0 <+ a (huddleRule @"int64" p)]
          , opt $ idx 2 ==> arr [0 <+ a (huddleRule @"int64" p)]
          , opt $ idx 3 ==> arr [0 <+ a (huddleRule @"int64" p)]
          , 0 <+ asKey ((4 :: Integer) ... (255 :: Integer)) ==> arr [0 <+ a (huddleRule @"int64" p)]
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Scripts.hs (L749-750)
```haskell
eraLanguages :: forall era. AlonzoEraScript era => [Language]
eraLanguages = [minBound .. eraMaxLanguage @era]
```

**File:** eras/alonzo/impl/src/Cardano/Ledger/Alonzo/Plutus/Context.hs (L320-331)
```haskell
supportedLanguages ::
  forall era.
  (HasCallStack, EraPlutusContext era) =>
  NonEmpty (SupportedLanguage era)
supportedLanguages =
  let langs =
        [ errorFail (mkSupportedLanguageM lang)
        | lang <- [minBound .. eraMaxLanguage @era]
        ]
   in case nonEmpty langs of
        Nothing -> error "Impossible: there are no supported languages"
        Just neLangs -> neLangs
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/Plutus/Language.hs (L576-584)
```haskell
guardPlutus :: Language -> Decoder s ()
guardPlutus lang =
  let v = case lang of
        PlutusV1 -> natVersion @5
        PlutusV2 -> natVersion @7
        PlutusV3 -> natVersion @9
        PlutusV4 -> natVersion @12
   in unlessDecoderVersionAtLeast v $
        fail (show lang <> " is not supported until " <> show v <> " major protocol version")
```
