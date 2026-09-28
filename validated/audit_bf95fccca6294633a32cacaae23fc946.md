### Title
Strategy fee is charged on top of gross debt principal, so borrowers pay interest on funds they never received - (File: contracts/pool/src/ops/strategy.rs)

### Summary
The Astaria finding's bug class — accounting debt on the gross borrow amount while deducting a fee from the payout — exists verbatim in XOXNO Lending's strategy-open path. `ops/strategy.rs::accounting` calls `borrow::mint_debt` for the full `action.amount`, then withholds `fee` from the cash paid out. The position's scaled debt therefore covers `amount`, while the user only ever controls `amount - fee`, and all subsequent borrow-index accrual charges interest on the fee component too.

### Finding Description
In `contracts/pool/src/ops/strategy.rs`:

```rust
let fee = compute_fee(env, &cache, amount, charge_fee);
borrow::mint_debt(env, &mut cache, &mut position, amount);   // debt minted on GROSS amount
let protocol_fee = Ray::from_asset(env, fee, ...);
interest::add_protocol_revenue(&mut cache, protocol_fee);
let amount_to_send = amount.checked_sub(fee)...;
cache.debit_cash(amount_to_send);                            // cash debited only by NET
``` [1](#0-0) 

`mint_debt` converts `amount` into scaled debt shares via `calculate_scaled_borrow` (ceil-rounded) and adds them to `position` and `borrowed`, so the borrower's recorded obligation — and the base on which `borrow_index` accrues interest — is the full `amount`, not the `amount - fee` actually received. [2](#0-1) 

Unprivileged reachability: `process_multiply` calls `borrow_into_controller(env, &mut account, debt, debt_to_flash_loan, true, PositionAction::Multiply, ...)` with `charge_fee` hard-coded `true`, and `process_swap_debt` does the same via `borrow_into_controller(..., new_debt_amount, true, PositionAction::SwDebtR, ...)`. [3](#0-2) [4](#0-3)  These map to `pool.create_strategy(receiver, action, charge_fee)` in the controller's pool client. [5](#0-4)  The fee rate itself is `params.flashloan_fee` bounded by `MAX_FLASHLOAN_FEE_BPS = 500` (5%), an ordinary market parameter — not a misconfiguration. [6](#0-5) 

### Impact Explanation
The borrower repays `amount × borrow_index_growth` but only received `amount − fee`. Concretely, with `flashloan_fee = 500 bps` and a 20% interest accrual period: borrow 100 units → receives 95, owes ≈120 → effective rate ≈ 26.3% instead of 20%. The excess over the intended fee is permanent and grows with the interest rate and time the position stays open. This is a direct, quantifiable overcharge of user funds on every `multiply` and `swap_debt` call whenever `flashloan_fee > 0` — it inflates the borrower's debt base beyond the value actually drawn, matching the "actual interest rate is higher than quoted" impact from the Astaria report.

### Likelihood Explanation
High whenever `flashloan_fee > 0` is configured on a market, which is the normal fee-setting path rather than an edge case. `multiply` is a core leverage entrypoint and `swap_debt` a core refinancing entrypoint; both always pass `charge_fee = true`, so every affected-strategy user pays the inflated rate deterministically. No special timing, oracle state, or attacker setup is required.

### Recommendation
Mint debt only on the amount actually delivered. Compute the fee first, then call `borrow::mint_debt` with `amount - fee` (and keep `debit_cash(amount - fee)` and the revenue accrual unchanged), or equivalently keep minting on `amount` and immediately repay/burn the fee portion. Apply the same fix in `ops/strategy.rs::accounting`; the mirrored certora rule `create_strategy_accounts_debt_cash_and_fee` in `certora/pool/spec/fee_strategy_accounting_rules.rs` currently encodes the buggy expectation (`expected_debt` derived from gross `amount`) and should be updated to assert debt on `amount - expected_fee`. [7](#0-6) 

### Proof of Concept
1. Admin configures a hub market with `flashloan_fee = 500` (5%) and a non-zero borrow rate — standard market setup.
2. User calls controller `multiply` with `debt_to_flash_loan = 1_000` units, sufficient collateral path via `swap`, `mode = Long`.
3. In `pool.create_strategy`: `compute_fee` → `fee = 50`; `mint_debt(amount = 1_000)` mints `ceil(1_000 / borrow_index)` scaled debt; `transfer_out` sends only `950`.
4. After one accrual period at +20% index growth, `repay` requires `ceil(1_000 × 1.2) = 1_200` (plus share rounding), while the user only ever had 950 units of purchasing power. Effective cost ≈ 26.3%, vs. the intended 20% on the 950 received (1_140 owed if debt were minted net).
5. The same applies to `swap_debt`, which also hard-codes `charge_fee = true`.

### Citations

**File:** contracts/pool/src/ops/strategy.rs (L66-79)
```rust
    let mut cache = ops::renewed_market(env, &hub_asset);
    let fee = compute_fee(env, &cache, amount, charge_fee);

    let mut position = Ray::from(position.scaled_amount);
    borrow::mint_debt(env, &mut cache, &mut position, amount);

    let protocol_fee = Ray::from_asset(env, fee, cache.params().asset_decimals);
    interest::add_protocol_revenue(&mut cache, protocol_fee);

    let amount_to_send = amount
        .checked_sub(fee)
        .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow));

    cache.debit_cash(amount_to_send);
```

**File:** contracts/pool/src/ops/strategy.rs (L94-100)
```rust
fn compute_fee(env: &Env, cache: &Cache, amount: i128, charge_fee: bool) -> i128 {
    if !charge_fee {
        return 0;
    }
    let fee = Bps::from(i128::from(cache.params().flashloan_fee)).flash_loan_fee_on(env, amount);
    assert_with_error!(env, fee <= amount, FlashLoanError::StrategyFeeExceeds);
    fee
```

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

**File:** contracts/controller/src/strategies/multiply.rs (L76-84)
```rust
    let amount_received = borrow_into_controller(
        env,
        &mut account,
        debt,
        debt_to_flash_loan,
        true,
        PositionAction::Multiply,
        &mut cache,
    );
```

**File:** contracts/controller/src/strategies/swap_debt.rs (L55-63)
```rust
    let amount_received = borrow_into_controller(
        env,
        &mut account,
        new_debt,
        new_debt_amount,
        true,
        PositionAction::SwDebtR,
        &mut cache,
    );
```

**File:** contracts/controller/src/external/pool.rs (L42-50)
```rust
pub(crate) fn pool_create_strategy_call(
    env: &Env,
    pool_addr: &Address,
    receiver: &Address,
    action: PoolAction,
    charge_fee: bool,
) -> PoolStrategyMutation {
    LiquidityPoolClient::new(env, pool_addr).create_strategy(receiver, &action, &charge_fee)
}
```

**File:** certora/pool/spec/fee_strategy_accounting_rules.rs (L324-345)
```rust
    let expected_debt =
        Ray::from_asset(&e, amount, ASSET_DECIMALS).div_ceil(&e, Ray::from(borrow_index));

    let StrategyOutcome {
        mutation: result,
        fee,
        ..
    } = crate::ops::strategy::accounting(
        &e,
        action(asset.clone(), debt_before, amount),
        charge_fee,
    );
    let post = read_state(&e, &asset);

    cvlr_assert!(fee == expected_fee);
    cvlr_assert!(result.actual_amount == amount);
    cvlr_assert!(result.amount_received == amount - expected_fee);
    cvlr_assert!(result.position.scaled_amount - debt_before == expected_debt.raw());
    cvlr_assert!(post.borrowed - pre.borrowed == expected_debt.raw());
    cvlr_assert!(post.revenue - pre.revenue == expected_fee_shares.raw());
    cvlr_assert!(post.supplied - pre.supplied == expected_fee_shares.raw());
    cvlr_assert!(pre.cash - post.cash == amount - expected_fee);
```
