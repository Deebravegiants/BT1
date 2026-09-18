### Title
Division by zero panic in `calc_take_pnl` when pool PC (or coin) reserves reach zero - (File: `program/src/processor.rs`)

### Summary
The `SpaceToBatchNd` bug class (unchecked division by an attacker-influenced value that can be zero) has a direct analog in Raydium's PnL-take routine, `Processor::calc_take_pnl`, which is invoked on every `Deposit` and `Withdraw` instruction. The function performs an unchecked `.checked_div(x1).unwrap()` where `x1` is derived from the pool's live PC-vault balance and can become `0`, causing an unrecoverable panic instead of a graceful error.

### Finding Description
`calc_take_pnl` computes `y2` using the current normalized PC reserve `x1` as a divisor: [1](#0-0) 

`x1` is computed from `total_pc_without_take_pnl`, which is the raw PC-vault token balance minus `amm.state_data.need_take_pnl_pc`: [2](#0-1) 

If the live PC vault balance equals `need_take_pnl_pc` exactly (i.e., `total_pc_without_take_pnl == 0`), then `x1 = Calculator::normalize_decimal_v2(0, ...) = 0`. The guard at line 190 (`pool_pc_amount.checked_mul(pool_coin_amount) >= calc_pc_amount.checked_mul(calc_coin_amount)`) does not exclude the zero case — with `pool_pc_amount == 0` the left side is `0`, and the branch is still entered whenever the stored `target.calc_pnl_x`/`calc_pnl_y` values are also `0` or small, which is the normal state directly after `Initialize2` (fresh `TargetOrders` accounts have `calc_pnl_x = calc_pnl_y = 0`). Inside the branch, `y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap()` divides by `x1 = 0`, and `Option::unwrap()` on `None` panics, aborting the transaction.

`calc_take_pnl` is reached from `process_deposit` and `process_withdraw` *before* any subsequent safety checks such as the `amm.lp_amount == 0` guard: [3](#0-2) [4](#0-3) 

Both call sites pass attacker-controllable, on-chain state (the current vault balances, read directly from the token accounts specified in the transaction) into `calc_take_pnl`, with no explicit `x1 != 0` / `y1 != 0` check before the division.

### Impact Explanation
A panic inside `calc_take_pnl` causes the enclosing `Deposit`/`Withdraw` transaction to fail/abort. Because the failure occurs deep in a `.unwrap()` rather than a typed `ProgramError`, it produces an uncontrolled panic instead of a clean revert path, and — depending on when `total_pc_without_take_pnl` (or symmetrically `total_coin_without_take_pnl`, dividing by `x1`/`y1` in the reciprocal path) is driven to `0` — any legitimate LP attempting to `Deposit` or `Withdraw` from that pool would have their transaction reliably fail. If this condition can be induced (e.g., a pool whose PC reserve has been fully skimmed down to the pending PnL amount through the normal pnl/OpenBook take-pnl flow, which is a privileged/administrative path, or through an edge state after `Initialize2`), it results in denial of service against depositors/withdrawers of that pool — a permanent inability to add or remove liquidity is a freezing-of-funds condition for LPs stuck in that pool.

### Likelihood Explanation
The likelihood is **uncertain/edge-case only** and could not be fully proven within the current investigation. Reaching `total_pc_without_take_pnl == 0` (or the coin symmetric case) generally requires the vault's real token balance to exactly equal `need_take_pnl_pc`, which is normally prevented by the `swap.amount_out >= total_pc_without_take_pnl` checks in the swap paths: [5](#0-4) 
That check stops ordinary swaps from ever driving `total_pc_without_take_pnl` to exactly `0`. It was not possible to fully confirm within this pass whether `need_take_pnl_pc`/`need_take_pnl_coin` accounting (updated elsewhere, e.g. `WithdrawPnl` or the take-pnl flow itself) can be driven to exactly equal the vault balance by an unprivileged party through repeated deposit/withdraw/swap sequences, or whether this state is only reachable by a privileged PnL-taking signer, which would put it out of scope per the rules.

### Recommendation
Replace the unchecked `.checked_div(x1).unwrap()` (and the analogous divisions by `y1`/reserve-derived denominators throughout `calc_take_pnl` and `Calculator`) with `checked_div` calls that propagate a typed `AmmError` (e.g., `AmmError::CalculationExRateFailure`) instead of panicking, and add explicit `x1 != U256::zero()` / `y1 != U256::zero()` guards before entering the pnl-adjustment branch in `calc_take_pnl`.

### Proof of Concept
Conceptual PoC (not fully validated against a live reachability path in this pass):
1. Attacker/LP interacts with a pool such that, at the start of a `Deposit` or `Withdraw` instruction, `amm_pc_vault.amount - amm.state_data.need_take_pnl_pc == 0` (equivalently for the coin side).
2. Submit `Deposit`/`Withdraw` — `Processor::calc_take_pnl` computes `x1 = 0`, enters the `pool_pc_amount * pool_coin_amount >= calc_pc_amount * calc_coin_amount` branch (satisfied since the left side is `0`), and executes `x2.checked_mul(y1).unwrap().checked_div(x1).unwrap()`, which panics on the zero divisor and aborts the transaction, blocking further deposits/withdrawals against the pool. Full confirmation of the exact sequence needed to reach the zero-reserve precondition as an unprivileged actor requires further analysis of the `need_take_pnl_pc`/`need_take_pnl_coin` update paths.

### Citations

**File:** program/src/processor.rs (L199-209)
```rust
            let x2_power = Calculator::calc_x_power(
                target.calc_pnl_x.into(),
                target.calc_pnl_y.into(),
                x1,
                y1,
            );
            // let x2 = Calculator::sqrt(x2_power).unwrap();
            let x2 = x2_power.integer_sqrt();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl x2_power:{}, x2:{}", x2_power, x2).as_str());
            let y2 = x2.checked_mul(y1).unwrap().checked_div(x1).unwrap();
            // msg!(arrform!(LOG_SIZE, "calc_take_pnl y2:{}", y2).as_str());
```

**File:** program/src/processor.rs (L1148-1180)
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
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
        let invariant = InvariantToken {
            token_coin: total_coin_without_take_pnl,
            token_pc: total_pc_without_take_pnl,
        };

        // let lp_mint  = Self::unpack_mint(&lp_mint_info, spl_token_program_id)?;
        if amm.lp_amount == 0 {
```

**File:** program/src/processor.rs (L1719-1749)
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
```

**File:** program/src/processor.rs (L2212-2216)
```rust
        match swap_direction {
            SwapDirection::Coin2PC => {
                if swap.amount_out >= total_pc_without_take_pnl {
                    return Err(AmmError::InsufficientFunds.into());
                }
```

**File:** program/src/math.rs (L238-250)
```rust
    pub fn calc_total_without_take_pnl_no_orderbook<'a>(
        pc_amount: u64,
        coin_amount: u64,
        amm: &'a AmmInfo,
    ) -> Result<(u64, u64), AmmError> {
        let total_pc_without_take_pnl = pc_amount
            .checked_sub(amm.state_data.need_take_pnl_pc)
            .ok_or(AmmError::CheckedSubOverflow)?;
        let total_coin_without_take_pnl = coin_amount
            .checked_sub(amm.state_data.need_take_pnl_coin)
            .ok_or(AmmError::CheckedSubOverflow)?;
        Ok((total_pc_without_take_pnl, total_coin_without_take_pnl))
    }
```
