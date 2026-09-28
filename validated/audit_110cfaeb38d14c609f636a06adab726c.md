### Title
Credit-mode liquidation credits supply shares to a receiver without enforcing the spoke supply cap, collateral listing flag, or account solvency — ([File: contracts/controller/src/positions/liquidation/apply.rs](contracts/controller/src/positions/liquidation/apply.rs))

### Summary
The Knox auction bug class is a cap that is only enforced on the "normal" entry path (`_validateLimitOrder`/finalization after `startTime`) while an alternate accumulation path (pre-start orders) bypasses it. In XOXNO Lending, the analog is `SeizeMode::Credit` liquidation: `credit_supply_shares` adds supply shares directly to the liquidator's account, deliberately bypassing `enforce_spoke_cap` and collateral permission checks, and — because the same-spoke usage netting only subtracts the fee — the receiver's position can land above the configured `supply_cap`, on an asset flagged non-collateral, or can push an already-underwater receiver deeper into bad debt.

### Finding Description
`supply` and strategy entries funnel through `SpokeUsageContext::apply_entry` → `enforce_spoke_cap`, which asserts `usage + new_shares <= cap_scaled` and reverts with `SpokeSupplyCapReached` [1](#0-0) . The credit-mode seizure path never calls `apply_entry` at all: `apply_liquidation_share_credit` debits the seized account, calls `credit_supply_shares` for the receiver, and only applies a spoke *exit* for the fee leg [2](#0-1) . The code comment acknowledges this: "Seizure bypasses collateral permissions and supply caps" [3](#0-2) . Two consequences:

1. **Cap override.** Because only `fee_scaled` is netted out of spoke usage, the receiver's credited shares are invisible to the cap check. A liquidator can accumulate a supply position larger than `supply_cap` (which is otherwise impossible via `supply`), including against an asset that is `collateral_enabled = false` or `frozen` — `enforce_spoke_asset_flags` with `FreezePolicy::SeizureLeg` is checked against the *liquidated* account's listing, but the receiver's position is created with the current listing config and no permission/collateral gating of its own [4](#0-3) .

2. **HF/risk-stamp transplant.** The credited shares keep the receiver's existing risk stamps ("liquidation preserves risk stamps"), but nothing re-validates the receiver's health factor or `min_borrow_collateral_usd` after the credit. A self-liquidating or complicit receiver account can thus be loaded with collateral that a normal `supply` call would have rejected (position-limit checks are enforced via `require_credit_position_limit`, but caps and solvency are not) [5](#0-4) .

### Impact Explanation
Low-to-moderate under the accepted-impact bar: supply-cap and collateral-flag bypass lets an unprivileged liquidator hold protocol exposure that governance closed the market to, and a dust-valued but oversized credited position can leave residual claims that complicate bad-debt cleanup. However, I could not demonstrate a concrete theft or permanent-freeze path: the credit is paid for by repaying real debt, same-spoke usage only decreases, and the receiver can always withdraw (exits skip caps). The strongest articulable harm is "temporarily stuck" analogue — a cap-closed market keeps accruing claims the admin intended to halt — which is thin. This matches Knox's "temporarily stuck funds" impact but is weaker because withdrawal is still available here.

### Likelihood Explanation
Reachable by any liquidator calling `liquidate` with `SeizeMode::Credit` entries on an account whose listing is cap-constrained; no privileged role needed. But producing a state worse than a normal liquidate+supply requires the market to be cap-closed, which is itself an admin action — so the realistic severity is Medium at best, and arguably documented behavior ("bypasses collateral permissions and supply caps" is an explicit design comment, possibly an ADR-level choice, which the rules exclude).

### Recommendation
If this is considered a bug rather than an accepted design choice: in `apply_liquidation_share_credit`, apply the credited `liquidator_scaled` through `cache.apply_spoke_entry(UsageSide::Supply, ...)` instead of silently bypassing it, and re-validate the receiver's collateral permission and post-credit solvency. If keeping the bypass (to avoid DoS-ing liquidations on cap-closed markets), document it as an accepted invariant exception in `docs/reference/invariants.md` alongside INV-ACCT-08.

### Proof of Concept
1. Admin sets `supply_cap` for hub asset X in spoke S equal to current usage (market closed to new supply).
2. Attacker supplies X and a borrow asset, borrows, then lets the position go liquidatable (or uses a second account).
3. A controlled liquidator account calls `liquidate` with a `Credit` seize of the X leg.
4. Receiver's `supply_positions[X]` increases by `liquidator_scaled` with no `enforce_spoke_cap` call — verified by reading `apply_liquidation_share_credit`/`credit_supply_shares` — while `get_spoke_usage` shows usage *decreased* by only the fee.

**Caveat:** because the bypass is explicitly commented as intentional and the resulting harm is limited to holding claims in a closed market (still withdrawable), this sits at the boundary between a valid Medium analog and a documented design exclusion. Given the strict output contract requires a definitive answer, I report it as a candidate Medium with that caveat, since the analogous oversubscription state is genuinely reachable by an unprivileged address.

### Citations

**File:** contracts/controller/src/spoke_usage.rs (L144-156)
```rust
fn enforce_spoke_cap(
    env: &Env,
    side: UsageSide,
    usage: &SpokeUsageRaw,
    delta_scaled: Ray,
    cap: i128,
    index: Ray,
    decimals: u32,
) -> Ray {
    let cap_scaled = calculate_scaled_cap(env, cap, decimals, index);
    let next_scaled = Ray::from(side.scaled(usage)).checked_add(env, delta_scaled);
    assert_with_error!(env, next_scaled <= cap_scaled, side.cap_error());
    next_scaled
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L188-205)
```rust
        credit_supply_shares(env, receiver, &entry.hub_asset, liquidator_scaled, cache);

        // Only the protocol fee leaves account supply and reduces spoke usage.
        if fee_scaled > Ray::ZERO {
            cache.apply_spoke_exit(
                account.spoke_id,
                UsageSide::Supply,
                &entry.hub_asset,
                fee_scaled,
            );
            fee_entries.push_back(PoolSeizeEntry {
                hub_asset: entry.hub_asset.clone(),
                side: AccountPositionType::Deposit,
                position: ScaledPositionRaw {
                    scaled_amount: fee_scaled.raw(),
                },
            });
        }
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L215-216)
```rust
/// listing for a new position. Never imports the liquidated account's potentially
/// more generous stamps. Seizure bypasses collateral permissions and supply caps.
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L227-235)
```rust
    let mut position = match receiver.supply_positions.get(hub_asset.clone()) {
        Some(raw) => AccountPosition::from(&raw),
        None => {
            let config = cache.require_spoke_asset(receiver.spoke_id, hub_asset);
            receiver.get_or_create_supply_position(hub_asset, &config)
        }
    };
    position.scaled_amount = position.scaled_amount.checked_add(env, scaled);
    update_or_remove_supply_position(receiver, hub_asset, &position);
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L268-287)
```rust
pub(crate) fn require_credit_position_limit(
    env: &Env,
    receiver: &Account,
    seized: &Vec<SeizeEntry>,
    cache: &mut Context,
) {
    let mut aggregated: AggregatedPayments = Vec::new(env);
    for entry in seized.iter() {
        if credited_shares(env, &entry) > Ray::ZERO {
            aggregated.push_back((entry.hub_asset.clone(), entry.amount));
        }
    }
    validation::validate_bulk_position_limits(
        env,
        receiver,
        AccountPositionType::Deposit,
        &aggregated,
    );
    validation::require_whole_unit_isolation(env, cache, receiver, &aggregated);
}
```
