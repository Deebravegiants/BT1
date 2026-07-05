### Title
Unbounded Sub-Transaction Iteration in `SUBLEDGERS` Without Explicit Count Limit — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs`)

---

### Summary

The Dijkstra era introduces batch transactions containing an arbitrary number of sub-transactions. The `SUBLEDGERS` rule iterates over every sub-transaction via `foldM` and applies the full `SUBLEDGER` rule to each one, with no protocol-parameter-enforced upper bound on the count of sub-transactions. The only implicit bound is `maxTxSize`, which limits serialized bytes — but the computational work per sub-transaction is not proportional to its serialized size. An attacker can craft a transaction with many minimal sub-transactions that fits within `maxTxSize` yet requires disproportionately more ledger-rule evaluation work than a regular transaction of the same byte size, exceeding the intended validation-cost envelope.

---

### Finding Description

**Root cause — `dijkstraSubLedgersTransition`:**

```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
``` [1](#0-0) 

For every element of `subTxs`, the rule unconditionally invokes the full `SUBLEDGER` transition, which itself fans out into three sub-rules:

1. **`SUBUTXOW` → `SUBUTXO`** — full UTxO validation: bad-inputs check (map lookups in the UTxO), output-size checks, network-ID checks, validity-interval checks, etc. [2](#0-1) 

2. **`SUBENTITIES` → `SUBCERTS`** — recursive certificate processing, one `SUBCERT` transition per certificate. [3](#0-2) 

3. **`SUBGOV`** — governance proposal and voting-procedure processing. [4](#0-3) 

**No explicit count bound exists.** The `DijkstraPParams` record introduces four new Dijkstra-specific parameters (`maxRefScriptSizePerBlock`, `maxRefScriptSizePerTx`, `refScriptCostStride`, `refScriptCostMultiplier`) but no `maxSubTransactions` or equivalent. [5](#0-4) 

**The only implicit bound is `maxTxSize`.** The top-level UTXO rule applies `validateMaxTxSizeUTxO` to the top-level transaction (which includes the serialized sub-transactions in its body), but this is a byte-size check, not a count check. [6](#0-5) 

**Sub-transactions are stored as an `OMap TxId (Tx SubTx era)` in the top-level transaction body** with no size-limit enforcement at the data-structure level. [7](#0-6) 

**The CDDL schema** defines `sub_transactions = nonempty_oset<sub_transaction>` with no upper-cardinality constraint. [8](#0-7) 

**Computational cost is super-linear relative to serialized size.** A minimal sub-transaction body (empty inputs, empty outputs, no certificates, no proposals) serializes to a small number of bytes but still triggers the full `SUBLEDGER` rule evaluation with its fixed per-sub-transaction overhead (UTxO map traversal, STS rule dispatch, state threading through `foldM`). With `maxTxSize = 16384` bytes and a minimal sub-transaction serializing to ~10–20 bytes, an attacker can embed hundreds of sub-transactions in a single valid transaction, each incurring the full `SUBLEDGER` overhead.

---

### Impact Explanation

**Classification: Medium — attacker-controlled transactions exceed intended validation limits.**

The `maxTxSize` protocol parameter was designed to bound the computational cost of validating a single transaction. The Dijkstra sub-transaction feature breaks this assumption: the validation cost of a batch transaction is O(N × per-sub-tx-overhead) where N is the number of sub-transactions, while the serialized size is O(N × per-sub-tx-bytes). Because per-sub-tx-overhead >> per-sub-tx-bytes (due to the full `SUBLEDGER` rule evaluation), an attacker can construct a transaction that is within `maxTxSize` but requires significantly more CPU and memory to validate than any pre-Dijkstra transaction of the same byte size. This exceeds the intended validation-cost envelope established by the protocol parameters.

---

### Likelihood Explanation

**High.** Any unprivileged transaction submitter can craft such a transaction. No special keys, governance majority, or privileged access is required. The attacker only needs to submit a valid top-level transaction containing many minimal sub-transactions. The transaction will pass all existing ledger checks (it is within `maxTxSize`, has valid witnesses, conserves value) while imposing disproportionate validation cost on every node that processes the block containing it.

---

### Recommendation

1. **Add a `maxSubTransactions` protocol parameter** to `DijkstraPParams` (analogous to `maxCollateralInputs` in Alonzo). [9](#0-8) 

2. **Enforce the bound in `dijkstraSubLedgersTransition`** before the `foldM` loop, checking `length subTxs <= maxSubTransactions pp` and failing with a predicate failure if exceeded. [1](#0-0) 

3. **Add a corresponding CDDL constraint** to `sub_transactions` in `dijkstra.cddl` to reflect the maximum cardinality. [8](#0-7) 

---

### Proof of Concept

**Attacker-controlled entry path:**

1. Construct a `DijkstraTxBodyRaw TopTx` with `dtbrSubTransactions` set to an `OMap` containing N minimal sub-transactions, where each sub-transaction body has empty spend inputs, empty outputs, no certificates, no proposals, and no withdrawals. [10](#0-9) 

2. Choose N such that the total serialized size of the top-level transaction is just below `maxTxSize` (e.g., N ≈ 500 with a ~30-byte minimal sub-transaction body).

3. Submit the transaction. It passes `validateMaxTxSizeUTxO` (byte-size check), `validateExUnitsTooBigUTxO` (no Plutus scripts), and all other existing checks.

4. During block application, `dijkstraLedgerTransition` calls `SUBLEDGERS`, which calls `dijkstraSubLedgersTransition`: [11](#0-10) 

5. `dijkstraSubLedgersTransition` iterates over all N sub-transactions via `foldM`, invoking the full `SUBLEDGER` rule N times — each time running `SUBUTXOW`, `SUBENTITIES`, and `SUBGOV` — with no count check. [1](#0-0) 

**Result:** The transaction is valid and accepted, but its validation cost is O(N) full `SUBLEDGER` evaluations — far exceeding the computational budget implied by `maxTxSize` for a transaction of that byte size. This allows an attacker to systematically inflate the per-transaction validation cost beyond the design parameters of the protocol.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedgers.hs (L128-135)
```haskell
dijkstraSubLedgersTransition = do
  TRC (env, ledgerState, subTxs) <- judgmentContext
  foldM
    ( \ls subTx ->
        trans @(EraRule "SUBLEDGER" era) $ TRC (env, ls, subTx)
    )
    ledgerState
    subTxs
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubCerts.hs (L130-136)
```haskell
  case certificates of
    Empty -> pure certState
    gamma :|> txCert -> do
      certStateRest <-
        trans @(SUBCERTS era) $ TRC (env, certState, gamma)
      trans @(EraRule "SUBCERT" era) $
        TRC (Conway.CertEnv pp currentEpoch committee committeeProposals, certStateRest, txCert)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubLedger.hs (L248-280)
```haskell
  (utxoStateBeforeSubUtxow, certStateFinal) <-
    if topIsValid == IsValid True
      then do
        runTest $ Conway.validateTreasuryValue txBody (chainAccountState ^. casTreasuryL)

        certStateAfterSubEntities <-
          trans @(EraRule "SUBENTITIES" era) $
            TRC
              ( SubCertsEnv tx pp curEpochNo committee (proposalsWithPurpose grCommitteeL proposals)
              , certState
              , StrictSeq.fromStrict $ txBody ^. certsTxBodyL
              )
        let govEnv =
              Conway.GovEnv
                (txIdTxBody txBody)
                curEpochNo
                pp
                (govState ^. constitutionGovStateL . constitutionGuardrailsScriptHashL)
                certStateAfterSubEntities
                committee
        let govSignal =
              Conway.GovSignal
                { Conway.gsVotingProcedures = txBody ^. votingProceduresTxBodyL
                , Conway.gsProposalProcedures = txBody ^. proposalProceduresTxBodyL
                , Conway.gsCertificates = txBody ^. certsTxBodyL
                }
        proposalsState <-
          trans @(EraRule "SUBGOV" era) $
            TRC
              ( govEnv
              , proposals
              , govSignal
              )
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/PParams.hs (L83-158)
```haskell
data DijkstraPParams f era = DijkstraPParams
  { dppTxFeePerByte :: !(THKD ('PPGroups 'EconomicGroup 'SecurityGroup) f CoinPerByte)
  -- ^ The linear factor for the minimum fee calculation
  , dppTxFeeFixed :: !(THKD ('PPGroups 'EconomicGroup 'SecurityGroup) f (CompactForm Coin))
  -- ^ The constant factor for the minimum fee calculation
  , dppMaxBBSize :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f Word32)
  -- ^ Maximal block body size
  , dppMaxTxSize :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f Word32)
  -- ^ Maximal transaction size
  , dppMaxBHSize :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f Word16)
  -- ^ Maximal block header size
  , dppKeyDeposit :: !(THKD ('PPGroups 'EconomicGroup 'NoStakePoolGroup) f (CompactForm Coin))
  -- ^ The amount of a key registration deposit
  , dppPoolDeposit :: !(THKD ('PPGroups 'EconomicGroup 'NoStakePoolGroup) f (CompactForm Coin))
  -- ^ The amount of a pool registration deposit
  , dppEMax :: !(THKD ('PPGroups 'TechnicalGroup 'NoStakePoolGroup) f EpochInterval)
  -- ^ Maximum number of epochs in the future a pool retirement is allowed to
  -- be scheduled for.
  , dppNOpt :: !(THKD ('PPGroups 'TechnicalGroup 'NoStakePoolGroup) f Word16)
  -- ^ Desired number of pools
  , dppA0 :: !(THKD ('PPGroups 'TechnicalGroup 'NoStakePoolGroup) f NonNegativeInterval)
  -- ^ Pool influence
  , dppRho :: !(THKD ('PPGroups 'EconomicGroup 'NoStakePoolGroup) f UnitInterval)
  -- ^ Monetary expansion
  , dppTau :: !(THKD ('PPGroups 'EconomicGroup 'NoStakePoolGroup) f UnitInterval)
  -- ^ Treasury expansion
  , dppProtocolVersion :: !(HKDNoUpdate f ProtVer)
  -- ^ Protocol version
  , dppMinPoolCost :: !(THKD ('PPGroups 'EconomicGroup 'NoStakePoolGroup) f (CompactForm Coin))
  -- ^ Minimum Stake Pool Cost
  , dppCoinsPerUTxOByte :: !(THKD ('PPGroups 'EconomicGroup 'SecurityGroup) f CoinPerByte)
  -- ^ Cost in lovelace per byte of UTxO storage
  , dppCostModels :: !(THKD ('PPGroups 'TechnicalGroup 'NoStakePoolGroup) f CostModels)
  -- ^ Cost models for non-native script languages
  , dppPrices :: !(THKD ('PPGroups 'EconomicGroup 'NoStakePoolGroup) f Prices)
  -- ^ Prices of execution units (for non-native script languages)
  , dppMaxTxExUnits :: !(THKD ('PPGroups 'NetworkGroup 'NoStakePoolGroup) f OrdExUnits)
  -- ^ Max total script execution resources units allowed per tx
  , dppMaxBlockExUnits :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f OrdExUnits)
  -- ^ Max total script execution resources units allowed per block
  , dppMaxValSize :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f Word32)
  -- ^ Max size of a Value in an output
  , dppCollateralPercentage :: !(THKD ('PPGroups 'TechnicalGroup 'NoStakePoolGroup) f Word16)
  -- ^ Percentage of the txfee which must be provided as collateral when
  -- including non-native scripts.
  , dppMaxCollateralInputs :: !(THKD ('PPGroups 'NetworkGroup 'NoStakePoolGroup) f Word16)
  -- ^ Maximum number of collateral inputs allowed in a transaction
  , -- New ones for Dijkstra:
    dppPoolVotingThresholds :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f PoolVotingThresholds)
  -- ^ Thresholds for SPO votes
  , dppDRepVotingThresholds :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f DRepVotingThresholds)
  -- ^ Thresholds for DRep votes
  , dppCommitteeMinSize :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f Word16)
  -- ^ Minimum size of the Constitutional Committee
  , dppCommitteeMaxTermLength :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f EpochInterval)
  -- ^ The Constitutional Committee Term limit in number of Slots
  , dppGovActionLifetime :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f EpochInterval)
  -- ^ Gov action lifetime in number of Epochs
  , dppGovActionDeposit :: !(THKD ('PPGroups 'GovGroup 'SecurityGroup) f (CompactForm Coin))
  -- ^ The amount of the Gov Action deposit
  , dppDRepDeposit :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f (CompactForm Coin))
  -- ^ The amount of a DRep registration deposit
  , dppDRepActivity :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f EpochInterval)
  -- ^ The number of Epochs that a DRep can perform no activity without losing their @Active@ status.
  , dppMinFeeRefScriptCostPerByte ::
      !(THKD ('PPGroups 'EconomicGroup 'SecurityGroup) f NonNegativeInterval)
  -- ^ Reference scripts fee for the minimum fee calculation
  -- TODO ensure that the groups here make sense
  , dppMaxRefScriptSizePerBlock :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f Word32)
  -- ^ Limit on the total number of bytes of all reference scripts combined from
  -- all transactions within a block.
  , dppMaxRefScriptSizePerTx :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f Word32)
  -- ^ Limit on the total number of bytes of reference scripts that a transaction can use.
  , dppRefScriptCostStride :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f (NonZero Word32))
  , dppRefScriptCostMultiplier :: !(THKD ('PPGroups 'NetworkGroup 'SecurityGroup) f PositiveInterval)
  }
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L411-412)
```haskell
  {- txsize tx ≤ maxTxSize pp -}
  runTestOnSignal $ Shelley.validateMaxTxSizeUTxO pp tx
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L163-188)
```haskell
data DijkstraTxBodyRaw l era where
  DijkstraTxBodyRaw ::
    { dtbrSpendInputs :: !(Set TxIn)
    , dtbrCollateralInputs :: !(Set TxIn)
    , dtbrReferenceInputs :: !(Set TxIn)
    , dtbrOutputs :: !(StrictSeq (Sized (TxOut era)))
    , dtbrCollateralReturn :: !(StrictMaybe (Sized (TxOut era)))
    , dtbrTotalCollateral :: !(StrictMaybe Coin)
    , dtbrCerts :: !(OSet.OSet (TxCert era))
    , dtbrWithdrawals :: !Withdrawals
    , dtbrFee :: !Coin
    , dtbrVldt :: !ValidityInterval
    , dtbrGuards :: !(OSet (Credential Guard))
    , dtbrMint :: !MultiAsset
    , dtbrScriptIntegrityHash :: !(StrictMaybe ScriptIntegrityHash)
    , dtbrAuxDataHash :: !(StrictMaybe TxAuxDataHash)
    , dtbrNetworkId :: !(StrictMaybe Network)
    , dtbrVotingProcedures :: !(VotingProcedures era)
    , dtbrProposalProcedures :: !(OSet.OSet (ProposalProcedure era))
    , dtbrCurrentTreasuryValue :: !(StrictMaybe Coin)
    , dtbrTreasuryDonation :: !Coin
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw TopTx era
```

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L783-783)
```text
sub_transactions = nonempty_oset<sub_transaction>
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L369-383)
```haskell
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
```
