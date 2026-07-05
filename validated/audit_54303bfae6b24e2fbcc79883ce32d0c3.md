### Title
ParameterChange Immediately Lowers Voting Thresholds for Same-Epoch Ratification, Enabling Treasury Withdrawal Bypass — (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs`)

---

### Summary

In the Conway era `RATIFY` rule, when a `ParameterChange` governance action is enacted, the updated protocol parameters — including DRep voting thresholds such as `dvtTreasuryWithdrawal` — are immediately written into the live `EnactState` and used to evaluate all remaining proposals in the **same epoch's ratification run**. Because `ParameterChange` actions are always sorted ahead of `TreasuryWithdrawals` actions by `actionPriority`, an attacker who controls enough DRep stake to pass the governance-group parameter-change threshold can lower `dvtTreasuryWithdrawal` and have a co-submitted treasury withdrawal ratified in the same epoch under the new, lower threshold — bypassing the threshold that was in effect when the epoch began.

---

### Finding Description

**Vulnerability class:** Funds/accounting bug — governance threshold bypass via unstable same-epoch parameter application.

**Step 1 — Ordering guarantee.**
`reorderActions` sorts all proposals by `actionPriority` before the `RATIFY` rule processes them. `ParameterChange` has priority 4 and `TreasuryWithdrawals` has priority 5, so parameter changes are always processed first. [1](#0-0) 

**Step 2 — Immediate PParams mutation on enactment.**
`enactmentTransition` in the `ENACT` rule applies the `PParamsUpdate` directly to `ensCurPParams` in the `EnactState` the moment a `ParameterChange` is enacted. [2](#0-1) 

**Step 3 — Updated state fed back into the same ratification loop.**
`ratifyTransition` passes the freshly-updated `newEnactState` (containing the new PParams) as the state for the recursive `RATIFY` call that processes all remaining proposals. [3](#0-2) 

**Step 4 — Subsequent proposals read thresholds from the mutated state.**
`votingDRepThreshold` and `votingDRepThresholdInternal` derive the required threshold for every proposal from `rsEnactState . ensCurPParams` — the live, already-mutated state — not from the PParams that were current at the start of the epoch. [4](#0-3) 

`dvtTreasuryWithdrawal` is read from `DRepVotingThresholds`, which is part of `ppDRepVotingThresholds` — a governance-group parameter. Changing it requires passing the `dvtPPGovGroupL` threshold, not the (typically higher) `dvtTreasuryWithdrawal` threshold itself. [5](#0-4) 

**Step 5 — `ParameterChange` is explicitly non-delaying.**
`delayingAction ParameterChange {} = False`, so enacting a parameter change does not set `rsDelayed = True` and does not block subsequent proposals from being ratified in the same run. [6](#0-5) 

---

### Impact Explanation

An attacker who controls DRep stake ≥ `dvtPPGovGroupL` (the governance-group parameter-change threshold) but < `dvtTreasuryWithdrawal` (the treasury withdrawal threshold) can:

1. Submit a `ParameterChange` that sets `dvtTreasuryWithdrawal` to just below their own stake fraction.
2. Submit a `TreasuryWithdrawals` proposal in the same epoch.
3. Vote YES on both.

At the epoch boundary the `ParameterChange` is ratified first, `ensCurPParams` is mutated, and the `TreasuryWithdrawals` proposal is then evaluated against the new, lower threshold — which the attacker now satisfies. The treasury is drained in the same epoch, at a threshold lower than what was in effect when the epoch began.

This matches the allowed impact: **"Attacker-controlled transactions… modify… withdrawals outside design parameters."**

The Constitutional Committee must also approve both proposals. However, the CC may approve the `ParameterChange` without recognising that it will immediately lower the ratification bar for a co-pending `TreasuryWithdrawals` in the same epoch — exactly the "no time delay / no opt-out window" problem described in the reference report.

---

### Likelihood Explanation

- **Realistic configuration:** Governance designers commonly set `dvtPPGovGroupL` lower than `dvtTreasuryWithdrawal` to make parameter tuning easier than treasury access. The attack window exists whenever this ordering holds.
- **No guardrails required:** The guardrails script check (`checkGuardrailsScriptHash`) is only enforced when a constitution with a guardrails script is in place. Early in the Conway era, or if the constitution carries no script, no on-chain rule blocks the threshold reduction.
- **Attacker entry point:** Any DRep (or coalition of DReps) controlling the governance-group threshold fraction of active DRep stake can submit both proposals in a single transaction batch. No privileged key or leaked credential is required.
- **CC collusion not required:** The CC may approve the `ParameterChange` in good faith, not anticipating the same-epoch interaction with the treasury withdrawal. [7](#0-6) 

---

### Recommendation

1. **Snapshot PParams at epoch-boundary start.** Evaluate all proposals in a single ratification run against the PParams that were current when the epoch snapshot was taken (`dpEnactState` at pulser initialisation), not against the live `EnactState` that is mutated as proposals are enacted mid-run.
2. **Alternatively, mark `ParameterChange` as a delaying action** (set `delayingAction ParameterChange {} = True`). This would prevent any further ratification in the same epoch after a parameter change is enacted, giving the network one full epoch to observe the new thresholds before they affect other proposals.
3. **Guardrails script enforcement:** Require a guardrails script that explicitly prohibits lowering `dvtTreasuryWithdrawal` (or any voting threshold) in the same proposal batch as a treasury withdrawal.

---

### Proof of Concept

```
Preconditions:
  dvtPPGovGroupL      = 40%   (threshold to change governance-group params)
  dvtTreasuryWithdrawal = 67%  (threshold to ratify treasury withdrawals)
  Attacker DRep stake = 45%

Epoch N:
  Tx1: submit ParameterChange { dvtTreasuryWithdrawal := 44% }
  Tx2: submit TreasuryWithdrawals { recipient := attacker, amount := entire treasury }
  Attacker votes YES on both.

Epoch N boundary — RATIFY run (proposals sorted by actionPriority):
  1. ParameterChange (priority 4):
       dRepAccepted? 45% >= 40% (dvtPPGovGroupL) → YES
       ENACT fires:  ensCurPParams.dvtTreasuryWithdrawal ← 44%
  2. TreasuryWithdrawals (priority 5):
       dRepAccepted? 45% >= 44% (new dvtTreasuryWithdrawal) → YES  ← bypass
       Treasury drained.

Without the ParameterChange, step 2 would require 67% and fail.
``` [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Internal.hs (L311-327)
```haskell
pparamsUpdateThreshold ::
  forall era.
  ConwayEraPParams era =>
  DRepVotingThresholds ->
  PParamsUpdate era ->
  UnitInterval
pparamsUpdateThreshold thresholds ppu =
  let thresholdLens = \case
        NetworkGroup -> dvtPPNetworkGroupL
        GovGroup -> dvtPPGovGroupL
        TechnicalGroup -> dvtPPTechnicalGroupL
        EconomicGroup -> dvtPPEconomicGroupL
      lookupGroupThreshold (PPGroups grp _) =
        thresholds ^. thresholdLens grp
   in Set.foldr' max minBound $
        Set.map lookupGroupThreshold $
          modifiedPPGroups @era ppu
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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Internal.hs (L511-531)
```haskell
  let thresholds@DRepVotingThresholds
        { dvtCommitteeNoConfidence
        , dvtCommitteeNormal
        , dvtMotionNoConfidence
        , dvtUpdateToConstitution
        , dvtHardForkInitiation
        , dvtTreasuryWithdrawal
        } -- We reset all (except InfoAction) DRep thresholds to 0 during bootstrap phase
          | hardforkConwayBootstrapPhase (pp ^. ppProtocolVersionL) = def
          | otherwise = pp ^. ppDRepVotingThresholdsL
   in case action of
        NoConfidence {} -> VotingThreshold dvtMotionNoConfidence
        UpdateCommittee {} ->
          VotingThreshold $
            if isElectedCommittee
              then dvtCommitteeNormal
              else dvtCommitteeNoConfidence
        NewConstitution {} -> VotingThreshold dvtUpdateToConstitution
        HardForkInitiation {} -> VotingThreshold dvtHardForkInitiation
        ParameterChange _ ppu _ -> VotingThreshold $ pparamsUpdateThreshold thresholds ppu
        TreasuryWithdrawals {} -> VotingThreshold dvtTreasuryWithdrawal
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/Internal.hs (L534-540)
```haskell
actionPriority :: GovAction era -> Int
actionPriority NoConfidence {} = 0
actionPriority UpdateCommittee {} = 1
actionPriority NewConstitution {} = 2
actionPriority HardForkInitiation {} = 3
actionPriority ParameterChange {} = 4
actionPriority TreasuryWithdrawals {} = 5
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs (L83-116)
```haskell
enactmentTransition :: forall era. EraPParams era => TransitionRule (ENACT era)
enactmentTransition = do
  TRC ((), st, EnactSignal govActionId act) <- judgmentContext

  pure $!
    case act of
      ParameterChange _ ppup _ ->
        st
          & ensCurPParamsL %~ (`applyPPUpdates` ppup)
          & ensPrevPParamUpdateL .~ SJust (GovPurposeId govActionId)
      HardForkInitiation _ pv ->
        st
          & ensProtVerL .~ pv
          & ensPrevHardForkL .~ SJust (GovPurposeId govActionId)
      TreasuryWithdrawals wdrls _ ->
        let wdrlsAmount = fold wdrls
            wdrlsNoNetworkId = Map.mapKeys (^. accountAddressCredentialL) wdrls
         in st
              { ensWithdrawals = Map.unionWith (<>) wdrlsNoNetworkId $ ensWithdrawals st
              , ensTreasury = ensTreasury st <-> wdrlsAmount
              }
      NoConfidence _ ->
        st
          & ensCommitteeL .~ SNothing
          & ensPrevCommitteeL .~ SJust (GovPurposeId govActionId)
      UpdateCommittee _ membersToRemove membersToAdd newThreshold -> do
        st
          & ensCommitteeL %~ SJust . updatedCommittee membersToRemove membersToAdd newThreshold
          & ensPrevCommitteeL .~ SJust (GovPurposeId govActionId)
      NewConstitution _ c ->
        st
          & ensConstitutionL .~ c
          & ensPrevConstitutionL .~ SJust (GovPurposeId govActionId)
      InfoAction -> st
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L283-290)
```haskell
delayingAction :: GovAction era -> Bool
delayingAction NoConfidence {} = True
delayingAction HardForkInitiation {} = True
delayingAction UpdateCommittee {} = True
delayingAction NewConstitution {} = True
delayingAction TreasuryWithdrawals {} = False
delayingAction ParameterChange {} = False
delayingAction InfoAction {} = False
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L308-360)
```haskell
ratifyTransition ::
  forall era.
  ( Embed (EraRule "ENACT" era) (RATIFY era)
  , State (EraRule "ENACT" era) ~ EnactState era
  , Environment (EraRule "ENACT" era) ~ ()
  , Signal (EraRule "ENACT" era) ~ EnactSignal era
  , ConwayEraPParams era
  , ConwayEraAccounts era
  ) =>
  TransitionRule (RATIFY era)
ratifyTransition = do
  TRC
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
  case rsig of
    gas@GovActionState {gasId, gasExpiresAfter} SSeq.:<| sigs -> do
      let govAction = gasAction gas
      if prevActionAsExpected gas ensPrevGovActionIds
        && validCommitteeTerm govAction ensCurPParams reCurrentEpoch
        && not rsDelayed
        && withdrawalCanWithdraw govAction ensTreasury
        && acceptedByEveryone env st gas
        then do
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
        else do
          -- This action hasn't been ratified yet. Process the remaining actions.
          st' <- trans @(RATIFY era) $ TRC (env, st, RatifySignal sigs)
          -- Finally, filter out actions that have expired.
          if gasExpiresAfter < reCurrentEpoch
            then pure $ st' & rsExpiredL %~ Set.insert gasId
            else pure st'
    SSeq.Empty -> pure $ st & rsEnactStateL . ensTreasuryL .~ Coin 0
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L557-558)
```haskell
          ParameterChange _ _ proposalPolicy ->
            runTest $ checkGuardrailsScriptHash @era constitutionPolicy proposalPolicy
```
