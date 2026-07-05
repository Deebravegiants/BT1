### Title
Unvalidated `accountBalanceIntervals` TxBody Field Accepted Without Ledger Enforcement — (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs`)

---

### Summary

The Dijkstra era introduces an `accountBalanceIntervals` field (CBOR map key 26) in both top-level and sub-transaction bodies. This field maps `AccountId` credentials to `AccountBalanceInterval` constraints (lower bound, upper bound, or both). No STS transition rule in the Dijkstra era validates that the actual account balances in the ledger state satisfy the intervals declared in this field. Any unprivileged transaction author can include arbitrary, false interval claims; the ledger accepts the transaction unconditionally.

---

### Finding Description

**Data structure and encoding.** `accountBalanceIntervals` is defined in `DijkstraTxBodyRaw` for both `TopTx` and `SubTx` levels and is decoded at CBOR key 26 with only a non-empty check:

```haskell
26 ->
  Just $
    decodeAccA acc (accountBalanceIntervalsDijkstraTxBodyRawL .~) $
      pure <$> do
        x <- decCBOR
        failOnNull (unAccountBalanceIntervals x) $ emptyNamedFailure "AccountBalanceIntervals" "non-empty"
        pure x
``` [1](#0-0) 

The type itself encodes a meaningful balance constraint:

```haskell
data AccountBalanceInterval era
  = AccountBalanceLowerBound !(Inclusive Coin)
  | AccountBalanceUpperBound !(Exclusive Coin)
  | AccountBalanceBothBounds !(Inclusive Coin) !(Exclusive Coin)
``` [2](#0-1) 

**Missing enforcement in UTXO rule.** `dijkstraUtxoTransition` validates validity intervals, inputs, fees, collateral, withdrawals, network IDs, output sizes, and execution units — but contains no check against `accountBalanceIntervals`: [3](#0-2) 

**Missing enforcement in LEDGER rule.** `dijkstraLedgerTransition` calls `validateTreasuryValue`, `validateAllRefScriptSize`, `ENTITIES`, `GOV`, and `UTXOW` — but never reads or validates `accountBalanceIntervals`: [4](#0-3) 

**Missing enforcement in ENTITIES and SUBENTITIES rules.** `dijkstraEntitiesTransition` and `dijkstraSubEntitiesTransition` validate withdrawals and direct deposits but do not touch `accountBalanceIntervals`: [5](#0-4) [6](#0-5) 

**Blocked from Plutus V1–V3 but not validated for V4.** `guardDijkstraFeaturesForPlutusV1toV3` explicitly rejects transactions with non-empty `accountBalanceIntervals` when Plutus V1–V3 scripts are involved, confirming the field is intended to carry semantic meaning for Dijkstra-era (V4) scripts:

```haskell
unless (null $ unAccountBalanceIntervals accountBalanceIntervals) $
  Left $ inject $ AccountBalanceIntervalsNotSupported @era accountBalanceIntervals
``` [7](#0-6) 

Yet for Plutus V4 the field is passed to the script context without the ledger having verified the intervals against the actual `Accounts` state. A grep over all production rule files confirms `accountBalanceIntervals` appears only in `TxBody.hs` and `TxInfo.hs` — never in any STS rule. [8](#0-7) 

**Conformance spec translation exists.** The field has a formal Agda spec translation (`Agda.HSMap Agda.Credential Agda.BalanceInterval`), confirming it is not merely decorative: [9](#0-8) 

---

### Impact Explanation

A Plutus V4 script author may design a script that reads `accountBalanceIntervals` from the script context and trusts the ledger to have enforced the declared constraints — analogous to how a Permit-based smart contract trusts the wallet to have validated the `value` and `deadline` fields before signing. Because the ledger performs no such enforcement, a malicious transaction author can supply false interval claims (e.g., asserting an account balance is within `[0, 1 ADA)` when it holds 10 000 ADA). The script receives the fabricated data and may authorize operations it would otherwise reject. This allows attacker-controlled transactions to exceed intended validation limits on account-balance-gated operations, fitting the **Medium** impact class: *attacker-controlled transactions exceed intended validation limits outside design parameters*.

---

### Likelihood Explanation

Any unprivileged transaction author submitting a Dijkstra-era transaction can include arbitrary `accountBalanceIntervals` values. No special role, key, or governance threshold is required. The only prerequisite is that the targeted script trusts the field rather than independently re-reading account balances from the script context. Given that the field is explicitly designed to communicate balance conditions to scripts, such trust is a natural and expected pattern.

---

### Recommendation

Add a ledger rule check — most naturally inside `dijkstraUtxoTransition` or `dijkstraLedgerTransition` — that iterates over `accountBalanceIntervals`, looks up each `AccountId` in the current `Accounts` state, and fails with a new predicate failure (e.g., `AccountBalanceIntervalViolation`) if any account's balance falls outside its declared interval. The check should use the same `Accounts` snapshot used for withdrawal validation to ensure consistency within a batch. Sub-transaction bodies carrying `accountBalanceIntervals` should receive the same enforcement in the `SUBLEDGER` / `SUBENTITIES` path.

---

### Proof of Concept

1. Construct a Dijkstra-era `TopTx` whose `accountBalanceIntervals` (key 26) maps credential `C` to `AccountBalanceBothBounds (Inclusive 0) (Exclusive 1)`, asserting that account `C` holds less than 1 lovelace.
2. Ensure account `C` actually holds 10 000 000 lovelace in the ledger state.
3. Submit the transaction. `dijkstraUtxoTransition` and `dijkstraLedgerTransition` perform no interval check; the transaction is accepted.
4. A Plutus V4 script invoked by this transaction reads `accountBalanceIntervals` from its `ScriptContext`, observes the `[0, 1)` claim, and proceeds under the false assumption that account `C` is nearly empty — enabling logic that should have been gated on a low balance.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L439-445)
```haskell
        26 ->
          Just $
            decodeAccA acc (accountBalanceIntervalsDijkstraTxBodyRawL .~) $
              pure <$> do
                x <- decCBOR
                failOnNull (unAccountBalanceIntervals x) $ emptyNamedFailure "AccountBalanceIntervals" "non-empty"
                pure x
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Scripts.hs (L631-635)
```haskell
data AccountBalanceInterval era
  = AccountBalanceLowerBound !(Inclusive Coin)
  | AccountBalanceUpperBound !(Exclusive Coin)
  | AccountBalanceBothBounds !(Inclusive Coin) !(Exclusive Coin)
  deriving (Generic, Show, Eq, Ord, NoThunks, NFData)
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L358-443)
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
        runTest $ Conway.validateTreasuryValue txBody (chainAccountState ^. casTreasuryL)
        runTest $ validateAllRefScriptSize pp originalUtxo tx

        let govState = utxoStateAfterSubLedgers ^. utxosGovStateL
            committee = govState ^. committeeGovStateL
            proposals = govState ^. proposalsGovStateL
            committeeProposals = proposalsWithPurpose grCommitteeL proposals

        certStateAfterENTITIES <-
          trans @(EraRule "ENTITIES" era) $
            TRC
              ( EntitiesEnv
                  (stAnnTx ^. plutusLegacyModeStAnnTxG)
                  (Conway.CertsEnv tx pp curEpochNo committee committeeProposals)
              , certStateAfterSubLedgers
              , StrictSeq.fromStrict $ txBody ^. certsTxBodyL
              )

        let govSignal =
              Conway.GovSignal
                { Conway.gsVotingProcedures = txBody ^. votingProceduresTxBodyL
                , Conway.gsProposalProcedures = txBody ^. proposalProceduresTxBodyL
                , Conway.gsCertificates = txBody ^. certsTxBodyL
                }
        proposalsState <-
          trans @(EraRule "GOV" era) $
            TRC
              ( Conway.GovEnv
                  (txIdTxBody txBody)
                  curEpochNo
                  pp
                  (govState ^. constitutionGovStateL . constitutionGuardrailsScriptHashL)
                  certStateAfterENTITIES
                  (govState ^. committeeGovStateL)
              , proposals
              , govSignal
              )
        pure
          ( utxoStateAfterSubLedgers
              & utxosGovStateL . proposalsGovStateL .~ proposalsState
          , certStateAfterENTITIES
          )
      else pure (utxoStateAfterSubLedgers, certStateAfterSubLedgers)

  -- Call UTXOW with DijkstraUtxoEnv, passing the original UTxO and original certState
  utxoStateFinal <-
    trans @(EraRule "UTXOW" era) $
      TRC
        ( DijkstraUtxoEnv slot pp (lsCertState ledgerState) originalUtxo
        , utxoStateBeforeUtxow
        , stAnnTx
        )
  pure $ LedgerState utxoStateFinal certStateFinal
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Entities.hs (L191-216)
```haskell
dijkstraEntitiesTransition = do
  TRC (EntitiesEnv legacyMode certsEnv, certState, certificates) <- judgmentContext
  let Conway.CertsEnv tx pp curEpoch _committee _committeeProposals = certsEnv
      withdrawals = tx ^. bodyTxL . withdrawalsTxBodyL
      accounts = certState ^. certDStateL . accountsL

  runTest $ Conway.validateWithdrawalsDelegated accounts tx

  network <- liftSTS $ asks networkId

  validateWithdrawals legacyMode network withdrawals accounts

  let certStateBeforeCerts =
        certState
          & Conway.updateDormantDRepExpiries tx curEpoch
          & Conway.updateVotingDRepExpiries tx curEpoch (pp ^. ppDRepActivityL)
          & certDStateL . accountsL %~ applyWithdrawals withdrawals
  certStateAfterCerts <-
    trans @(EraRule "CERTS" era) $ TRC (certsEnv, certStateBeforeCerts, certificates)

  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterCerts = certStateAfterCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterCerts) $
    injectFailure . DirectDepositsToMissingAccounts

  pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L155-187)
```haskell
dijkstraSubEntitiesTransition = do
  TRC (subCertsEnv, certState, certificates) <- judgmentContext
  let tx = certsTx subCertsEnv
      pp = certsPParams subCertsEnv
      curEpoch = certsCurrentEpoch subCertsEnv
      withdrawals = tx ^. bodyTxL . withdrawalsTxBodyL
      accounts = certState ^. certDStateL . accountsL

  runTest $ Conway.validateWithdrawalsDelegated accounts tx

  network <- liftSTS $ asks networkId
  let (missingWithdrawals, exceededWithdrawals) =
        case withdrawalsThatExceedAccountBalance withdrawals network accounts of
          Nothing -> (Map.empty, Map.empty)
          Just (missing, exceeded) -> (unWithdrawals missing, exceeded)
  failOnNonEmptyMap missingWithdrawals $
    injectFailure . SubWithdrawalsMissingAccounts . Withdrawals . NEM.toMap
  failOnNonEmptyMap exceededWithdrawals $ injectFailure . SubWithdrawalAmountsExceedAccountBalances

  let certStateBeforeSubCerts =
        certState
          & Conway.updateDormantDRepExpiries tx curEpoch
          & Conway.updateVotingDRepExpiries tx curEpoch (pp ^. ppDRepActivityL)
          & certDStateL . accountsL %~ applyWithdrawals withdrawals
  certStateAfterSubCerts <-
    trans @(EraRule "SUBCERTS" era) $ TRC (subCertsEnv, certStateBeforeSubCerts, certificates)

  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
    injectFailure . SubDirectDepositsToMissingAccounts

  pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxInfo.hs (L414-440)
```haskell
guardDijkstraFeaturesForPlutusV1toV3 ::
  forall era.
  ( EraTx era
  , DijkstraEraTxBody era
  , Inject (DijkstraContextError era) (ContextError era)
  ) =>
  Tx TopTx era ->
  Either (ContextError era) ()
guardDijkstraFeaturesForPlutusV1toV3 tx = do
  let txBody = tx ^. bodyTxL
      directDeposits = txBody ^. directDepositsTxBodyL
      accountBalanceIntervals = txBody ^. accountBalanceIntervalsTxBodyL
      scriptHashes = [sh | ScriptHashObj sh <- toList (txBody ^. guardsTxBodyL)]
  unless (null $ unDirectDeposits directDeposits) $
    Left $
      inject $
        DirectDepositsNotSupported @era directDeposits
  unless (null $ unAccountBalanceIntervals accountBalanceIntervals) $
    Left $
      inject $
        AccountBalanceIntervalsNotSupported @era accountBalanceIntervals
  case NE.nonEmpty scriptHashes of
    Nothing -> Right ()
    Just neScriptHashes ->
      Left $
        inject $
          GuardScriptHashesNotSupported @era neScriptHashes
```

**File:** libs/cardano-ledger-conformance/src/Test/Cardano/Ledger/Conformance/SpecTranslate/Dijkstra/Base.hs (L200-206)
```haskell
instance SpecTranslate DijkstraEra (AccountBalanceIntervals DijkstraEra) where
  type
    SpecRep DijkstraEra (AccountBalanceIntervals DijkstraEra) =
      Agda.HSMap Agda.Credential Agda.BalanceInterval

  toSpecRep (AccountBalanceIntervals m) =
    toSpecRepMap $ Map.mapKeys (\(AccountId c) -> c) m
```
