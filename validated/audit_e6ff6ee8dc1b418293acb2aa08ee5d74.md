### Title
Third-party supply top-up defeats the bad-debt dust gate, permanently blocking `clean_bad_debt` and front-running `force_socialize_bad_debt` - (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary
The analog of CVE-2022-36289 (a failed protection mechanism enabling denial of service) maps onto the dust-threshold guard for bad-debt socialization. Permissionless `clean_bad_debt` admits an insolvent account only when `total_collateral <= BAD_DEBT_USD_THRESHOLD` ($5 WAD) [1](#0-0) . Any unprivileged address can `supply` additional collateral into a *foreign* account as long as the account already holds a supply position in that hub asset [2](#0-1) . An insolvent account awaiting cleanup always retains residual collateral — that residual is exactly what the dust gate measures — so the attacker can top up that existing leg by a few dollars and flip `is_socializable_bad_debt` to false indefinitely.

### Finding Description
`socialize_bad_debt` loads the account, computes risk totals, and reverts with `CannotCleanBadDebt` when the `DustCapped` gate fails [3](#0-2) . The same gate is applied inside `check_bad_debt_after_liquidation`, so liquidation-driven cleanup is blocked too [4](#0-3) .

Attack path, all permissionless:

1. Victim account becomes insolvent: `total_debt > total_collateral`, collateral e.g. $3 ≤ $5 → `clean_bad_debt` should be callable by anyone.
2. Attacker calls `controller::supply(caller=attacker, account_id=victim, spoke_id=victim_spoke, assets=[(existing_collateral_hub_asset, ~$6)])`. `require_third_party_existing_supply` permits it because the victim already holds that supply position [2](#0-1) ; `supply` has no solvency gate [5](#0-4) .
3. `total_collateral` now exceeds the $5 threshold while `total_debt > total_collateral` still holds. Every `clean_bad_debt` call reverts with `CannotCleanBadDebt` [6](#0-5) .
4. The owner-gated fallback `force_socialize_bad_debt` must go through a Sensitive-tier timelock [7](#0-6) . During the delay the attacker watches the mempool/governance state and re-tops-up just before execution — each re-grief costs only enough dust to push collateral back over $5 — so even the privileged escape is DoS-able on demand.

### Impact Explanation
Bad-debt socialization is the mechanism that writes off uncollectable debt onto the supply index and deletes the dead account [8](#0-7) . While it is blocked, the insolvent debt keeps accruing interest against real suppliers, the account, its NFT and its spoke usage are never released, and the eventual write-down grows. This is a protection-mechanism failure (the dust cap, intended to bound cleanup, becomes the attacker's lever) producing a denial of service of a protocol-critical cleanup path and worsening protocol insolvency — the accepted impact class.

### Likelihood Explanation
Fully reachable by a single unprivileged address: `supply` requires only `caller.require_auth()` and an existing supply slot on the target [9](#0-8) . No timing, flash loan, or oracle manipulation is needed; the preconditions (an insolvent account with residual collateral in a listed asset) arise naturally on every bad-debt event. Cost per grief is ~$5 of the collateral asset, donated to the victim's position — cheap relative to blocking indefinite accrual on arbitrary debt sizes.

### Recommendation
Make the dust gate measure only *pre-existing* residual collateral, not freshly donated amounts. Options: (a) snapshot the collateral value used for the gate before allowing third-party top-ups, or have `clean_bad_debt` first reclassify/seize the residual collateral and then evaluate insolvency on debt alone; (b) restrict third-party `supply` on accounts that are already insolvent (`HF < 1` and `D > C`), since a top-up only delays liquidation anyway; (c) drop the collateral cap entirely for permissionless cleanup when `D > C` holds — the cap exists to protect the residual collateral owner, but on an insolvent account that collateral is already seized as revenue during cleanup.

### Proof of Concept
```
# victim: supply $X collateral in USDC (spoke S, hub H), borrow ETH, price crash
# state: total_collateral = $3, total_debt = $100 → clean_bad_debt ready

# attacker: top up the victim's existing USDC supply leg
controller.supply(
    caller      = ATTACKER,
    account_id  = VICTIM_ID,
    spoke_id    = S,
    assets      = [(HubAssetKey{hub_id: H, asset: USDC}, 6_000_000)],  # ~$6
)
# require_third_party_existing_supply passes: USDC slot already exists
# total_collateral = $9 > $5 threshold, total_debt still > collateral

controller.clean_bad_debt(caller = ANYONE, account_id = VICTIM_ID)
# → panics CollateralError::CannotCleanBadDebt (#114)

# governance proposes ForceSocializeBadDebt; during the Sensitive delay the
# attacker repeats the top-up, so execution reverts again. Repeatable forever
# at ~$5 per round.
```
Supporting gate code: `is_socializable_bad_debt` requires `total_collateral <= BAD_DEBT_USD_THRESHOLD` [1](#0-0)  and the revert site is `assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt)` [3](#0-2) .

### Citations

**File:** contracts/controller/src/positions/liquidation/curve.rs (L25-27)
```rust
pub(crate) fn is_socializable_bad_debt(total_debt: Wad, total_collateral: Wad) -> bool {
    total_debt > total_collateral && total_collateral <= Wad::from(BAD_DEBT_USD_THRESHOLD)
}
```

**File:** contracts/controller/src/positions/supply.rs (L47-61)
```rust
    validation::require_authorized_caller(env, caller);
    let aggregated = payments::aggregate_positive_payments(env, assets);
    let mut cache = Context::new(env);

    let (acct_id, mut account) = account::load_or_create_account(
        env,
        caller,
        account_id,
        spoke_id,
        PositionMode::Normal,
        account::AccountGuard::Supply,
        &mut cache,
    );

    require_third_party_existing_supply(env, account_id, acct_id, caller, &account, &aggregated);
```

**File:** contracts/controller/src/positions/supply.rs (L86-95)
```rust
    if account_id != 0
        && !account::is_owner_or_delegate(env, resolved_account_id, caller, &account.owner)
    {
        for (hub_asset, _) in aggregated.iter() {
            assert_with_error!(
                env,
                account.supply_positions.contains_key(hub_asset.clone()),
                GenericError::NotAuthorized
            );
        }
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L229-237)
```rust
    let admits = match gate {
        BadDebtGate::DustCapped => {
            is_socializable_bad_debt(totals.total_debt, totals.total_collateral)
        }
        BadDebtGate::InsolventOnly => totals.total_debt > totals.total_collateral,
    };
    assert_with_error!(env, admits, CollateralError::CannotCleanBadDebt);

    bad_debt::execute_bad_debt_cleanup(env, &mut cache, account_id, &account, &totals);
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L313-315)
```rust
    if is_socializable_bad_debt(totals.total_debt, totals.total_collateral) {
        bad_debt::execute_bad_debt_cleanup(env, cache, account_id, account, totals);
    }
```

**File:** scripts/permissionless_entrypoints.txt (L69-69)
```text
controller::supply | caller-auth | INV-AUTH-03, INV-ACCT-03 | Anyone may top up an account they do not own, but only for hub assets it already holds a supply position in; a caller that is neither the owner nor an active delegate cannot open a new asset slot, and account_id 0 creates an account owned by the caller.
```

**File:** docs/reference/runbooks/force-socialize-bad-debt.md (L19-22)
```markdown
1. Confirm the network, target controller, governance contract, account id,
   NFT owner, positions and spoke. `force_socialize_bad_debt` is owner-only.
   Governance, the controller owner, schedules `ForceSocializeBadDebt` on the
   Sensitive delay tier; follow the
```

**File:** docs/reference/invariants.md (L463-479)
```markdown
### INV-LIQ-04 — Bad-debt socialization is explicit and total

Permissionless cleanup requires ceil risk debt greater than half-up unweighted
collateral and collateral at or below the fixed $5 dust threshold. Owner-only
forced cleanup omits the dust cap. Both require debt, readable account and NFT
state, valid required prices and no active flash guard. Listing flags and
global pause do not block standalone cleanup.

Cleanup reclassifies all remaining collateral shares as revenue and writes off
all remaining debt against each debt's market. It releases spoke usage and
atomically removes account entries and the NFT. It does not net same-market
supply against debt. Standalone cleanup emits `CleanBadDebtEvent` with
pre-cleanup USD totals, without a controller position-update batch.

Ordinary liquidation and cleanup apply no final account-health or full-backing
assertion. The index floor can leave a shortfall. Recapitalization fills that
shortfall without restoring the lost index or deleted account.
```
