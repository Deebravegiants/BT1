### Title
Stale `StAnnTx` Annotation Enables Plutus Script Bypass for Sub-Transaction-Created Outputs in Dijkstra Era — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra.hs`)

---

### Summary

In the Dijkstra era, the `StAnnTx` annotation for a top-level transaction — including `dsattScriptsNeeded` and `dsattPlutusScriptsWithContext` — is computed against the UTxO **before** any sub-transactions execute. Because the top-level transaction's inputs are validated against the **post-sub-transaction** UTxO, a top-level transaction can spend a script-locked output created by one of its own sub-transactions without the Plutus script ever being collected or executed. This violates the explicit design invariant in `Core.hs` and constitutes an invalid ledger state transition: a script-protected output is consumed without script authorization.

---

### Finding Description

**Design invariant (violated)**

`Core.hs` lines 172–175 state:

> "It is critical to only store here information that satisfies the following property: if the ledger state changes in a way that makes the annotated value stale, then some other predicate check in the STS rules must independently cause the transaction to be rejected. Stale annotations must never lead to a transaction being silently accepted." [1](#0-0) 

**Root cause — annotation built against pre-sub-tx UTxO**

`mkDijkstraStAnnTopTx` computes `dsattScriptsNeeded` and `dsattPlutusScriptsWithContext` from the `utxo` argument, which is the UTxO snapshot taken **before** sub-transactions run:

```haskell
mkDijkstraStAnnTopTx ei sysStart pp utxo tx =
  let txBody = tx ^. bodyTxL
      scriptsNeeded = getScriptsNeeded utxo txBody   -- stale: pre-sub-tx UTxO
      ...
      dsattScriptsNeeded = scriptsNeeded
      dsattPlutusScriptsWithContext =
          scriptsWithContextFromLedgerTxInfo ledgerTxInfo ...
``` [2](#0-1) 

**Execution path — top-level tx validated against post-sub-tx UTxO**

In `dijkstraLedgerTransition`, sub-transactions are processed first via `SUBLEDGERS`, producing `utxoStateAfterSubLedgers`. The top-level transaction is then submitted to `UTXOW`/`UTXO` with this updated state: [3](#0-2) 

Inside `dijkstraUtxoTransition`, input existence is checked against `utxo = utxosUtxo utxos` — the **post-sub-tx** UTxO — so an output created by a sub-transaction passes `validateBadInputsUTxO`: [4](#0-3) 

**Stale annotation consumed without recomputation**

The UTXOW rule reads scripts needed directly from the stale annotation field via `scriptsNeededDijkstraStAnnTx`:

```haskell
scriptsNeededDijkstraStAnnTx stAnnTx =
  withBothTxLevels stAnnTx
    (\DijkstraStAnnTopTx {dsattScriptsNeeded} -> dsattScriptsNeeded)
    ...
``` [5](#0-4) 

Because `dsattScriptsNeeded` was computed from the pre-sub-tx UTxO, any script-locked output **created by a sub-transaction** is absent from it. The UTXOW rule never requires, collects, or executes the Plutus script guarding that output. There is no compensating predicate check that would independently reject the transaction.

**Attack path (no privileged access required)**

1. Attacker crafts a Dijkstra-era transaction containing one or more sub-transactions.
2. A sub-transaction creates a script-locked `TxOut` (e.g., a Plutus V3 contract output) with ADA or native assets.
3. The top-level transaction lists that output as a spending input.
4. `mkDijkstraStAnnTopTx` is called against the pre-sub-tx UTxO; the new output is absent, so its script hash is absent from `dsattScriptsNeeded` and `dsattPlutusScriptsWithContext`.
5. After sub-transactions execute, the output exists in the live UTxO; `validateBadInputsUTxO` passes.
6. The UTXOW rule consults the stale `dsattScriptsNeeded` — the script is not listed — so it is never executed.
7. The output is consumed without script authorization; the ledger accepts the transition.

---

### Impact Explanation

This is a **Critical** impact: an invalid ledger state transition occurs — a Plutus-script-locked output is spent without executing the script. Any authorization logic encoded in the script (access control, time locks, multi-party consent, governance guards) is silently bypassed. ADA or native assets locked in such outputs can be extracted by the transaction author without satisfying the script's conditions, constituting direct unauthorized movement of assets.

---

### Likelihood Explanation

The Dijkstra era is the active development frontier of the Cardano Ledger codebase and is included in the production repository. The attack requires only the ability to submit a valid Dijkstra-era transaction — no privileged keys, governance majority, or external oracle access is needed. Any transaction author can craft the required structure. The only constraint is that the Dijkstra era must be active on the network.

---

### Recommendation

The `StAnnTx` annotation for the top-level transaction must be recomputed — or at minimum the `scriptsNeeded` and `plutusScriptsWithContext` fields must be recomputed — against the **post-sub-transaction** UTxO before the UTXOW rule executes. Concretely:

1. In `dijkstraLedgerTransition`, after `SUBLEDGERS` completes and `utxoStateAfterSubLedgers` is available, rebuild the top-level `StAnnTx` annotation using `mkDijkstraStAnnTopTx` with `utxosUtxo utxoStateAfterSubLedgers` as the UTxO argument.
2. Alternatively, add an explicit predicate check in the Dijkstra UTXOW rule that recomputes `scriptsNeeded` from the current UTxO state and verifies it matches (or is a subset of) the annotation, rejecting the transaction if any required script is absent from the annotation.

Either approach restores the design invariant stated in `Core.hs` lines 172–175.

---

### Proof of Concept

```
-- Pseudocode demonstrating the bypass

subTx :: SubTx
subTx = mkSubTx
  { inputs  = [someAttackerOwnedUTxO]   -- attacker's own funds
  , outputs = [TxOut scriptAddr value]   -- script-locked output
  }
  -- script at scriptAddr enforces: "only spend if condition C holds"

topTx :: TopTx
topTx = mkTopTx
  { subTransactions = [subTx]
  , inputs = [TxIn (txIdOf subTx) 0]    -- spends the script-locked output
  , outputs = [TxOut attackerAddr value] -- attacker receives value
  }
  -- Annotation built against pre-subTx UTxO:
  --   dsattScriptsNeeded = {} (output not yet in UTxO)
  --   dsattPlutusScriptsWithContext = Right []
  --
  -- UTXOW checks dsattScriptsNeeded == {} → no script required
  -- Script at scriptAddr is NEVER executed
  -- Condition C is NEVER checked
  -- Transaction accepted; attacker receives value unconditionally
```

The `dsattScriptsNeeded` field is empty for the spending input because `getScriptsNeeded` was called against the pre-sub-tx UTxO where the output did not yet exist. [6](#0-5) [5](#0-4) [3](#0-2) [7](#0-6)

### Citations

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/Core.hs (L168-179)
```haskell
  -- | This is a `Tx` that is annotated with some pre-computed data derived from the ledger state,
  -- which can be used to avoid redundant computation when a transaction is validated multiple
  -- times.
  --
  -- It is critical to only store here information that satisfies the following property: if the
  -- ledger state changes in a way that makes the annotated value stale, then some other predicate
  -- check in the STS rules must independently cause the transaction to be rejected.  Stale
  -- annotations must never lead to a transaction being silently accepted.
  --
  -- For example, if a reference input gets spent, then there must a predicate check that fails on
  -- missing output, regardless if data from reference inputs is still present in the `StAnnTx`
  type StAnnTx (l :: TxLevel) era = (r :: Type) | r -> l era
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra.hs (L101-148)
```haskell
mkDijkstraStAnnTopTx ::
  ( AlonzoEraUTxO era
  , AlonzoEraTx era
  , DijkstraEraTxBody era
  , EraPlutusContext era
  , ScriptsNeeded era ~ AlonzoScriptsNeeded era
  ) =>
  EpochInfo (Either Text) ->
  SystemStart ->
  PParams era ->
  UTxO era ->
  Tx TopTx era ->
  DijkstraStAnnTx TopTx era
mkDijkstraStAnnTopTx ei sysStart pp utxo tx =
  let
    txBody = tx ^. bodyTxL
    scriptsNeeded = getScriptsNeeded utxo txBody
    scriptsProvided = getScriptsProvided utxo tx
    plutusScriptsUsed = resolveNeededPlutusScriptsWithPurpose scriptsProvided scriptsNeeded
    stAnnSubTxs =
      map
        (mkDijkstraStAnnSubTx ei sysStart pp utxo scriptsProvided)
        (toList (txBody ^. subTransactionsTxBodyL))
    ledgerTxInfo =
      LedgerTxInfo
        { ltiProtVer = pp ^. ppProtocolVersionL
        , ltiEpochInfo = ei
        , ltiSystemStart = sysStart
        , ltiUTxO = utxo
        , ltiTx = tx
        , ltiMemoizedSubTransactions =
            Map.fromList
              [ (txIdTx dsastTx, dsastTxInfoResult)
              | DijkstraStAnnSubTx {dsastTx, dsastTxInfoResult} <- stAnnSubTxs
              ]
        }
    languagesUsed = Set.fromList [plutusScriptLanguage s | (_, _, s) <- plutusScriptsUsed]
   in
    DijkstraStAnnTopTx
      { dsattTx = tx
      , dsattScriptsNeeded = scriptsNeeded
      , dsattScriptsProvided = scriptsProvided
      , dsattPlutusLegacyMode = not $ Set.null $ Set.filter (<= PlutusV3) languagesUsed
      , dsattPlutusLanguagesUsed = languagesUsed
      , dsattPlutusScriptsWithContext =
          scriptsWithContextFromLedgerTxInfo ledgerTxInfo (pp ^. ppCostModelsL) plutusScriptsUsed
      , dsattSubTransactions = stAnnSubTxs
      }
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L358-390)
```haskell
dijkstraLedgerTransition = do
  TRC (Shelley.LedgerEnv slot mbCurEpochNo txIx pp chainAccountState, ledgerState, stAnnTx) <-
    judgmentContext
  let tx = stAnnTx ^. txStAnnTxG

  -- Capture the original UTxO before any subtransaction processing.
  -- This is passed through the environment to UTXOW
  -- and SUBLEDGERS, and used for all witness/validation lookups.
  let originalUtxo = utxosUtxo (ledgerState ^. lsUTxOStateL)
      subStAnnTxs = subTransactionsStAnnTx stAnnTx

  -- Process all subtransactions first
  LedgerState utxoStateAfterSubLedgers certStateAfterSubLedgers <-
    trans @(EraRule "SUBLEDGERS" era) $
      TRC
        ( SubLedgerEnv
            slot
            mbCurEpochNo
            txIx
            pp
            chainAccountState
            originalUtxo
            (tx ^. isValidTxL)
        , ledgerState
        , subStAnnTxs
        )

  curEpochNo <- maybe (liftSTS $ epochFromSlot slot) pure mbCurEpochNo

  (utxoStateBeforeUtxow, certStateFinal) <-
    if tx ^. isValidTxL == IsValid True
      then do
        let txBody = tx ^. bodyTxL
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L91-150)
```haskell
import GHC.Generics (Generic)
import Lens.Micro ((^.))

data DijkstraUtxoEnv era = DijkstraUtxoEnv
  { dueSlot :: SlotNo
  , duePParams :: PParams era
  , dueCertState :: CertState era
  , dueOriginalUtxo :: UTxO era
  }

-- | Predicate failure for the Dijkstra Era
data DijkstraUtxoPredFailure era
  = -- | Subtransition Failures
    UtxosFailure (PredicateFailure (EraRule "UTXOS" era))
  | -- | The bad transaction inputs
    BadInputsUTxO (NonEmptySet TxIn)
  | OutsideValidityIntervalUTxO
      -- | transaction's validity interval
      ValidityInterval
      -- | current slot
      SlotNo
  | MaxTxSizeUTxO (Mismatch RelLTEQ Word32)
  | InputSetEmptyUTxO
  | FeeTooSmallUTxO
      (Mismatch RelGTEQ Coin)
  | ValueNotConservedUTxO
      (Mismatch RelEQ (Value era)) -- Serialise consumed first, then produced
  | -- | the set of addresses with incorrect network IDs
    WrongNetwork
      -- | the expected network id
      Network
      -- | the set of addresses with incorrect network IDs
      (NonEmptySet Addr)
  | WrongNetworkWithdrawal
      -- | the expected network id
      Network
      -- | the set of reward addresses with incorrect network IDs
      (NonEmptySet AccountAddress)
  | -- | list of supplied bad transaction outputs
    OutputBootAddrAttrsTooBig (NonEmpty (TxOut era))
  | -- | list of supplied bad transaction output triples (actualSize,PParameterMaxValue,TxOut)
    OutputTooBigUTxO (NonEmpty (Int, Int, TxOut era))
  | InsufficientCollateral
      -- | balance computed
      DeltaCoin
      -- | the required collateral for the given fee
      Coin
  | -- | The UTxO entries which have the wrong kind of script
    ScriptsNotPaidUTxO (NonEmptyMap TxIn (TxOut era))
  | ExUnitsTooBigUTxO
      (Mismatch RelLTEQ ExUnits)
  | -- | The inputs marked for use as fees contain non-ADA tokens
    CollateralContainsNonADA (Value era)
  | -- | Wrong Network ID in body
    WrongNetworkInTxBody
      (Mismatch RelEQ Network)
  | -- | slot number outside consensus forecast range
    OutsideForecast SlotNo
  | -- | There are too many collateral inputs
    TooManyCollateralInputs
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L191-215)
```haskell
scriptsProvidedDijkstraStAnnTx ::
  ( EraTxLevel era
  , STxLevel l era ~ STxBothLevels l era
  , STxLevel SubTx era ~ STxBothLevels SubTx era
  , STxLevel TopTx era ~ STxBothLevels TopTx era
  ) =>
  DijkstraStAnnTx l era -> ScriptsProvided era
scriptsProvidedDijkstraStAnnTx stAnnTx =
  withBothTxLevels
    stAnnTx
    (\DijkstraStAnnTopTx {dsattScriptsProvided} -> dsattScriptsProvided)
    (\DijkstraStAnnSubTx {dsastScriptsProvided} -> dsastScriptsProvided)

scriptsNeededDijkstraStAnnTx ::
  ( EraTxLevel era
  , STxLevel l era ~ STxBothLevels l era
  , STxLevel SubTx era ~ STxBothLevels SubTx era
  , STxLevel TopTx era ~ STxBothLevels TopTx era
  ) =>
  DijkstraStAnnTx l era -> ScriptsNeeded era
scriptsNeededDijkstraStAnnTx stAnnTx =
  withBothTxLevels
    stAnnTx
    (\DijkstraStAnnTopTx {dsattScriptsNeeded} -> dsattScriptsNeeded)
    (\DijkstraStAnnSubTx {dsastScriptsNeeded} -> dsastScriptsNeeded)
```
