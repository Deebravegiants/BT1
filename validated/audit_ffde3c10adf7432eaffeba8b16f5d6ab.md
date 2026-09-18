## Title
Missing/Bypassable Slippage Protection in `process_withdraw` (Optional `min_coin_amount`/`min_pc_amount`) - (File: `program/src/processor.rs`)

### Summary
The Raydium AMM `Withdraw` instruction lets the withdrawing user supply optional minimum-out amounts (`min_coin_amount`, `min_pc_amount`) to guard against price movement between transaction submission and execution. Because both fields are `Option<u64>` and the slippage check is only performed when *both* are `Some`, a withdrawal transaction that omits them (or supplies only one) executes with **zero** minimum-output enforcement, exactly the "missing slippage protection" bug class described in the external report (there applied to Bancor's liquidity-removal helpers using a fixed 1-wei floor; here the floor can be entirely absent).

### Finding Description
`WithdrawInstruction` declares the minimum amounts as optional: [1](#0-0) 

The instruction unpacker only populates these fields when the caller includes 16 extra bytes in the instruction data; otherwise both remain `None`: [2](#0-1) 

In `process_withdraw`, the resulting `coin_amount`/`pc_amount` are computed from the pool's current vault balances (which can be moved by any intervening swap in the same slot/block) via `Calculator::calc_total_without_take_pnl_no_orderbook` and the LP-share invariant: [3](#0-2) 

The slippage guard is then applied conditionally — only when **both** `min_coin_amount` and `min_pc_amount` are `Some`: [4](#0-3) 

If a caller (or an SDK/CLI that defaults to no minimums) submits the instruction without these fields, this check is skipped entirely and the withdrawal proceeds with whatever `coin_amount`/`pc_amount` the manipulated pool state yields, then burns the user's LP tokens and transfers out the resulting amounts unconditionally: [5](#0-4) 

This mirrors the reported pattern in `BancorPortal._uniV2RemoveLiquidity` / `BancorV1Migration.migratePoolTokens`, which always pass a fixed 1-wei minimum to third-party liquidity removal — except here the floor is not even a fixed dust value, it is fully absent (`0` effective minimum) whenever the option is omitted.

### Impact Explanation
An attacker observing a pending `Withdraw` transaction in the mempool (or simply trading against the pool before the withdraw lands) can shift the coin/pc vault ratio with a swap immediately before the withdrawal executes, then reverse the trade afterward (a sandwich), capturing value from the withdrawing LP whose transaction has no on-chain floor to reject an unfavorable execution. Because `min_coin_amount`/`min_pc_amount` are optional and the check is bypassed unless both are supplied, LP funds can be extracted via front-running with no protocol-level protection, unlike the swap instructions (`SwapBaseIn`/`SwapBaseOut`) which enforce mandatory `minimum_amount_out`/`max_amount_in`.

### Likelihood Explanation
Any unprivileged user (or any client/SDK integration that does not proactively populate the optional minimums, e.g. defaulting behavior similar to the CLI's `slippage_limit: false` flag noted in `README.md`) can trigger this path in a single transaction with attacker-chosen data; no privileged role is required, and MEV/sandwich bots are a well-established and continuously active threat on any public chain, making exploitation practically certain whenever an unprotected withdrawal is broadcast.

### Recommendation
Make `min_coin_amount` and `min_pc_amount` mandatory (non-`Option`) fields of `WithdrawInstruction`, or enforce the check whenever *either* is `Some` (using a safe default of `0` only as an explicit, intentional opt-out) rather than requiring both to be present before any check runs, so partial/omitted slippage parameters cannot silently disable protection.

### Proof of Concept
1. Attacker monitors the mempool for a `Withdraw` instruction whose packed data omits the trailing 16 bytes (i.e., `min_coin_amount`/`min_pc_amount` unset) — this is valid per the `unpack` logic at [2](#0-1) .
2. Before the withdraw lands, attacker submits a swap that skews `amm_coin_vault`/`amm_pc_vault` balances in their favor.
3. The withdraw executes: `calc_total_without_take_pnl_no_orderbook` and the LP invariant compute `coin_amount`/`pc_amount` off the manipulated reserves [3](#0-2) , and because both minimums are `None`, the guard at [4](#0-3)  never triggers, so the withdrawal completes unconditionally at [5](#0-4) .
4. Attacker reverses the swap, capturing the difference at the withdrawer's expense.

### Citations

**File:** program/src/instruction.rs (L67-75)
```rust
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct WithdrawInstruction {
    /// Pool token amount to transfer. token_a and token_b amount are set by
    /// the current exchange rate and size of the pool
    pub amount: u64,
    pub min_coin_amount: Option<u64>,
    pub min_pc_amount: Option<u64>,
}
```

**File:** program/src/instruction.rs (L372-386)
```rust
            4 => {
                let (amount, rest) = Self::unpack_u64(rest)?;
                let (min_coin_amount, min_pc_amount) = if rest.len() >= 16 {
                    let (min_coin_amount, rest) = Self::unpack_u64(rest)?;
                    let (min_pc_amount, _rest) = Self::unpack_u64(rest)?;
                    (Some(min_coin_amount), Some(min_pc_amount))
                } else {
                    (None, None)
                };
                Self::Withdraw(WithdrawInstruction {
                    amount,
                    min_coin_amount,
                    min_pc_amount,
                })
            }
```

**File:** program/src/processor.rs (L1719-1761)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;

        let x1 = Calculator::normalize_decimal_v2(
            total_pc_without_take_pnl,
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let y1 = Calculator::normalize_decimal_v2(
            total_coin_without_take_pnl,
            amm.coin_decimals,
            amm.sys_decimal_value,
        );

        // calc and update pnl
        let mut delta_x: u128 = 0;
        let mut delta_y: u128 = 0;
        if amm.status != AmmStatus::WithdrawOnly.into_u64() {
            (delta_x, delta_y) = Self::calc_take_pnl(
                &target_orders,
                &mut amm,
                &mut total_pc_without_take_pnl,
                &mut total_coin_without_take_pnl,
                x1.as_u128().into(),
                y1.as_u128().into(),
            )?;
        }

        // coin_amount / total_coin_amount = amount / lp_mint.supply => coin_amount = total_coin_amount * amount / pool_mint.supply
        let invariant = InvariantPool {
            token_input: withdraw.amount,
            token_total: amm.lp_amount,
        };
        let coin_amount = invariant
            .exchange_pool_to_token(total_coin_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
        let pc_amount = invariant
            .exchange_pool_to_token(total_pc_without_take_pnl, RoundDirection::Floor)
            .ok_or(AmmError::CalculationExRateFailure)?;
```

**File:** program/src/processor.rs (L1779-1786)
```rust
        if coin_amount < amm_coin_vault.amount && pc_amount < amm_pc_vault.amount {
            if withdraw.min_coin_amount.is_some() && withdraw.min_pc_amount.is_some() {
                if withdraw.min_coin_amount.unwrap() > coin_amount
                    || withdraw.min_pc_amount.unwrap() > pc_amount
                {
                    return Err(AmmError::ExceededSlippage.into());
                }
            }
```

**File:** program/src/processor.rs (L1787-1812)
```rust
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_dest_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                coin_amount,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_dest_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                pc_amount,
            )?;
            Invokers::token_burn(
                token_program_info.clone(),
                user_source_lp_info.clone(),
                amm_lp_mint_info.clone(),
                source_lp_owner_info.clone(),
                withdraw.amount,
            )?;
            amm.lp_amount = amm.lp_amount.checked_sub(withdraw.amount).unwrap();
```
