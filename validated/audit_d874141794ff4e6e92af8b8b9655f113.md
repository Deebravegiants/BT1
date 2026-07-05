### Title
`DirectDeposits` Credits ADA to Account Balances Without Value Conservation Enforcement - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs`)

---

### Summary

In the Dijkstra era, a transaction's `directDeposits` field credits arbitrary ADA amounts to registered account balances via the `ENTITIES` rule, but these amounts are never included in the `consumed = produced` value conservation equation enforced by the `UTXO` rule. Any unprivileged transaction author can include a `directDeposits` map crediting large ADA sums to any registered accounts without spending corresponding UTxO inputs, creating ADA out of thin air and permanently inflating the total ADA supply.

---

### Finding Description

**Vulnerability class:** Funds/accounting bug — missing term in the preservation-of-value equation.

**Analog to the external report:** The stETH report describes minting stETH on L2 without minting the corresponding backing wstETH, so the stETH contract becomes insolvent. The analog here is that `directDeposits` credits ADA to account balances without deducting that ADA from the UTxO, so the total ADA in the system increases.

**Root cause — step by step:**

**Step 1.** The Dijkstra `TxBody` (both `TopTx` and `SubTx` levels) carries a `dtbrDirectDeposits :: !DirectDeposits` field, which is a `Map AccountAddress Coin`. [1](#0-0) [2](#0-1) 

**Step 2.** In the `ENTITIES` transition rule, after certificates are processed, `applyDirectDeposits` is called unconditionally, adding the specified coin amounts to the matching account balances:

```haskell
pure $ certStateAfterCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
``` [3](#0-2) 

The same pattern is repeated in `SUBENTITIES` for sub-transactions: [4](#0-3) 

**Step 3.** `applyDirectDeposits` simply adds the coin amount to each account's balance with no further checks:

```haskell
applyDirectDeposits (DirectDeposits dd) =
  updateAccountBalances
    (\amount account -> addCompactCoin amount (account ^. balanceAccountStateL))
    dd
``` [5](#0-4) 

**Step 4.** The Dijkstra UTXO rule enforces value conservation at line 381:

```haskell
{- consumed pp utxo₀ txb = produced pp certState txb -}
runTest $ Shelley.validateValueNotConservedUTxO pp originalUtxo certState txBody
``` [6](#0-5) 

This calls `getConsumedValue` and `getProducedValue`, which for Dijkstra resolve to `getConsumedDijkstraValue` and `getProducedDijkstraValue`: [7](#0-6) 

**Step 5.** `getConsumedDijkstraValue` aggregates consumed value using `getConsumedMaryValue` for each tx body. `getConsumedMaryValue` sums: UTxO inputs + minted multi-assets + withdrawals + refunds. **`directDeposits` is absent.** [8](#0-7) [9](#0-8) 

**Step 6.** `getProducedDijkstraValue` aggregates produced value using `conwayProducedValue` (outputs + fee + certificate deposits) for each tx body. **`directDeposits` is absent.** [10](#0-9) 

**Step 7.** The only validation applied to `directDeposits` in the UTXO rule is a network-ID check and a "missing accounts" check in ENTITIES. Neither enforces that the deposited ADA is funded from UTxO inputs. [11](#0-10) [12](#0-11) 

**Net effect:** A transaction can balance its UTxO inputs against its UTxO outputs + fee + certificate deposits (satisfying `consumed = produced`), while simultaneously specifying a `directDeposits` map that credits an arbitrary amount of ADA to registered accounts. That ADA is created from nothing — it is not deducted from any UTxO input, deposit pot, treasury, or reserves.

---

### Impact Explanation

**Critical. Direct creation of ADA through an invalid ledger state transition.**

The Cardano ledger's core invariant is that the total ADA across all six pots (circulation, deposits, fees, rewards, treasury, reserves) is constant. `directDeposits` credits ADA to the rewards/account-balance pot without debiting any other pot. An attacker can inflate the total ADA supply by an arbitrary amount in a single transaction, permanently breaking the preservation-of-value invariant. All honest nodes would accept this transaction (it passes all validation checks), so the inflated state would be canonical and irrecoverable without a hard fork.

---

### Likelihood Explanation

**High.** The entry path requires only the ability to submit a valid Dijkstra-era transaction. No privileged keys, governance majority, or special role is needed. The attacker must:
1. Have at least one UTxO input (to satisfy `inputsTxBodyL ≠ ∅`).
2. Know the `AccountAddress` of at least one registered account (publicly observable on-chain).
3. Construct a transaction with a non-empty `directDeposits` field targeting that account.

The transaction passes all existing validation checks because `directDeposits` is never included in the `consumed = produced` equation. The attack is deterministic and repeatable.

---

### Recommendation

Include the total coin value of `directDeposits` in the `produced` side of the value conservation equation, analogously to how certificate deposits are handled. Concretely, `getProducedDijkstraValue` (and `dijkstraSubTxProducedValue`) should add `sum (unDirectDeposits (txBody ^. directDepositsTxBodyL))` to the produced value, so that the ADA credited to accounts must be explicitly funded by UTxO inputs.

The corrected `produced` equation for Dijkstra should be:

```
produced = outputs + fee + certificate_deposits + direct_deposits
```

This mirrors the existing pattern for certificate deposits and ensures that `directDeposits` transfers ADA from the UTxO circulation into account balances rather than creating it.

---

### Proof of Concept

1. Register a stake credential `C` on-chain (standard `RegDepositTxCert`).
2. Construct a Dijkstra top-level transaction `tx` with:
   - One UTxO input worth 2 ADA.
   - One UTxO output worth 1 ADA (to the attacker's own address).
   - Fee = 1 ADA.
   - `directDeposits = { AccountAddress(C) → 1_000_000_000_000 }` (one trillion lovelace).
3. The `consumed = produced` check passes: `2 ADA = 1 ADA (output) + 1 ADA (fee)`.
4. The `directDepositsMissingAccounts` check passes because `C` is registered.
5. The network-ID check passes if the correct network is used.
6. The ENTITIES rule applies `applyDirectDeposits`, crediting 1,000,000 ADA to account `C`.
7. The attacker can now withdraw 1,000,000 ADA from account `C` into any UTxO output, having spent only 2 ADA in inputs. [13](#0-12) [14](#0-13) [15](#0-14)

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L183-188)
```haskell
    , dtbrTreasuryDonation :: !Coin
    , dtbrSubTransactions :: !(OMap TxId (Tx SubTx era))
    , dtbrDirectDeposits :: !DirectDeposits
    , dtbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw TopTx era
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L205-209)
```haskell
    , dstbrRequiredTopLevelGuards :: !(Map (Credential Guard) (StrictMaybe (Data era)))
    , dstbrDirectDeposits :: !DirectDeposits
    , dstbrAccountBalanceIntervals :: !(AccountBalanceIntervals era)
    } ->
    DijkstraTxBodyRaw SubTx era
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/SubEntities.hs (L182-187)
```haskell
  let directDeposits = tx ^. bodyTxL . directDepositsTxBodyL
      accountsAfterSubCerts = certStateAfterSubCerts ^. certDStateL . accountsL
  failOnJust (directDepositsMissingAccounts directDeposits accountsAfterSubCerts) $
    injectFailure . SubDirectDepositsToMissingAccounts

  pure $ certStateAfterSubCerts & certDStateL . accountsL %~ applyDirectDeposits directDeposits
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/Rules/Utxo.hs (L343-381)
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
```

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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/UTxO.hs (L124-131)
```haskell
instance EraUTxO DijkstraEra where
  type ScriptsNeeded DijkstraEra = AlonzoScriptsNeeded DijkstraEra

  consumed = conwayConsumed

  getConsumedValue = getConsumedDijkstraValue

  getProducedValue = getProducedDijkstraValue
```

**File:** eras/mary/impl/src/Cardano/Ledger/Mary/UTxO.hs (L69-87)
```haskell
getConsumedMaryValue ::
  (MaryEraTxBody era, Value era ~ MaryValue) =>
  PParams era ->
  (Credential Staking -> Maybe Coin) ->
  (Credential DRepRole -> Maybe Coin) ->
  UTxO era ->
  TxBody l era ->
  MaryValue
getConsumedMaryValue pp lookupStakingDeposit lookupDRepDeposit utxo txBody =
  consumedValue <> MaryValue mempty mintedMultiAsset
  where
    mintedMultiAsset = filterMultiAsset (\_ _ -> (> 0)) $ txBody ^. mintTxBodyL
    {- balance (txins tx ◁ u) + wbalance (txwdrls tx) + keyRefunds pp tx -}
    consumedValue =
      sumUTxO (txInsFilter utxo (txBody ^. inputsTxBodyL))
        <> inject (refunds <> withdrawals)
    refunds = getTotalRefundsTxBody pp lookupStakingDeposit lookupDRepDeposit txBody
    withdrawals = fold . unWithdrawals $ txBody ^. withdrawalsTxBodyL

```
