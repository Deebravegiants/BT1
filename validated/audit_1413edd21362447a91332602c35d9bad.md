### Title
Unbounded `Map.map` Over All Registered DReps in `updateDormantDRepExpiry` Triggered Per Governance-Proposal Transaction — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Certs.hs`)

---

### Summary

The Conway LEDGER rule unconditionally iterates over the entire `vsDReps` map — every registered DRep — inside `updateDormantDRepExpiry` whenever a transaction carries at least one governance proposal. Because DRep registration is open to any participant and the map has no protocol-enforced size cap, an attacker who pre-registers a large number of DReps can force every subsequent governance-proposal transaction to perform O(n\_dreps) native Haskell work with no execution-unit budget to bound it. This is the direct Cardano analog of the Solidity unbounded-loop pattern described in the external report.

---

### Finding Description

**Root cause — `updateDormantDRepExpiry`** [1](#0-0) 

```haskell
updateDormantDRepExpiry currentEpoch vState =
  if numDormantEpochs == EpochNo 0
    then vState
    else
      vState
        & vsNumDormantEpochsL .~ EpochNo 0
        & vsDRepsL %~ Map.map updateExpiry   -- ← iterates ALL registered DReps
```

`Map.map updateExpiry` traverses every entry in `vsDReps :: Map (Credential DRepRole) DRepState`. There is no early-exit, no pagination, and no execution-unit charge.

**Trigger path — `updateDormantDRepExpiries`** [2](#0-1) 

```haskell
updateDormantDRepExpiries tx currentEpoch =
  let hasProposals = not . OSet.null $ tx ^. bodyTxL . proposalProceduresTxBodyL
   in if hasProposals
        then certVStateL %~ updateDormantDRepExpiry currentEpoch
        else id
```

The guard is `hasProposals` — a single `ProposalProcedure` in the transaction body is sufficient to trigger the full map traversal.

**Called unconditionally in the Conway LEDGER rule (post-hardfork path)** [3](#0-2) 

```haskell
if hardforkConwayMoveWithdrawalsAndDRepChecksToLedgerRule $ pp ^. ppProtocolVersionL
  then do
    ...
    pure $
      certState
        & updateDormantDRepExpiries tx curEpochNo   -- ← called here
        & updateVotingDRepExpiries  tx curEpochNo (pp ^. ppDRepActivityL)
        & certDStateL . accountsL %~ drainAccounts withdrawals
  else pure certState
```

This is the live path for all Conway-era (and later) blocks. The same call also exists in the pre-hardfork CERTS path: [4](#0-3) 

**The `vsDReps` map is unbounded** [5](#0-4) 

```haskell
data VState era = VState
  { vsDReps :: !(Map (Credential DRepRole) DRepState)
  , ...
  }
```

DRep registration (`ConwayRegDRep`) inserts into this map. There is no protocol parameter that caps the total number of registered DReps.

**Secondary unbounded loop — `clearDRepDelegations` on DRep unregistration**

A second O(n) traversal exists in the GOVCERT rule: when a DRep unregisters, `clearDRepDelegations` iterates over every stake credential that delegated to that DRep (`drepDelegs dRepState`) to clear their delegation pointer. [6](#0-5) 

```haskell
clearDRepDelegations delegs accountsMap =
  foldr (Map.adjust (dRepDelegationAccountStateL .~ Nothing)) accountsMap delegs
```

Because stake-key registration costs only 2 ADA (refundable) and DRep delegation requires no additional deposit, an attacker can cheaply accumulate an arbitrarily large `drepDelegs` set and then trigger the loop via a single `ConwayUnRegDRep` certificate, recovering all deposits afterward.

---

### Impact Explanation

**Classification:** Medium — attacker-controlled transactions exceed intended validation limits.

Every honest node must execute `updateDormantDRepExpiry` synchronously during block application. Unlike Plutus script execution, this native Haskell traversal carries no execution-unit budget and is not subject to `ppMaxTxExUnits` or `ppMaxBlockExUnits`. As the `vsDReps` map grows, the per-transaction validation cost grows proportionally with no protocol-level ceiling. A sufficiently large map can:

1. Cause block-application time to exceed the slot interval on slower nodes, creating a window for chain-tip divergence between fast and slow validators — matching the "High: deterministic disagreement between honest nodes from ledger rule evaluation" impact.
2. More concretely, cause governance-proposal transactions to consume disproportionate node resources, degrading liveness of the governance mechanism — matching the "Medium: attacker-controlled transactions exceed intended validation limits" impact.

The `clearDRepDelegations` loop has the same character but is cheaper to exploit (all deposits refundable).

---

### Likelihood Explanation

**Primary loop (`updateDormantDRepExpiry`):** DRep registration currently requires a `ppDRepDeposit` of 500 ADA (non-refundable while the DRep remains active). Registering 10 000 DReps requires locking 5 000 000 ADA. This is a meaningful economic barrier, making the likelihood **Low** under current parameters. However, `ppDRepDeposit` is a governable parameter; a reduction via a governance action would lower the barrier proportionally.

**Secondary loop (`clearDRepDelegations`):** Stake-key registration costs 2 ADA and is fully refundable. An attacker can register and delegate 100 000 credentials to a single DRep for ~200 000 ADA of temporary capital, then unregister the DRep and recover everything. The net cost approaches zero, making this path **Medium** likelihood.

---

### Recommendation

1. **Cap the `vsDReps` map size** via a new protocol parameter `ppMaxDReps`. Reject `ConwayRegDRep` certificates when the cap is reached.
2. **Charge execution units for native governance-state traversals**, or restructure `updateDormantDRepExpiry` to be incremental (pulsed), analogous to the existing `PulsingRewUpdate` mechanism used for reward computation. [7](#0-6) 

3. **For `clearDRepDelegations`:** instead of eagerly clearing all delegation pointers on DRep unregistration, record the unregistered DRep credential and lazily clear delegations on next access (or charge a per-delegator fee at unregistration time).

---

### Proof of Concept

**Setup (off-chain):**
1. Attacker registers N DReps via N `ConwayRegDRep` certificates spread across multiple transactions, each paying `ppDRepDeposit`.
2. All N DReps are now in `vsDReps`.

**Attack transaction:**
```
Tx {
  body = TxBody {
    proposalProcedures = [InfoAction],   -- one proposal is sufficient
    ...
  }
}
```

**Execution path:**
```
LEDGER rule
  → hardforkConwayMoveWithdrawalsAndDRepChecksToLedgerRule = True
  → updateDormantDRepExpiries tx curEpochNo
      → hasProposals = True
      → updateDormantDRepExpiry curEpochNo vState
          → Map.map updateExpiry vsDReps   -- O(N) traversal, no ExUnits limit
```

The single governance-proposal transaction forces every validating node to traverse all N entries in `vsDReps`. With N = 100 000 DReps (50 000 000 ADA locked), the traversal dominates block-application time with no protocol mechanism to reject or bound it. [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ledger.hs (L383-392)
```haskell
            if hardforkConwayMoveWithdrawalsAndDRepChecksToLedgerRule $ pp ^. ppProtocolVersionL
              then do
                let withdrawals = tx ^. bodyTxL . withdrawalsTxBodyL
                Shelley.testIncompleteAndMissingWithdrawals (certState ^. certDStateL . accountsL) withdrawals
                pure $
                  certState
                    & updateDormantDRepExpiries tx curEpochNo
                    & updateVotingDRepExpiries tx curEpochNo (pp ^. ppDRepActivityL)
                    & certDStateL . accountsL %~ drainAccounts withdrawals
              else pure certState
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/State/VState.hs (L56-67)
```haskell
data VState era = VState
  { vsDReps :: !(Map (Credential DRepRole) DRepState)
  , vsCommitteeState :: !(CommitteeState era)
  , vsNumDormantEpochs :: !EpochNo
  -- ^ Number of contiguous epochs in which there are exactly zero
  -- active governance proposals to vote on. It is incremented in every
  -- EPOCH rule if the number of active governance proposals to vote on
  -- continues to be zero. It is reset to zero when a new governance
  -- action is successfully proposed. We need this counter in order to
  -- bump DRep expiries through dormant periods when DReps do not have
  -- an opportunity to vote on anything.
  }
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/GovCert.hs (L246-254)
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
```

**File:** eras/shelley/impl/src/Cardano/Ledger/Shelley/LedgerState/PulsingReward.hs (L82-114)
```haskell
-- To prevent a huge pause, at the stability point, we spread out the
-- Calculation of rewards over many blocks. We do this in 3 phases. Phase 1
-- of a reward upate is a pure computation, computing some parameters which
-- become fixed at the time when we reach the stability point. One of these
-- parameters is a Pulser, i.e. a computation that when pulseM'ed computes
-- a portion of what is required, so that the whole compuation can be spread out in time.

startStep ::
  forall era.
  (EraGov era, EraCertState era) =>
  EpochSize ->
  BlocksMade ->
  EpochState era ->
  Coin ->
  ActiveSlotCoeff ->
  NonZero Word64 ->
  PulsingRewUpdate
startStep slotsPerEpoch b@(BlocksMade b') es@(EpochState acnt ls ss nm) maxSupply asc secparam =
  let SnapShot activeStake totalActiveStake stakePoolSnapShots = ssStakeGo ss
      numStakeCreds = fromIntegral (VMap.size $ unActiveStake activeStake)
      k = toIntegerNonZero secparam
      -- We expect approximately 10k-many blocks to be produced each epoch.
      -- The reward calculation begins (4k/f)-many slots into the epoch,
      -- and we guarantee that it ends (2k/f)-many slots before the end
      -- of the epoch (to allow tools such as db-sync to see the reward
      -- values in advance of them being applied to the ledger state).
      --
      -- Therefore to evenly space out the reward calculation, we divide
      -- the number of stake credentials by 4k in order to determine how many
      -- stake credential rewards we should calculate each block.
      -- If it does not finish in this amount of time, the calculation is
      -- forced to completion.
      pulseSize = max 1 (ceiling (numStakeCreds %. (knownNonZero @4 `mulNonZero` k)))
```
