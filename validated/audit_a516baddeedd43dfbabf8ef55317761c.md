### Title
One-base-unit flash/strategy fee floor overcharges low-decimal markets - (File: `contracts/pool/src/ops/strategy.rs`)

### Summary
Charged strategy openings and flash loans apply a positive configured fee with a minimum of one asset base unit, independent of the asset’s decimals or USD value. [1](#0-0)  On a valid 3-decimal high-value market, that floor can turn a small configured BPS fee into an effective fee of 10% or even 100%. [2](#0-1) 

### Finding Description
The protocol allows listed assets with as few as zero decimals and allows borrowable/flash-loanable markets at three decimals or more. [2](#0-1)  `MarketParamsRaw::verify` enforces that decimal minimum only for flash-loanable markets and does not require the fee floor to be economically meaningful for each asset. [3](#0-2) 

Charged strategies compute their fee from the market’s `flashloan_fee` BPS through `Bps::flash_loan_fee_on` and do not consult `is_flashloanable`. [4](#0-3)  The shared fee formula rounds a positive-rate fee up to one base unit when the proportional amount would otherwise be zero. [1](#0-0) 

The strategy then mints debt for the gross `amount`, books `fee` as protocol revenue, and transfers only `amount - fee` to the receiver. [5](#0-4)  The only bound is `fee <= amount`, so a one-base-unit fee is allowed to consume the entire proceeds of a one-unit borrow. [6](#0-5) 

### Impact Explanation
For a 3-decimal asset worth $100,000 per whole token, one base unit is worth $100. [7](#0-6)  With a configured `flashloan_fee` of 5 BPS, borrowing 10 base units should pay a proportional fee that rounds to zero, but the floor charges 1 base unit: an effective 10% fee, 200 times the configured rate. [1](#0-0) 

Borrowing 1 base unit charges 1 base unit, leaves `amount_received == 0`, and still mints 1 base unit of debt plus subsequent interest. [8](#0-7)  The excess over the configured percentage is permanently retained as protocol revenue while the user remains liable for the gross debt, constituting loss of user funds through an unintended fee floor. [9](#0-8) 

### Likelihood Explanation
The condition only requires a valid low-decimal market and any positive `flashloan_fee` below the allowed 500 BPS cap. [10](#0-9)  An unprivileged user can reach the charged path through `multiply`, whose pool action supplies the debt `hub_asset` and `amount`, or through a direct flash loan where `terms` computes the same floored fee before collecting `amount + fee`. [11](#0-10) [12](#0-11) 

### Recommendation
Remove the absolute one-base-unit minimum from `flash_loan_fee_on`, or replace it with a USD/WAD-denominated minimum that uses the asset’s decimals and oracle price. [6](#0-5)  If dust collection is intentionally blocked, return zero instead of charging a minimum that can exceed the configured BPS rate or consume all proceeds. [1](#0-0) 

### Proof of Concept
1. Configure a borrowable market for a 3-decimal token valued at $100,000 per whole token with `flashloan_fee = 5` BPS; both the decimals and fee are within protocol bounds. [7](#0-6) [10](#0-9) 
2. Open a charged strategy through `multiply` with debt `amount = 10` base units; `compute_fee` calls `flash_loan_fee_on` and receives `1` base unit rather than the proportional 5-BPS value rounded to zero. [11](#0-10) [6](#0-5) 
3. The pool mints debt for 10 base units, books 1 base unit as revenue, and sends only 9 base units to the strategy receiver, producing an effective 10% fee instead of 0.05%. [8](#0-7) 
4. Repeating with `amount = 1` yields `fee = 1`, `amount_received = 0`, and a gross debt obligation of 1 base unit because `fee <= amount` still passes. [13](#0-12)

### Citations

**File:** docs/reference/formulas.md (L419-420)
```markdown
Flash-loan and charged strategy fees are half-up BPS of principal, with a
minimum of one base unit for a positive rate. Flash position has no origination
```

**File:** common/src/constants/shared.rs (L19-24)
```rust
/// Minimum allowed market / listed-token decimals (governance + price-aggregator).
pub const MIN_ASSET_DECIMALS: u32 = 0;

/// Minimum decimals for a market listed as borrowable in any spoke.
pub const MIN_BORROWABLE_ASSET_DECIMALS: u32 = 3;

```

**File:** common/src/types/pool.rs (L64-77)
```rust
    /// Validates `asset_decimals` and the rate model. Panics if `asset_decimals` exceeds
    /// `WAD_DECIMALS`, if a market below `MIN_BORROWABLE_ASSET_DECIMALS` is
    /// flash-loanable, or if the rate model fails its own checks.
    pub fn verify(&self, env: &Env) {
        assert_with_error!(
            env,
            self.asset_decimals <= WAD_DECIMALS,
            CollateralError::AssetDecimalsTooHigh
        );
        assert_with_error!(
            env,
            !self.is_flashloanable || self.asset_decimals >= MIN_BORROWABLE_ASSET_DECIMALS,
            CollateralError::InvalidBorrowParams
        );
```

**File:** common/src/types/pool.rs (L215-224)
```rust
        assert_with_error!(
            env,
            i128::from(self.reserve_factor) < BPS,
            CollateralError::InvalidReserveFactor
        );
        assert_with_error!(
            env,
            i128::from(self.flashloan_fee) <= MAX_FLASHLOAN_FEE_BPS,
            CollateralError::InvalidBorrowParams
        );
```

**File:** contracts/pool/src/ops/strategy.rs (L58-100)
```rust
pub(crate) fn accounting(env: &Env, action: PoolAction, charge_fee: bool) -> StrategyOutcome {
    let PoolAction {
        position,
        amount,
        hub_asset,
    } = action;
    require_nonneg_amount(env, amount);

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

    cache.commit();
    let mutation = cache.strategy_mutation(position, amount, amount_to_send);
    StrategyOutcome {
        cache,
        mutation,
        fee,
    }
}

/// Computes the strategy fee from `flashloan_fee` bps when `charge_fee` is true;
/// returns 0 otherwise (does not consult the market flash-loan enable flag).
///
/// Panics if the fee would exceed principal when charging.
fn compute_fee(env: &Env, cache: &Cache, amount: i128, charge_fee: bool) -> i128 {
    if !charge_fee {
        return 0;
    }
    let fee = Bps::from(i128::from(cache.params().flashloan_fee)).flash_loan_fee_on(env, amount);
    assert_with_error!(env, fee <= amount, FlashLoanError::StrategyFeeExceeds);
    fee
```

**File:** contracts/pool/src/ops/flash.rs (L106-120)
```rust
/// Computes fee and expected pool balances from the pre-loan token balance.
pub(crate) fn terms(env: &Env, amount: i128, fee_bps: u32, pre_balance: i128) -> FlashTerms {
    let fee = Bps::from(i128::from(fee_bps)).flash_loan_fee_on(env, amount);
    FlashTerms {
        fee,
        total_repayment: amount
            .checked_add(fee)
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow)),
        balance_after_payout: pre_balance
            .checked_sub(amount)
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow)),
        balance_after_repayment: pre_balance
            .checked_add(fee)
            .unwrap_or_else(|| panic_with_error!(env, GenericError::MathOverflow)),
    }
```
