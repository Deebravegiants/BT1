### Title
DRep Expiry Check in Ratification Ignores Accumulated Dormant Epochs, Allowing Governance Proposals to Pass Below Required Threshold — (`File: eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs`)

---

### Summary

The `dRepAcceptedRatio` function in the Conway RATIFY rule checks DRep expiry using only the raw `drepExpiry` field stored in the epoch-boundary snapshot (`dpDRepState`). It does not account for `vsNumDormantEpochs`, the counter that extends every DRep's effective lifetime during periods with no governance proposals. When dormant epochs have accumulated, DReps whose raw expiry has passed but whose *actual* expiry (raw + dormant) has not are incorrectly excluded from both the numerator and denominator of the ratification ratio. This artificially inflates the accepted ratio, allowing governance proposals to be ratified with fewer yes-votes than the protocol threshold requires.

---

### Finding Description

**Root cause — two inconsistent expiry definitions**

The ledger maintains two notions of DRep expiry:

1. **Stored raw expiry** (`drepExpiry` in `DRepState`): updated only when a DRep votes, submits an update certificate, or a new proposal is submitted (triggering `updateDormantDRepExpiry`).
2. **Actual expiry** (`drepExpiry + vsNumDormantEpochs`): the value used by `isDRepExpired` and `vsActualDRepExpiry` to determine whether a DRep is truly inactive. [1](#0-0) 

The ratification ratio function uses only the raw stored expiry:

```haskell
| reCurrentEpoch > drepExpiry drepState -> (yes, tot) -- drep is expired, so we don't consider it
``` [2](#0-1) 

**Root cause — pulser snapshot does not capture `numDormantEpochs`**

The `DRepPulser` is created at the epoch boundary and captures `dpDRepState = vsDReps vState` and `dpCurrentEpoch = epochNo`. It has no `dpNumDormantEpochs` field. [3](#0-2) 

**Root cause — `updateDormantDRepExpiry` is never called at the epoch boundary**

`updateDormantDRepExpiry` (which writes `numDormantEpochs` into the raw `drepExpiry` fields and resets the counter) is only triggered inside `updateDormantDRepExpiries`, which is called from the CERTS transition rule when a transaction contains a governance proposal. [4](#0-3) 

It is **not** called during the EPOCH or NEWEPOCH boundary rules. Therefore, when the pulser is created at the epoch boundary, the raw `drepExpiry` values in `dpDRepState` have not been adjusted for any dormant epochs that accumulated during the previous epoch. [5](#0-4) 

**Concrete discrepancy**

| Check | Formula | Used where |
|---|---|---|
| `isDRepExpired` (correct) | `drepExpiry + numDormantEpochs < currentEpoch` | `ImpTest`, `vsActualDRepExpiry` |
| `dRepAcceptedRatio` (incorrect) | `currentEpoch > drepExpiry` | RATIFY rule | [6](#0-5) 

**Attack scenario**

1. DRep A registers at epoch 1 with `drepActivity = 5`, so `rawExpiry = 6`.
2. Epochs 2–4 pass with no proposals; `numDormantEpochs = 3`.
3. Epoch 5 boundary: pulser snapshot captures `rawExpiry = 6`, `dpCurrentEpoch = 5`. Actual expiry = `6 + 3 = 9` → DRep A is **not** expired.
4. Attacker (DRep B, registered in epoch 4, `rawExpiry = 9`) submits a proposal and votes yes.
5. `updateDormantDRepExpiry` updates the live `certState` (DRep A's raw expiry → 9), but the pulser snapshot is **not** updated.
6. Ratification runs using the stale snapshot: `5 > 6` = False for DRep A — in this example DRep A is fine. But consider DRep C registered at epoch 1 with `drepActivity = 3`, `rawExpiry = 4`. Check: `5 > 4` = **True** → DRep C is excluded. Actual expiry = `4 + 3 = 7 ≥ 5` → DRep C should be **active**.
7. DRep C's stake is removed from the denominator. If DRep C voted No, the yes-ratio rises above the threshold and the proposal is enacted.

The codebase itself acknowledges the discrepancy in disabled conformance tests: [7](#0-6) 

---

### Impact Explanation

By incorrectly excluding active DReps from the ratification denominator, an attacker can cause governance proposals — including `ParameterChange`, `TreasuryWithdrawals`, `HardForkInitiation`, `UpdateCommittee`, and `NewConstitution` — to be ratified below the protocol-mandated threshold. This constitutes an **unauthorized governance, treasury, protocol-parameter, committee, constitution, or hard-fork action being enacted**, which is a Critical/High impact under the allowed scope.

---

### Likelihood Explanation

Dormant epochs accumulate naturally whenever no governance proposals are submitted for one or more epochs. This is a realistic condition on mainnet during periods of low governance activity. An attacker needs only to:
- Register as a DRep (permissionless, requires only a deposit)
- Wait for dormant epochs to accumulate passively
- Submit a proposal and vote yes

No privileged access, key compromise, or supermajority is required. The attacker controls the timing of the proposal submission.

---

### Recommendation

1. **Include `numDormantEpochs` in the pulser snapshot** (`DRepPulser`) so that `dRepAcceptedRatio` can apply the correct expiry check: `reCurrentEpoch > drepExpiry drepState + numDormantEpochs`.

2. **Alternatively**, call `updateDormantDRepExpiry` at the epoch boundary (inside the EPOCH rule) *before* `startDRepPulser` is invoked, so that the raw `drepExpiry` values in the snapshot already reflect accumulated dormant epochs.

3. **Align the expiry predicate** in `dRepAcceptedRatio` with the one used in `isDRepExpired` / `vsActualDRepExpiry` to eliminate the two-definition inconsistency.

---

### Proof of Concept

The existing (currently disabled) conformance test at line 190 of `EpochSpec.hs` already demonstrates the discrepancy:

```
isDRepExpired drep `shouldReturn` False
-- numDormantEpochs is added to the drep expiry calculation
``` [8](#0-7) 

A targeted test would:
1. Register DRep with `drepActivity = 3` at epoch 0 → `rawExpiry = 3`.
2. Pass 4 epochs with no proposals → `numDormantEpochs = 4`, `actualExpiry = 7`.
3. At epoch 4 boundary, pulser snapshot: `rawExpiry = 3`, `dpCurrentEpoch = 4`.
4. Submit a proposal and vote yes with a second DRep.
5. Assert `dRepAcceptedRatio` incorrectly excludes DRep 1 (`4 > 3 = True`) even though `isDRepExpired drep1 = False` (`3 + 4 = 7 ≥ 4`).
6. Observe the proposal ratified despite DRep 1's no-vote being silently dropped from the denominator. [9](#0-8) [10](#0-9)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L252-281)
```haskell
dRepAcceptedRatio ::
  forall era.
  RatifyEnv era ->
  Map (Credential DRepRole) Vote ->
  GovAction era ->
  Rational
dRepAcceptedRatio RatifyEnv {reDRepDistr, reDRepState, reCurrentEpoch} gasDRepVotes govAction =
  toInteger yesStake %? toInteger totalExcludingAbstainStake
  where
    accumStake (!yes, !tot) drep (CompactCoin stake) =
      case drep of
        DRepCredential cred ->
          case Map.lookup cred reDRepState of
            Nothing -> (yes, tot) -- drep is not registered, so we don't consider it
            Just drepState
              | reCurrentEpoch > drepExpiry drepState -> (yes, tot) -- drep is expired, so we don't consider it
              | otherwise ->
                  case Map.lookup cred gasDRepVotes of
                    -- drep hasn't voted for this action, so we don't count
                    -- the vote but we consider it in the denominator:
                    Nothing -> (yes, tot + stake)
                    Just VoteYes -> (yes + stake, tot + stake)
                    Just Abstain -> (yes, tot)
                    Just VoteNo -> (yes, tot + stake)
        DRepAlwaysNoConfidence ->
          case govAction of
            NoConfidence _ -> (yes + stake, tot + stake)
            _ -> (yes, tot + stake)
        DRepAlwaysAbstain -> (yes, tot)
    (yesStake, totalExcludingAbstainStake) = Map.foldlWithKey' accumStake (0, 0) reDRepDistr
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/DRepPulser.hs (L249-283)
```haskell
data DRepPulser era (m :: Type -> Type) ans where
  DRepPulser ::
    forall era ans m.
    (ans ~ RatifyState era, m ~ Identity, RunConwayRatify era) =>
    { dpPulseSize :: !Int
    -- ^ How many elements of 'dpAccounts' to consume each pulse.
    , dpAccounts :: !(Accounts era)
    -- ^ Snapshot containing the mapping of stake credentials to DReps, Pools and Rewards.
    , dpIndex :: !Int
    -- ^ The index of the iterator over `dpAccounts`. Grows with each pulse.
    , dpInstantStake :: !(InstantStake era)
    -- ^ Snapshot of the stake distr (comes from the IncrementalStake)
    , dpStakePoolDistr :: PoolDistr
    -- ^ Snapshot of the pool distr. Lazy on purpose: See `ssStakeMarkPoolDistr` and ADR-7
    -- for explanation.
    , dpDRepDistr :: !(Map DRep (CompactForm Coin))
    -- ^ The partial result that grows with each pulse. The purpose of the pulsing.
    , dpDRepState :: !(Map (Credential DRepRole) DRepState)
    -- ^ Snapshot of registered DRep credentials
    , dpCurrentEpoch :: !EpochNo
    -- ^ Snapshot of the EpochNo this pulser will complete in.
    , dpCommitteeState :: !(CommitteeState era)
    -- ^ Snapshot of the CommitteeState
    , dpEnactState :: !(EnactState era)
    -- ^ Snapshot of the EnactState, Used to build the Env of the RATIFY rule
    , dpProposals :: !(StrictSeq (GovActionState era))
    -- ^ Snapshot of the proposals. This is the Signal for the RATIFY rule
    , dpProposalDeposits :: !(Map (Credential Staking) (CompactForm Coin))
    -- ^ Snapshot of the proposal-deposits per account-address-staking-credential
    , dpGlobals :: !Globals
    , dpStakePools :: !(Map (KeyHash StakePool) StakePoolState)
    -- ^ Snapshot of the parameters of stake pools -
    --   this is needed to get the account address for SPO vote calculation
    } ->
    DRepPulser era m ans
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/DRepPulser.hs (L395-417)
```haskell
    !leftOver = Map.drop dpIndex (dpAccounts ^. accountsMapL)
    (finalDRepDistr, finalStakePoolDistr) =
      computeDRepDistr dpInstantStake dpDRepState dpProposalDeposits dpStakePoolDistr dpDRepDistr leftOver
    !ratifyEnv =
      RatifyEnv
        { reInstantStake = dpInstantStake
        , reStakePoolDistr = finalStakePoolDistr
        , reDRepDistr = finalDRepDistr
        , reDRepState = dpDRepState
        , reCurrentEpoch = dpCurrentEpoch
        , reCommitteeState = dpCommitteeState
        , reAccounts = dpAccounts
        , reStakePools = dpStakePools
        }
    !ratifySig = RatifySignal dpProposals
    !ratifyState =
      RatifyState
        { rsEnactState = dpEnactState
        , rsEnacted = mempty
        , rsExpired = mempty
        , rsDelayed = False
        }
    !ratifyState' = runConwayRatify dpGlobals ratifyEnv ratifyState ratifySig
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

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/ImpTest.hs (L1602-1614)
```haskell
isDRepExpired ::
  (HasCallStack, ConwayEraCertState era) =>
  Credential DRepRole ->
  ImpTestM era Bool
isDRepExpired drep = do
  vState <- getsNES $ nesEsL . esLStateL . lsCertStateL . certVStateL
  currentEpoch <- getsNES nesELL
  case Map.lookup drep $ vState ^. vsDRepsL of
    Nothing -> error $ unlines ["DRep not found", show drep]
    Just drep' ->
      pure $
        binOpEpochNo (+) (vState ^. vsNumDormantEpochsL) (drep' ^. drepExpiryL)
          < currentEpoch
```

**File:** eras/conway/impl/testlib/Test/Cardano/Ledger/Conway/Imp/EpochSpec.hs (L188-219)
```haskell
    -- https://github.com/IntersectMBO/formal-ledger-specifications/issues/923
    -- TODO: Re-enable after issue is resolved, by removing this override
    disableInConformanceIt "expiry is not updated for inactive DReps" $ do
      let
        drepActivity = 2
      modifyPParams $ \pp ->
        pp
          & ppGovActionLifetimeL .~ EpochInterval 2
          & ppDRepActivityL .~ EpochInterval drepActivity
      (drep, _, _) <- setupSingleDRep 1_000_000
      startEpochNo <- getsNES nesELL
      let
        -- compute the epoch number that is an offset from starting epoch number plus
        -- the ppDRepActivity parameter
        offDRepActivity offset =
          addEpochInterval startEpochNo $ EpochInterval (drepActivity + offset)

      expectNumDormantEpochs 0

      -- epoch 0: we submit a proposal
      submitParamChangeProposal
      passNEpochsChecking 2 $ do
        expectNumDormantEpochs 0
        expectDRepExpiry drep $ offDRepActivity 0

      passEpoch -- entering epoch 3
      -- proposal has expired
      -- drep has expired
      expectNumDormantEpochs 1
      expectDRepExpiry drep $ offDRepActivity 0
      expectActualDRepExpiry drep $ offDRepActivity 1
      isDRepExpired drep `shouldReturn` False -- numDormantEpochs is added to the drep exiry calculation
```
