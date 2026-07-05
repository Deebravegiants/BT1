### Title
Implicit DRep Expiry State Corruption via Sequential `updateDormantDRepExpiries` + `updateVotingDRepExpiries` in Same Transaction - (File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs)

---

### Summary

The Conway era manages DRep expiry through two implicit state-mutation functions applied sequentially during transaction processing. When a single transaction contains **both** governance proposals and DRep votes, the sequential application of `updateDormantDRepExpiries` followed by `updateVotingDRepExpiries` produces an incorrect DRep expiry. The first function resets `numDormantEpochs` to zero before the second function reads it, causing voting DReps to receive a longer expiry than the protocol intends. An expired DRep can exploit this to silently resurrect their active status without re-registering.

---

### Finding Description

**Root cause — split-state representation and implicit mutation order**

DRep expiry is stored as two separate fields:
- `drepExpiry` in `DRepState` (the stored value)
- `vsNumDormantEpochs` in `VState` (an additive offset)

The "actual" expiry is `drepExpiry + numDormantEpochs`, computed on the fly by `vsActualDRepExpiry`. [1](#0-0) 

Two functions mutate this split state during transaction processing:

**`updateDormantDRepExpiries`** — triggered when the transaction contains proposals. It bumps every DRep's stored `drepExpiry` by `numDormantEpochs` (skipping DReps whose actual expiry is already past `currentEpoch`), then **resets `numDormantEpochs` to 0**. [2](#0-1) [3](#0-2) 

**`updateVotingDRepExpiries`** — triggered when the transaction contains DRep votes. It sets each voting DRep's expiry to `computeDRepExpiry drepActivity currentEpoch numDormantEpochs`, where `numDormantEpochs` is read **from the current `certState`**. [4](#0-3) 

Both are applied in sequence in both the pre-v11 path (`conwayCertsTransition`) and the post-v11 path (`conwayLedgerTransitionTRC`):

```haskell
certState
  & updateDormantDRepExpiries tx currentEpoch      -- resets numDormantEpochs → 0
  & updateVotingDRepExpiries  tx currentEpoch ...  -- reads numDormantEpochs = 0 (already reset)
``` [5](#0-4) [6](#0-5) 

The inline comment on `updateVotingDRepExpiries` asserts the two functions are "mutual-exclusion" because "if there are no proposals to vote on, there will be no votes either." This reasoning applies to the **global** state (no active proposals ⇒ no votes), but a **single transaction** can legally contain both new proposals and votes on existing proposals. The mutual-exclusion assumption is therefore false at the transaction level.

**Consequence 1 — inflated expiry for active DReps**

When `numDormantEpochs = N > 0` and a transaction has both proposals and votes:

| Step | `numDormantEpochs` | Voting DRep expiry |
|------|--------------------|--------------------|
| Before | N | `E` (stored) |
| After `updateDormantDRepExpiries` | 0 | `E + N` (bumped) |
| After `updateVotingDRepExpiries` | 0 (reads reset value) | `currentEpoch + drepActivity - 0` |

The intended result of `updateVotingDRepExpiries` is `currentEpoch + drepActivity - N`. The actual result is `currentEpoch + drepActivity`. The DRep receives `N` extra epochs of activity beyond the protocol's design.

**Consequence 2 — expired DRep resurrection**

`updateDormantDRepExpiry` explicitly skips DReps whose actual expiry is already past `currentEpoch`:

```haskell
if actualExpiry < currentEpoch
  then currentExpiry   -- expired DRep: do NOT update
  else actualExpiry
``` [7](#0-6) 

However, `updateVotingDRepExpiries` has **no such guard**. It unconditionally overwrites the expiry of any DRep that appears in the transaction's voting procedures. After `updateDormantDRepExpiries` resets `numDormantEpochs` to 0, `updateVotingDRepExpiries` sets the expired DRep's expiry to `currentEpoch + drepActivity`, fully resurrecting them.

The GOV rule does not check DRep expiry when recording votes — it only checks voter type eligibility (`isDRepVotingAllowed`) and voter existence (registration). An expired but still-registered DRep passes both checks. [8](#0-7) 

At ratification time, `dRepAcceptedRatio` uses the stored `drepExpiry` from `reDRepState`. Because the resurrection updated the stored field, the DRep is now treated as active and their vote is counted.

<cite repo="Tylerpinwa/cardano-ledger--016" path="eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs" start="297"

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/State/VState.hs (L154-156)
```haskell
vsActualDRepExpiry :: Credential DRepRole -> VState era -> Maybe EpochNo
vsActualDRepExpiry cred vs =
  binOpEpochNo (+) (vsNumDormantEpochs vs) . drepExpiry <$> Map.lookup cred (vsDReps vs)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L237-241)
```haskell
          pure $
            certState
              & updateDormantDRepExpiries tx currentEpoch
              & updateVotingDRepExpiries tx currentEpoch (pp ^. ppDRepActivityL)
              & certDStateL . accountsL %~ drainAccounts withdrawals
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L257-267)
```haskell
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs (L308-328)
```haskell
updateDormantDRepExpiry ::
  -- | Current Epoch
  EpochNo ->
  VState era ->
  VState era
updateDormantDRepExpiry currentEpoch vState =
  if numDormantEpochs == EpochNo 0
    then vState
    else
      vState
        & vsNumDormantEpochsL .~ EpochNo 0
        & vsDRepsL %~ Map.map updateExpiry
  where
    numDormantEpochs = vState ^. vsNumDormantEpochsL
    updateExpiry =
      drepExpiryL
        %~ \currentExpiry ->
          let actualExpiry = binOpEpochNo (+) numDormantEpochs currentExpiry
           in if actualExpiry < currentEpoch
                then currentExpiry
                else actualExpiry
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L387-391)
```haskell
                pure $
                  certState
                    & updateDormantDRepExpiries tx curEpochNo
                    & updateVotingDRepExpiries tx curEpochNo (pp ^. ppDRepActivityL)
                    & certDStateL . accountsL %~ drainAccounts withdrawals
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
