### Title
Expired DRep Self-Revival via Vote Submission Bypasses Activity-Based Expiry Mechanism - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs)

---

### Summary

The `updateVotingDRepExpiries` function in the Conway `CERTS` rule unconditionally resets the expiry of any registered DRep that submits a vote, without first checking whether that DRep is already expired. Simultaneously, `checkVotersAreValid` in the `GOV` rule does not verify DRep expiry status before accepting a vote. An expired-but-still-registered DRep can therefore submit a vote, have its expiry silently reset to a future epoch, and have that vote counted in governance ratification — bypassing the activity-based expiry mechanism entirely.

---

### Finding Description

**Root cause — `updateVotingDRepExpiries` (no expiry guard):** [1](#0-0) 

```haskell
updateVotingDRepExpiries tx currentEpoch drepActivity certState =
  let numDormantEpochs = certState ^. certVStateL . vsNumDormantEpochsL
      updateVSDReps vsDReps =
        Map.foldlWithKey'
          ( \dreps voter _ -> case voter of
              DRepVoter cred ->
                Map.adjust
                  (drepExpiryL .~ computeDRepExpiry drepActivity currentEpoch numDormantEpochs)
                  cred
                  dreps
              _ -> dreps
          )
          vsDReps
          (unVotingProcedures $ tx ^. bodyTxL . votingProceduresTxBodyL)
   in certState & certVStateL . vsDRepsL %~ updateVSDReps
```

`Map.adjust` updates any registered DRep that appears in the transaction's voting procedures. There is **no guard** checking whether `currentEpoch > drepExpiry drepState` before overwriting the expiry field.

**Contrast with `updateDormantDRepExpiry` — which explicitly skips expired DReps:** [2](#0-1) 

```haskell
    updateExpiry =
      drepExpiryL
        %~ \currentExpiry ->
          let actualExpiry = binOpEpochNo (+) numDormantEpochs currentExpiry
           in if actualExpiry < currentEpoch
                then currentExpiry   -- expired DReps are NOT updated
                else actualExpiry
```

The dormant-epoch path explicitly preserves the stale expiry for already-expired DReps. The voting path has no equivalent guard, creating an asymmetry.

**Root cause — `checkVotersAreValid` does not check DRep expiry:** [3](#0-2) 

```haskell
checkVotersAreValid currentEpoch committeeState votes =
  checkDisallowedVotes votes DisallowedVoters $ \gas ->
    \case
      CommitteeVoter {} -> isCommitteeVotingAllowed currentEpoch committeeState (gasAction gas)
      DRepVoter {}      -> isDRepVotingAllowed (gasAction gas)   -- no expiry check
      StakePoolVoter {} -> isStakePoolVotingAllowed (gasAction gas)
```

For `CommitteeVoter`, `isCommitteeVotingAllowed` receives `currentEpoch` and `committeeState` and internally filters out expired members via `activeCommitteeSize`: [4](#0-3) 

For `DRepVoter`, only the action type is checked — expiry is never consulted at vote-submission time.

**Ratification confirms expired DReps are excluded — but only if their expiry was not reset:** [5](#0-4) 

```haskell
Just drepState
  | reCurrentEpoch > drepExpiry drepState -> (yes, tot) -- drep is expired, skip
  | otherwise -> ...
```

Because `updateVotingDRepExpiries` runs in `CERTS` **before** `GOV` processes the vote (confirmed by the comment at line 252–256 of Certs.hs), the DRep's expiry is already reset to `currentEpoch + drepActivity` by the time ratification evaluates it. The ratification guard therefore sees a future expiry and counts the vote. [6](#0-5) 

---

### Impact Explanation

An expired DRep — one that has been inactive for more than `ppDRepActivity` epochs — retains its registration and its delegated stake. By submitting a single vote transaction, it silently reactivates itself and causes its full delegated-stake weight to count toward (or against) ratification of any governance action: `ParameterChange`, `HardForkInitiation`, `TreasuryWithdrawals`, `NewConstitution`, or `UpdateCommittee`. If the expired DRep's stake is sufficient to tip the `dRepAcceptedRatio` threshold, a governance action that would otherwise fail ratification can be enacted — or one that would otherwise pass can be blocked. This maps to the **Critical** allowed impact: *Unauthorized governance, treasury, protocol-parameter, committee, constitution, or hard-fork action is enacted.*

---

### Likelihood Explanation

A DRep that registered with significant delegated stake, became inactive, and allowed its expiry to lapse is a realistic on-chain state. The DRep key-holder retains the signing key and can craft a vote transaction at any time. No privileged access, consensus majority, or external dependency is required — only a valid transaction signed by the DRep credential. The attack is fully self-contained and repeatable each epoch.

---

### Recommendation

Add an expiry guard to `updateVotingDRepExpiries`, mirroring the guard already present in `updateDormantDRepExpiry`:

```haskell
DRepVoter cred ->
  Map.adjust
    ( \drepState ->
        if drepExpiry drepState < currentEpoch
          then drepState   -- do not revive expired DReps
          else drepState & drepExpiryL .~ computeDRepExpiry drepActivity currentEpoch numDormantEpochs
    )
    cred
    dreps
```

Additionally, `checkVotersAreValid` should reject votes from expired DReps with a dedicated predicate failure (analogous to `VotingOnExpiredGovAction`), so the transaction fails cleanly rather than silently discarding the expiry reset.

---

### Proof of Concept

1. DRep `D` registers at epoch 0; `ppDRepActivity = 10`; expiry set to epoch 10.
2. `D` casts no votes and submits no update certificates. Epochs 11–20 pass; `D` is expired (`drepExpiry = 10 < currentEpoch = 20`).
3. A governance action `G` (e.g., `TreasuryWithdrawals`) is submitted in epoch 20. Without `D`'s stake, `dRepAcceptedRatio` is below threshold.
4. `D` submits a transaction in epoch 20 containing `VotingProcedures { DRepVoter D → VoteYes on G }`.
5. **CERTS rule**: `updateVotingDRepExpiries` calls `Map.adjust (drepExpiryL .~ computeDRepExpiry 10 20 0) D vsDReps`, setting `D`'s expiry to epoch 30. No expiry check is performed.
6. **GOV rule**: `checkVotersAreValid` calls `isDRepVotingAllowed (TreasuryWithdrawals ...)` → `True`. Vote is stored in `gasDRepVotes`.
7. **Epoch 20 boundary — RATIFY**: `reCurrentEpoch = 19`, `drepExpiry D = 30`. Since `19 ≤ 30`, `D` is treated as active; its full delegated stake is added to `yesStake`. `dRepAcceptedRatio` now exceeds threshold; `G` is ratified and enacted.

Without step 5's missing expiry guard, `D`'s expiry would remain 10, `reCurrentEpoch = 19 > 10`, and `D`'s stake would be excluded — `G` would not be ratified.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L248-267)
```haskell
-- | If there is a new governance proposal to vote on in this transaction,
-- AND the number of dormant-epochs recorded is greater than zero, we bump
-- the expiry for all DReps by the number of dormant epochs, and reset the
-- counter to zero.
--
-- It does not matter that this is called _before_ the GOV rule in LEDGER, even
-- though we cannot validate any governance proposal here, since the entire
-- transaction will fail if the proposal is not accepted in GOV, and so will
-- this expiry bump done here.
updateDormantDRepExpiries ::
  ( EraTx era
  , ConwayEraTxBody era
  , ConwayEraCertState era
  ) =>
  Tx l era -> EpochNo -> CertState era -> CertState era
updateDormantDRepExpiries tx currentEpoch =
  let hasProposals = not . OSet.null $ tx ^. bodyTxL . proposalProceduresTxBodyL
   in if hasProposals
        then certVStateL %~ updateDormantDRepExpiry currentEpoch
        else id
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L272-292)
```haskell
updateVotingDRepExpiries ::
  ( EraTx era
  , ConwayEraTxBody era
  , ConwayEraCertState era
  ) =>
  Tx l era -> EpochNo -> EpochInterval -> CertState era -> CertState era
updateVotingDRepExpiries tx currentEpoch drepActivity certState =
  let numDormantEpochs = certState ^. certVStateL . vsNumDormantEpochsL
      updateVSDReps vsDReps =
        Map.foldlWithKey'
          ( \dreps voter _ -> case voter of
              DRepVoter cred ->
                Map.adjust
                  (drepExpiryL .~ computeDRepExpiry drepActivity currentEpoch numDormantEpochs)
                  cred
                  dreps
              _ -> dreps
          )
          vsDReps
          (unVotingProcedures $ tx ^. bodyTxL . votingProceduresTxBodyL)
   in certState & certVStateL . vsDRepsL %~ updateVSDReps
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L322-328)
```haskell
    updateExpiry =
      drepExpiryL
        %~ \currentExpiry ->
          let actualExpiry = binOpEpochNo (+) numDormantEpochs currentExpiry
           in if actualExpiry < currentEpoch
                then currentExpiry
                else actualExpiry
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L364-376)
```haskell
checkVotersAreValid ::
  forall era.
  ConwayEraPParams era =>
  EpochNo ->
  CommitteeState era ->
  [(Voter, GovActionState era)] ->
  Test (ConwayGovPredFailure era)
checkVotersAreValid currentEpoch committeeState votes =
  checkDisallowedVotes votes DisallowedVoters $ \gas ->
    \case
      CommitteeVoter {} -> isCommitteeVotingAllowed currentEpoch committeeState (gasAction gas)
      DRepVoter {} -> isDRepVotingAllowed (gasAction gas)
      StakePoolVoter {} -> isStakePoolVotingAllowed (gasAction gas)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Internal.hs (L472-479)
```haskell
    isActive coldKey validUntil =
      case Map.lookup coldKey hotKeys of
        Just (CommitteeMemberResigned _) -> False
        Just _ -> currentEpoch <= validUntil
        Nothing -> False
    activeCommitteeSize =
      fromIntegral . Map.size . Map.filterWithKey isActive $
        foldMap' committeeMembers committee
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L264-268)
```haskell
          case Map.lookup cred reDRepState of
            Nothing -> (yes, tot) -- drep is not registered, so we don't consider it
            Just drepState
              | reCurrentEpoch > drepExpiry drepState -> (yes, tot) -- drep is expired, so we don't consider it
              | otherwise ->
```
