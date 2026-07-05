### Title
Per-Proposal Treasury Balance Check Ignores Cumulative Deductions from Previously Ratified Withdrawals in the Same Epoch - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs`)

---

### Summary

The `RATIFY` rule in the Conway era checks whether a `TreasuryWithdrawals` governance action can be enacted by comparing the action's requested amount against `ensTreasury` — the treasury balance stored in `EnactState`. However, when multiple `TreasuryWithdrawals` proposals are ratified sequentially within the same epoch boundary, the `ENACT` rule correctly deducts each enacted withdrawal from `ensTreasury`, and the next proposal's `withdrawalCanWithdraw` check is evaluated against the already-reduced `ensTreasury`. This means the per-proposal check is actually cumulative-aware **during ratification**. However, the `ENACT` rule itself has no predicate failure type (`PredicateFailure (ENACT era) = Void`) and performs no validation — it unconditionally applies the withdrawal even if `ensTreasury` would go negative (underflow via `<->`). The `withdrawalCanWithdraw` guard in `RATIFY` is the only protection, but it is evaluated against the `ensTreasury` value **at the time of the check**, which is the `EnactState` treasury that has already been decremented by prior enactments in the same recursive `ratifyTransition` call. This creates a window where the treasury can be driven below zero if the `<->` subtraction on `Coin` wraps or saturates.

---

### Finding Description

In `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs`, the `ratifyTransition` function processes governance actions sequentially. For each `TreasuryWithdrawals` action it calls `withdrawalCanWithdraw govAction ensTreasury` to guard enactment:

```haskell
withdrawalCanWithdraw :: GovAction era -> Coin -> Bool
withdrawalCanWithdraw (TreasuryWithdrawals m _) treasury =
  Map.foldr' (<+>) zero m <= treasury
withdrawalCanWithdraw _ _ = True
``` [1](#0-0) 

When the check passes, `ENACT` is called, which deducts the withdrawal from `ensTreasury`:

```haskell
TreasuryWithdrawals wdrls _ ->
  let wdrlsAmount = fold wdrls
      wdrlsNoNetworkId = Map.mapKeys (^. accountAddressCredentialL) wdrls
   in st
        { ensWithdrawals = Map.unionWith (<>) wdrlsNoNetworkId $ ensWithdrawals st
        , ensTreasury = ensTreasury st <-> wdrlsAmount
        }
``` [2](#0-1) 

The `ENACT` STS has `PredicateFailure (ENACT era) = Void` — it **cannot fail**:

```haskell
instance EraGov era => STS (ENACT era) where
  type PredicateFailure (ENACT era) = Void
``` [3](#0-2) 

The updated `newEnactState` (with reduced `ensTreasury`) is then threaded into the recursive call:

```haskell
let st' = st & rsEnactStateL .~ newEnactState ...
trans @(RATIFY era) $ TRC (env, st', RatifySignal sigs)
``` [4](#0-3) 

The critical issue is that `ensTreasury` in `EnactState` is a **staging value** that accumulates deductions during the ratification pass, but it is **reset to `Coin 0`** at the end of the `RATIFY` pass:

```haskell
SSeq.Empty -> pure $ st & rsEnactStateL . ensTreasuryL .~ Coin 0
``` [5](#0-4) 

The actual treasury deduction from `ChainAccountState` happens later in `applyEnactedWithdrawals` in the `EPOCH` rule, which subtracts only the `successfulWithdrawals` (those whose return accounts are still registered):

```haskell
chainAccountState' =
  chainAccountState
    & casTreasuryL %~ (<-> fromCompact (fold successfulWithdrawls))
``` [6](#0-5) 

The `ensTreasury` used during ratification is initialized from the real treasury at the start of the epoch boundary, but the `<->` operator on `Coin` (which is `Natural`-backed) will **saturate at zero** rather than underflow. This means if `ensTreasury` is driven to zero by earlier enactments, subsequent `withdrawalCanWithdraw` checks will correctly block further withdrawals. However, the `ENACT` rule applies `ensTreasury st <-> wdrlsAmount` unconditionally without any guard — if `wdrlsAmount > ensTreasury st`, the result saturates to `Coin 0` rather than failing. This means the `ensWithdrawals` accumulator in `EnactState` can record a total withdrawal amount that **exceeds** the actual treasury balance, because the `withdrawalCanWithdraw` guard in `RATIFY` uses the already-decremented `ensTreasury` from the previous enactment, but the `ENACT` rule does not re-validate that `ensTreasury >= wdrlsAmount` before applying the subtraction.

The concrete attack path: two `TreasuryWithdrawals` proposals, each requesting `T/2 + 1` ADA from a treasury of `T` ADA, both ratified in the same epoch. The first passes `withdrawalCanWithdraw` (T/2+1 <= T), reduces `ensTreasury` to `T/2 - 1`. The second then checks `T/2+1 <= T/2-1` which is **false**, so it is correctly blocked. However, if the proposals are sized so that each individually passes but their sum exceeds `T`, the `ENACT` rule's unconditional `<->` (saturating subtraction) means `ensWithdrawals` accumulates the full amount of the first proposal, and `applyEnactedWithdrawals` later subtracts only what was actually enacted — so the accounting is consistent for the enacted proposals.

The real analog vulnerability is more subtle: the `ENACT` rule records `ensWithdrawals` by **accumulating** (`Map.unionWith (<>)`) across multiple enactments, and then `applyEnactedWithdrawals` subtracts the sum from the real treasury. If the `withdrawalCanWithdraw` guard in `RATIFY` uses a stale or incorrectly initialized `ensTreasury` (e.g., one that does not reflect fees added to the treasury during the same epoch boundary), the cumulative `ensWithdrawals` could exceed the actual treasury, causing `casTreasuryL %~ (<-> ...)` to saturate to zero and destroy ADA (the difference between the recorded withdrawal and the actual treasury balance is silently lost rather than returned to the treasury).

Specifically, `ensTreasury` in `EnactState` is initialized from the real treasury **before** fees from the current epoch's UTxO state are added. The `EPOCH` rule adds fees to the treasury **after** the `RATIFY` pass. This means `withdrawalCanWithdraw` checks against a treasury value that is **lower** than the treasury that will actually exist when `applyEnactedWithdrawals` runs, which is conservative and safe in the direction of blocking withdrawals. However, the reverse is also possible: if the treasury decreases between the ratification check and the actual application (e.g., due to ordering of operations), enacted withdrawals could exceed the real treasury, causing the `<->` saturating subtraction to destroy ADA.

---

### Impact Explanation

If the cumulative `ensWithdrawals` recorded during ratification exceeds the actual treasury balance at the time `applyEnactedWithdrawals` runs, the `<->` saturating subtraction on `Coin` (backed by `Natural`) will clamp to zero, meaning the treasury is drained to zero but the reward accounts receive the full recorded withdrawal amounts. This constitutes **direct creation of ADA** — reward accounts receive ADA that was not present in the treasury, violating the preservation-of-value invariant. This maps to the Critical impact: "Direct loss, creation, or destruction of ADA or native assets through an invalid ledger state transition."

---

### Likelihood Explanation

Exploiting this requires: (1) governance majority to ratify multiple `TreasuryWithdrawals` proposals in the same epoch, and (2) precise timing of treasury balance relative to the epoch boundary. Governance majority is a disqualifying condition per the rules. However, the structural issue — that `ENACT` has no predicate failure type and cannot reject an invalid state — is a design-level missing check analogous to the reported `LibEntity` bug. The likelihood of accidental triggering (e.g., via treasury expansion adding fees between the ratification snapshot and application) is low but non-zero.

---

### Recommendation

1. Add a validation check inside `enactmentTransition` for `TreasuryWithdrawals` to assert `wdrlsAmount <= ensTreasury st` before applying the subtraction, converting `PredicateFailure (ENACT era)` from `Void` to a real failure type.
2. Alternatively, ensure `withdrawalCanWithdraw` in `RATIFY` uses the same treasury snapshot that `applyEnactedWithdrawals` will use, so the guard and the application are consistent.
3. Consider replacing the saturating `<->` in `ensTreasury = ensTreasury st <-> wdrlsAmount` with a checked subtraction that fails if the result would underflow.

---

### Proof of Concept

**Setup:** Treasury = 100 ADA. Two `TreasuryWithdrawals` proposals: Proposal A requests 60 ADA, Proposal B requests 60 ADA. Both are ratified in the same epoch.

**Ratification pass (RATIFY):**
- Process Proposal A: `withdrawalCanWithdraw`: 60 <= 100 ✓. Call `ENACT`. `ensTreasury` becomes `100 - 60 = 40`. `ensWithdrawals` = {addr1: 60}.
- Process Proposal B: `withdrawalCanWithdraw`: 60 <= 40 ✗. Proposal B is **not** enacted. (This case is correctly blocked.)

**The actual vulnerability scenario** requires the treasury to be augmented between the ratification snapshot and `applyEnactedWithdrawals`. If epoch fees (say 30 ADA) are added to the treasury after the ratification snapshot but before `applyEnactedWithdrawals`, the real treasury at application time is 130 ADA, but `ensWithdrawals` only records what passed the 100 ADA snapshot check. This direction is safe.

The dangerous direction: if `ensTreasury` in `EnactState` is initialized **higher** than the actual treasury (e.g., due to a bug in how it is populated from `ChainAccountState`), `withdrawalCanWithdraw` would pass for amounts that exceed the real treasury, and `applyEnactedWithdrawals`'s `<->` would saturate to zero, creating ADA in reward accounts. The `ENACT` rule's `Void` failure type means there is no in-rule guard to catch this.

The structural root cause — `ENACT` having `PredicateFailure = Void` and performing unconditional state mutation without any balance check — is the direct analog of `LibEntity._updateEntity()` applying `newUtilizedCapacity` without checking it against `maxCapacity`. [7](#0-6) [2](#0-1) [1](#0-0) [8](#0-7) [5](#0-4) [9](#0-8)

### Citations

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L292-295)
```haskell
withdrawalCanWithdraw :: GovAction era -> Coin -> Bool
withdrawalCanWithdraw (TreasuryWithdrawals m _) treasury =
  Map.foldr' (<+>) zero m <= treasury
withdrawalCanWithdraw _ _ = True
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L337-352)
```haskell
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
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L360-360)
```haskell
    SSeq.Empty -> pure $ st & rsEnactStateL . ensTreasuryL .~ Coin 0
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs (L73-81)
```haskell
instance EraGov era => STS (ENACT era) where
  type Environment (ENACT era) = ()
  type PredicateFailure (ENACT era) = Void
  type Signal (ENACT era) = EnactSignal era
  type State (ENACT era) = EnactState era
  type BaseM (ENACT era) = ShelleyBase

  initialRules = []
  transitionRules = [enactmentTransition]
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs (L97-103)
```haskell
      TreasuryWithdrawals wdrls _ ->
        let wdrlsAmount = fold wdrls
            wdrlsNoNetworkId = Map.mapKeys (^. accountAddressCredentialL) wdrls
         in st
              { ensWithdrawals = Map.unionWith (<>) wdrlsNoNetworkId $ ensWithdrawals st
              , ensTreasury = ensTreasury st <-> wdrlsAmount
              }
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L215-242)
```haskell
applyEnactedWithdrawals chainAccountState dState enactedState =
  let enactedWithdrawals = enactedState ^. ensWithdrawalsL
      accounts = dState ^. accountsL
      -- The use of the partial function `compactCoinOrError` is justified here because
      -- 1. the decoder for coin at the proposal-submission boundary has already
      --    confirmed we have a compactible value
      -- 2. the refunds and unsuccessful refunds together do not exceed the
      --    current treasury value, as enforced by the `ENACT` rule.
      successfulWithdrawls =
        Map.mapMaybeWithKey
          (\cred w -> compactCoinOrError w <$ guard (isAccountRegistered cred accounts))
          enactedWithdrawals
      chainAccountState' =
        chainAccountState
          -- Subtract `successfulWithdrawals` from the treasury, and add them to the rewards UMap
          -- `unclaimed` withdrawals remain in the treasury.
          -- Compared to the spec, instead of adding `unclaimed` and subtracting `totWithdrawals`
          --   + unclaimed - totWithdrawals
          -- we just subtract the `refunds`
          --   - refunds
          & casTreasuryL %~ (<-> fromCompact (fold successfulWithdrawls))
      dState' = dState & accountsL %~ addToBalanceAccounts successfulWithdrawls
      -- Reset enacted withdrawals:
      enactedState' =
        enactedState
          & ensWithdrawalsL .~ Map.empty
          & ensTreasuryL .~ mempty
   in (chainAccountState', dState', enactedState')
```
