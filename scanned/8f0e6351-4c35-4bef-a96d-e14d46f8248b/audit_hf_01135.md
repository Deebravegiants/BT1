# [H] Ineffective slippage control

## Summary
Severity: High
Reporter: 99Crits
Contest weight: 0.4054
Dataset id: 4801
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The deposit instruction of Lockbox V2 performs insuﬃcient slippage control. This allows an attacker to sandwich the LP deposit for proﬁt and cause the depositor to get much less liquidity than he ought to get. The deposit function takes token_max_a and token_max_b as input parameters:
```rust
pub fn deposit(ctx: Context<DepositPositionForLiquidity>,
    token_max_a: u64,
    token_max_b: u64,
) -> Result<()> {
```
token_max_a is used to calculate the liquidity that will be requested at current prices:
```rust
let sqrt_price_current_x64 = ctx.accounts.whirlpool.sqrt_price;
let sqrt_price_upper_x64 = sqrt_price_from_tick_index(ctx.accounts.position.tick_upper_index);
let liquidity_amount = get_liquidity_from_token_a(token_max_a as u128, sqrt_price_current_x64,
    sqrt_price_upper_x64)?;
```
liquidity_amount is subsequently used to determine the deltas for token A and B:
```rust
let (delta_a, delta_b) = calculate_liquidity_token_deltas(
    tick_index_current,
    sqrt_price_current_x64,
    &ctx.accounts.position,
    liquidity_amount as i128
)?;
```
Those 3 values are then used to invoke the increase_liquidity instruction of ORCAs whirlpool program:
```rust
whirlpool::cpi::increase_liquidity(cpi_ctx_modify_liquidity, liquidity_amount, delta_a, delta_b)?;
```
The issue is that the liquidity that the user requests is determined based on token_max_a at the current onchain price of the pool.
That enables an attacker to sandwich the LP transaction (e.g. using Jito Bundles) doing the following:
1. Buy up a lot of token B.
2. User transaction executes. They will deposit token_max_a and a little amount of token b, due to the skewed prices. However, they will also get much less liquidity accounted for than they intended to.
Looking at the calculation of get_liquidity_from_token_a:
```rust
fn get_liquidity_from_token_a(amount: u128, sqrt_price_lower_x64: u128, sqrt_price_upper_x64: u128 ){
    // liquidity = a * ((sqrt_price_lower * sqrt_price_upper) / (sqrt_price_upper - sqrt_price_lower))
```
sqrt_price_lower will be the current price of the pool (see snippet above) and buy buying up a lot of token B it will be lower. Lower sqrt_price_lower means the numerator decreases while the denominator increases, resulting in lower amount liquidity requested (and received)
3. Sell token B back into the pool and proﬁt due to higher liquidity.

## Recommendation
The deposit instruction should mimic the interface of Orca's increase_liquidity instruction and take an additional liquidity_amount parameter. From a high level perspective, this is what should happen to have proper slippage control:
1. User selects the amount he wants to deposit and a slippage value in percent, e.g. 100 token A, 200 token B and 1.5% max slippage.
2. Frontend (or other client) calculates the liquidity amount that the user should get at current non-manipulated prices.
3. Frontend makes user sign a deposit transaction with the calculated liquidity_amount from step 2 and max_token_a and max_token_b values that account for max acceptable slippage.
4. The lockbox forwards these params to the Orca whirlpool program.
3.2
