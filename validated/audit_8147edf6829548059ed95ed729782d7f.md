### Title
Sub-Transaction Withdrawals Bypass Stake Credential Witness Requirement in Dijkstra Era — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, sub-transactions (`SubTx`) can include reward-account withdrawals in their `withdrawalsTxBodyL` field. The UTXOW witness-requirement check (`validateNeededWitnesses`) only inspects the **top-level** transaction body for required withdrawal witnesses; sub-transaction withdrawal credentials are never added to the "needed witnesses" set. An unprivileged attacker can therefore drain any registered account's reward balance by embedding that account's withdrawal inside a sub-transaction, without supplying the stake-credential witness that Cardano has required since Shelley.

---

### Finding Description

**Vulnerability class:** Missing authorization check — the ledger enforces witness requirements for top-level withdrawals but omits the equivalent check for sub-transaction withdrawals, allowing an unauthorized party to trigger a state change that should require the victim's credential.

**Root cause — `getWitsVKeyNeeded` ignores sub-transaction withdrawals**

`DijkstraEra`'s `EraUTxO` instance delegates witness computation to `getConwayWitsVKeyNeeded`:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs
getWitsVKeyNeeded _ = getConwayWitsVKeyNeeded
``` [1](#0-0) 

`getConwayWitsVKeyNeeded` calls `getShelleyWitsVKeyNeededNoGov`, which collects withdrawal authors only from the **top-level** `txBody ^. withdrawalsTxBodyL`:

```haskell
-- eras/shelley/impl/src/Cardano/Ledger/Shelley/UTxO.hs
wdrlAuthors = Map.foldrWithKey' accum Set.empty
                (unWithdrawals (txBody ^. withdrawalsTxBodyL))
``` [2](#0-1) 

Sub-transactions live in `txBody ^. subTransactionsTxBodyL`; their `withdrawalsTxBodyL` fields are never visited by this function.

**Root cause — UTXOW witness check uses only top-level body**

In `dijkstraUtxowTransition`, the witness check is:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs
let witsKeyHashes = keyHashWitnessesTxWits (tx ^. witsTxL)
...
runTest $ Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody
``` [3](#0-2) 

`txBody` is the top-level body; `witsKeyHashes` is built from the top-level witness set. Neither sub-transaction bodies nor sub-transaction witness sets are consulted.

**Root cause — SUBENTITIES applies sub-transaction withdrawals without any witness check**

`dijkstraSubEntitiesTransition` validates amounts and DRep delegation, then unconditionally applies the withdrawals:

```haskell
-- eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs
let (missingWithdrawals, exceededWithdrawals) =
      case withdrawalsThatExceedAccountBalance withdrawals network accounts of ...
failOnNonEmptyMap missingWithdrawals ...
failOnNonEmptyMap exceededWithdrawals ...
...
& certDStateL . accountsL %~ applyWithdrawals withdrawals
``` [4](#0-3) 

There is no call to any witness-validation function for the sub-transaction's withdrawal credentials. The same gap exists in `dijkstraEntitiesTransition`: [5](#0-4) 

**Contrast with the correct top-level behavior**

For top-level withdrawals, Shelley through Conway all require the stake credential's key hash to be present in the transaction's witness set, as enforced by `wdrlAuthors` inside `getShelleyWitsVKeyNeededNoGov`: [2](#0-1) 

The formal specification also mandates this:

> *"spending from a reward account requires a witness for a stake credential"* [6](#0-5) 

Sub-transaction withdrawals receive none of this protection.

---

### Impact Explanation

**Critical — Direct loss of ADA through an invalid ledger state transition.**

An attacker constructs a Dijkstra top-level transaction containing a sub-transaction whose `withdrawalsTxBodyL` lists the victim's reward account with its full balance. The SUBENTITIES rule validates the amount and DRep delegation, then calls `applyWithdrawals`, zeroing the victim's account balance. The withdrawn ADA enters the sub-transaction's value balance and can be routed to any output the attacker controls. The victim's reward balance is permanently drained without their knowledge or consent. No hard fork is needed to execute the attack; it is a valid (from the ledger's perspective) state transition that violates the authorization invariant.

---

### Likelihood Explanation

Any unprivileged transaction submitter can craft this transaction. The attacker needs only:
1. Knowledge of the victim's stake credential (publicly derivable from any staking address on-chain).
2. Enough ADA to cover the transaction fee and minimum UTxO outputs.

No privileged access, key leakage, or consensus majority is required. The attack is deterministic and repeatable against any registered account with a non-zero reward balance.

---

### Recommendation

Extend `getConwayWitsVKeyNeeded` (or introduce a Dijkstra-specific override) to iterate over all sub-transactions and collect their withdrawal credential witnesses into the required set, mirroring the existing `wdrlAuthors` logic:

```haskell
-- Pseudocode
subWdrlAuthors txBody =
  foldMap wdrlAuthorsOf (OMap.elems $ txBody ^. subTransactionsTxBodyL)
  where
    wdrlAuthorsOf subTxBody =
      Map.foldrWithKey' accum Set.empty
        (unWithdrawals (subTxBody ^. withdrawalsTxBodyL))
    accum key _ !ans =
      case credKeyHashWitness (key ^. accountAddressCredentialL) of
        Nothing    -> ans
        Just vkWit -> Set.insert vkWit ans
```

Alternatively, prohibit withdrawals in sub-transactions entirely if the design intent is that sub-transactions are not independently authorized spending actions.

---

### Proof of Concept

```
Attacker observes victim's stake credential C_victim with reward balance R.

1. Attacker builds a DijkstraSubTxBody:
     withdrawals = { AccountAddress Testnet (AccountId C_victim) => R }
     outputs     = [ TxOut attackerAddr R ]   -- attacker receives R

2. Attacker wraps it in a DijkstraTxBody (top-level):
     subTransactions = { subTxId => subTx }
     inputs          = { someUTxO }           -- to cover fees
     witnesses       = { sig(attackerPayKey) } -- only attacker's payment key

3. Attacker submits the transaction.

Ledger processing:
  UTXOW: validateNeededWitnesses checks top-level txBody only.
         Top-level withdrawals = empty → no stake witness required. ✓
  SUBENTITIES: withdrawalsThatExceedAccountBalance(R, R) → OK. ✓
               applyWithdrawals drains C_victim's account. ✓

Result:
  victim's reward balance: 0  (was R)
  attacker's UTxO:         +R ADA
```

The attack succeeds because `getWitsVKeyNeeded` never adds `credKeyHashWitness C_victim` to the required set, so the missing witness is never detected.

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L139-139)
```haskell
  getWitsVKeyNeeded _ = getConwayWitsVKeyNeeded
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/UTxO.hs (L241-248)
```haskell
    wdrlAuthors :: Set (KeyHash Witness)
    wdrlAuthors = Map.foldrWithKey' accum Set.empty (unWithdrawals (txBody ^. withdrawalsTxBodyL))
      where
        accum key _ !ans =
          let cred = key ^. accountAddressCredentialL
           in case credKeyHashWitness cred of
                Nothing -> ans
                Just vkeyWit -> Set.insert vkeyWit ans
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxow.hs (L226-277)
```haskell
      witsKeyHashes = keyHashWitnessesTxWits (tx ^. witsTxL)

  -- All lookups use originalUtxo.
  -- A subtx may consume a txout that the top-level tx references, so the UTXO threaded in the state may not contain it.

  -- scriptsNeeded for the top-level tx
  let topScriptsNeeded = scriptsNeededStAnnTx stAnnTx
      topScriptHashesNeeded = getScriptsHashesNeeded topScriptsNeeded
      subStAnnTxs = subTransactionsStAnnTx stAnnTx

  -- scriptsNeeded aggregated across all levels
  let allScriptHashesNeeded =
        Set.unions $
          topScriptHashesNeeded
            : (getScriptsHashesNeeded . scriptsNeededStAnnTx <$> subStAnnTxs)

  {- ∀s ∈ (txscripts txw utxo neededHashes ) ∩ Scriptph1 , validateScript s tx -}
  -- Per-level: phase-1 script validation is per-tx (script execution)
  runTest $ Babbage.validateFailedBabbageScripts tx scriptsProvided topScriptHashesNeeded

  {- neededHashes − dom(refScripts tx utxo) = dom(txwitscripts txw) -}
  -- Aggregated: missing/extraneous scripts across all levels.
  let witnessScripts =
        Map.keysSet (tx ^. witsTxL . scriptTxWitsL)
          <> foldMap (Map.keysSet . (^. witsTxL . scriptTxWitsL)) subTxs
      allRefScriptInputs =
        txBody ^. referenceInputsTxBodyL
          <> txBody ^. inputsTxBodyL
          <> foldMap
            ( \subTx ->
                subTx ^. bodyTxL . referenceInputsTxBodyL
                  <> subTx ^. bodyTxL . inputsTxBodyL
            )
            subTxs
      refScripts = Map.keysSet $ getReferenceScripts originalUtxo allRefScriptInputs
  runTest $ Babbage.babbageMissingScripts pp allScriptHashesNeeded refScripts witnessScripts

  {-  inputHashes ⊆  dom(txdats txw) ⊆  allowed -}
  -- Per-level: datum check for top-level tx's own spend inputs
  runTest $ Alonzo.missingRequiredDatums scriptsProvided originalUtxo tx

  {- dom (txrdmrs tx) = { rdptr txb sp | (sp, h) ∈ scriptsNeeded utxo tx,
                          h ↦ s ∈ txscripts txw, s ∈ Scriptph2} -}
  -- Per-level: redeemer indexing is per-tx
  runTest $ Alonzo.hasExactSetOfRedeemers tx scriptsProvided topScriptsNeeded

  -- check VKey witnesses
  {- ∀ (vk ↦ σ) ∈ (txwitsVKey txw), V_vk⟦ txbodyHash ⟧_σ -}
  runTestOnSignal $ Shelley.validateVerifiedWits tx

  {- witsVKeyNeeded utxo tx genDelegs ⊆ witsKeyHashes -}
  runTest $ Shelley.validateNeededWitnesses witsKeyHashes certState originalUtxo txBody
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

**File:** eras/shelley/design-spec/shelley-delegation.tex (L826-828)
```tex
  address. Thus, spending from a reward account requires a witness for a stake
  credential, rather than a payment credential.
\end{itemize}
```
