### Title
DRep Vote Cleanup Incorrectly Removes Votes for Re-Registered DReps in the Same Transaction - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs)

---

### Summary

The `cleanupProposalVotes` logic in the Conway `GOV` rule removes existing DRep votes from all governance action proposals by scanning the raw certificate list (`gsCertificates`) for `UnRegDRepTxCert` entries. It does not cross-check whether the same credential was re-registered later in the same transaction. Because the CERTS rule processes certificates sequentially before GOV runs, a DRep that unregisters and immediately re-registers in one transaction is fully present in `knownDReps` (the final cert state) yet still appears in `unregisteredDReps` (the raw cert scan). The cleanup therefore incorrectly erases that DRep's accumulated votes — including any new vote cast in the same transaction — even though the DRep is still a valid, registered voter at the end of the transaction.

---

### Finding Description

In `conwayGovTransition` the voter-existence check and the vote-cleanup check use two different sources of truth:

**Voter existence check** (uses final cert state — correct):
```haskell
knownDReps = vsDReps certVState          -- post-CERTS final state
internVoter = \case
  DRepVoter cred -> DRepVoter <$> internMap cred knownDReps
``` [1](#0-0) 

**Vote cleanup** (uses raw certificate list — stale):
```haskell
unregisteredDReps =
  let collectRemovals drepCreds = \case
        UnRegDRepTxCert drepCred _ -> Set.insert drepCred drepCreds
        _ -> drepCreds
   in F.foldl' collectRemovals mempty gsCertificates   -- raw tx certs
cleanupProposalVotes
  | Set.null unregisteredDReps = id
  | otherwise =
      let cleanupVoters gas =
            gas & gasDRepVotesL %~ (`Map.withoutKeys` unregisteredDReps)
       in mapProposals cleanupVoters
``` [2](#0-1) 

The CERTS rule processes certificates sequentially. When a transaction contains `[UnRegDRepTxCert drepCred, ConwayRegDRep drepCred]`, the GOVCERT handler first removes the DRep from `vsDReps`, then the subsequent `ConwayRegDRep` check (`Map.notMember cred vsDReps`) passes and re-inserts it: [3](#0-2) 

After CERTS completes, `certState` passed to GOV contains the re-registered DRep in `vsDReps`. The voter-existence check therefore accepts any vote submitted by this DRep in the same transaction. However, `gsCertificates` still contains the raw `UnRegDRepTxCert`, so `unregisteredDReps` includes the credential. The cleanup then removes:

1. All previously accumulated votes by this DRep on every live governance action proposal.
2. Any new vote the DRep submitted in the same transaction (because `cleanupProposalVotes` is applied *after* `addVoterVote`). [4](#0-3) 

The transaction succeeds with no predicate failure, but the DRep's votes are silently discarded.

---

### Impact Explanation

**Allowed impact matched**: *Medium — attacker-controlled certificates modify votes outside design parameters.*

A DRep controlling a credential can:

- **Erase accumulated YES/NO votes** on any live governance action (ParameterChange, TreasuryWithdrawals, HardForkInitiation, UpdateCommittee, NewConstitution) without any on-chain indication of wrongdoing.
- **Silently void a new vote** cast in the same transaction, causing the DRep's intent to be ignored even though the transaction was accepted.
- **Shift ratification outcomes**: removing a YES vote reduces both the numerator and the effective denominator of the DRep acceptance ratio, potentially preventing a governance action from reaching its threshold — or, conversely, removing a NO vote could allow an action to pass that otherwise would not.

If the deposit amount is unchanged between unregistration and re-registration, the net ADA cost to the attacker is zero (deposit refunded then re-paid). The DRep's delegations are cleared on unregistration, but the vote-erasure effect is independent of that.

---

### Likelihood Explanation

The attack is fully self-contained in a single transaction authored by the DRep key-holder. No privileged access, governance majority, or external dependency is required. The only prerequisite is that the attacker controls a registered DRep credential and has previously voted on at least one live governance action. The financial barrier is zero when the `ppDRepDeposit` parameter is unchanged. The scenario is reachable on mainnet by any registered DRep.

---

### Recommendation

Restrict `unregisteredDReps` to credentials that are genuinely absent from the final cert state:

```haskell
unregisteredDReps =
  let collected =
        F.foldl'
          (\s -> \case UnRegDRepTxCert c _ -> Set.insert c s; _ -> s)
          Set.empty
          gsCertificates
  in collected `Set.difference` Map.keysSet knownDReps
```

This mirrors the fix suggested in the referenced report: compare the specific entity instance (final registration state) rather than relying solely on a secondary scan of the raw certificate list.

---

### Proof of Concept

1. DRep Alice registers (`ConwayRegDRep aliceCred`) and votes YES on governance action `G` in earlier transactions.
2. Alice constructs a transaction containing:
   - `UnRegDRepTxCert aliceCred refund`
   - `ConwayRegDRep aliceCred deposit`
   - (optionally) a new vote on `G`
3. CERTS processes the certificates sequentially: Alice is removed from `vsDReps`, then re-inserted. Final `certState` has Alice in `vsDReps`.
4. GOV runs: `knownDReps` contains `aliceCred` → voter-existence check passes; any new vote is accepted into `knownVotesWithCast`.
5. `unregisteredDReps` is built from `gsCertificates` → `aliceCred` is included.
6. `cleanupProposalVotes` removes Alice's YES vote on `G` (and any new vote just cast) via `gasDRepVotesL %~ Map.withoutKeys unregisteredDReps`.
7. Transaction is accepted. Alice's vote on `G` is gone. If Alice's YES was the marginal vote needed for ratification, the governance action now fails to pass.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L472-474)
```haskell
      knownDReps = vsDReps certVState
      knownStakePools = psStakePools certPState
      knownCommitteeMembers = authorizedHotCommitteeCredentials committeeState
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L610-625)
```haskell
  let
    !updatedProposalStates =
      let addVoterVote ps (voter, vote, gas) = proposalsAddVote voter vote (gasId gas) ps
       in cleanupProposalVotes $ F.foldl' addVoterVote proposals knownVotesWithCast
    unregisteredDReps =
      let collectRemovals drepCreds = \case
            UnRegDRepTxCert drepCred _ -> Set.insert drepCred drepCreds
            _ -> drepCreds
       in F.foldl' collectRemovals mempty gsCertificates
    cleanupProposalVotes
      -- optimization: avoid iterating over proposals when there is nothing to cleanup
      | Set.null unregisteredDReps = id
      | otherwise =
          let cleanupVoters gas =
                gas & gasDRepVotesL %~ (`Map.withoutKeys` unregisteredDReps)
           in mapProposals cleanupVoters
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs (L210-233)
```haskell
    ConwayRegDRep cred deposit mAnchor -> do
      Map.notMember cred (certState ^. certVStateL . vsDRepsL)
        ?! (injectFailure . ConwayDRepAlreadyRegistered) cred
      deposit
        == ppDRepDeposit
          ?! (injectFailure . ConwayDRepIncorrectDeposit)
            Mismatch
              { mismatchSupplied = deposit
              , mismatchExpected = ppDRepDeposit
              }
      let drepState =
            DRepState
              { drepExpiry =
                  computeDRepExpiryVersioned
                    cgcePParams
                    cgceCurrentEpoch
                    (certState ^. certVStateL . vsNumDormantEpochsL)
              , drepAnchor = mAnchor
              , drepDeposit = ppDRepDepositCompact
              , drepDelegs = mempty
              }
      pure $
        certState
          & certVStateL . vsDRepsL %~ Map.insert cred drepState
```
