### Title
DRep Voting Power Inflatable via Live `InstantStake` Snapshot at Epoch Boundary — (`eras/conway/impl/src/Cardano/Ledger/Conway/Governance.hs`)

---

### Summary

The Conway governance ratification system initializes the `DRepPulser` at each epoch boundary by reading the live `utxosInstantStake` field directly from the current `UTxOState`. This live value — which is updated by every transaction — is stored as `dpInstantStake` and used to compute each DRep's voting power. Because any transaction included in the last block of an epoch is reflected in `utxosInstantStake` before the epoch boundary is processed, an attacker can temporarily inflate a DRep's voting power by sending ADA to a UTxO whose stake reference points to a credential they control, causing a governance action that would otherwise fail ratification to be enacted, and then recovering the ADA in the next epoch.

---

### Finding Description

At the epoch boundary, `setFreshDRepPulsingState` is called to initialize a fresh `DRepPulser`:

```haskell
-- eras/conway/impl/src/Cardano/Ledger/Conway/Governance.hs
let utxoState   = lsUTxOState ledgerState
    instantStake = utxoState ^. instantStakeG   -- live UTxO-derived stake
    ...
    dpInstantStake = instantStake               -- stored verbatim in the pulser
``` [1](#0-0) 

`utxosInstantStake` is the incremental, live aggregate of all UTxO coin grouped by stake credential. It is updated on every transaction application:

```haskell
utxosInstantStake =
  deleteInstantStake deletedUTxO (addInstantStake utxoAdd (utxos ^. instantStakeL))
``` [2](#0-1) 

`dpInstantStake` is then consumed by `computeDRepDistr`, which adds the UTxO stake for each registered credential to the DRep distribution:

```haskell
go (!drepAccum, !poolAccum) stakeCred accountState =
  let mInstantStake    = Map.lookup stakeCred instantStakeCredentials
      mProposalDeposit = Map.lookup stakeCred proposalDeposits
      stakeAndDeposits = fold $ mInstantStake <> mProposalDeposit
   in ( addToDRepDistr accountState stakeAndDeposits drepAccum, ... )
``` [3](#0-2) 

The resulting `reDRepDistr` is passed to `dRepAcceptedRatio` inside `ratifyTransition`, which decides whether a governance action clears the DRep threshold:

```haskell
&& withdrawalCanWithdraw govAction ensTreasury
&& acceptedByEveryone env st gas   -- calls dRepAccepted → dRepAcceptedRatio
``` [4](#0-3) 

`dRepAcceptedRatio` iterates over `reDRepDistr` to compute `yesStake / totalExcludingAbstainStake`: [5](#0-4) 

**The attack path:**

1. Attacker controls credential `C`, registered and delegated to DRep `D` (which they also control). DRep `D` has voted YES on a `TreasuryWithdrawals` action `G` requiring 51 % DRep stake. Currently DRep `D` holds 49 %.
2. In the last block of epoch N, attacker sends a large amount of ADA to a new UTxO whose `StakeRefBase` points to credential `C`. This is a normal transaction; no special privilege is required.
3. The epoch boundary is processed. `setFreshDRepPulsingState` reads `utxosInstantStake`, which now includes the extra ADA under credential `C`. `dpInstantStake` is set to this inflated value.
4. `computeDRepDistr` adds the extra ADA to DRep `D`'s entry in `dpDRepDistr`. DRep `D` now holds 53 %.
5. `ratifyTransition` evaluates `dRepAccepted` → `True`. Action `G` is enacted; the treasury is drained.
6. In epoch N+1, the attacker spends the UTxO and recovers the ADA.

The rewards system avoids this exact problem by using the two-epoch-old `go` snapshot for reward calculation, providing a stable, manipulation-resistant baseline. The DRep distribution has no equivalent delay — it uses the live `InstantStake` at the current epoch boundary.

Note also that `dpStakePoolDistr` is explicitly marked lazy and sourced from `ssStakeMarkPoolDistr` (the mark snapshot, one epoch old) per ADR-7, creating an inconsistency: SPO voting power uses a delayed snapshot while DRep voting power uses the live value. [6](#0-5) 

---

### Impact Explanation

An attacker with sufficient ADA can cause any governance action — `TreasuryWithdrawals`, `HardForkInitiation`, `UpdateCommittee`, `NoConfidence`, `ParameterChange`, `NewConstitution` — to be ratified and enacted without the genuine consent of the DRep body. This maps directly to:

> **Critical. Unauthorized governance, treasury, protocol-parameter, committee, constitution, or hard-fork action is enacted.**

The most severe concrete outcome is a complete treasury drain in a single epoch boundary. Secondary outcomes include unauthorized hard forks, committee replacement, or constitution changes.

---

### Likelihood Explanation

The attacker needs:
- A registered staking credential delegated to a DRep they control (routine operation).
- Enough ADA to push the DRep's share above the relevant threshold for one epoch boundary.
- The ability to submit a standard transaction in the last block of an epoch (no special access).

Unlike a flash-loan attack, the ADA must be held for at least one block. However, the ADA is fully recoverable in the next epoch, so the net cost is only transaction fees plus the opportunity cost of one block. For a treasury holding billions of ADA, the profit-to-cost ratio is extremely high for a well-capitalised attacker. The attack is deterministic and requires no probabilistic success.

---

### Recommendation

Replace `dpInstantStake` with a stable, epoch-delayed snapshot. Two options:

1. **Use the `mark` snapshot** produced by the `SNAP` rule at the same epoch boundary. The `SNAP` rule already calls `snapShotFromInstantStake` on the same `instantStake`; storing that resolved `ActiveStake` (or the underlying `InstantStake` before resolution) in the pulser instead of the raw live value would be consistent with how `dpStakePoolDistr` is handled.

2. **Use the `set` or `go` snapshot** (one or two epochs old), mirroring the reward-calculation pipeline. This provides a stronger manipulation barrier at the cost of a one- or two-epoch lag in DRep power reflecting new delegations.

At minimum, align `dpInstantStake` with `dpStakePoolDistr` by sourcing it from the same epoch-boundary snapshot rather than the live `utxosInstantStake`.

---

### Proof of Concept

```
Epoch N, last block:
  tx = { inputs  = [some_utxo]
       , outputs = [TxOut { addr  = Addr Mainnet paymentKey (StakeRefBase C)
                          , value = 500_000_000_000 }]  -- 500k ADA
       }
  submit tx

Epoch N boundary:
  setFreshDRepPulsingState reads utxosInstantStake
  → dpInstantStake[C] += 500_000_000_000
  → computeDRepDistr inflates DRep D's entry
  → dRepAcceptedRatio(D) crosses threshold
  → TreasuryWithdrawals action G enacted

Epoch N+1, first block:
  tx2 = { inputs = [output of tx above], outputs = [attacker_wallet] }
  submit tx2   -- ADA recovered, net cost = 2 tx fees
``` [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance.hs (L480-516)
```haskell
  let ledgerState = epochState ^. esLStateL
      utxoState = lsUTxOState ledgerState
      instantStake = utxoState ^. instantStakeG
      certState = lsCertState ledgerState
      dState = certState ^. certDStateL
      vState = certState ^. certVStateL
      govState = epochState ^. epochStateGovStateL
      props = govState ^. cgsProposalsL
      -- Maximum number of blocks we are allowed to roll back: usually a small positive number
      k = securityParameter globals -- On mainnet set to 2160
      numAccounts = Map.size $ dState ^. accountsL . accountsMapL
      pulseSize = max 1 (fromIntegral numAccounts %. (knownNonZero @4 `mulNonZero` toIntegerNonZero k))
      govState' =
        predictFuturePParams $
          govState
            & cgsDRepPulsingStateL
              .~ DRPulsing
                ( DRepPulser
                    { dpPulseSize = floor pulseSize
                    , dpAccounts = dState ^. accountsL
                    , dpIndex = 0 -- used as the index of the remaining UMap
                    , dpInstantStake = instantStake -- used as part of the snapshot
                    , dpStakePoolDistr = stakePoolDistr
                    , dpDRepDistr = Map.empty -- The partial result starts as the empty map
                    , dpDRepState = vsDReps vState
                    , dpCurrentEpoch = epochNo
                    , dpCommitteeState = vsCommitteeState vState
                    , dpEnactState =
                        mkEnactState govState
                          & ensTreasuryL .~ epochState ^. treasuryL
                    , dpProposals = proposalsActions props
                    , dpProposalDeposits = proposalsDeposits props
                    , dpGlobals = globals
                    , dpStakePools = epochState ^. epochStateStakePoolsL
                    }
                )
  pure $ epochState & epochStateGovStateL .~ govState'
```

**File:** docs/reward-calculation/HowRewardCalculationWorks.md (L344-349)
```markdown
  pure $!
    UTxOState
      { utxosUtxo = UTxO newUTxO
      , utxosInstantStake =
          deleteInstantStake deletedUTxO (addInstantStake utxoAdd (utxos ^. instantStakeL))
      }
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/DRepPulser.hs (L200-241)
```haskell
computeDRepDistr ::
  (EraStake era, ConwayEraAccounts era) =>
  InstantStake era ->
  Map (Credential DRepRole) DRepState ->
  Map (Credential Staking) (CompactForm Coin) ->
  PoolDistr ->
  Map DRep (CompactForm Coin) ->
  Map (Credential Staking) (AccountState era) ->
  (Map DRep (CompactForm Coin), PoolDistr)
computeDRepDistr instantStake regDReps proposalDeposits poolDistr dRepDistr =
  Map.foldlWithKey' go (dRepDistr, poolDistr)
  where
    go (!drepAccum, !poolAccum) stakeCred accountState =
      let instantStakeCredentials = instantStake ^. instantStakeCredentialsL
          mInstantStake = Map.lookup stakeCred instantStakeCredentials
          mProposalDeposit = Map.lookup stakeCred proposalDeposits
          stakeAndDeposits = fold $ mInstantStake <> mProposalDeposit
       in ( addToDRepDistr accountState stakeAndDeposits drepAccum
          , addToPoolDistr accountState mProposalDeposit poolAccum
          )
    addToPoolDistr accountState mProposalDeposit distr = fromMaybe distr $ do
      stakePool <- accountState ^. stakePoolDelegationAccountStateL
      proposalDeposit <- mProposalDeposit
      ips <- Map.lookup stakePool $ distr ^. poolDistrDistrL
      pure $
        distr
          & poolDistrDistrL %~ Map.insert stakePool (ips & individualTotalPoolStakeL <>~ proposalDeposit)
          & poolDistrTotalL %~ \t -> unsafeNonZero (unNonZero t <> fromCompact proposalDeposit)
    addToDRepDistr accountState stakeAndDeposits distr = fromMaybe distr $ do
      dRep <- accountState ^. dRepDelegationAccountStateL
      let
        balance = accountState ^. balanceAccountStateL
        updatedDistr = Map.insertWith (<>) dRep (stakeAndDeposits <> balance) distr
      Just $ case dRep of
        DRepAlwaysAbstain -> updatedDistr
        DRepAlwaysNoConfidence -> updatedDistr
        DRepCredential cred
          -- TODO: Potential optimization. Avoid this membership check, since delegation is
          -- guaranteed to exist. I believe it would also be safe for PV9, but we need to verify
          -- that it is in fact true due to #4772
          | Map.member cred regDReps -> updatedDistr
          | otherwise -> distr
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Governance/DRepPulser.hs (L259-263)
```haskell
    , dpInstantStake :: !(InstantStake era)
    -- ^ Snapshot of the stake distr (comes from the IncrementalStake)
    , dpStakePoolDistr :: PoolDistr
    -- ^ Snapshot of the pool distr. Lazy on purpose: See `ssStakeMarkPoolDistr` and ADR-7
    -- for explanation.
```

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
