### Title
DRep Unregistration Temporarily Freezes Reward Withdrawals for All Delegators - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs)

### Summary
In Conway era (post-bootstrap, protocol version > 9), any registered DRep can unilaterally unregister themselves via a `ConwayUnRegDRep` certificate. This clears the DRep delegation field for every staking credential that had delegated to them. Because `validateWithdrawalsDelegated` in the LEDGER rule blocks reward withdrawals for any key-hash staking credential that lacks an active DRep delegation, all affected delegators are unable to withdraw their accumulated rewards until they submit a new delegation transaction.

### Finding Description

**Root cause — `ConwayUnRegDRep` clears delegators' DRep field**

In `GovCert.hs`, processing a `ConwayUnRegDRep` certificate iterates over every staking credential that had delegated to the departing DRep and sets their `dRepDelegationAccountStateL` to `Nothing`:

```haskell
clearDRepDelegations delegs accountsMap =
  foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs
pure $
  case mDRepState of
    Nothing -> certState'
    Just dRepState ->
      certState'
        & certDStateL . accountsL . accountsMapL
          %~ clearDRepDelegations (drepDelegs dRepState)
``` [1](#0-0) 

**Root cause — `validateWithdrawalsDelegated` blocks withdrawals when DRep field is `Nothing`**

In `Ledger.hs`, for every key-hash staking credential in a transaction's withdrawal map, the LEDGER rule checks that `dRepDelegationAccountStateL` is not `Nothing`. If it is `Nothing`, the transaction is rejected with `ConwayWdrlNotDelegatedToDRep`:

```haskell
isNotDRepDelegated keyHash = isNothing $ do
  accountState <- lookupAccountState (KeyHashObj keyHash) accounts
  accountState ^. dRepDelegationAccountStateL
nonExistentDelegations =
  filter isNotDRepDelegated wdrlsKeyHashes
in failureOnNonEmpty nonExistentDelegations ConwayWdrlNotDelegatedToDRep
``` [2](#0-1) 

This check is applied unconditionally (outside the bootstrap phase) before any certificates in the transaction are processed: [3](#0-2) 

**Attacker-controlled entry path**

1. Victim registers a staking credential and delegates to DRep `D` (legitimate user action).
2. Victim accumulates staking rewards.
3. Attacker (who controls DRep `D`) submits a transaction containing `ConwayUnRegDRep D refund`. This is a permissionless certificate — any DRep may unregister themselves at any time.
4. `clearDRepDelegations` sets `dRepDelegationAccountStateL = Nothing` for every delegator of `D`, including the victim.
5. Victim submits a withdrawal transaction. `validateWithdrawalsDelegated` finds the victim's DRep field is `Nothing` and rejects the transaction with `ConwayWdrlNotDelegatedToDRep`.
6. Victim's rewards are frozen until they submit a separate `DelegVote` or `RegDepositDelegTxCert` transaction to re-establish a DRep delegation.

This behavior is confirmed by the existing test: [4](#0-3) 

Note: script-hash staking credentials are **exempt** from this check because `credKeyHash` returns `Nothing` for them — only key-hash credentials are affected. [5](#0-4) 

### Impact Explanation

Any DRep can freeze reward withdrawals for an arbitrary number of staking credentials by unregistering. The victim cannot withdraw accumulated rewards until they submit a new delegation transaction. This is a temporary but attacker-controlled freeze of reward withdrawals triggered by a single, permissionless certificate. It maps to:

**Medium. Attacker-controlled certificates modify withdrawals outside design parameters** — a DRep's unregistration certificate unilaterally removes the withdrawal capability of all their delegators, which is an externally imposed restriction on a user's own funds that the user cannot prevent.

### Likelihood Explanation

Moderate. Any registered DRep can execute this attack against all their delegators at any time. A malicious or compromised DRep with many delegators could affect a large number of users simultaneously. The attacker does pay back their own DRep deposit on unregistration, so there is a cost, but no ongoing cost to sustain the freeze — the victim bears the burden of re-delegating.

### Recommendation

The `validateWithdrawalsDelegated` check should be relaxed so that a staking credential whose DRep delegation was cleared by a third-party unregistration event is not blocked from withdrawing its own rewards. One approach: allow withdrawals when `dRepDelegationAccountStateL` is `Nothing` (i.e., treat undelegated credentials the same as credentials delegated to a predefined DRep such as `DRepAlwaysAbstain` for the purpose of withdrawal eligibility). Alternatively, the DRep unregistration flow could preserve delegators' withdrawal rights by not clearing their DRep field until they actively re-delegate, or by allowing a grace-period withdrawal path.

### Proof of Concept

The existing test at `eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/LedgerSpec.hs` lines 104–123 directly demonstrates the issue:

```
it "Withdraw from a key delegated to an unregistered DRep"
  1. Register staking credential `cred` (key hash `kh`)
  2. Accumulate rewards via submitAndExpireProposalToMakeReward
  3. Setup DRep, then call unRegisterDRep
  4. Attempt withdrawal → fails with ConwayWdrlNotDelegatedToDRep [kh]
```

The `ConwayUnRegDRep` certificate processing in `GovCert.hs` (lines 234–254) clears `dRepDelegationAccountStateL` for all delegators, and `validateWithdrawalsDelegated` in `Ledger.hs` (lines 473–488) then rejects any withdrawal from those credentials.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs (L243-254)
```haskell
      let
        certState' =
          certState & certVStateL . vsDRepsL %~ Map.delete cred
        clearDRepDelegations delegs accountsMap =
          foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs
      pure $
        case mDRepState of
          Nothing -> certState'
          Just dRepState ->
            certState'
              & certDStateL . accountsL . accountsMapL
                %~ clearDRepDelegations (drepDelegs dRepState)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L379-380)
```haskell
          unless (hardforkConwayBootstrapPhase (pp ^. ppProtocolVersionL)) $ do
            runTest $ validateWithdrawalsDelegated accounts tx
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L479-482)
```haskell
  let wdrls = unWithdrawals $ tx ^. bodyTxL . withdrawalsTxBodyL
      wdrlsKeyHashes =
        [ kh | (ra, _) <- Map.toList wdrls, Just kh <- [credKeyHash $ ra ^. accountAddressCredentialL]
        ]
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L483-488)
```haskell
      isNotDRepDelegated keyHash = isNothing $ do
        accountState <- lookupAccountState (KeyHashObj keyHash) accounts
        accountState ^. dRepDelegationAccountStateL
      nonExistentDelegations =
        filter isNotDRepDelegated wdrlsKeyHashes
   in failureOnNonEmpty nonExistentDelegations ConwayWdrlNotDelegatedToDRep
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/LedgerSpec.hs (L104-123)
```haskell
  it "Withdraw from a key delegated to an unregistered DRep" $ do
    modifyPParams $ ppGovActionLifetimeL .~ EpochInterval 2
    kh <- freshKeyHash
    let cred = KeyHashObj kh
    ra <- registerStakeCredential cred
    submitAndExpireProposalToMakeReward cred
    balance <- getBalance cred

    (drep, _, _) <- setupSingleDRep 1_000_000

    unRegisterDRep drep
    expectDRepNotRegistered drep
    let tx =
          mkBasicTx $
            mkBasicTxBody
              & withdrawalsTxBodyL
                .~ Withdrawals
                  [(ra, balance)]
    ifBootstrap (submitTx_ tx >> (getBalance cred `shouldReturn` mempty)) $ do
      submitFailingTx tx [injectFailure $ ConwayWdrlNotDelegatedToDRep [kh]]
```
