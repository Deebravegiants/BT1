### Title
`directDeposits` Applied to Account Balances After `consumed == produced` Balance Check, Enabling Unbounded ADA Creation — (`File: eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, the `directDeposits` field of a transaction body is applied to stake-account balances **after** the `consumed == produced` preservation-of-value check, and the field is absent from both the `consumed` and `produced` accounting functions. Any transaction author who controls a registered stake credential can include an arbitrarily large `directDeposits` entry, pass the balance check, and have that amount credited to their account balance without any corresponding deduction from UTxO outputs — creating ADA out of thin air.

---

### Finding Description

**Execution order in the Dijkstra LEDGER rule:**

1. **UTXOW → UTXO** (`dijkstraUtxoTransition`, line 381): runs `Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody`, which checks `consumed pp certState utxo txBody == produced pp certState txBody`.
2. **ENTITIES** (`dijkstraEntitiesTransition`, line 216): runs `applyDirectDeposits directDeposits` on the post-CERTS account state.

**`consumed` for Dijkstra** is `conwayConsumed` → `getConsumedDijkstraValue` → `getConsumedMaryValue` → UTxO inputs + withdrawals + cert refunds + minted tokens. No `directDeposits` term. [1](#0-0) 

**`produced` for Dijkstra** is `getProducedDijkstraValue` → `dijkstraProducedValue` → `conwayProducedValue` → UTxO outputs + fees + cert deposits + treasury donation. No `directDeposits` term. [2](#0-1) 

The balance check therefore enforces:

```
inputs + withdrawals + cert_refunds  ==  outputs + fees + cert_deposits + treasury_donation
```

After this check passes, `dijkstraEntitiesTransition` calls `applyDirectDeposits`, which unconditionally **adds** the declared amounts to account balances: [3](#0-2) 

`applyDirectDeposits` itself performs no amount validation: [4](#0-3) 

The only pre-application check is `directDepositsMissingAccounts`, which only verifies that target credentials are registered — it does not constrain amounts: [5](#0-4) 

The UTXO rule validates network IDs in direct deposits but nothing else: [6](#0-5) 

The identical flaw exists in the sub-transaction path via `dijkstraSubEntitiesTransition`: [7](#0-6) 

**Preservation-of-value accounting gap:**

The true invariant requires:

```
inputs + withdrawals + cert_refunds  ==  outputs + fees + cert_deposits + direct_deposits + treasury_donation
```

The implemented check omits `direct_deposits` from the right-hand side. Every lovelace credited via `directDeposits` is therefore unaccounted for — it is not deducted from any UTxO output, deposit pot, or treasury. The total ADA in the system increases by exactly `sum(directDeposits)` per transaction.

---

### Impact Explanation

**Critical — Direct creation of ADA through an invalid ledger state transition.**

An attacker can register a stake credential (a normal, unprivileged operation), craft a Dijkstra-era transaction whose `directDeposits` field credits their own account with an arbitrary amount, have the transaction accepted by all honest nodes (the balance check passes), and then withdraw the fabricated ADA in a subsequent transaction. This violates the fundamental preservation-of-value invariant of the Cardano ledger and constitutes unbounded ADA minting by any transaction author.

---

### Likelihood Explanation

Any transaction author who can submit a valid Dijkstra-era transaction can trigger this. No special privilege, governance majority, or key compromise is required. The only prerequisite is a registered stake credential, which is a standard user operation. The attack is deterministic and repeatable.

---

### Recommendation

`directDeposits` must be included in the `produced` side of the balance equation. Concretely, `dijkstraProducedValue` (and `dijkstraSubTxProducedValue`) should add `inject (sum (unDirectDeposits (txBody ^. directDepositsTxBodyL)))` to the produced value, mirroring how `treasuryDonationTxBodyL` is handled in `conwayProducedValue`. [2](#0-1) 

This ensures that the ADA credited to accounts via direct deposits is funded by the transaction's UTxO inputs, restoring the preservation-of-value invariant.

---

### Proof of Concept

1. Register stake credential `C` on the Dijkstra era ledger (standard `RegTxCert`).
2. Construct a top-level Dijkstra transaction `tx` with:
   - Any valid UTxO inputs/outputs/fees satisfying `consumed == produced` (e.g., 5 ADA input → 4 ADA output + 1 ADA fee).
   - `directDeposits = DirectDeposits { AccountAddress mainnet C → 1_000_000_000_000 }` (1 million ADA).
3. Submit `tx`. The UTXO rule checks `consumed == produced` over inputs/outputs/fees only — passes. The ENTITIES rule then calls `applyDirectDeposits`, crediting 1 million ADA to account `C`.
4. Submit a withdrawal transaction draining account `C`. The 1 million ADA is now in a UTxO output.

Total ADA in the system has increased by 1 million ADA with no corresponding destruction of any existing value. [8](#0-7) [9](#0-8)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L65-91)
```haskell
getConsumedDijkstraValue ::
  forall era l.
  ( DijkstraEraTxBody era
  , EraUTxO era
  , Value era ~ MaryValue
  , STxLevel l era ~ STxBothLevels l era
  ) =>
  PParams era ->
  (Credential Staking -> Maybe Coin) ->
  (Credential DRepRole -> Maybe Coin) ->
  UTxO era ->
  TxBody l era ->
  Value era
getConsumedDijkstraValue pp lookupStakingDeposit lookupDRepDeposit utxo txBody =
  withBothTxLevels
    txBody
    ( \topTxBody ->
        txBodyConsumedValue topTxBody <> subTransactionsConsumedValue topTxBody
    )
    txBodyConsumedValue
  where
    txBodyConsumedValue :: forall m. TxBody m era -> Value era
    txBodyConsumedValue = getConsumedMaryValue pp lookupStakingDeposit lookupDRepDeposit utxo
    subTransactionsConsumedValue topTxBody =
      foldMap'
        (getConsumedValue pp lookupStakingDeposit lookupDRepDeposit utxo . view bodyTxL)
        (topTxBody ^. subTransactionsTxBodyL)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L93-106)
```haskell
dijkstraProducedValue ::
  ( DijkstraEraTxBody era
  , EraUTxO era
  , Value era ~ MaryValue
  ) =>
  PParams era ->
  (KeyHash StakePool -> Bool) ->
  TxBody TopTx era ->
  MaryValue
dijkstraProducedValue pp isRegPoolId txBody =
  conwayProducedValue pp isRegPoolId txBody
    <> foldMap'
      (getProducedValue pp isRegPoolId . view bodyTxL)
      (txBody ^. subTransactionsTxBodyL)
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

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L287-298)
```haskell
-- | Add each direct-deposit amount to the matching account balance.
--
-- /Note/ - There are no checks that direct deposits mention only registered accounts.
applyDirectDeposits ::
  EraAccounts era =>
  DirectDeposits ->
  Accounts era ->
  Accounts era
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/State/Account.hs (L329-343)
```haskell
directDepositsMissingAccounts ::
  EraAccounts era =>
  DirectDeposits ->
  Accounts era ->
  Maybe DirectDeposits
directDepositsMissingAccounts (DirectDeposits dds) accounts
  | Map.foldrWithKey' checkRegistered True dds = Nothing
  | otherwise = Just $ DirectDeposits $ Map.foldrWithKey' collectMissing Map.empty dds
  where
    isRegistered (AccountAddress _ (AccountId credential)) =
      isAccountRegistered credential accounts
    checkRegistered addr _ acc = acc && isRegistered addr
    collectMissing addr amount acc
      | isRegistered addr = acc
      | otherwise = Map.insert addr amount acc
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L304-316)
```haskell
validateWrongNetworkInDirectDeposit ::
  DijkstraEraTxBody era =>
  Network ->
  TxBody t era ->
  Test (DijkstraUtxoPredFailure era)
validateWrongNetworkInDirectDeposit netId txb =
  failureOnNonEmptySet depositsWrongNetwork (WrongNetworkInDirectDeposit netId)
  where
    depositsWrongNetwork =
      Map.keysSet $
        Map.filterWithKey
          (\a _ -> aaNetworkId a /= netId)
          (unDirectDeposits $ txb ^. directDepositsTxBodyL)
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L378-382)
```haskell
  runTest $ validateBatchWithdrawals accounts tx

  {- consumed pp utxo₀ txb = produced pp certState txb -}
  runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody

```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L182-187)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
    injectFailure . SubDirectDepositsToMissingAccounts

  pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
```
