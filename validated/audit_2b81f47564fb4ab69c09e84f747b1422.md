### Title
Sub-Transaction Value Conservation Not Enforced in Dijkstra Era Allows Unauthorized Native Token Creation - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxo.hs`)

---

### Summary

The Dijkstra era introduces nested transactions (`SubTx`). The `SUBUTXO` rule that processes sub-transactions calls `updateUTxOStateNoFees` to update the UTxO but **never calls `validateValueNotConservedUTxO`**. This means a sub-transaction's outputs are not required to balance against its inputs plus its mint field. An unprivileged transaction author can craft a sub-transaction whose outputs contain more native tokens than its inputs plus mint field, creating tokens out of thin air. The top-level `UTXO` rule's value conservation check does not cover sub-transaction bodies, so the discrepancy is never caught.

---

### Finding Description

**Root cause — missing `validateValueNotConservedUTxO` in `dijkstraSubUtxoTransition`:**

The top-level Dijkstra UTXO rule explicitly enforces value conservation: [1](#0-0) 

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

The sub-transaction rule `dijkstraSubUtxoTransition` performs no equivalent check. It validates inputs exist, checks network IDs, output sizes, and validity intervals, then directly calls `updateUTxOStateNoFees`: [2](#0-1) 

`updateUTxOStateNoFees` simply removes inputs and inserts outputs with no balance verification: [3](#0-2) 

**Sub-transactions have a `mint` field** (confirmed in both the CDDL spec and the Haskell type): [4](#0-3) [5](#0-4) 

**The top-level value conservation check cannot compensate.** In `dijkstraLedgerTransition`, sub-transactions are processed first (via `SUBLEDGERS`), then the top-level `UTXOW`/`UTXO` runs. The top-level check uses `originalUtxo` (the UTxO snapshot before sub-transactions) and only examines the top-level `txBody`: [6](#0-5) 

Sub-transaction inputs/outputs/mint fields are entirely invisible to the top-level conservation check.

**The `SUBUTXOW` minting-script check is insufficient.** `dijkstraSubUtxowTransition` does validate that minting policy scripts are present and pass for whatever is declared in the sub-transaction's `mint` field: [7](#0-6) 

But this only enforces that the declared `mint` field is authorized. It does not enforce that the outputs' token quantities equal `inputs + mint`. An attacker can declare an empty `mint` field (requiring no minting scripts) while placing arbitrary native tokens in the outputs.

---

### Impact Explanation

**Critical — Direct creation of native assets through an invalid ledger state transition.**

An attacker can include a sub-transaction with:
- **Inputs**: any valid UTxO entries (e.g., 100 ADA)
- **Outputs**: same ADA + an arbitrary quantity of any native token (e.g., 1,000,000 `AttackerToken`)
- **Mint field**: empty (no minting policy required)

`SUBUTXO` accepts this because `validateBadInputsUTxO` passes (inputs exist), no value conservation check is performed, and `updateUTxOStateNoFees` inserts the outputs verbatim. The 1,000,000 `AttackerToken` now exist in the UTxO without any minting policy ever being validated. These tokens persist and can be spent in subsequent transactions, constituting unauthorized creation of native assets.

---

### Likelihood Explanation

**High.** The Dijkstra era is the only era with sub-transactions. Any transaction author (no special privilege required) can submit a `TopTx` containing a `SubTx` with this imbalance. The attack requires only knowledge of the missing check and the ability to construct a valid Dijkstra-era transaction, which is within reach of any node operator or wallet user on the Dijkstra network.

---

### Recommendation

Add a value conservation check inside `dijkstraSubUtxoTransition`, analogous to the top-level check, before calling `updateUTxOStateNoFees`. The check should use `originalUtxo` (already available in `SubUtxoEnv` as `sueOriginalUtxo`) and the sub-transaction body:

```haskell
-- In dijkstraSubUtxoTransition, before the isValid branch:
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
```

This mirrors the invariant enforced by the formal specification for all minting transactions: [8](#0-7) 

where `consumed` includes the `mint` field and must equal `produced`.

---

### Proof of Concept

1. Obtain a UTxO entry `txIn` containing 5,000,000 lovelace at address `addrA`.
2. Construct a `SubTx` with:
   - `inputs = {txIn}`
   - `outputs = [{addrA, 5_000_000 lovelace + 1_000_000 AttackerToken}]`
   - `mint = mempty` (empty — no minting policy script needed)
   - `witnesses = {vkey witness for addrA}`
3. Wrap it in a `TopTx` with a valid fee input and include the `SubTx` in `subTransactions`.
4. Submit the transaction to a Dijkstra-era node.
5. Observe that the UTxO now contains `1_000_000 AttackerToken` at `addrA` with no minting policy ever having been executed.

The `SUBUTXO` rule passes because:
- `validateBadInputsUTxO` passes (`txIn` is in the UTxO) [9](#0-8) 
- No `validateValueNotConservedUTxO` is called [10](#0-9) 
- `updateUTxOStateNoFees` inserts the outputs unconditionally [11](#0-10)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L380-381)
```haskell
  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
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

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/Rules/Utxo.hs (L618-641)
```haskell
updateUTxOStateNoFees pp utxos txBody certState govState depositChangeEvent txUtxODiffEvent = do
  let UTxOState {utxosUtxo, utxosDeposited, utxosFees, utxosDonation} = utxos
      UTxO utxo = utxosUtxo
      !utxoAdd = txouts txBody -- These will be inserted into the UTxO
      {- utxoDel  = txins txb ◁ utxo -}
      !(utxoWithout, utxoDel) = extractKeys utxo (txBody ^. inputsTxBodyL)
      {- newUTxO = (txins txb ⋪ utxo) ∪ outs txb -}
      newUTxO = utxoWithout `Map.union` unUTxO utxoAdd
      deletedUTxO = UTxO utxoDel
      totalRefunds = certsTotalRefundsTxBody pp certState txBody
      totalDeposits = certsTotalDepositsTxBody pp certState txBody
      depositChange = totalDeposits <-> totalRefunds
  depositChangeEvent depositChange
  txUtxODiffEvent deletedUTxO utxoAdd
  pure $!
    UTxOState
      { utxosUtxo = UTxO newUTxO
      , utxosDeposited = utxosDeposited <> depositChange
      , utxosFees = utxosFees
      , utxosGovState = govState
      , utxosInstantStake =
          deleteInstantStake deletedUTxO (addInstantStake utxoAdd (utxos ^. instantStakeL))
      , utxosDonation = utxosDonation
      }
```

**File:** eras/dijkstra/impl/cddl/data/dijkstra.cddl (L788-808)
```text
sub_transaction_body =
  {   0  : set<transaction_input>
  ,   1  : [* transaction_output]
  , ? 3  : slot
  , ? 4  : certificates
  , ? 5  : withdrawals
  , ? 7  : auxiliary_data_hash
  , ? 8  : slot
  , ? 9  : mint
  , ? 11 : script_data_hash
  , ? 14 : guards
  , ? 15 : network_id
  , ? 18 : nonempty_set<transaction_input>
  , ? 19 : voting_procedures
  , ? 20 : proposal_procedures
  , ? 21 : coin
  , ? 22 : positive_coin
  , ? 24 : required_top_level_guards
  , ? 25 : direct_deposits
  , ? 26 : account_balance_intervals
  }
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L189-209)
```haskell
  DijkstraSubTxBodyRaw ::
    { dstbrSpendInputs :: !(Set TxIn)
    , dstbrReferenceInputs :: !(Set TxIn)
    , dstbrOutputs :: !(StrictSeq (Sized (TxOut era)))
    , dstbrCerts :: !(OSet.OSet (TxCert era))
    , dstbrWithdrawals :: !Withdrawals
    , dstbrVldt :: !ValidityInterval
    , dstbrGuards :: !(OSet (Credential Guard))
    , dstbrMint :: !MultiAsset
    , dstbrScriptIntegrityHash :: !(StrictMaybe ScriptIntegrityHash)
    , dstbrAuxDataHash :: !(StrictMaybe TxAuxDataHash)
    , dstbrNetworkId :: !(StrictMaybe Network)
    , dstbrVotingProcedures :: !(VotingProcedures era)
    , dstbrProposalProcedures :: !(OSet.OSet (ProposalProcedure era))
    , dstbrCurrentTreasuryValue :: !(StrictMaybe Coin)
    , dstbrTreasuryDonation :: !Coin
    , dstbrRequiredTopLevelGuards :: !(Map (Credential Guard) (StrictMaybe (Data era)))
    , dstbrDirectDeposits :: !DirectDeposits
    , dstbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw SubTx era
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Ledger.hs (L358-384)
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

```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubUtxow.hs (L263-267)
```haskell
  let scriptsNeeded = scriptsNeededStAnnTx stAnnTx
      scriptHashesNeeded = getScriptsHashesNeeded scriptsNeeded

  {- ∀[ s ∈ p1ScriptsNeeded ] validP1Script vKeyHashesProvided txVldt s -}
  runTest $ Babbage.validateFailedBabbageScripts tx scriptsProvided scriptHashesNeeded
```

**File:** eras/shelley-ma/formal-spec/utxo.tex (L49-58)
```tex
    & \fun{consumed} \in \PParams \to \UTxO \to \TxBody \to \hldiff{\ValMonoid} \\
    & \consumed{pp}{utxo}{txb} = \\
    & ~~\ubalance{(\txins{txb} \restrictdom \var{utxo})} ~+~ \hldiff{\fun{mint}~\var{txb}} \\
    &~~+~\hldiff{\fun{inject}}(\fun{wbalance}~(\fun{txwdrls}~{txb})~+~ \keyRefunds{pp}{txb})
    \nextdef
    & \fun{produced} \in \PParams \to \StakePools \to \TxBody \to \hldiff{\ValMonoid} \\
    & \fun{produced}~\var{pp}~\var{stpools}~\var{txb} = \\
    &~~\ubalance{(\fun{outs}~{txb})} \\
    &~~+ \hldiff{\fun{inject}}(\txfee{txb} + \totalDeposits{pp}{stpools}{(\txcerts{txb})})
  \end{align*}
```
