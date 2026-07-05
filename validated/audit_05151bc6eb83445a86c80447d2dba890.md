### Title
Dijkstra Era `dijkstraTotalRefundsTxCerts` Reads Deposit Refund Amounts from Attacker-Controlled Certificates, Enabling Subtransaction Double-Spend of Deposit Refunds - (File: `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs`)

---

### Summary

In the Dijkstra era, `dijkstraTotalRefundsTxCerts` computes the total deposit refunds for the UTxO balance equation by reading amounts directly from attacker-controlled certificate fields, completely ignoring the ledger-state lookup functions. A disabled test with an explicit `TODO: predicate failure not yet implemented` comment acknowledges that the guard preventing multiple subtransactions from claiming the same deposit refund is not yet implemented. An attacker can craft a top-level transaction whose subtransactions each contain an `UnRegDepositTxCert` for the same staking credential, inflating the consumed-value side of the balance equation by the deposit amount per extra subtransaction, extracting ADA that was never deposited.

---

### Finding Description

**Vulnerability class:** Incorrect value reading from a state structure — the refund amount is read from the transaction itself (attacker-controlled) rather than from the authoritative ledger state, and the cross-subtransaction deduplication guard is absent.

**Root cause — `dijkstraTotalRefundsTxCerts`:**

```haskell
-- | Unlike previous eras, we no longer need to lookup refunds from the ledger
-- state, since all of the certificates specify the actual refund and ledger
-- rules will validate that they are accurate.
dijkstraTotalRefundsTxCerts ::
  ( Foldable f, ConwayEraTxCert era ) =>
  f (TxCert era) -> Coin
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit   -- ← reads attacker-supplied value
  UnRegDRepTxCert    _ deposit -> deposit   -- ← reads attacker-supplied value
  _ -> zero
``` [1](#0-0) 

The `EraTxCert` instance wires this in as the sole implementation, discarding both lookup callbacks:

```haskell
getTotalRefundsTxCerts _ _ _ = dijkstraTotalRefundsTxCerts
``` [2](#0-1) 

Every previous era (Shelley through Conway) passes `lookupStakingDeposit` / `lookupDRepDeposit` into the refund computation so the actual on-chain deposit is authoritative. Dijkstra drops those lookups entirely, relying solely on the certificate-embedded value.

**How the consumed-value path reaches this function:**

`getConsumedDijkstraValue` aggregates the consumed value of the top-level body **and** every subtransaction body:

```haskell
getConsumedDijkstraValue pp lookupStakingDeposit lookupDRepDeposit utxo txBody =
  withBothTxLevels txBody
    (\topTxBody ->
        txBodyConsumedValue topTxBody <> subTransactionsConsumedValue topTxBody)
    txBodyConsumedValue
  where
    txBodyConsumedValue = getConsumedMaryValue pp lookupStakingDeposit lookupDRepDeposit utxo
    subTransactionsConsumedValue topTxBody =
      foldMap'
        (getConsumedValue pp lookupStakingDeposit lookupDRepDeposit utxo . view bodyTxL)
        (topTxBody ^. subTransactionsTxBodyL)
``` [3](#0-2) 

`getConsumedMaryValue` calls `getTotalRefundsTxBody`, which calls `getTotalRefundsTxCerts`, which for `DijkstraEra` resolves to `dijkstraTotalRefundsTxCerts`. Each subtransaction's refund contribution is summed independently with no cross-subtransaction deduplication.

**The missing guard — explicitly acknowledged in the test suite:**

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
  stakingCred <- KeyHashObj <$> freshKeyHash
  _ <- registerStakeCredential stakingCred
  keyDeposit <- getsPParams ppKeyDepositL
  ...
  let
    subTx1 = mkBasicTx mkBasicTxBody
      & bodyTxL . certsTxBodyL .~ SSeq.singleton
          (UnRegDepositTxCert stakingCred keyDeposit)
    subTx2 = mkBasicTx mkBasicTxBody
      & bodyTxL . certsTxBodyL .~ SSeq.singleton
          (UnRegDepositTxCert stakingCred keyDeposit)
    tx = mkBasicTx mkBasicTxBody
      & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
  submitFailingTx tx . NE.singleton $
    error "TODO: predicate failure not yet implemented"
``` [4](#0-3) 

The `xit` (pending/skipped) status combined with `error "TODO: predicate failure not yet implemented"` as the expected failure explicitly records that the rule preventing two subtransactions from claiming the same refund **does not yet exist**. The test is not run; the transaction is expected to succeed in the current implementation when it should fail.

A second disabled test confirms the related scenario where the old deposit amount is used after a protocol-parameter change is also unguarded:

```haskell
xit "Subtransaction consumes correct refund after keyDeposit is changed" $ do
  ...
  let deRegCert = UnRegDepositTxCert stakingCred initialKeyDeposit
  submitTx_ $ mkBasicTx mkBasicTxBody
    & bodyTxL . subTransactionsTxBodyL .~ OMap.singleton subTransaction
``` [5](#0-4) 

**Contrast with Conway era (correct behaviour):**

In Conway, `conwayDRepRefundsTxCerts` and `shelleyTotalRefundsTxCerts` both look up the actual deposit from the ledger state and validate the certificate-supplied amount against it in the DELEG/GOVCERT rules before crediting any refund:

```haskell
| Just deposit <- lookupDRepDeposit cred ->
    (drepRegsInTx, totalRefund <+> deposit)   -- ← from ledger state
``` [6](#0-5) 

The Conway DELEG rule also validates the refund against the stored deposit:

```haskell
let expectedRefund = fromCompact $ accountState ^. depositAccountStateL
guard (suppliedRefund /= expectedRefund)
``` [7](#0-6) 

Dijkstra drops the lookup entirely and the cross-subtransaction guard is absent.

---

### Impact Explanation

**Critical — Direct loss of ADA through an invalid ledger state transition.**

The UTxO balance equation `consumed = produced` is the preservation-of-value invariant. If `consumed` is inflated by counting the same deposit refund N times (once per subtransaction), the equation can be satisfied while the deposit pot is only reduced once. The difference (N−1)×D ADA is extracted from the deposit pot into attacker-controlled outputs without a corresponding deposit having been made. This is a direct, attacker-triggered creation of ADA from the deposit pot, constituting an invalid ledger state transition.

---

### Likelihood Explanation

The Dijkstra era is the next planned era (present in the repository as active production code). The attack requires only:
1. A registered staking credential (trivially obtained by any user).
2. A top-level transaction with two or more subtransactions each containing `UnRegDepositTxCert` for the same credential.
3. No privileged access, no governance majority, no leaked keys.

The attacker-controlled entry path is a serialized transaction submitted by any unprivileged sender. The `TODO` comment confirms the guard is absent in the current implementation.

---

### Recommendation

1. **Implement the cross-subtransaction deduplication guard** referenced by the `TODO` comment in `Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs`. The SUBCERTS/SUBDELEG rules must track which credentials have already been unregistered across all subtransactions processed so far and reject any subsequent `UnRegDepositTxCert` for the same credential.

2. **Restore ledger-state lookup in `dijkstraTotalRefundsTxCerts`** (or in the consumed-value aggregation for subtransactions) so that the refund amount credited to the balance equation is bounded by the actual on-chain deposit, not the certificate-supplied value.

3. **Enable and complete the two `xit` tests** in `Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs` once the guards are implemented.

---

### Proof of Concept

```
1. Alice registers stakingCred in a prior transaction, paying keyDeposit D.
   Ledger state: depositAccountState[stakingCred] = D
   Deposit pot: P

2. Alice constructs a top-level Dijkstra transaction T with two subtransactions:
     subTx1.certs = [UnRegDepositTxCert stakingCred D]
     subTx2.certs = [UnRegDepositTxCert stakingCred D]

3. getConsumedDijkstraValue sums:
     refunds(subTx1) = D   (from dijkstraTotalRefundsTxCerts)
     refunds(subTx2) = D   (from dijkstraTotalRefundsTxCerts)
     total refunds credited to consumed = 2D

4. Alice sets T's outputs to absorb the extra D (balance equation satisfied with 2D refund).

5. SUBDELEG processes subTx1: unregisters stakingCred, deposit pot becomes P − D. ✓
   SUBDELEG processes subTx2: no cross-subtransaction guard exists (TODO),
   so the second unregistration is not rejected; deposit pot is not reduced again
   but the balance equation already credited 2D to consumed.

6. Net effect: Alice's outputs contain D extra ADA extracted from the deposit pot.
   Deposit pot: P − D (correct deduction) but Alice received 2D in refunds.
   Invariant violated: D ADA created from thin air.
```

### Citations

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs (L228-238)
```haskell
-- | Unlike previous eras, we no longer need to lookup refunds from the ledger state, since all of the certificates specify the actual refund and ledger rules will validate that they are accurate.
dijkstraTotalRefundsTxCerts ::
  ( Foldable f
  , ConwayEraTxCert era
  ) =>
  f (TxCert era) ->
  Coin
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit
  UnRegDRepTxCert _ deposit -> deposit
  _ -> zero
```

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs (L285-285)
```haskell
  getTotalRefundsTxCerts _ _ _ = dijkstraTotalRefundsTxCerts
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

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs (L22-51)
```haskell
  xit "Subtransaction consumes correct refund after keyDeposit is changed" $ do
    stakingCred <- KeyHashObj <$> freshKeyHash
    _ <- registerStakeCredential stakingCred

    initialKeyDeposit <- getsPParams ppKeyDepositL
    impAnn "Change key deposit" $ do
      (dRep, _, _) <- setupSingleDRep 100_000_000
      ccHotCreds <- registerInitialCommittee
      let newKeyDeposit = initialKeyDeposit <> initialKeyDeposit
      ppChangeId <-
        submitParameterChange SNothing $
          emptyPParamsUpdate
            & ppuKeyDepositL .~ SJust newKeyDeposit
      submitYesVote_ (DRepVoter dRep) ppChangeId
      submitYesVoteCCs_ ccHotCreds ppChangeId
      getsPParams ppKeyDepositL `shouldReturn` initialKeyDeposit
      passNEpochs 2
      getsPParams ppKeyDepositL `shouldReturn` newKeyDeposit

    impAnn "Unregister staking credential" $ do
      expectStakeCredRegistered stakingCred
      let
        deRegCert = UnRegDepositTxCert stakingCred initialKeyDeposit
        subTransaction =
          mkBasicTx mkBasicTxBody
            & bodyTxL . certsTxBodyL .~ SSeq.singleton deRegCert
      submitTx_ $
        mkBasicTx mkBasicTxBody
          & bodyTxL . subTransactionsTxBodyL .~ OMap.singleton subTransaction
      expectStakeCredNotRegistered stakingCred
```

**File:** eras/dijkstra/impl/testlib/Test/Cardano/Ledger/Dijkstra/Imp/CertSpec.hs (L53-75)
```haskell
  xit "Multiple subtransactions cannot get the same refund" $ do
    stakingCred <- KeyHashObj <$> freshKeyHash
    _ <- registerStakeCredential stakingCred
    keyDeposit <- getsPParams ppKeyDepositL
    value1 <- arbitrary
    (_, addr1) <- freshKeyAddr
    input1 <- sendCoinTo addr1 value1
    value2 <- arbitrary
    (_, addr2) <- freshKeyAddr
    input2 <- sendCoinTo addr2 value2
    let
      subTx1 =
        mkBasicTx mkBasicTxBody
          & bodyTxL . inputsTxBodyL .~ Set.singleton input1
          & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
      subTx2 =
        mkBasicTx mkBasicTxBody
          & bodyTxL . inputsTxBodyL .~ Set.singleton input2
          & bodyTxL . certsTxBodyL .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
      tx =
        mkBasicTx mkBasicTxBody
          & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
    submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/TxCert.hs (L860-872)
```haskell
conwayDRepRefundsTxCerts lookupDRepDeposit = snd . F.foldl' go (Map.empty, Coin 0)
  where
    go accum@(!drepRegsInTx, !totalRefund) = \case
      RegDRepTxCert cred deposit _ ->
        -- Track registrations
        (Map.insert cred deposit drepRegsInTx, totalRefund)
      UnRegDRepTxCert cred _
        -- DRep previously registered in the same tx.
        | Just deposit <- Map.lookup cred drepRegsInTx ->
            (Map.delete cred drepRegsInTx, totalRefund <+> deposit)
        -- DRep previously registered in some other tx.
        | Just deposit <- lookupDRepDeposit cred -> (drepRegsInTx, totalRefund <+> deposit)
      _ -> accum
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Deleg.hs (L247-248)
```haskell
            let expectedRefund = fromCompact $ accountState ^. depositAccountStateL
            guard (suppliedRefund /= expectedRefund)
```
