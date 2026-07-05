### Title
Multiple Sub-Transactions Can Claim the Same Deposit Refund in Dijkstra Era — (`eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs`)

---

### Summary

In the Dijkstra era, `dijkstraTotalRefundsTxCerts` computes deposit refunds by naively summing the amounts stated in the certificates themselves, without consulting the ledger state. Because the specific guard preventing multiple sub-transactions from each claiming the same deposit refund has not been implemented (the test is explicitly disabled with `error "TODO: predicate failure not yet implemented"`), an attacker can include two sub-transactions that each carry an `UnRegDepositTxCert` for the same staking credential. Each sub-transaction's UTxO balance check independently counts the full refund, allowing the outer transaction to extract more ADA from the deposit pot than was ever deposited.

---

### Finding Description

**Root cause — `dijkstraTotalRefundsTxCerts` ignores ledger state:**

In `eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxCert.hs`, the refund-computation function for the Dijkstra era is:

```haskell
-- | Unlike previous eras, we no longer need to lookup refunds from the ledger
-- state, since all of the certificates specify the actual refund and ledger
-- rules will validate that they are accurate.
dijkstraTotalRefundsTxCerts ::
  ( Foldable f, ConwayEraTxCert era ) =>
  f (TxCert era) -> Coin
dijkstraTotalRefundsTxCerts = foldMap' $ \case
  UnRegDepositTxCert _ deposit -> deposit
  UnRegDRepTxCert  _ deposit -> deposit
  _ -> zero
``` [1](#0-0) 

This function is wired into the `EraTxCert` instance, discarding the `lookupStakingDeposit` and `lookupDRepDeposit` callbacks that previous eras used to cross-check against the actual deposit stored in the ledger state:

```haskell
getTotalRefundsTxCerts _ _ _ = dijkstraTotalRefundsTxCerts
``` [2](#0-1) 

The comment says "ledger rules will validate that they are accurate," but the specific rule that would prevent the same credential's refund from being claimed twice across sub-transactions has not been implemented.

**Missing guard — disabled test with `TODO`:**

The test suite for the Dijkstra era explicitly acknowledges this gap:

```haskell
xit "Multiple subtransactions cannot get the same refund" $ do
  stakingCred <- KeyHashObj <$> freshKeyHash
  _ <- registerStakeCredential stakingCred
  keyDeposit <- getsPParams ppKeyDepositL
  ...
  let
    subTx1 = mkBasicTx mkBasicTxBody
      & bodyTxL . inputsTxBodyL .~ Set.singleton input1
      & bodyTxL . certsTxBodyL  .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    subTx2 = mkBasicTx mkBasicTxBody
      & bodyTxL . inputsTxBodyL .~ Set.singleton input2
      & bodyTxL . certsTxBodyL  .~ SSeq.singleton (UnRegDepositTxCert stakingCred keyDeposit)
    tx = mkBasicTx mkBasicTxBody
      & bodyTxL . subTransactionsTxBodyL .~ OMap.fromFoldable [subTx1, subTx2]
  submitFailingTx tx . NE.singleton $ error "TODO: predicate failure not yet implemented"
``` [3](#0-2) 

`xit` disables the test entirely. The `error "TODO: predicate failure not yet implemented"` confirms that no predicate failure has been wired up to reject this case. The developers know the transaction should be rejected but have not yet implemented the enforcement.

**How the UTxO balance check is exploited:**

Each sub-transaction is validated by its own UTxO rule. The UTxO rule calls `getTotalRefundsTxBody`, which calls `getTotalRefundsTxCerts`, which resolves to `dijkstraTotalRefundsTxCerts`. Because that function simply reads the deposit amount from the certificate field without checking whether the credential is still registered or whether another sub-transaction has already claimed the refund, both `subTx1` and `subTx2` pass their individual UTxO balance checks with a full refund of `keyDeposit` each. [4](#0-3) 

The deposit pot is debited twice while only one credential was ever registered, creating ADA from nothing.

**Contrast with Conway era (the correct approach):**

In Conway, `conwayTotalRefundsTxCerts` passes the `lookupStakingDeposit` callback, which reads the actual deposit stored in the `DState`. A second deregistration for the same credential returns `Nothing` from the lookup and contributes zero to the refund total: [5](#0-4) [6](#0-5) 

---

### Impact Explanation

An attacker who registers one staking credential (paying deposit `D`) can construct a Dijkstra-era transaction containing two sub-transactions that each carry `UnRegDepositTxCert stakingCred D`. Each sub-transaction's UTxO balance check independently credits `D` as a refund. The deposit pot is reduced by `2D` while only `D` was ever deposited, constituting **direct creation of ADA through an invalid ledger state transition** — matching the Critical impact category: *"Direct loss, creation, or destruction of ADA or native assets through an invalid ledger state transition."*

---

### Likelihood Explanation

The Dijkstra era is the current development frontier and will be deployed on mainnet. The attack requires only:
1. Submitting a valid Dijkstra-era transaction with two sub-transactions sharing a deregistration certificate for the same credential.
2. No privileged access, no governance majority, no leaked keys.

The disabled test and the `TODO` comment confirm the developers are aware of the gap and that no enforcement exists yet.

---

### Recommendation

1. **Implement the missing predicate failure** in the sub-ledger/sub-certs rule that detects when two sub-transactions within the same outer transaction both attempt to deregister the same credential (or claim the same DRep refund).
2. **Restore ledger-state cross-checking** in `dijkstraTotalRefundsTxCerts` (or in the sub-transaction CERT rule) so that a refund is only credited if the credential is still registered at the point of processing and has not already been claimed by an earlier sub-transaction in the same batch.
3. **Enable and complete the test** `"Multiple subtransactions cannot get the same refund"` in `Test.Cardano.Ledger.Dijkstra.Imp.CertSpec` once the predicate failure is implemented.

---

### Proof of Concept

```
1. Register stakingCred, paying keyDeposit D.
2. Construct outer tx with:
     subTx1: inputs={utxo1}, certs=[UnRegDepositTxCert stakingCred D]
     subTx2: inputs={utxo2}, certs=[UnRegDepositTxCert stakingCred D]
3. Submit outer tx.
4. dijkstraTotalRefundsTxCerts counts D for subTx1 and D for subTx2
   independently (no ledger-state lookup).
5. Both sub-transactions pass their UTxO balance checks.
6. No predicate failure exists to reject the double-claim.
7. Deposit pot is debited 2D; attacker net-gains D ADA.
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

**File:** eras/dijkstra/impl/src/Cardano/Ledger/Dijkstra/TxBody.hs (L977-978)
```haskell
  getTotalRefundsTxBody pp lookupStakingDeposit lookupDRepDeposit txBody =
    getTotalRefundsTxCerts pp lookupStakingDeposit lookupDRepDeposit (txBody ^. certsTxBodyL)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/TxCert.hs (L849-851)
```haskell
conwayTotalRefundsTxCerts pp lookupStakingDeposit lookupDRepDeposit certs =
  shelleyTotalRefundsTxCerts pp lookupStakingDeposit certs
    <+> conwayDRepRefundsTxCerts lookupDRepDeposit certs
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/TxCert.hs (L639-659)
```haskell
shelleyTotalRefundsTxCerts pp lookupDeposit = snd . F.foldl' accum (mempty, Coin 0)
  where
    keyDeposit = pp ^. ppKeyDepositL
    accum (!regCreds, !totalRefunds) cert =
      case lookupRegStakeTxCert cert of
        Just k ->
          -- Need to track new delegations in case that the same key is later deregistered in
          -- the same transaction.
          (Set.insert k regCreds, totalRefunds)
        Nothing ->
          case lookupUnRegStakeTxCert cert of
            Just cred
              -- We first check if there was already a registration certificate in this
              -- transaction.
              | Set.member cred regCreds -> (Set.delete cred regCreds, totalRefunds <+> keyDeposit)
              -- Check for the deposit left during registration in some previous
              -- transaction. This de-registration check will be matched first, despite being
              -- the last case to match, because registration is not possible without
              -- de-registration.
              | Just deposit <- lookupDeposit cred -> (regCreds, totalRefunds <+> deposit)
            _ -> (regCreds, totalRefunds)
```
