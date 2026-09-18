## Title
Rebasing/Fee-on-Transfer Token Vault Balance Decrease Causes Permanent DoS via Underflow in `calc_total_without_take_pnl_no_orderbook` - (File: program/src/math.rs)

### Summary
`Calculator::calc_total_without_take_pnl_no_orderbook()` computes the pool's "usable" reserves by subtracting the accrued-but-unwithdrawn PnL (`need_take_pnl_pc` / `need_take_pnl_coin`) from the *current* vault token balance, using `checked_sub` that errors (rather than saturating) if the vault balance ever falls below the accounted PnL amount. This function is invoked on every `Deposit`, `Withdraw`, `WithdrawPnl`, `SwapBaseIn`, `SwapBaseOut` (and their v2 variants) code path. If either the coin or pc mint is a non-standard token (rebasing, fee-on-transfer, or any token whose SPL account balance can decrease without an explicit pool-initiated transfer), the vault's on-chain balance can drop below the previously accounted `need_take_pnl_*` value, causing every subsequent pool instruction to fail permanently.

### Finding Description
`calc_total_without_take_pnl_no_orderbook` is: [1](#0-0) 

It assumes `pc_amount >= amm.state_data.need_take_pnl_pc` and `coin_amount >= amm.state_data.need_take_pnl_coin` always hold, where `pc_amount`/`coin_amount` are the *live* SPL vault balances read directly from the token accounts, and `need_take_pnl_pc`/`need_take_pnl_coin` are PnL amounts accrued in `calc_take_pnl` during prior deposit/withdraw/swap calls (persisted in `AmmInfo.state_data`), reserved for later withdrawal by the pool owner via `process_withdrawpnl`.

This function is called unconditionally at the start of every pool instruction that touches vault balances:
- `process_deposit` [2](#0-1) 
- `process_withdraw` (same pattern, prior to line 1737 pnl calc)
- `process_withdrawpnl` [3](#0-2) 
- `process_swap_base_in` / `process_swap_base_in_v2` [4](#0-3) [5](#0-4) 
- `process_swap_base_out` / `process_swap_base_out_v2` [6](#0-5) [7](#0-6) 

An unprivileged pool creator chooses `coin_mint`/`pc_mint` at `Initialize2` — there is no on-chain check rejecting non-standard ERC20/SPL-equivalent tokens (rebasing, fee-on-transfer, or otherwise balance-shrinking tokens). Once such a token is used as either side of the pool, any external mechanism that decreases the vault's token account balance (rebase down-adjustment, negative-yield accrual, etc., independent of pool-driven transfers) can push the live `amount` below the already-accrued `need_take_pnl_*` counter. Because the subtraction uses `checked_sub(...).ok_or(AmmError::CheckedSubOverflow)?` instead of a saturating/graceful-degradation path, every subsequent call to *any* pool instruction (`Deposit`, `Withdraw`, `WithdrawPnl`, both swap directions) immediately fails with `AmmError::CheckedSubOverflow` [8](#0-7) , because they all invoke this function before doing anything else.

This mirrors the reported bug class exactly: the accounting system assumes token balances only move via tracked transfers and breaks when a non-standard token's balance decreases independently, leaving the protocol unable to reconcile "accounted" vs "actual" balance.

### Impact Explanation
Once the underflow condition is triggered, the pool becomes permanently non-functional: swaps, deposits, withdrawals, and PnL withdrawal all revert unconditionally, since the failing calculation sits at the very top of each handler before any subsequent logic executes. This permanently freezes all LP funds and any user funds inside the affected pool's vaults — there is no recovery path exposed to any unprivileged user (no instruction resets or bypasses `need_take_pnl_*` accounting). This satisfies the "permanent freezing of user or LP funds" impact bar.

### Likelihood Explanation
Likelihood depends on whether a rebasing/fee-on-transfer/balance-shrinking token is ever paired in a pool. `Initialize2` performs no token-mint allow-listing check reachable in this program version, so any user can create a pool with an arbitrary mint via `AmmCommands::CreatePool` / `AmmInstruction::Initialize2`. Given the proliferation of rebasing and yield/negative-yield-bearing SPL tokens, and that the trigger condition only requires accrued PnL to exceed the post-rebase balance (which naturally accumulates over time as fees/PnL accrue and any downward rebase event occurs), this is a realistically reachable Medium-to-High likelihood scenario for any pool using such a mint.

### Recommendation
`calc_total_without_take_pnl_no_orderbook` should not hard-fail the entire instruction pipeline on underflow. Either:
1. Clamp `need_take_pnl_pc`/`need_take_pnl_coin` to the current vault balance (saturating subtraction, e.g. `pc_amount.saturating_sub(need_take_pnl_pc)`), re-syncing the accounted PnL downward when the vault balance decreases unexpectedly, or
2. Maintain a per-mint "supported token" allow-list at `Initialize2` that rejects rebasing/fee-on-transfer/balance-mutating tokens outright, consistent with the referenced protocol's stated mitigation for the analogous issue.

### Proof of Concept
1. Create a pool via `Initialize2` where either `coin_mint` or `pc_mint` is a rebasing/fee-on-transfer SPL token (no on-chain check blocks this) [9](#0-8) .
2. Perform normal swaps/deposits so that `calc_take_pnl` accrues `need_take_pnl_pc`/`need_take_pnl_coin` to some positive value [10](#0-9) .
3. Trigger (or wait for) a downward rebase / balance-decreasing event on the vault's token account so that `amm_pc_vault.amount` (or coin) falls below `amm.state_data.need_take_pnl_pc` (or coin).
4. Any subsequent call to `Deposit`, `Withdraw`, `WithdrawPnl`, `SwapBaseIn`, or `SwapBaseOut` now hits `calc_total_without_take_pnl_no_orderbook` [11](#0-10)  and reverts with `AmmError::CheckedSubOverflow`, permanently freezing the pool for all users.

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

**File:** program/src/processor.rs (L244-254)
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
```

**File:** program/src/processor.rs (L1148-1153)
```rust
        let (mut total_pc_without_take_pnl, mut total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L1459-1464)
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

**File:** program/src/processor.rs (L2154-2159)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L2342-2347)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/processor.rs (L2533-2538)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```

**File:** program/src/error.rs (L1-1)
```rust
//! Error types
```

**File:** program/src/instruction.rs (L343-354)
```rust
            1 => {
                let (nonce, rest) = Self::unpack_u8(rest)?;
                let (open_time, rest) = Self::unpack_u64(rest)?;
                let (init_pc_amount, rest) = Self::unpack_u64(rest)?;
                let (init_coin_amount, _reset) = Self::unpack_u64(rest)?;
                Self::Initialize2(InitializeInstruction2 {
                    nonce,
                    open_time,
                    init_pc_amount,
                    init_coin_amount,
                })
            }
```
