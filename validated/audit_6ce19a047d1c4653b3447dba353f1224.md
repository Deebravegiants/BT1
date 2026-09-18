No vulnerability found for this question.

The Opyn issue concerns a missing validation that a user-supplied `_ethToDeposit` parameter cannot exceed the actual funds available (`msg.value` plus flash-swap proceeds) before it is used in downstream calculations. Searching for the analogous bug class in raydium-amm — instructions where a caller-supplied amount is used without validating it against the actual balance available — shows that this exact check is consistently present across all reachable instructions:

- `process_deposit` explicitly checks `deduct_coin_amount > user_source_coin.amount || deduct_pc_amount > user_source_pc.amount` before transferring, returning `AmmError::InsufficientFunds` [1](#0-0) .
- `process_swap_base_in` (and its `_v2` variant) checks `user_source.amount < swap.amount_in` before computing/transferring the swap [2](#0-1) .
- `process_swap_base_out` checks `user_source.amount < swap_in_after_add_fee` before transferring [3](#0-2) .
- `process_withdraw` checks `withdraw.amount > user_source_lp.amount` and `withdraw.amount >= amm.lp_amount` before burning LP and transferring [4](#0-3) .

Since the bug class described in the report (a caller-supplied amount parameter used without validation against actual available funds) is already guarded against in every unprivileged-reachable instruction (`Deposit`, `Withdraw`, `SwapBaseIn`, `SwapBaseOut`), there is no analogous missing-check vulnerability to report.

### Citations

**File:** program/src/processor.rs (L1319-1322)
```rust
        if deduct_coin_amount > user_source_coin.amount || deduct_pc_amount > user_source_pc.amount
        {
            return Err(AmmError::InsufficientFunds.into());
        }
```

**File:** program/src/processor.rs (L1713-1717)
```rust
        if withdraw.amount > user_source_lp.amount {
            return Err(AmmError::InsufficientFunds.into());
        }
        if withdraw.amount > lp_mint.supply || withdraw.amount >= amm.lp_amount {
            return Err(AmmError::NotAllowZeroLP.into());
```

**File:** program/src/processor.rs (L1957-1969)
```rust
        if user_source.amount < swap.amount_in {
            encode_ray_log(SwapBaseInLog {
                log_type: LogType::SwapBaseIn.into_u8(),
                amount_in: swap.amount_in,
                minimum_out: swap.minimum_amount_out,
                direction: swap_direction as u64,
                user_source: user_source.amount,
                pool_coin: total_coin_without_take_pnl,
                pool_pc: total_pc_without_take_pnl,
                out_amount: 0,
            });
            return Err(AmmError::InsufficientFunds.into());
        }
```

**File:** program/src/processor.rs (L2202-2204)
```rust
        if user_source.amount < swap_in_after_add_fee {
            return Err(AmmError::InsufficientFunds.into());
        }
```
