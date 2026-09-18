## Analog Found

### Title
Unchecked `U128::as_u64()` downcast in `swap_base_out`/`swap_base_out_v2` truncates the fee-inclusive input amount, letting a swapper pay far less than required while draining pool reserves - (File: `program/src/processor.rs`)

### Summary
`process_swap_base_out` and `process_swap_base_out_v2` compute the amount a swapper must actually deposit (`swap_in_after_add_fee`) using `U128` (128-bit) arithmetic and then convert the result down to `u64` with the raw `.as_u64()` method instead of the crate's own checked helper `Calculator::to_u64()` (which uses `try_into()` and returns `AmmError::ConversionFailure` on overflow). This mirrors the reported Tokensoft `Distributor.sol` issue: a downcast (`uint120(_totalAmount)` there, `.as_u64()` here) that can silently truncate instead of failing, and the validation that exists is performed on the wrong/insufficient value.

### Finding Description
`Calculator::swap_token_amount_base_out` returns a `U128` value representing the pre-fee input amount: [1](#0-0) 

In `process_swap_base_out`, this `U128` is scaled up by `swap_fee_denominator` and divided by `(swap_fee_denominator - swap_fee_numerator)` and then converted straight to `u64` via `.as_u64()`, with no overflow check on the pre-cast `U128` value: [2](#0-1) 

The identical unchecked pattern is repeated in `process_swap_base_out_v2`: [3](#0-2) 

Elsewhere in the same file, the authors are clearly aware overflow-safe downcasting is required and provide `Calculator::to_u64`, which safely fails via `try_into()`: [4](#0-3) 

But that safe helper is bypassed in the `swap_base_out` paths above in favor of the raw `uint` crate `.as_u64()` accessor, which (per the `uint::construct_uint!` macro used to define `U128`) simply returns the low 64 bits of the value — i.e. it **silently truncates** rather than panicking or erroring when the value does not fit in 64 bits: [5](#0-4) 

After the truncated `swap_in_after_add_fee` is computed, it is used directly to (a) validate the swapper has sufficient balance, (b) enforce the slippage/`max_amount_in` check, and (c) perform the actual token transfer from the swapper into the pool vault — while the pool pays out the full attacker-chosen `swap.amount_out`: [6](#0-5) 

Because every check (`user_source.amount < swap_in_after_add_fee`, `swap.max_amount_in < swap_in_after_add_fee`) is performed against the already-truncated value, none of them protect against the truncation itself — exactly analogous to the reported bug where `require(totalAmount <= type(uint120).max, ...)` checked the already-downcasted variable instead of the pre-cast one.

### Impact Explanation
If the true (untruncated) fee-inclusive input amount exceeds `u64::MAX` (~1.8446744e19), `.as_u64()` wraps it down to a small residual value. The swapper then only needs to hold/transfer that small truncated amount to receive the full, attacker-chosen `swap.amount_out` of pool tokens. This is a direct path to draining pool/LP reserves — unbacked withdrawal of vault funds without paying proportional consideration, i.e. insolvent pool accounting and theft of LP funds.

### Likelihood Explanation
Vault balances (`amm_pc_vault.amount`, `amm_coin_vault.amount`) are `u64` and can approach `u64::MAX` given sufficiently large token supplies/deposits (a swapper or LP can inflate reserves via legitimate `Deposit`/`Initialize2` calls, both reachable by any unprivileged account). The overflow condition (`swap_in_before_add_fee * swap_fee_denominator / (swap_fee_denominator - swap_fee_numerator)` exceeding `u64::MAX`) is only reachable when reserves are already near the `u64` ceiling combined with an aggressive `amount_out`, so likelihood is low-to-moderate under normal usage but concretely reachable for a single, unprivileged, attacker-crafted transaction with chosen `amount_out`/`max_amount_in` once reserves are large enough — matching the sponsor's own acknowledgment in the source report that this "could be a problem for scalability later on."

### Recommendation
Replace the unchecked `.as_u64()` calls in `process_swap_base_out` and `process_swap_base_out_v2` with the existing `Calculator::to_u64()` helper (or `u64::try_from`) and propagate/return `AmmError::ConversionFailure` on failure, so an oversized fee-inclusive input amount aborts the swap instead of silently truncating.

### Proof of Concept
1. Attacker (or in concert with LPs) grows `amm_coin_vault`/`amm_pc_vault` balances so that `total_pc_without_take_pnl`/`total_coin_without_take_pnl` are close to `u64::MAX`.
2. Attacker calls `SwapBaseOut`/`SwapBaseOutV2` with a large `swap.amount_out` such that `swap_in_before_add_fee` (from `Calculator::swap_token_amount_base_out`) scaled by `swap_fee_denominator / (swap_fee_denominator - swap_fee_numerator)` exceeds `u64::MAX` when computed in `U128`.
3. `.as_u64()` at `program/src/processor.rs:2191` (or `:2570`) truncates the value to a small `swap_in_after_add_fee`.
4. The balance and slippage checks at `program/src/processor.rs:2202-2207` pass trivially against the truncated value.
5. `Invokers::token_transfer` at `program/src/processor.rs:2218-2224` pulls only the truncated (small) amount from the attacker, while `Invokers::token_transfer_with_authority` pays out the full attacker-chosen `swap.amount_out` from the pool vault, draining pool/LP funds disproportionately.

### Citations

**File:** program/src/math.rs (L9-16)
```rust
use uint::construct_uint;

construct_uint! {
    pub struct U256(4);
}
construct_uint! {
    pub struct U128(2);
}
```

**File:** program/src/math.rs (L46-48)
```rust
    pub fn to_u64(val: u128) -> Result<u64, AmmError> {
        val.try_into().map_err(|_| AmmError::ConversionFailure)
    }
```

**File:** program/src/math.rs (L327-367)
```rust
    pub fn swap_token_amount_base_out(
        amount_out: U128,
        total_pc_without_take_pnl: U128,
        total_coin_without_take_pnl: U128,
        swap_direction: SwapDirection,
    ) -> U128 {
        let amount_in;
        match swap_direction {
            SwapDirection::Coin2PC => {
                // (x + delta_x) * (y + delta_y) = x * y
                // (coin + amount_in) * (pc - amount_out) = coin * pc
                // => amount_in = coin * pc / (pc - amount_out) - coin
                // => amount_in = (coin * pc - pc * coin + amount_out * coin) / (pc - amount_out)
                // => amount_in = (amount_out * coin) / (pc - amount_out)
                let denominator = total_pc_without_take_pnl.checked_sub(amount_out).unwrap();
                amount_in = total_coin_without_take_pnl
                    .checked_mul(amount_out)
                    .unwrap()
                    .checked_ceil_div(denominator)
                    .unwrap()
            }
            SwapDirection::PC2Coin => {
                // (x + delta_x) * (y + delta_y) = x * y
                // (pc + amount_in) * (coin - amount_out) = coin * pc
                // => amount_out = coin - coin * pc / (pc + amount_in)
                // => amount_out = (coin * pc + coin * amount_in - coin * pc) / (pc + amount_in)
                // => amount_out = coin * amount_in / (pc + amount_in)

                // => amount_in = coin * pc / (coin - amount_out) - pc
                // => amount_in = (coin * pc - pc * coin + pc * amount_out) / (coin - amount_out)
                // => amount_in = (pc * amount_out) / (coin - amount_out)
                let denominator = total_coin_without_take_pnl.checked_sub(amount_out).unwrap();
                amount_in = total_pc_without_take_pnl
                    .checked_mul(amount_out)
                    .unwrap()
                    .checked_ceil_div(denominator)
                    .unwrap()
            }
        }
        return amount_in;
    }
```

**File:** program/src/processor.rs (L2172-2191)
```rust
        let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
            swap.amount_out.into(),
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        );
        // swap_in_after_add_fee * (1 - 0.0025) = swap_in_before_add_fee
        // swap_in_after_add_fee = swap_in_before_add_fee / (1 - 0.0025)
        let swap_in_after_add_fee = swap_in_before_add_fee
            .checked_mul(amm.fees.swap_fee_denominator.into())
            .unwrap()
            .checked_ceil_div(
                (amm.fees
                    .swap_fee_denominator
                    .checked_sub(amm.fees.swap_fee_numerator)
                    .unwrap())
                .into(),
            )
            .unwrap()
            .as_u64();
```

**File:** program/src/processor.rs (L2202-2224)
```rust
        if user_source.amount < swap_in_after_add_fee {
            return Err(AmmError::InsufficientFunds.into());
        }
        if swap.max_amount_in < swap_in_after_add_fee {
            return Err(AmmError::ExceededSlippage.into());
        }
        if swap_in_after_add_fee == 0 || swap.amount_out == 0 {
            return Err(AmmError::InvalidInput.into());
        }

        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
                // deposit source coin to amm_coin_vault
                Invokers::token_transfer(
                    token_program_info.clone(),
                    user_source_info.clone(),
                    amm_coin_vault_info.clone(),
                    user_source_owner.clone(),
                    swap_in_after_add_fee,
                )?;
```

**File:** program/src/processor.rs (L2551-2570)
```rust
        let swap_in_before_add_fee = Calculator::swap_token_amount_base_out(
            swap.amount_out.into(),
            total_pc_without_take_pnl.into(),
            total_coin_without_take_pnl.into(),
            swap_direction,
        );
        // swap_in_after_add_fee * (1 - 0.0025) = swap_in_before_add_fee
        // swap_in_after_add_fee = swap_in_before_add_fee / (1 - 0.0025)
        let swap_in_after_add_fee = swap_in_before_add_fee
            .checked_mul(amm.fees.swap_fee_denominator.into())
            .unwrap()
            .checked_ceil_div(
                (amm.fees
                    .swap_fee_denominator
                    .checked_sub(amm.fees.swap_fee_numerator)
                    .unwrap())
                .into(),
            )
            .unwrap()
            .as_u64();
```
