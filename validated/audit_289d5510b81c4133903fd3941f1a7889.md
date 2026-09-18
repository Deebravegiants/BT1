### Title
Rebasing/inflationary vault tokens are misclassified as protocol PnL and diverted from LPs to the `pnl_owner` - (File: `program/src/processor.rs`)

### Summary
Raydium's constant-product invariant is tracked via `TargetOrders.calc_pnl_x` / `calc_pnl_y`, which record the "last known" normalized reserves. Any growth of the pool's `k = x*y` beyond this recorded value is treated as accumulated trading-fee profit and is credited to `AmmInfo.state_data.need_take_pnl_coin` / `need_take_pnl_pc`, which are later swept out to the `pnl_owner` account via `WithdrawPnl`. This mirrors the Napier report: any surplus balance in the pool's vaults — regardless of its true source — is unconditionally routed to a privileged fee-collecting address rather than to the liquidity providers who actually own it.

### Finding Description
`Calculator::calc_take_pnl` computes the difference between the pool's current reserves and the last recorded "no-pnl" reserves purely from the raw vault token balances (`amm_coin_vault.amount`, `amm_pc_vault.amount`), with no way to distinguish balance growth caused by trading fees from balance growth caused by an underlying token that rebases upward (or otherwise auto-appreciates in the vault, e.g. fee-on-transfer tokens that lower balances asymmetrically): [1](#0-0) 

This function is invoked from the unprivileged `Deposit` and `Withdraw` instruction handlers before any pool-share math is done: [2](#0-1) [3](#0-2) 

Any surplus (`delta_x`, `delta_y`) computed this way is added to `need_take_pnl_coin` / `need_take_pnl_pc`: [4](#0-3) 

and is later transferred out of the vaults to the `pnl_owner`-controlled destination account in `process_withdrawpnl`, entirely bypassing LP share accounting: [5](#0-4) 

If the coin or pc mint used in a pool is a rebasing token (balance increases automatically over time without any corresponding trade), or any token whose vault balance can grow independent of swap activity, that growth is indistinguishable to `calc_take_pnl` from organic trading-fee profit. The very next `Deposit` or `Withdraw` call by any unprivileged user will "bake in" that surplus as PnL owed to `pnl_owner`, permanently removing it from the LP-owned reserve (`total_pc_without_take_pnl` / `total_coin_without_take_pnl`) used for LP redemption math.

### Impact Explanation
Rebase gains (or other externally-injected balance growth) that rightfully belong to LPs are permanently reallocated to the pool's `pnl_owner`/fee-recipient account instead of increasing the redeemable value of LP tokens. This is a direct, ongoing loss of user/LP funds — every rebase-up event effectively transfers value from LPs to the protocol fee recipient, and once `need_take_pnl_*` is incremented and later withdrawn, it cannot be recovered by LPs.

### Likelihood Explanation
Triggering the misclassification requires no special privilege: any user calling the standard `Deposit` or `Withdraw` instruction on a pool whose underlying token is rebasing (or otherwise capable of increasing vault balance outside of swaps) will cause `calc_take_pnl` to run and skim the surplus into `need_take_pnl_*`. The actual sweep to `pnl_owner` requires the `WithdrawPnl` signer, which is the protocol's normal expected operational flow — not an attack requiring a compromised key — so the loss occurs whenever such a token is paired in a pool.

### Recommendation
Exclude rebase-driven/external balance growth from the PnL computation, e.g., by tracking expected reserves from actual swap/deposit/withdraw deltas rather than trusting the raw SPL token account balance as ground truth, or explicitly disallow rebasing/balance-mutating tokens as pool mints. Alternatively, ensure any surplus detected by `calc_take_pnl` that cannot be attributed to recorded trade fees is credited back to LP share value instead of `need_take_pnl_coin`/`need_take_pnl_pc`.

### Proof of Concept
1. Create a pool via `Initialize2` where the `coin` mint is a rebasing SPL token (balance auto-increases for all holders, including the AMM's `coin_vault`).
2. Let the rebase event occur, increasing `amm_coin_vault.amount` without any swap.
3. Any user calls `Deposit` (or `Withdraw`) — `process_deposit`/`process_withdraw` calls `Calculator::calc_take_pnl` with the inflated `total_coin_without_take_pnl`, computing a positive `delta_y` that is added to `amm.state_data.need_take_pnl_coin`. [6](#0-5) 
4. The `pnl_owner` later calls `WithdrawPnl`, receiving the rebase-driven surplus that should have accrued to LP token holders. [5](#0-4)

### Citations

**File:** program/src/processor.rs (L159-196)
```rust
    /// The Detailed calculation of pnl
    /// 1. calc last_k witch dose not take pnl: last_k = calc_pnl_x * calc_pnl_y;
    /// 2. calc current price: current_price = current_x / current_y;
    /// 3. calc x after take pnl: x_after_take_pnl = sqrt(last_k * current_price);
    /// 4. calc y after take pnl: y_after_take_pnl = x_after_take_pnl / current_price;
    ///                           y_after_take_pnl = x_after_take_pnl * current_y / current_x;
    /// 5. calc pnl_x & pnl_y:  pnl_x = current_x - x_after_take_pnl;
    ///                         pnl_y = current_y - y_after_take_pnl;
    pub fn calc_take_pnl(
        target: &TargetOrders,
        amm: &mut AmmInfo,
        total_pc_without_take_pnl: &mut u64,
        total_coin_without_take_pnl: &mut u64,
        x1: U256,
        y1: U256,
    ) -> Result<(u128, u128), ProgramError> {
        // calc pnl
        let mut delta_x: u128;
        let mut delta_y: u128;
        let calc_pc_amount = Calculator::restore_decimal(
            target.calc_pnl_x.into(),
            amm.pc_decimals,
            amm.sys_decimal_value,
        );
        let calc_coin_amount = Calculator::restore_decimal(
            target.calc_pnl_y.into(),
            amm.coin_decimals,
            amm.sys_decimal_value,
        );
        let pool_pc_amount = U128::from(*total_pc_without_take_pnl);
        let pool_coin_amount = U128::from(*total_coin_without_take_pnl);
        if pool_pc_amount.checked_mul(pool_coin_amount).unwrap()
            >= (calc_pc_amount).checked_mul(calc_coin_amount).unwrap()
        {
            // last k is
            // let last_k: u128 = (target.calc_pnl_x as u128).checked_mul(target.calc_pnl_y as u128).unwrap();
            // current k is
            // let current_k: u128 = (x1 as u128).checked_mul(y1 as u128).unwrap();
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

**File:** program/src/processor.rs (L1145-1173)
```rust
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
        // calc the remaining total_pc & total_coin
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
```

**File:** program/src/processor.rs (L1505-1529)
```rust
        if amm.state_data.need_take_pnl_coin <= amm_coin_vault.amount
            && amm.state_data.need_take_pnl_pc <= amm_pc_vault.amount
        {
            // coin & pc is enough, transfer directly
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_coin_vault_info.clone(),
                user_pnl_coin_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_coin,
            )?;
            Invokers::token_transfer_with_authority(
                token_program_info.clone(),
                amm_pc_vault_info.clone(),
                user_pnl_pc_info.clone(),
                amm_authority_info.clone(),
                AUTHORITY_AMM,
                amm.nonce as u8,
                amm.state_data.need_take_pnl_pc,
            )?;
            // clear need take pnl
            amm.state_data.need_take_pnl_coin = 0u64;
            amm.state_data.need_take_pnl_pc = 0u64;
```

**File:** program/src/processor.rs (L1737-1749)
```rust
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
