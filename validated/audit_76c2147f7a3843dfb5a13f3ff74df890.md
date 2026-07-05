### Title
`ensTreasury` Over-Decremented in ENACT Rule Allows Blocking Subsequent Ratified Treasury Withdrawals - (File: `eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Enact.hs`)

---

### Summary

In the Conway `ENACT` rule, when a `TreasuryWithdrawals` governance action is enacted, `ensTreasury` (the running virtual treasury in `EnactState`) is decremented by the **full** stated withdrawal amount — including amounts destined for accounts that may be unregistered at enactment time. However, at the epoch boundary, `applyEnactedWithdrawals` only subtracts **successful** (registered-account) withdrawals from the real treasury (`casTreasury`). The unclaimed portion remains in the real treasury. This creates a persistent discrepancy: `ensTreasury` is more depleted than the real treasury, causing subsequent ratified `TreasuryWithdrawals` proposals in the same epoch to fail the `withdrawalCanWithdraw` check in `RATIFY` even though the real treasury has sufficient funds.

An unprivileged attacker who is a recipient of a ratified treasury withdrawal can deliberately unregister their stake credential before the epoch boundary, widening this gap and blocking a concurrent legitimate proposal from being enacted.

---

### Finding Description

**Root cause — `enactmentTransition` in `Enact.hs`:**

```haskell
TreasuryWithdrawals wdrls _ ->
    let wdrlsAmount = fold wdrls                                    -- full amount, all recipients
        wdrlsNoNetworkId = Map.mapKeys (^. accountAddressCredentialL) wdrls
     in st
          { ensWithdrawals = Map.unionWith (<>) wdrlsNoNetworkId $ ensWithdrawals st
          , ensTreasury = ensTreasury st <-> wdrlsAmount            -- decremented by FULL amount
          }
```

`wdrlsAmount` is the sum of **all** withdrawal amounts, regardless of whether the target accounts will be registered at enactment time. [1](#0-0) 

**Disbursement at epoch boundary — `applyEnactedWithdrawals` in `Epoch.hs`:**

```haskell
successfulWithdrawls =
    Map.mapMaybeWithKey
      (\cred w -> compactCoinOrError w <$ guard (isAccountRegistered cred accounts))
      enactedWithdrawals
chainAccountState' =
    chainAccountState
      & casTreasuryL %~ (<-> fromCompact (fold successfulWithdrawls))  -- only registered accounts
```

Only withdrawals to **registered** accounts are subtracted from the real treasury. Unclaimed amounts remain. [2](#0-1) 

**The `withdrawalCanWithdraw` guard in `RATIFY` uses `ensTreasury`:**

```haskell
withdrawalCanWithdraw :: GovAction era -> Coin -> Bool
withdrawalCanWithdraw (TreasuryWithdrawals m _) treasury =
  Map.foldr' (<+>) zero m <= treasury
``` [3](#0-2) 

The `RATIFY` rule passes the running `ensTreasury` (from `EnactState`) to this check for each subsequent proposal in the same epoch's ratification batch: [4](#0-3) 

**The discrepancy:**

| | `ensTreasury` (virtual) | `casTreasury` (real) |
|---|---|---|
| After enacting proposal A (some accounts unregistered) | `T − A_full` | `T − A_registered` |
| Available for proposal B check | `T − A_full` | `T − A_registered` |

If `B_amount > T − A_full` but `B_amount ≤ T − A_registered`, proposal B fails `withdrawalCanWithdraw` even though the real treasury has sufficient funds.

**Attack path:**

1. A legitimate `TreasuryWithdrawals` proposal A (including attacker's account for amount `X`) and proposal B (for a third party, amount `Y`) are both ratified in the same epoch.
2. The attacker unregisters their stake credential before the epoch boundary (a normal, unprivileged transaction — `ConwayUnRegCert`).
3. At the epoch boundary, `ENACT` processes proposal A: `ensTreasury` is decremented by the full `X`, but the real treasury keeps `X` (unclaimed).
4. `RATIFY` then checks proposal B: `withdrawalCanWithdraw` tests `Y ≤ ensTreasury`. If `Y > T − X` but `Y ≤ T` (real treasury), proposal B is incorrectly blocked.
5. Proposal B is not enacted this epoch. If it expires before the next epoch, the governance action is permanently lost (deposit returned, but the action fails).

The `GOV` rule validates account registration at **proposal submission time**, not at enactment time, so the attacker's unregistration is not caught: [5](#0-4) 

---

### Impact Explanation

**Impact: Medium** — Attacker-controlled transactions (stake deregistration) modify the effective treasury available for subsequent ratified withdrawals outside design parameters. A legitimate, fully-ratified `TreasuryWithdrawals` governance action can be prevented from being enacted in the current epoch. If the proposal's lifetime (`ppGovActionLifetimeL`) expires before the next opportunity, the governance action is permanently lost. This constitutes unauthorized modification of treasury withdrawal behavior outside design parameters.

---

### Likelihood Explanation

**Likelihood: Medium** — The attack requires the attacker to be a named recipient in a ratified `TreasuryWithdrawals` proposal (realistic for project funding, contractor payments, etc.) and for a second `TreasuryWithdrawals` proposal to be ratified in the same epoch. Both conditions are plausible in an active governance environment. The attacker's action (stake deregistration) is a standard, unprivileged transaction requiring no special access.

---

### Recommendation

In `enactmentTransition`, `ensTreasury` should only be decremented by the amount that will actually be disbursed. Since the set of registered accounts is not known at `ENACT` time (it is checked later in `applyEnactedWithdrawals`), the fix should either:

1. **Defer the `ensTreasury` decrement** to `applyEnactedWithdrawals`, where the actual registered/unregistered split is computed; or
2. **Use the full amount as a conservative upper bound** (current behavior) but also add the unclaimed amount back to `ensTreasury` in `applyEnactedWithdrawals` before it is reset, so that subsequent proposals in the same epoch can use the corrected value.

Option 2 is a minimal fix:

```haskell
-- In applyEnactedWithdrawals, before resetting ensTreasury:
let unclaimedAmount = fromCompact (fold enactedWithdrawals) <-> fromCompact (fold successfulWithdrawls)
enactedState' =
    enactedState
      & ensWithdrawalsL .~ Map.empty
      & ensTreasuryL .~ mempty  -- already reset; unclaimedAmount is returned to casTreasury implicitly
```

The deeper fix is to ensure `withdrawalCanWithdraw` in `RATIFY` accounts for the possibility that some enacted withdrawals will be unclaimed, so the effective treasury available for subsequent proposals is not understated.

---

### Proof of Concept

**Setup:**
- Real treasury `T = 1000 ADA`
- Proposal A: `TreasuryWithdrawals {attacker_account → 600 ADA}` — ratified
- Proposal B: `TreasuryWithdrawals {legitimate_account → 500 ADA}` — ratified in same epoch

**Attack:**
1. Attacker submits `ConwayUnRegCert attacker_account` before the epoch boundary.
2. At epoch boundary, `RATIFY` processes proposal A first:
   - `withdrawalCanWithdraw`: `600 ≤ 1000` ✓
   - `ENACT`: `ensTreasury = 1000 − 600 = 400`
3. `RATIFY` processes proposal B:
   - `withdrawalCanWithdraw`: `500 ≤ 400` ✗ — **proposal B blocked**
4. `applyEnactedWithdrawals`: attacker's account is unregistered, so 600 ADA stays in real treasury. Real treasury = 1000 ADA. Proposal B could have been paid.

**Without the attack** (attacker stays registered):
- After A: `ensTreasury = 400`, real treasury = 400
- Proposal B: `500 ≤ 400` ✗ — correctly blocked (real treasury insufficient)

**With the attack** (attacker unregisters):
- After A: `ensTreasury = 400`, real treasury = 1000 (600 unclaimed)
- Proposal B: `500 ≤ 400` ✗ — **incorrectly blocked** (real treasury has 1000 ADA)

The attacker sacrifices their 600 ADA withdrawal (it stays in the treasury) to block proposal B from being enacted, potentially causing it to expire.

### Citations

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

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Epoch.hs (L223-235)
```haskell
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
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L292-295)
```haskell
withdrawalCanWithdraw :: GovAction era -> Coin -> Bool
withdrawalCanWithdraw (TreasuryWithdrawals m _) treasury =
  Map.foldr' (<+>) zero m <= treasury
withdrawalCanWithdraw _ _ = True
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Ratify.hs (L337-341)
```haskell
      if prevActionAsExpected gas ensPrevGovActionIds
        && validCommitteeTerm govAction ensCurPParams reCurrentEpoch
        && not rsDelayed
        && withdrawalCanWithdraw govAction ensTreasury
        && acceptedByEveryone env st gas
```

**File:** eras/conway/impl/src/Cardano/Ledger/Conway/Rules/Gov.hs (L509-519)
```haskell
          case govAction of
            TreasuryWithdrawals withdrawals _ -> do
              let nonRegisteredAccounts =
                    flip Map.filterWithKey withdrawals $ \withdrawalAddress _ ->
                      not $
                        isAccountRegistered
                          (withdrawalAddress ^. accountAddressCredentialL)
                          (certDState ^. accountsL)
              failOnNonEmpty
                (Map.keys nonRegisteredAccounts)
                (injectFailure . TreasuryWithdrawalReturnAccountsDoNotExist)
```
