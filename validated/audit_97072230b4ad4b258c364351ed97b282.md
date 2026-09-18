## Finding

### Title
Permanent DOS of swap, deposit, and withdraw via unrecoverable `checked_sub` on accumulated PnL accounting - (File: `program/src/math.rs`, `program/src/processor.rs`)

### Summary
The Raydium AMM program tracks protocol-owed PnL in `amm.state_data.need_take_pnl_pc` / `need_take_pnl_coin`, an accumulator that only ever grows (via `calc_take_pnl`) and is only ever reset by the privileged `WithdrawPnl` instruction. Every core, unprivileged user instruction — `process_swap_base_in`, `process_swap_base_out`, `process_deposit`, and `process_withdraw` — begins by computing the "real" pool reserves through `Calculator::calc_total_without_take_pnl_no_orderbook`, which performs an unguarded `checked_sub` of this accumulator against the live vault balance and hard-errors with `AmmError::CheckedSubOverflow` if it ever exceeds the vault balance. [1](#0-0) 

This is structurally the same bug class as the Reserve report: a monotonically-mutated piece of state is subtracted from a live balance with no fallback, and that subtraction gates every primary user-facing action, so any divergence between the tracked accumulator and the actual vault balance freezes the entire pool permanently — with no unprivileged recovery path.

### Finding Description
`calc_take_pnl` increases `need_take_pnl_pc`/`need_take_pnl_coin` on essentially every swap, deposit, and withdraw that doesn't happen while the pool is `WithdrawOnly`: [2](#0-1) 

The only path that decreases these accumulators back toward zero is `process_withdrawpnl`, gated to `amm_config.pnl_owner` / `config_feature::amm_owner::ID` — i.e., a privileged actor, not the unprivileged swapper/LP that the scope restricts this analysis to: [3](#0-2) 

Crucially, `process_withdrawpnl` itself calls the exact same `calc_total_without_take_pnl_no_orderbook` before it can zero out the accumulator: [4](#0-3) 

So if `need_take_pnl_pc`/`need_take_pnl_coin` ever exceeds the vault's actual token balance for any reason (rounding drift across the repeated `normalize_decimal_v2`/`restore_decimal` conversions in `calc_take_pnl`, or any other divergence between tracked and real balances), then:
- `swap_base_in` / `swap_base_out` revert at their initial `calc_total_without_take_pnl_no_orderbook` call.
- `deposit` reverts at the same call.
- `withdraw` reverts at the same call.
- `withdrawpnl` — the only instruction capable of resetting the accumulator — also reverts at the same call, closing off the sole recovery path. [5](#0-4) [6](#0-5) 

This exactly mirrors the referenced Reserve issue: `RToken.issueTo`/`RToken.redeemTo` call `furnace.melt()` unguarded, and once `totalSupply` dips too low the melt reverts, permanently freezing `issue`. Here, every core AMM instruction is unconditionally gated on a `checked_sub` against an accumulator with no unprivileged (or even privileged, given the same gate applies to `withdrawpnl`) recovery mechanism.

### Impact Explanation
If the `need_take_pnl_*` accumulator ever exceeds actual vault reserves, the pool becomes permanently unusable: no swaps, no new deposits, no LP withdrawals, and even the admin-only PnL sweep is blocked by the identical check. All funds locked in the coin/pc vaults and any outstanding LP positions become frozen indefinitely, since there is no code path that resets or bypasses `need_take_pnl_pc`/`need_take_pnl_coin` other than the same gated computation.

### Likelihood Explanation
The accumulator is updated on essentially every trade (`calc_take_pnl` runs in swap/deposit/withdraw paths) using fixed-point decimal conversions (`normalize_decimal_v2`/`restore_decimal`) that involve repeated integer division. While each individual step's floor-division tends to be conservative, the analog to the Reserve report is present at the structural level — the *unguarded, un-fallback-able* `checked_sub` used as a gate on all core operations, identical in shape to Furnace's `melt()` gate on `issue`/redeem. Establishing the precise numeric sequence needed to force the accumulator past the real balance in this program would require deeper simulation across many swaps/decimal configurations than can be confirmed here, so confidence in immediate exploitability is lower than in the original report, which had a concrete 5-step PoC.

### Recommendation
Wrap the `calc_total_without_take_pnl_no_orderbook` result (or the `need_take_pnl_*` subtraction specifically) in a saturating/clamped calculation instead of a hard `checked_sub` that errors, at minimum within `process_withdrawpnl`, so that the privileged recovery path can never itself be bricked. Additionally, consider clamping `need_take_pnl_pc`/`need_take_pnl_coin` to the live vault balance whenever it is read, so a stale/drifted accumulator degrades gracefully instead of permanently halting swap/deposit/withdraw.

### Proof of Concept
A full deterministic PoC would require driving `amm.state_data.need_take_pnl_pc` or `need_take_pnl_coin` (accumulated across repeated `calc_take_pnl` calls during ordinary swaps/deposits/withdraws) above the corresponding vault's real SPL token balance, then observing that:
1. `swap_base_in`/`swap_base_out` revert via `Calculator::calc_total_without_take_pnl_no_orderbook` → `AmmError::CheckedSubOverflow` (`program/src/math.rs:243-248`, called from `program/src/processor.rs:1940-1945`).
2. `deposit` and `withdraw` revert at the same call site (`program/src/processor.rs:1148-1153`, `1719-1724`).
3. `withdrawpnl`, the only privileged path meant to zero the accumulator, also reverts at the identical call site (`program/src/processor.rs:1458-1464`), leaving no recovery path.

I was not able to construct the exact numeric sequence (decimals, fee parameters, swap sizes) that forces the accumulator past real reserves within the scope of this analysis; this would need dedicated simulation/testing against the `Calculator::calc_take_pnl` rounding behavior across many iterations.

### Citations

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

**File:** program/src/processor.rs (L244-262)
```rust
            if pc_pnl_amount != 0 && coin_pnl_amount != 0 {
                amm.state_data.need_take_pnl_pc = amm
                    .state_data
                    .need_take_pnl_pc
                    .checked_add(pc_pnl_amount)
                    .unwrap();
                amm.state_data.need_take_pnl_coin = amm
                    .state_data
                    .need_take_pnl_coin
                    .checked_add(coin_pnl_amount)
                    .unwrap();

                // step3: update total_coin and total_pc without pnl
                *total_pc_without_take_pnl = (*total_pc_without_take_pnl)
                    .checked_sub(pc_pnl_amount)
                    .unwrap();
                *total_coin_without_take_pnl = (*total_coin_without_take_pnl)
                    .checked_sub(coin_pnl_amount)
                    .unwrap();
```

**File:** program/src/processor.rs (L1406-1411)
```rust
        if !pnl_owner_info.is_signer
            || (*pnl_owner_info.key != config_feature::amm_owner::ID
                && *pnl_owner_info.key != amm_config.pnl_owner)
        {
            return Err(AmmError::InvalidSignAccount.into());
        }
```

**File:** program/src/processor.rs (L1458-1464)
```rust
        // calc the remaining total_pc & total_coin
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1719-1724)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1940-1945)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```
