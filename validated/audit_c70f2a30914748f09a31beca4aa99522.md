### Title
Unbounded O(n) Iteration Over Growing Governance Proposals Set in `cleanupProposalVotes` Triggered Per-Transaction - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs`)

### Summary
The Conway era `GOV` rule unconditionally iterates over every governance proposal in the ledger state whenever a transaction contains an `UnRegDRepTxCert` certificate. Because the proposals set grows continuously across epochs and has no hard upper-bound enforced at the ledger level, this O(n) scan per transaction grows without bound, allowing an attacker to inflate validation cost for any block that includes a DRep-unregistration transaction.

### Finding Description
In `Gov.hs` lines 619–625, after processing votes, the rule computes `cleanupProposalVotes`:

```haskell
cleanupProposalVotes
  | Set.null unregisteredDReps = id
  | otherwise =
      let cleanupVoters gas =
            gas & gasDRepVotesL %~ (`Map.withoutKeys` unregisteredDReps)
       in mapProposals cleanupVoters
``` [1](#0-0) 

`mapProposals` is defined as:

```haskell
mapProposals f props = props {pProps = OMap.mapUnsafe f (pProps props)}
``` [2](#0-1) 

`OMap.mapUnsafe` traverses every entry in the ordered map — O(n) in the total number of live proposals. This is invoked for every transaction that contains at least one `UnRegDRepTxCert` certificate, regardless of how many proposals that DRep actually voted on.

A second O(n) scan occurs unconditionally for every transaction that carries voting procedures: `proposalsActionsMap proposals` at line 592 converts the entire OMap to a plain `Map` before any vote lookup is performed. [3](#0-2) 

The proposals set is bounded only by the `govActionLifetime` protocol parameter (`EpochInterval`, a `Word32`). With the example mainnet value of 6 epochs, proposals submitted across those 6 epochs all remain live simultaneously. [4](#0-3) 

There is no protocol-level cap on the total number of live proposals; the only natural limit is the per-proposal deposit (`ppGovActionDepositL`). [5](#0-4) 

A third O(n) scan occurs at every epoch boundary in `updateNumDormantEpochs`, which calls `OMap.filter` over all live proposals. [6](#0-5) 

### Impact Explanation
Block producers in Cardano must complete all ledger validation within the slot duration (1 second). The `GOV` rule runs in pure Haskell with no execution-unit budget; its only resource constraint is wall-clock time. As the live proposals set grows, every transaction containing `UnRegDRepTxCert` forces an O(n) traversal of the entire proposals OMap. If the set is large enough, this traversal can push the total block-validation time past the slot boundary, causing the block producer to miss the slot. Repeated across many blocks, this constitutes a resource-limit DoS matching the allowed Medium impact: attacker-controlled certificates exceed intended validation limits.

### Likelihood Explanation
The attack requires accumulating a large number of live proposals. Each proposal requires a deposit (100,000 ADA at mainnet example parameters). Deposits are returned on expiry, so the cost is temporary capital lockup rather than permanent loss, but the capital requirement is substantial. With current mainnet parameters the number of proposals achievable by a single attacker is limited. However:

- The `govActionLifetime` and `govActionDeposit` are both governance-adjustable protocol parameters; a reduction in deposit or increase in lifetime directly amplifies the attack surface.
- Multiple independent actors submitting legitimate proposals for their own purposes can organically grow the set without any coordination.
- The `proposalsActionsMap` O(n) conversion is triggered by any voting transaction, not just DRep-unregistration, broadening the surface.

Likelihood is **low** under current mainnet parameters but structurally unbounded by design.

### Recommendation
1. Replace the full-scan `mapProposals cleanupVoters` with a targeted removal: maintain a reverse index from `Credential DRepRole` to the set of `GovActionId`s that DRep has voted on, so cleanup is O(k log n) where k is the number of proposals the DRep voted on.
2. Replace `proposalsActionsMap` (full OMap-to-Map conversion) with direct `proposalsLookupId` calls (already available at `Proposals.hs` line 596–600) so vote lookups are O(log n) without a full traversal.
3. Consider introducing a protocol parameter `maxGovProposals` to cap the total number of live proposals, analogous to `maxCollInputs` for collateral.

### Proof of Concept
1. Governance sets `govActionLifetime` to a large value (e.g., 20 epochs) and `govActionDeposit` to a low value.
2. Attacker submits N governance proposals across multiple epochs, each paying the deposit. All N proposals remain live simultaneously.
3. Attacker registers as a DRep, then submits a transaction containing `UnRegDRepTxCert`.
4. The `GOV` rule evaluates `cleanupProposalVotes`, which calls `mapProposals cleanupVoters` — iterating over all N `GovActionState` entries in the OMap.
5. As N grows, the per-transaction validation cost grows linearly. At sufficient N, block producers including such a transaction miss their slot, causing the block to be dropped and the transaction to be re-queued, creating a sustained validation-cost amplification.

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L592-592)
```haskell
      curGovActionIds = proposalsActionsMap proposals
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L619-625)
```haskell
    cleanupProposalVotes
      -- optimization: avoid iterating over proposals when there is nothing to cleanup
      | Set.null unregisteredDReps = id
      | otherwise =
          let cleanupVoters gas =
                gas & gasDRepVotesL %~ (`Map.withoutKeys` unregisteredDReps)
           in mapProposals cleanupVoters
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Proposals.hs (L258-259)
```haskell
mapProposals :: (GovActionState era -> GovActionState era) -> Proposals era -> Proposals era
mapProposals f props = props {pProps = OMap.mapUnsafe f (pProps props)}
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Examples.hs (L379-380)
```haskell
    & ppGovActionLifetimeL .~ EpochInterval 6
    & ppGovActionDepositL .~ Coin 100_000_000_000
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L197-201)
```haskell
updateNumDormantEpochs :: EpochNo -> Proposals era -> VState era -> VState era
updateNumDormantEpochs currentEpoch ps vState =
  if null $ OMap.filter ((currentEpoch <=) . gasExpiresAfter) $ ps ^. pPropsL
    then vState & vsNumDormantEpochsL %~ succ
    else vState
```
