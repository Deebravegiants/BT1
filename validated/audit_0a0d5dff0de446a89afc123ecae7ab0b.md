### Title
Direct SPL "donation" to `amm_coin_vault`/`amm_pc_vault` inflates live-balance-based pnl accounting, allowing over-crediting of `need_take_pnl_*` and permanent freezing of all pool funds - (File: `program/src/processor.rs`, `program/src/math.rs`)

### Summary
The Raydium AMM computes its working reserves (`total_pc_without_take_pnl`, `total_coin_without_take_pnl`) every instruction by reading the *live* SPL token balance of `amm_coin_vault`/`amm_pc_vault` via `unpack_token_account`, exactly the same "read live balance instead of internally tracked reserve" pattern the external dTRINITY report exploited (`totalAssets()` reading a live, attacker-inflatable lending-pool balance). Because anyone can transfer SPL tokens directly into the pool's vault token accounts without going through the program (no permission check on the *destination* of a plain `spl_token::transfer`), an attacker can inflate `amm_coin_vault.amount`/`amm_pc_vault.amount` for free before calling `deposit`/`withdraw`, which triggers `calc_take_pnl` to compare this inflated, donation-driven balance against the stale `target_orders.calc_pnl_x/y` baseline and mis-credit the difference as legitimate trading profit into `amm.state_data.need_take_pnl_pc/coin`.

### Finding Description
`calc_total_without_take_pnl_no_orderbook` derives the pool's usable reserves directly from the vault's live token-account balance and the currently stored `need_take_pnl_pc/coin`: [1](#0-0) 

This same live-balance read (`amm_pc_vault.amount`, `amm_coin_vault.amount` via `Self::unpack_token_account`) feeds every state-changing instruction — deposit, withdraw, withdrawpnl and swap: [2](#0-1) [3](#0-2) [4](#0-3) 

`calc_take_pnl` (invoked from deposit/withdraw/withdrawpnl) treats *any* increase in the live `x*y` product over the last stored `calc_pnl_x*calc_pnl_y` invariant as trading profit and credits a share into `need_take_pnl_pc/coin`, without distinguishing whether that increase came from genuine swap fees or from an unsolicited direct token transfer into the vault: [5](#0-4) [6](#0-5) 

An attacker can:
1. Directly `spl_token::transfer` tokens into `amm_coin_vault` (or `amm_pc_vault`) — this requires no cooperation from the AMM program since anyone can be the destination of an SPL transfer.
2. Call `deposit` (or `withdraw`) immediately after; `calc_take_pnl` sees the donation-inflated `x1*y1` vs. the old `calc_pnl_x/y` baseline and credits a large chunk of the donated amount into `amm.state_data.need_take_pnl_pc/coin`, treating a free donation as "profit."
3. Recover the donated principal via a normal swap (`swap_base_in`/`swap_base_out`), which never touches `calc_take_pnl` and simply exchanges at the (now pnl-adjusted) reserve ratio: [7](#0-6) 

After extracting the donated value back out, the vault's real token balance can end up lower than the `need_take_pnl_pc/coin` amount that was credited based on the artificial donation. Every subsequent call to `calc_total_without_take_pnl_no_orderbook` (used by swap, deposit, and withdraw alike) then executes `pc_amount.checked_sub(amm.state_data.need_take_pnl_pc)` / the coin equivalent, which underflows and returns `AmmError::CheckedSubOverflow`, permanently reverting every instruction for the pool: [8](#0-7) 

This is the direct structural analog of the dTRINITY finding: both bugs stem from computing "total assets/reserves" from a live, externally-manipulable balance rather than an internally tracked and reconciled value, letting an attacker inflate that figure with an unsolicited donation, have the system's own accounting logic (increaseLeverage / calc_take_pnl) convert the inflated figure into a real, withdrawable claim, and leave the pool permanently under-collateralized once the donation principal is withdrawn back out — freezing all remaining depositors' funds.

### Impact Explanation
Once `need_take_pnl_pc` or `need_take_pnl_coin` exceeds the real vault balance, `calc_total_without_take_pnl_no_orderbook`'s `checked_sub` fails for every future `deposit`, `withdraw`, `withdrawpnl`, and `swap_base_in/out(_v2)` call, since all of them call this function on the current live vault balances. This is a permanent, pool-wide denial of service that locks all LP and trader funds in the vault with no recovery path in the current instruction set — matching the "High" severity of permanent freezing described in the source report.

### Likelihood Explanation
The precondition is a single unprivileged SPL `transfer` to a publicly known vault ATA (no signer/authority requirement on the receiving side) followed by a normal `deposit`/`withdraw` call and a normal `swap` — all reachable in ordinary transactions with attacker-chosen accounts and data, requiring no special privileges, leaked keys, or off-chain assumptions.

### Recommendation
Do not derive `total_pc_without_take_pnl`/`total_coin_without_take_pnl` (and thus pnl accounting) purely from the live SPL balance of the vaults. Track pool reserves internally (updated only through program-mediated deposit/withdraw/swap paths) or reconcile/clamp `need_take_pnl_pc/coin` against verified trading-fee accrual rather than raw balance deltas, and add an invariant check that `need_take_pnl_*` can never be set to a value unsupported by actual realized fee income.

### Proof of Concept
1. Deploy/observe an existing Raydium pool with `amm_coin_vault`, `amm_pc_vault`, and `target_orders.calc_pnl_x/y` reflecting current reserves.
2. Attacker calls `spl_token::transfer` sending a large amount of the coin token directly into `amm_coin_vault` (no AMM program interaction required).
3. Attacker calls `deposit` (or `withdraw`) with a minimal amount; the program computes `total_coin_without_take_pnl` from the now-inflated `amm_coin_vault.amount` and invokes `calc_take_pnl`, which — since current `x*y` exceeds the stored last-k baseline purely due to the donation — credits a portion of the donated amount into `amm.state_data.need_take_pnl_coin`.
4. Attacker calls `swap_base_in` to swap the donated coin back to pc (or otherwise extract the donated value); this path does not call `calc_take_pnl`, so `need_take_pnl_coin` is not adjusted downward.
5. Repeat until real `amm_coin_vault.amount` < `need_take_pnl_coin`.
6. Any subsequent `deposit`, `withdraw`, `withdrawpnl`, or `swap` call reverts with `AmmError::CheckedSubOverflow` from `Calculator::calc_total_without_take_pnl_no_orderbook`, permanently freezing the pool for all users.

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

**File:** program/src/processor.rs (L159-212)
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
            // current p is
            // let current_p: u128 = (x1 as u128).checked_div(y1 as u128).unwrap();
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

            // transfer to token_coin_pnl and token_pc_pnl
            // (x1 -x2) * pnl / sys_decimal_value
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

**File:** program/src/processor.rs (L1138-1153)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;
        let user_source_coin =
            Self::unpack_token_account(&user_source_coin_info, spl_token_program_id)?;
        let user_source_pc =
            Self::unpack_token_account(&user_source_pc_info, spl_token_program_id)?;
        let mut target_orders =
            TargetOrders::load_mut_checked(&amm_target_orders_info, program_id, amm_info.key)?;
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

**File:** program/src/processor.rs (L2342-2347)
```rust
        let (total_pc_without_take_pnl, total_coin_without_take_pnl) =
            Calculator::calc_total_without_take_pnl_no_orderbook(
                amm_pc_vault.amount,
                amm_coin_vault.amount,
                &amm,
            )?;
```
