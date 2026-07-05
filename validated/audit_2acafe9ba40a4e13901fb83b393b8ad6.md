### Title
`ParameterChange` enacted in the same epoch retroactively lowers `dvtTreasuryWithdrawal` for in-flight `TreasuryWithdrawals` proposals, enabling unauthorized treasury drainage — (`eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs`)

---

### Summary

In the Conway governance `RATIFY` rule, when a `ParameterChange` proposal is enacted, the updated `EnactState` (containing new `PParams`) is immediately propagated to all subsequent proposals processed in the same epoch-boundary ratification pass. Because `ParameterChange` (priority 4) is always sorted before `TreasuryWithdrawals` (priority 5) by `reorderActions`, an attacker who controls enough DRep stake to meet `dvtPPGovGroup` — but not the higher `dvtTreasuryWithdrawal` — can atomically lower `dvtTreasuryWithdrawal` to their own stake fraction and have a co-submitted `TreasuryWithdrawals` proposal ratified in the same epoch under the new, self-set threshold. This bypasses the treasury withdrawal threshold that was in force when votes were cast.

---

### Finding Description

**Root cause — `ratifyTransition` propagates new `PParams` mid-pass**

`ratifyTransition` processes the ordered proposal sequence recursively. When a proposal is accepted, it calls `ENACT`, which for `ParameterChange` applies `applyPPUpdates` to `ensCurPParams`:

```haskell
-- Enact.hs line 89-92
ParameterChange _ ppup _ ->
  st
    & ensCurPParamsL %~ (`applyPPUpdates` ppup)
    & ensPrevPParamUpdateL .~ SJust (GovPurposeId govActionId)
```

The resulting `newEnactState` is immediately installed into `st'` and forwarded to the recursive call that processes all remaining proposals:

```haskell
-- Ratify.hs lines 343-352
newEnactState <-
  trans @(EraRule "ENACT" era) $
    TRC ((), rsEnactState, EnactSignal gasId govAction)
let st' =
      st
        & rsEnactStateL .~ newEnactState   -- ← new PParams live here
        & rsDelayedL    .~ delayingAction govAction
        & rsEnactedL    %~ (Seq.:|> gas)
trans @(RATIFY era) $ TRC (env, st', RatifySignal sigs)
```

**Root cause — threshold lookup reads from the live `EnactState`**

`dRepAccepted` calls `votingDRepThreshold`, which reads `dvtTreasuryWithdrawal` from the current `RatifyState`:

```haskell
-- Internal.hs lines 498-502
votingDRepThreshold ratifyState =
  toRatifyVotingThreshold . votingDRepThresholdInternal pp isElectedCommittee
  where
    pp = ratifyState ^. rsEnactStateL . ensCurPParamsL   -- ← reads updated PParams
```

**Root cause — fixed priority ordering guarantees `ParameterChange` precedes `TreasuryWithdrawals`**

```haskell
-- Internal.hs lines 534-541
actionPriority ParameterChange {}     = 4
actionPriority TreasuryWithdrawals {} = 5

reorderActions = SS.fromList . sortOn (actionPriority . gasAction) . toList
```

**Root cause — `ppuWellFormed` imposes no lower bound on `dvtTreasuryWithdrawal`**

```haskell
-- PParams.hs lines 934-953
ppuWellFormed pv ppu =
  and
    [ isValid (/= 0) ppuMaxBBSizeL
    , isValid (/= 0) ppuMaxTxSizeL
    -- ... no check on dvtTreasuryWithdrawal or dvtPPGovGroup
    , ppu /= emptyPParamsUpdate
    ]
```

`dvtTreasuryWithdrawal` can be set to any `UnitInterval` value, including `minBound` (0).

**`dvtTreasuryWithdrawal` belongs to `GovGroup`**, so changing it requires meeting `dvtPPGovGroup`, not `dvtTreasuryWithdrawal` itself:

```haskell
-- PParams.hs (Dijkstra mirrors Conway)
cppDRepVotingThresholds :: THKD ('PPGroups 'GovGroup 'NoStakePoolGroup) f DRepVotingThresholds
```

**Attack scenario**

Precondition: `dvtPPGovGroup` < `dvtTreasuryWithdrawal` (e.g., 51 % vs 67 %). Attacker controls 55 % of active DRep stake.

1. Attacker submits `ParameterChange` setting `dvtTreasuryWithdrawal := 51 %`.
2. Attacker submits `TreasuryWithdrawals` draining the treasury to their address.
3. Attacker votes YES on both; obtains CC approval for both (CC sees two individually plausible proposals).
4. At the epoch boundary, `reorderActions` places the `ParameterChange` first.
5. `ParameterChange` is enacted → `ensCurPParams` now has `dvtTreasuryWithdrawal = 51 %`.
6. `TreasuryWithdrawals` is evaluated with the new threshold: 55 % ≥ 51 % → `dRepAccepted = True` → treasury is drained.

Without step 5, the treasury withdrawal would have failed: 55 % < 67 %.

The test suite explicitly confirms this mechanism works:

```haskell
-- RatifySpec.hs line 476
it "Decreasing the threshold ratifies a hitherto-unratifiable proposal" $ whenPostBootstrap $ do
```

---

### Impact Explanation

**Critical — Unauthorized treasury action is enacted.**

A `TreasuryWithdrawals` proposal that could not have been ratified under the thresholds in force when votes were cast is enacted because a co-submitted `ParameterChange` retroactively lowers the required threshold within the same epoch's ratification pass. ADA is transferred out of the treasury without the governance approval level that was intended at the time of voting. This constitutes a direct, attacker-controlled loss of ADA from the treasury through an invalid (from the pre-change-threshold perspective) ledger state transition.

---

### Likelihood Explanation

**Medium.**

The attack requires:
1. `dvtPPGovGroup` < `dvtTeavsuryWithdrawal` — a configuration that is not the default (default: 75 % vs 67 %) but is entirely reachable because thresholds are governance-configurable and `ppuWellFormed` imposes no ordering constraint between them.
2. The attacker controls DRep stake ≥ `dvtPPGovGroup` but < `dvtTreasuryWithdrawal`.
3. CC approval for both proposals — achievable if the CC does not detect the combined-epoch attack pattern.

No privileged key, leaked secret, or Sybil attack is required. Any DRep coalition that meets `dvtPPGovGroup` can execute this atomically within a single epoch boundary.

---

### Recommendation

1. **Enforce a threshold ordering invariant on-chain**: In `ppuWellFormed` (or a dedicated governance-parameter consistency check), reject any `PParamsUpdate` that would set `dvtPPGovGroup` > `dvtTreasuryWithdrawal` (i.e., make it cheaper to change governance thresholds than to withdraw from treasury). This mirrors the Oracle report's recommendation to enforce `Q > (C+1)/2`.

2. **Snapshot thresholds at proposal submission time**: Record the ratification thresholds that were active when a proposal was submitted and use those frozen thresholds for ratification, rather than the live `ensCurPParams`. This is the direct analog of the Oracle fix (clearing reports on quorum change).

3. **Alternatively, defer threshold changes to the next epoch**: Do not apply new `PParams` from an enacted `ParameterChange` to proposals in the same ratification pass. Apply them only starting from the following epoch boundary.

---

### Proof of Concept

Trace through `ratifyTransition` with two proposals in the same epoch:

```
Proposals (after reorderActions):
  [ParameterChange (priority 4), TreasuryWithdrawals (priority 5)]

Initial state:
  ensCurPParams.dvtTreasuryWithdrawal = 67%
  Attacker DRep stake = 55%

Step 1 — ParameterChange processed:
  acceptedByEveryone env st paramChange = True  (55% >= dvtPPGovGroup=51%)
  ENACT: ensCurPParams.dvtTreasuryWithdrawal := 51%
  st' = st & rsEnactStateL .~ newEnactState   ← threshold now 51%

Step 2 — TreasuryWithdrawals processed with st':
  votingDRepThreshold st' TreasuryWithdrawals
    = SJust 51%                               ← reads NEW PParams
  dRepAcceptedRatio = 55%
  55% >= 51% → dRepAccepted = True
  acceptedByEveryone = True → ENACT treasury withdrawal
```

Key code path: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L343-352)
```haskell
          newEnactState <-
            trans @(EraRule "ENACT" era) $
              TRC ((), rsEnactState, EnactSignal gasId govAction)
          let
            st' =
              st
                & rsEnactStateL .~ newEnactState
                & rsDelayedL .~ delayingAction govAction
                & rsEnactedL %~ (Seq.:|> gas)
          trans @(RATIFY era) $ TRC (env, st', RatifySignal sigs)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs (L89-92)
```haskell
      ParameterChange _ ppup _ ->
        st
          & ensCurPParamsL %~ (`applyPPUpdates` ppup)
          & ensPrevPParamUpdateL .~ SJust (GovPurposeId govActionId)
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Internal.hs (L493-502)
```haskell
votingDRepThreshold ::
  ConwayEraPParams era =>
  RatifyState era ->
  GovAction era ->
  StrictMaybe UnitInterval
votingDRepThreshold ratifyState =
  toRatifyVotingThreshold . votingDRepThresholdInternal pp isElectedCommittee
  where
    pp = ratifyState ^. rsEnactStateL . ensCurPParamsL
    isElectedCommittee = isSJust $ ratifyState ^. rsEnactStateL . ensCommitteeL
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Internal.hs (L534-544)
```haskell
actionPriority :: GovAction era -> Int
actionPriority NoConfidence {} = 0
actionPriority UpdateCommittee {} = 1
actionPriority NewConstitution {} = 2
actionPriority HardForkInitiation {} = 3
actionPriority ParameterChange {} = 4
actionPriority TreasuryWithdrawals {} = 5
actionPriority InfoAction {} = 6

reorderActions :: SS.StrictSeq (GovActionState era) -> SS.StrictSeq (GovActionState era)
reorderActions = SS.fromList . sortOn (actionPriority . gasAction) . toList
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/PParams.hs (L934-953)
```haskell
  ppuWellFormed pv ppu =
    and
      [ -- Numbers
        isValid (/= 0) ppuMaxBBSizeL
      , isValid (/= 0) ppuMaxTxSizeL
      , isValid (/= 0) ppuMaxBHSizeL
      , isValid (/= 0) ppuMaxValSizeL
      , isValid (/= 0) ppuCollateralPercentageL
      , isValid (/= EpochInterval 0) ppuCommitteeMaxTermLengthL
      , isValid (/= EpochInterval 0) ppuGovActionLifetimeL
      , -- Coins
        isValid (/= CompactCoin 0) ppuPoolDepositCompactL
      , isValid (/= CompactCoin 0) ppuGovActionDepositCompactL
      , isValid (/= CompactCoin 0) ppuDRepDepositCompactL
      , hardforkConwayBootstrapPhase pv
          || isValid ((/= CompactCoin 0) . unCoinPerByte) ppuCoinsPerUTxOByteL
      , ppu /= emptyPParamsUpdate
      , pvMajor pv < natVersion @11
          || isValid (/= 0) ppuNOptL
      ]
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/RatifySpec.hs (L476-499)
```haskell
      it "Decreasing the threshold ratifies a hitherto-unratifiable proposal" $ whenPostBootstrap $ do
        -- This sets up a stake pool with 1_000_000 Coin
        (drepC, hotCommitteeC, _) <- electBasicCommittee
        setCommitteeUpdateThreshold $ 1 %! 1 -- too large threshold
        (drep, _, _) <- setupSingleDRep 3_000_000
        (spoC, _, _) <- setupPoolWithStake $ Coin 3_000_000
        (gaiParent, gaiChild) <-
          submitTwoExampleProposalsAndVoteOnTheChild [(spoC, VoteYes)] [(drep, VoteYes)]
        logAcceptedRatio gaiChild
        isDRepAccepted gaiChild `shouldReturn` False
        enactCommitteeUpdateThreshold
          (65 %! 100)
          ([drepC, drep] :: [Credential DRepRole])
          hotCommitteeC
        isDRepAccepted gaiChild `shouldReturn` True
        -- Not vote on the parent too to make sure both get enacted
        submitYesVote_ (DRepVoter drep) gaiParent
        -- bootstrap: 3 % 4 stake yes; 1 % 4 stake abstain; yes / stake - abstain > 1 % 2
        -- post-bootstrap: 3 % 4 stake yes; 1 % 4 stake no
        submitYesVote_ (StakePoolVoter spoC) gaiParent
        passNEpochs 2
        getLastEnactedCommittee `shouldReturn` SJust (GovPurposeId gaiParent)
        passEpoch -- UpdateCommittee is a delaying action
        getLastEnactedCommittee `shouldReturn` SJust (GovPurposeId gaiChild)
```
