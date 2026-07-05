### Title
Stale Absolute Expiry Epoch in `GovActionState.gasExpiresAfter` Not Retroactively Updated When `govActionLifetime` Parameter Changes - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

---

### Summary

In the Conway era, every governance proposal stores an absolute expiry epoch (`gasExpiresAfter`) computed once at submission time by adding the then-current `govActionLifetime` protocol parameter to the current epoch. When `govActionLifetime` is later reduced via a ratified `ParameterChange` governance action, all in-flight proposals retain their original, larger `gasExpiresAfter` values. The `RATIFY` rule compares only the stored absolute epoch against the current epoch, so existing proposals survive longer than the new parameter dictates and remain eligible for ratification and enactment during the unintended window.

---

### Finding Description

**Root cause — absolute deadline stored at submission time:**

`GovActionState` stores `gasExpiresAfter :: !EpochNo` as a plain absolute epoch number:

```haskell
data GovActionState era = GovActionState
  { gasId               :: !GovActionId
  , ...
  , gasProposedIn       :: !EpochNo   -- submission epoch (already stored)
  , gasExpiresAfter     :: !EpochNo   -- absolute deadline, frozen at submission
  }
``` [1](#0-0) 

`mkGovActionState` computes this value once, using `ppGovActionLifetimeL` at the moment the proposal transaction is processed:

```haskell
mkGovActionState actionId proposal expiryInterval curEpoch =
  GovActionState { ...
    , gasProposedIn   = curEpoch
    , gasExpiresAfter = addEpochInterval curEpoch expiryInterval
    }
``` [2](#0-1) 

The caller reads the parameter at submission time and never revisits it:

```haskell
let expiry      = pp ^. ppGovActionLifetimeL
    actionState = mkGovActionState newGaid proposal expiry currentEpoch
``` [3](#0-2) 

**Expiry check in `RATIFY` uses only the frozen field:**

```haskell
if gasExpiresAfter < reCurrentEpoch
  then pure $ st' & rsExpiredL %~ Set.insert gasId
  else pure st'
``` [4](#0-3) 

There is no code path that iterates over existing proposals and adjusts `gasExpiresAfter` when `govActionLifetime` changes. The `gasProposedIn` field — the exact analog of the "cooldown start time" recommended in the external report — is already persisted but is never used to recompute the deadline.

**`govActionLifetime` is a mutable, governance-updatable parameter:**

`cppGovActionLifetime` is tagged with `PParamUpdate 29 ppuGovActionLifetimeL`, making it changeable by any ratified `ParameterChange` action: [5](#0-4) [6](#0-5) 

The `ppuWellFormed` guard prevents setting it to `EpochInterval 0`, so the minimum is 1 epoch, but any reduction from a larger value triggers the stale-deadline condition: [7](#0-6) 

---

### Impact Explanation

**Allowed impact matched:** *Medium — attacker-controlled proposals exceed intended validation limits or modify treasury withdrawals/governance actions outside design parameters.*

When `govActionLifetime` is reduced (e.g., from 6 epochs to 1 epoch), every proposal already in the queue retains `gasExpiresAfter = submissionEpoch + 6`. New proposals expire after 1 epoch; existing ones remain alive for up to 5 additional epochs beyond what the updated parameter permits. During this unintended window, any of the following proposal types can still accumulate votes and be ratified and enacted:

- `TreasuryWithdrawals` — ADA drained from the treasury outside the intended governance timeline
- `HardForkInitiation` — a hard fork enacted after the governance system intended to kill the proposal
- `ParameterChange` — protocol parameters modified outside the intended window
- `UpdateCommittee` / `NewConstitution` — committee or constitution changed after intended expiry

The governance system's ability to retroactively tighten proposal lifetimes — a natural emergency lever — is silently ineffective for all in-flight proposals.

---

### Likelihood Explanation

**Moderate.** The trigger requires a ratified `ParameterChange` that reduces `govActionLifetime`, which itself requires governance majority. However, this is a routine governance operation (e.g., shortening the voting window for efficiency or security reasons). Any proposal submitted before the reduction automatically benefits from the stale deadline without any further action by the original proposer. The proposer still needs enough votes to ratify their proposal in the extended window, but the governance system's intent to shorten that window is silently bypassed.

---

### Recommendation

The `gasProposedIn` field is already stored in every `GovActionState`. The fix mirrors the external report's recommendation exactly: replace the stored absolute deadline with a dynamic computation in `RATIFY`:

```haskell
-- Instead of:
if gasExpiresAfter < reCurrentEpoch

-- Compute dynamically using the current parameter and the stored start epoch:
let currentLifetime = ensCurPParams ^. ppGovActionLifetimeL
    dynamicExpiry   = addEpochInterval gasProposedIn currentLifetime
if dynamicExpiry < reCurrentEpoch
```

This makes every proposal's effective expiry always reflect the current `govActionLifetime`, regardless of when the proposal was submitted. The `gasExpiresAfter` field can then be removed or retained only for informational/query purposes (recomputed on read).

---

### Proof of Concept

```
Epoch 0:  govActionLifetime = 6
          Alice submits TreasuryWithdrawals proposal P
          → gasExpiresAfter = 0 + 6 = epoch 6

Epoch 1:  Governance ratifies ParameterChange: govActionLifetime = 1
          New proposals now expire after 1 epoch.
          P.gasExpiresAfter is still epoch 6 (not updated).

Epoch 2:  Under the new parameter, P should have expired at epoch 0+1 = epoch 1.
          But RATIFY checks: gasExpiresAfter (6) < reCurrentEpoch (2) → False
          P is still alive and eligible for ratification.

Epochs 2–5: Alice accumulates DRep/SPO/committee votes on P.

Epoch 5:  P reaches ratification threshold → enacted.
          TreasuryWithdrawals disbursed despite governance having reduced
          the lifetime specifically to prevent long-lived proposals.
```

The `gasProposedIn` field already present in `GovActionState` (line 225) and the `ensCurPParams` already available in `RatifyState` (via `rsEnactState`) provide all the data needed for the dynamic check without any new state. [8](#0-7) [9](#0-8)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Procedures.hs (L219-227)
```haskell
data GovActionState era = GovActionState
  { gasId :: !GovActionId
  , gasCommitteeVotes :: !(Map (Credential HotCommitteeRole) Vote)
  , gasDRepVotes :: !(Map (Credential DRepRole) Vote)
  , gasStakePoolVotes :: !(Map (KeyHash StakePool) Vote)
  , gasProposalProcedure :: !(ProposalProcedure era)
  , gasProposedIn :: !EpochNo
  , gasExpiresAfter :: !EpochNo
  }
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L409-418)
```haskell
mkGovActionState actionId proposal expiryInterval curEpoch =
  GovActionState
    { gasId = actionId
    , gasCommitteeVotes = mempty
    , gasDRepVotes = mempty
    , gasStakePoolVotes = mempty
    , gasProposalProcedure = proposal
    , gasProposedIn = curEpoch
    , gasExpiresAfter = addEpochInterval curEpoch expiryInterval
    }
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L562-563)
```haskell
        let expiry = pp ^. ppGovActionLifetimeL
            actionState = mkGovActionState newGaid proposal expiry currentEpoch
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L320-333)
```haskell
    ( env@RatifyEnv {reCurrentEpoch}
      , st@( RatifyState
               rsEnactState@EnactState
                 { ensCurPParams
                 , ensTreasury
                 , ensPrevGovActionIds
                 }
               _rsEnacted
               _rsExpired
               rsDelayed
             )
      , RatifySignal rsig
      ) <-
    judgmentContext
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L357-359)
```haskell
          if gasExpiresAfter < reCurrentEpoch
            then pure $ st' & rsExpiredL %~ Set.insert gasId
            else pure st'
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L698-699)
```haskell
  , cppGovActionLifetime :: !(THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f EpochInterval)
  -- ^ Gov action lifetime in number of Epochs
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L943-943)
```haskell
      , isValid (/= EpochInterval 0) ppuGovActionLifetimeL
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L1301-1308)
```haskell
ppGovActionLifetime :: ConwayEraPParams era => PParam era
ppGovActionLifetime =
  PParam
    { ppName = "govActionLifetime"
    , ppLens = ppGovActionLifetimeL
    , ppEraDecoder = Nothing
    , ppUpdate = Just $ PParamUpdate 29 ppuGovActionLifetimeL
    }
```
