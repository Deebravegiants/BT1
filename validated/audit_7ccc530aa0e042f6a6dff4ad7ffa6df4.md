## Title
Unhandled U256 overflow panic in PnL calculation causes permanent freezing of LP funds - (`program/src/math.rs`)

### Summary
The Raydium AMM's PnL "take-profit" logic (`Calculator::calc_x_power`) performs a chain of `checked_mul`/`checked_div` operations on `U256` values and immediately calls `.unwrap()` on the result, exactly the kind of unhandled arithmetic-overflow exception that the cited rippled `gateway_balances` fix (#4355) addressed by catching the overflow and clamping to a safe maximum. Unlike rippled's fix, Raydium does not catch or bound this condition: if the normalized token amounts fed into `calc_x_power` become large enough, the internal `U256` multiplication overflows, `.unwrap()` panics, and the enclosing instruction reverts — every time it is invoked, permanently blocking `Withdraw` and `WithdrawPnl` for that pool.

### Finding Description
`Calculator::calc_x_power` multiplies three `U256` values together before dividing: [1](#0-0) 

It is called from `Processor::calc_take_pnl`, which is on the hot path of both `process_withdraw` (reachable by any LP-token holder) and `process_withdrawpnl`: [2](#0-1) [3](#0-2) 

The magnitude of the values passed into `calc_x_power` (`x1`, `y1`, `target.calc_pnl_x`, `target.calc_pnl_y`) is controlled by `Calculator::normalize_decimal_v2`, which scales a raw vault balance by `amm.sys_decimal_value` (`10^max(coin_decimals, pc_decimals)`) and divides by `10^native_decimal` of that specific token: [4](#0-3) 

`sys_decimal_value` itself is derived at `Initialize2` time directly from the *unprivileged, attacker-supplied* coin/pc mint decimals: [5](#0-4) 

Because `Initialize2` lets the caller pick arbitrary coin/pc mints they control (including newly created ones with attacker-chosen decimals and attacker-controlled supply), an attacker can create a pool where one mint has a much higher decimals value (up to 19, the largest value that doesn't itself overflow the `checked_pow` in `initialize()`) than the other. Once real total vault balances are normalized through `normalize_decimal_v2` with this skewed `sys_decimal_value`, the resulting `x1`/`y1` values can already approach `U128` limits, and their product-of-three-terms inside `calc_x_power` (using `U256`) can be pushed past `U256::MAX` for realistic (attacker fundable, low-decimal, high-supply) token balances. When that happens, `checked_mul(...).unwrap()` panics.

### Impact Explanation
A panic inside the Solana program aborts the transaction, but crucially the *pool state that causes the panic persists on-chain* (it was set during `Initialize2`/normal deposits/swaps). Since `calc_take_pnl` is invoked unconditionally on every `Withdraw` (unless status is `WithdrawOnly`) and every `WithdrawPnl`, once the overflow condition exists it recurs deterministically on every future call. This permanently freezes LP withdrawals (and PnL withdrawals) for that pool, locking any legitimate liquidity providers' funds in the pool with no recovery path through the program's own instructions — matching the "permanent freezing of user or LP funds" impact bar.

### Likelihood Explanation
`Initialize2` is a fully permissionless instruction (`Deposit`, `Withdraw`, and `Initialize2` are all in scope per the reachable-instruction set), and nothing in `process_initialize2` restricts the decimals of `amm_coin_mint_info`/`amm_pc_mint_info` beyond what would cause `AmmInfo::initialize` itself to panic (i.e., decimals ≤ 19 are accepted). An attacker fully controls both the mint parameters and, since they mint their own token, its supply, making the required extreme/skewed balances directly reachable in a small number of transactions (`Initialize2` + `Deposit`/direct SPL transfer to inflate vault balance).

### Recommendation
- Replace the `.unwrap()` calls in `Calculator::calc_x_power` (and the surrounding `checked_mul/checked_div` chains in `calc_take_pnl`) with propagated errors (e.g., `ok_or(AmmError::CheckedMulOverflow)?`) instead of panicking.
- Alternatively, following the spirit of the referenced rippled fix, clamp/saturate the overflowing intermediate value to the maximum representable amount rather than aborting, and add an explicit sanity bound on `coin_decimals`/`pc_decimals` (and/or the resulting `sys_decimal_value`) accepted in `process_initialize2` so extreme skew between the two mints' decimals cannot be used to push later PnL math outside safe ranges.

### Proof of Concept
1. Attacker creates two SPL mints they control: `mint_hi` with `decimals = 19` and `mint_lo` with `decimals = 0`, minting a large supply (near `u64::MAX`) of `mint_lo`.
2. Attacker calls `Initialize2` with `amm_coin_mint = mint_hi`, `amm_pc_mint = mint_lo`, seeding the pool (`sys_decimal_value` becomes `10^19`) — this succeeds because 19 is below the `checked_pow` panic threshold in `AmmInfo::initialize` (`program/src/state.rs:737-745`).
3. Attacker (or anyone) deposits/transfers a large `mint_lo` balance into `amm_pc_vault`, inflating `total_pc_without_take_pnl`.
4. Any user (e.g., the attacker themself as sole LP) calls `Withdraw`; `process_withdraw` computes `x1 = normalize_decimal_v2(total_pc_without_take_pnl, 0, 10^19)` which can approach `~1e38`, then `Processor::calc_take_pnl` → `Calculator::calc_x_power` computes `last_x * last_y * current_x` (~`(1e38)^3`), overflowing `U256::MAX` (~1.16e77) and panicking on `.unwrap()`.
5. The `Withdraw` transaction reverts every time it is attempted, permanently freezing LP funds in the pool.

### Citations

**File:** program/src/math.rs (L50-60)
```rust
    pub fn calc_x_power(last_x: U256, last_y: U256, current_x: U256, current_y: U256) -> U256 {
        // must be use u256, because u128 may be overflow
        let x_power = last_x
            .checked_mul(last_y)
            .unwrap()
            .checked_mul(current_x)
            .unwrap()
            .checked_div(current_y)
            .unwrap();
        x_power
    }
```

**File:** program/src/math.rs (L106-116)
```rust
    pub fn normalize_decimal_v2(val: u64, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = ret_mut
            .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        ret
    }
```

**File:** program/src/processor.rs (L167-209)
```rust
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

**File:** program/src/state.rs (L717-745)
```rust
    pub fn initialize(
        &mut self,
        nonce: u8,
        open_time: u64,
        coin_decimals: u8,
        pc_decimals: u8,
        _coin_lot_size: u64,
        _pc_lot_size: u64,
    ) -> Result<(), AmmError> {
        self.fees.initialize()?;
        self.state_data.initialize(open_time)?;

        self.status = AmmStatus::Uninitialized.into_u64();
        self.nonce = nonce as u64;
        self.order_num = 7;
        self.depth = 3;
        self.coin_decimals = coin_decimals as u64;
        self.pc_decimals = pc_decimals as u64;
        self.state = AmmState::IdleState.into_u64();
        self.reset_flag = AmmResetFlag::ResetNo.into_u64();
        if pc_decimals > coin_decimals {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(pc_decimals.try_into().unwrap())
                .unwrap();
        } else {
            self.sys_decimal_value = (10 as u64)
                .checked_pow(coin_decimals.try_into().unwrap())
                .unwrap();
        }
```
