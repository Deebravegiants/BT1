### Title
Reward Withdrawal Allowed When Delegated DRep Is Expired — Missing Expiry Check in `validateWithdrawalsDelegated` - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs`)

---

### Summary

The Conway ledger rule `validateWithdrawalsDelegated` enforces that a staking key must be delegated to a DRep before its reward account can be withdrawn. However, the check only verifies that a DRep delegation record *exists* in the account state — it does not verify that the delegated DRep is still **active** (non-expired). A staking key holder whose delegated DRep has expired can still successfully withdraw accumulated rewards, bypassing the governance-participation requirement that is the design intent of the check.

---

### Finding Description

In the Conway era, the `validateWithdrawalsDelegated` function in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs` is the gating check for reward withdrawals:

```haskell
validateWithdrawalsDelegated accounts tx =
  let wdrls = unWithdrawals $ tx ^. bodyTxL . withdrawalsTxBodyL
      wdrlsKeyHashes =
        [ kh | (ra, _) <- Map.toList wdrls, Just kh <- [credKeyHash $ ra ^. accountAddressCredentialL]
        ]
      isNotDRepDelegated keyHash = isNothing $ do
        accountState <- lookupAccountState (KeyHashObj keyHash) accounts
        accountState ^. dRepDelegationAccountStateL
      nonExistentDelegations =
        filter isNotDRepDelegated wdrlsKeyHashes
   in failureOnNonEmpty nonExistentDelegations ConwayWdrlNotDelegatedToDRep
``` [1](#0-0) 

The predicate `isNotDRepDelegated` returns `False` (i.e., "is delegated") whenever `dRepDelegationAccountStateL` is `Just _` — regardless of whether the DRep pointed to is still registered or still active. When a DRep expires, its `DRepState` record remains in `vsDReps` with a past `drepExpiry` epoch, and the staking account's `dRepDelegationAccountStateL` field continues to hold `Just (DRepCredential expiredDRep)`. The check therefore passes.

By contrast, the ratification rule `dRepAcceptedRatio` in `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs` explicitly excludes expired DReps from vote counting:

```haskell
Just drepState
  | reCurrentEpoch > drepExpiry drepState -> (yes, tot) -- drep is expired, so we don't consider it
``` [2](#0-1) 

So the ratification layer correctly treats expired DReps as inactive, but the withdrawal-validation layer does not.

The existing test suite confirms this gap. The test `"Withdraw from a key delegated to an expired DRep"` in `eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/LedgerSpec.hs` uses `submitTx_` (expects success) after confirming `isDRepExpired drep \`shouldReturn\` True`: [3](#0-2) 

A second test, `"Withdraw from a key delegated to a DRep that expired after delegation"`, is explicitly disabled with `disableInConformanceIt` and references formal spec issue #635, acknowledging that the formal specification disagrees with the implementation on this point: [4](#0-3) 

The `dRepDelegationAccountStateL` field in `AccountState` stores the DRep the account is delegated to, but carries no expiry information: [5](#0-4) 

The actual DRep expiry is stored in `DRepState.drepExpiry` inside `VState.vsDReps`, which `validateWithdrawalsDelegated` never consults: [6](#0-5) 

The `vsActualDRepExpiry` helper that correctly computes effective expiry (accounting for `vsNumDormantEpochs`) exists but is not used in the withdrawal path: [7](#0-6) 

---

### Impact Explanation

The design intent of `validateWithdrawalsDelegated` is to enforce governance participation as a precondition for reward withdrawal: a staking key holder must be actively delegating their vote to a live DRep. An expired DRep contributes zero voting power to governance (excluded in `dRepAcceptedRatio`), so a staking key delegated to an expired DRep is effectively not participating in governance. Allowing such a key to withdraw rewards violates the design parameter.

This maps to the allowed impact: **Medium — attacker-controlled transactions modify withdrawals outside design parameters.** Any staking key holder can craft a withdrawal transaction after their delegated DRep expires, draining their accumulated reward balance without satisfying the active-governance-participation requirement. The formal specification (issue #635) explicitly identifies this as incorrect behavior.

---

### Likelihood Explanation

The entry path requires no privilege: any staking key holder whose delegated DRep has expired (which happens automatically after `ppDRepActivity` epochs of DRep inactivity) can submit a standard withdrawal transaction. DRep expiry is a normal, predictable on-chain event. The attacker does not need to control the DRep, only to have previously delegated to one that subsequently expired. This is reachable by an unprivileged transaction sender.

---

### Recommendation

`validateWithdrawalsDelegated` should additionally verify that the DRep pointed to by `dRepDelegationAccountStateL` is not expired. This requires consulting `VState.vsDReps` and comparing `drepExpiry + vsNumDormantEpochs` against the current epoch, mirroring the logic already used in `dRepAcceptedRatio` and `vsActualDRepExpiry`. The function signature already receives `Accounts era`; it would also need access to `VState era` and the current epoch number to perform this check.

---

### Proof of Concept

The existing test at lines 148–173 of `eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/LedgerSpec.hs` already demonstrates the issue:

1. Register a staking credential and accumulate rewards.
2. Register a DRep and let it expire (`isDRepExpired drep \`shouldReturn\` True`).
3. Delegate the staking credential to the now-expired DRep.
4. Submit a withdrawal transaction — `submitTx_` succeeds (no failure expected).

The `disableInConformanceIt` test immediately following (lines 177–198) covers the case where the DRep expires *after* delegation and is disabled precisely because the implementation diverges from the formal specification on this point, confirming the root cause is the missing expiry check in `validateWithdrawalsDelegated`. [8](#0-7)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L379-380)
```haskell
          unless (hardforkConwayBootstrapPhase (pp ^. ppProtocolVersionL)) $ do
            runTest $ validateWithdrawalsDelegated accounts tx
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L473-488)
```haskell
validateWithdrawalsDelegated ::
  ( EraTx era
  , ConwayEraCertState era
  ) =>
  Accounts era -> Tx l era -> Test (ConwayLedgerPredFailure era)
validateWithdrawalsDelegated accounts tx =
  let wdrls = unWithdrawals $ tx ^. bodyTxL . withdrawalsTxBodyL
      wdrlsKeyHashes =
        [ kh | (ra, _) <- Map.toList wdrls, Just kh <- [credKeyHash $ ra ^. accountAddressCredentialL]
        ]
      isNotDRepDelegated keyHash = isNothing $ do
        accountState <- lookupAccountState (KeyHashObj keyHash) accounts
        accountState ^. dRepDelegationAccountStateL
      nonExistentDelegations =
        filter isNotDRepDelegated wdrlsKeyHashes
   in failureOnNonEmpty nonExistentDelegations ConwayWdrlNotDelegatedToDRep
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L266-267)
```haskell
            Just drepState
              | reCurrentEpoch > drepExpiry drepState -> (yes, tot) -- drep is expired, so we don't consider it
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/LedgerSpec.hs (L148-173)
```haskell
  it "Withdraw from a key delegated to an expired DRep" $ do
    modifyPParams $ \pp ->
      pp
        & ppGovActionLifetimeL .~ EpochInterval 4
        & ppDRepActivityL .~ EpochInterval 1
    kh <- freshKeyHash
    let cred = KeyHashObj kh
    ra <- registerStakeCredential cred
    submitAndExpireProposalToMakeReward cred
    balance <- getBalance cred

    (drep, _, _) <- setupSingleDRep 1_000_000

    -- expire the drep before delegation
    mkMinFeeUpdateGovAction SNothing >>= submitGovAction_
    passNEpochs 4
    isDRepExpired drep `shouldReturn` True

    _ <- delegateToDRep cred (Coin 1_000_000) (DRepCredential drep)

    submitTx_ $
      mkBasicTx $
        mkBasicTxBody
          & withdrawalsTxBodyL
            .~ Withdrawals
              [(ra, balance)]
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/LedgerSpec.hs (L175-198)
```haskell
  -- https://github.com/IntersectMBO/formal-ledger-specifications/issues/635
  -- TODO: Re-enable after issue is resolved, by removing this override
  disableInConformanceIt "Withdraw from a key delegated to a DRep that expired after delegation" $ do
    modifyPParams $ \pp ->
      pp
        & ppGovActionLifetimeL .~ EpochInterval 4
        & ppDRepActivityL .~ EpochInterval 1
    (drep, cred, _) <- setupSingleDRep 1_000_000
    ra <- getAccountAddressFor cred
    submitAndExpireProposalToMakeReward cred
    balance <- getBalance cred

    -- expire the drep after delegation
    mkMinFeeUpdateGovAction SNothing >>= submitGovAction_

    passNEpochs 4
    isDRepExpired drep `shouldReturn` True

    submitTx_ $
      mkBasicTx $
        mkBasicTxBody
          & withdrawalsTxBodyL
            .~ Withdrawals
              [(ra, balance)]
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/State/Account.hs (L301-304)
```haskell
lookupDRepDelegation :: ConwayEraAccounts era => Credential Staking -> Accounts era -> Maybe DRep
lookupDRepDelegation cred accounts = do
  accountState <- lookupAccountState cred accounts
  accountState ^. dRepDelegationAccountStateL
```

**File:** libs/cardano-ledger-core/src/Cardano/Ledger/DRep.hs (L166-171)
```haskell
data DRepState = DRepState
  { drepExpiry :: !EpochNo
  , drepAnchor :: !(StrictMaybe Anchor)
  , drepDeposit :: !(CompactForm Coin)
  , drepDelegs :: !(Set (Credential Staking))
  }
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/State/VState.hs (L154-156)
```haskell
vsActualDRepExpiry :: Credential DRepRole -> VState era -> Maybe EpochNo
vsActualDRepExpiry cred vs =
  binOpEpochNo (+) (vsNumDormantEpochs vs) . drepExpiry <$> Map.lookup cred (vsDReps vs)
```
