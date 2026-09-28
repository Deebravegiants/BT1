### Title
Attacker can pin utilization at `max_utilization` to block all supplier withdrawals and revenue claims - (File: contracts/pool/src/guards.rs)

### Summary
`require_utilization_below_max` is an absolute post-state check applied to every non-liquidation `withdraw` and to `claim_revenue`, but `borrow` is allowed to land utilization exactly at the cap. A single unprivileged account can borrow the market up to `max_utilization`, after which interest accrual alone pushes `borrowed × borrow_index` above the cap, permanently reverting every supplier withdrawal and revenue claim until someone repays the attacker's debt.

### Finding Description
In `contracts/pool/src/ops/borrow.rs`, `mint_debt` enforces `require_reserves`, `require_liquidation_buffer` and finally `guards::require_utilization_below_max` after minting the new debt [1](#0-0) . The guard accepts equality: `borrowed.div_ceil(supplied) <= max_utilization` [2](#0-1) .

The same guard runs on every ordinary exit. In `withdraw`, `gate_and_debit` calls `require_utilization_below_max` whenever the withdrawal is not a liquidation and not a footprint-only close [3](#0-2) . The guard recomputes `borrowed` with the freshly accrued `borrow_index` [4](#0-3) , so once utilization drifts above `max_utilization`, withdrawing any amount — even a single base unit that would reduce `supplied` further — reverts with `UtilizationAboveMax` (127). `claim_revenue` is gated the same way per the pool README's guard table, and `update_indexes` accrual is what pushes the market over the edge.

There is no burn-side release valve analogous to Alchemix's missing `increase` on the limiter: the only ways utilization comes back below the cap are (a) permissionless `repay` on the attacker's debt by anyone, (b) liquidation if the attacker's account becomes unhealthy (liquidation withdraws skip the check), or (c) governance raising `max_utilization`. The attacker keeps their account healthy by holding the borrowed tokens as value backing the position, so option (b) only fires from price movement, and option (a) requires a third party to spend their own funds.

### Impact Explanation
Temporary freezing of user funds and unclaimed yield: every supplier in that market is unable to withdraw any of their supply, and `claim_revenue` reverts, for as long as utilization stays at or above the cap. Since borrow interest accrues on the attacker's position, utilization only increases over time, so the freeze is self-sustaining with no ongoing attacker action. Duration is bounded only by an external actor repaying the debt, a liquidation, or a governance parameter change.

### Likelihood Explanation
A single unprivileged address with sufficient collateral executes `controller.borrow` repeatedly (or once sized correctly) until the post-state utilization equals `max_utilization`. The cost is real — collateral must be posted and borrow interest accrues to suppliers — so this is a griefing attack requiring financing, matching the original report's profile. It is cheapest on markets where `optimal_utilization`/`max_utilization` is configured low relative to available cash, and attack capital is amplified because each unit of collateral borrows up to LTV. No flash-loan amplification is needed since the position must be held.

### Recommendation
Apply the utilization cap asymmetrically, or remove it from exits:
- Skip `require_utilization_below_max` for withdrawals up to available cash, or gate it only when the withdrawal itself draws `cash` below reserves (the check is already redundant with `require_reserves` and `require_supply_for_debt` on exit paths).
- Alternatively, enforce `utilization < max_utilization` strictly on `borrow` (e.g., require headroom of at least one accrual interval), so interest drift cannot strand the cap already crossed.
- At minimum, exempt `claim_revenue` from the utilization gate since protocol revenue withdrawal does not worsen supplier backing beyond the booked shortfall.

### Proof of Concept
1. Market listed with `max_utilization = 0.9 × RAY`, cash C, utilization currently below cap.
2. Attacker supplies collateral in another market (or the same market in a different spoke) and calls `controller.borrow` with `amount` sized so post-mint `borrowed × borrow_index / supplied × supply_index == max_utilization` exactly (passes the `<=` check at `guards.rs:31`).
3. Wait one accrual interval and call `update_indexes` (permissionless). `borrowed` grows by the borrow rate; `supplied` grows slower by `1 - reserve_factor`, so utilization now exceeds `max_utilization`.
4. Any supplier calling `controller.withdraw` reverts: `withdraw::accounting → gate_and_debit → require_utilization_below_max` panics `UtilizationAboveMax` (`#127`). `claim_revenue` reverts identically.
5. The freeze persists while utilization ≥ cap; the attacker needs only keep their position above the liquidation threshold by holding the borrowed assets.

### Citations

**File:** contracts/pool/src/ops/borrow.rs (L63-78)
```rust
pub(crate) fn mint_debt(env: &Env, cache: &mut Cache, position: &mut Ray, amount: i128) {
    require_positive_amount(env, amount);
    cache.require_reserves(amount);
    guards::require_liquidation_buffer(env, cache, amount);

    let minted = cache.calculate_scaled_borrow(amount);

    assert_with_error!(
        env,
        minted.raw() > 0,
        GenericError::BorrowRoundsToZeroShares
    );

    *position = position.checked_add(env, minted);
    cache.mint_debt(minted);
    guards::require_utilization_below_max(env, cache);
```

**File:** contracts/pool/src/guards.rs (L19-33)
```rust
pub(crate) fn require_utilization_below_max(env: &Env, cache: &Cache) {
    if cache.supplied() == Ray::ZERO || cache.params().max_utilization >= Ray::ONE {
        return;
    }

    let borrowed = cache.borrowed().mul_ceil(env, cache.borrow_index());
    if borrowed == Ray::ZERO {
        return;
    }
    let supplied = cache.supplied().mul_floor(env, cache.supply_index());
    assert_with_error!(
        env,
        supplied > Ray::ZERO && borrowed.div_ceil(env, supplied) <= cache.params().max_utilization,
        CollateralError::UtilizationAboveMax
    );
```

**File:** contracts/pool/src/ops/withdraw.rs (L111-119)
```rust
fn gate_and_debit(env: &Env, cache: &mut Cache, net_transfer: i128, skip_utilization_check: bool) {
    cache.require_reserves(net_transfer);

    if !skip_utilization_check {
        guards::require_utilization_below_max(env, cache);
    }
    guards::require_supply_for_debt(env, cache);
    cache.debit_cash(net_transfer);
}
```
