### Title
Borrowers can permanently freeze supplier withdrawals and revenue claims by letting utilization drift above `max_utilization` — (`contracts/pool/src/ops/withdraw.rs`)

### Summary
The bug class in the reference report is "a claim is front-run/denied because funds or preconditions no longer hold when it executes." The analog in XOXNO Lending is a utilization lockout: any ordinary `withdraw` — the supplier's claim on deposited principal and yield — reverts with `UtilizationAboveMax` whenever market utilization exceeds `params.max_utilization`. Since interest accrual lets utilization drift above that cap without any new borrows, a single unprivileged borrower who draws utilization to the cap and simply stays healthy can keep every supplier exit and every `claim_revenue` call reverting indefinitely.

### Finding Description
`pool::withdraw` runs `ops::withdraw::accounting`, which calls `gate_and_debit` for every non-liquidation exit. `gate_and_debit` enforces `guards::require_utilization_below_max` unless the call is a liquidation or an empty footprint-only close [1](#0-0) . The guard recomputes utilization as `borrowed * borrow_index (ceil) / supplied * supply_index (floor)` and panics with `UtilizationAboveMax` when it exceeds `max_utilization` [2](#0-1) .

Two properties make this a griefing lock rather than a self-healing one:

1. Withdrawing makes utilization *worse*, not better: burning supply shrinks the denominator, so the post-exit state is exactly the state the gate rejects. Once utilization is above the cap, no supplier can exit through the normal path — each attempt reverts before `debit_cash`.
2. Nothing requires the attacker to act again. `borrow` only needs utilization `<= max_utilization` at mint time; afterwards the borrow index accrues faster than the supply index (reserve factor < 100%), so utilization drifts over the cap on its own via millisecond chunked accrual. The same guard also bricks `claim_revenue`, which calls `require_utilization_below_max` inside `ops::revenue::accounting` [3](#0-2) , and `recapitalize`/other guarded paths, matching the pool README's documented `UtilizationAboveMax` (127) errors on `withdraw` and `claim_revenue` [4](#0-3) .

An unprivileged attacker only needs to: supply collateral, call `controller::borrow` to push utilization to the cap (or near it on a market whose `max_utilization < RAY`), and keep their own health factor above liquidation. Repay by third parties is the only un-stick mechanism, and the attacker can front-run any large repay with a fresh borrow, or simply re-borrow after each repay.

### Impact Explanation
Temporary-to-indefinite freezing of user funds: all suppliers in the affected `(hub, asset)` market are unable to withdraw principal or yield while utilization stays above the cap, and protocol revenue cannot be claimed either. This is a market-wide DoS of the two "claim" surfaces (`withdraw`, `claim_revenue`) reachable by a single unprivileged borrower, analogous to the reference finding's claim denial — except here no privileged owner is needed. Severity Medium: funds are not stolen, and the freeze resolves if the attacker repays or is liquidated, but the attacker controls both levers.

### Likelihood Explanation
High on any market configured with `max_utilization < RAY` (the fixture pins `0.9 RAY`, so capped markets are the intended configuration [5](#0-4) ). The attacker only needs enough collateral to borrow up to the cap — a normal, fully collateralized position that never becomes liquidatable. Accrual does the rest automatically since debt value grows faster than supply value whenever `reserve_factor > 0`. No front-running of a specific victim transaction is even required; the state persists across ledgers.

### Recommendation
Do not gate supplier exits on post-withdraw utilization. Withdrawals strictly reduce utilization pressure in cash terms (cash leaves but the borrowed/supplied ratio is what the cap protects for *new* borrows); the check belongs on `borrow`/`create_strategy`/`flash` debt-minting paths only — consistent with `require_liquidation_buffer`, whose comment already states "Exits do not" [6](#0-5) . Remove `require_utilization_below_max` from `gate_and_debit` (and reconsider it in `ops::revenue::accounting`, where claiming revenue also reduces cash but should not be blocked by borrower inaction), or apply the utilization check only when a withdrawal would newly breach the cap rather than when the cap is already breached.

### Proof of Concept
1. Governance lists market `(hub, USDC)` with `max_utilization = 0.9e27`, `reserve_factor > 0`.
2. Alice supplies 100k USDC (`controller::supply`). Mallory supplies ETH collateral and calls `controller::borrow` for ~90k USDC, pushing utilization to `0.9 RAY`.
3. Time passes (`update_indexes` or any touching call accrues); the borrow index outpaces the supply index, so `borrowed_ceil/supplied_floor > 0.9 RAY`.
4. Alice calls `controller::withdraw`. Pool `withdraw` → `accounting` → `gate_and_debit` → `require_utilization_below_max` reverts with `UtilizationAboveMax` (127). The same revert hits `claim_revenue`.
5. Mallory keeps HF > 1 forever (her debt is the market's debt; her collateral value is independent). Any whale repaying part of her debt is countered by a re-borrow. Alice's funds remain frozen until Mallory chooses to deleverage.

### Citations

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

**File:** contracts/pool/src/guards.rs (L19-34)
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
}
```

**File:** contracts/pool/src/guards.rs (L36-39)
```rust
/// Panics with `InsufficientLiquidity` if drawing `draw` leaves cash below the liquidation buffer.
///
/// Every debt mint checks it, borrows and strategy openings alike (INV-ACCT-07). Exits do not.
pub(crate) fn require_liquidation_buffer(env: &Env, cache: &Cache, draw: i128) {
```

**File:** contracts/pool/src/ops/revenue.rs (L39-47)
```rust
pub(crate) fn accounting(env: &Env, hub_asset: HubAssetKey) -> RevenueOutcome {
    let mut cache = ops::renewed_market(env, &hub_asset);

    let net_transfer = cache.burn_claimable_revenue();

    guards::require_utilization_below_max(env, &cache);
    guards::require_supply_for_debt(env, &cache);
    cache.debit_cash(net_transfer);

```

**File:** contracts/pool/README.md (L141-148)
```markdown
| `withdraw` | `AmountMustBePositive` (14) on a negative amount or fee, `WithdrawRoundsToZeroShares` (49), `WithdrawLessThanFee` (115), `InsufficientLiquidity` (112), `UtilizationAboveMax` (127) on non-liquidation calls, `PoolInsolvent` (123), `InternalError` (34) |
| `repay` | `AmountMustBePositive` (14), `RepayRoundsToZeroShares` (52), `MathOverflow` (33) |
| `net_settle` | `AmountMustBePositive` (14), `NetSettleRoundsToZeroShares` (50), `PoolInsolvent` (123), `InternalError` (34) |
| `seize_positions` | `AmountMustBePositive` (14), `InternalError` (34) |
| `flash_loan` | `AmountMustBePositive` (14), `FlashloanNotEnabled` (401), `InsufficientLiquidity` (112), `InvalidFlashloanReceiver` (412) for a non-Wasm receiver, `InvalidFlashloanRepay` (402) for a short allowance or a balance mismatch |
| `create_strategy` | `AmountMustBePositive` (14) on a negative amount, `StrategyFeeExceeds` (409), plus the whole `borrow` set — it mints debt through the same path |
| `recapitalize` | `AmountMustBePositive` (14) on a negative amount, `MathOverflow` (33) |
| `claim_revenue` | `UtilizationAboveMax` (127), `PoolInsolvent` (123), `OwnerNotSet` (32), `InternalError` (34) |
```

**File:** certora/pool/spec/README.md (L111-111)
```markdown
| `max_utilization` | `RAY` (uncapped) | `optimal_utilization..=RAY` | `params_with_max_util` pins `0.9 RAY` in the two utilization-cap rules |
```
