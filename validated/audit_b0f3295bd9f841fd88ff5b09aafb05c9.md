### Title
Decimal-scaling overflow in `calc_x_power` used by `calc_take_pnl` can permanently freeze pool/LP funds - ([File: program/src/math.rs])

### Summary
`Processor::calc_take_pnl`, which is invoked on every swap, deposit, withdraw, and `withdrawpnl` instruction, calls `Calculator::calc_x_power` to compute a `U256` product of normalized pc/coin balances. When a pool is created with mismatched token decimals (permitted up to the point where `AmmInfo::initialize`'s `checked_pow` doesn't overflow `u64`, i.e. up to `10^19`), the decimal-normalization step (`normalize_decimal_v2`) scales one side of the pool massively more than the other. With realistically large vault balances, the subsequent `last_x.checked_mul(last_y).unwrap().checked_mul(current_x).unwrap()` chain in `calc_x_power` can exceed `U256::MAX`, causing an `unwrap()` panic that aborts the transaction. This is directly analogous to the reported `unitsToValue`/`FixidityLib.divide` overflow: fixed-point scaling combined with large amounts overflows and reverts, permanently locking funds that can no longer be withdrawn because every instruction that reaches `calc_take_pnl` fails.

### Finding Description
`calc_x_power` performs unchecked-but-panicking arithmetic on `U256`: [1](#0-0) 

It's fed values produced by `normalize_decimal_v2`, which scales a raw `u64` token amount by `amm.sys_decimal_value`: [2](#0-1) 

`sys_decimal_value` is set at pool `initialize` time to `10^max(pc_decimals, coin_decimals)`, with no bound on the *difference* between `pc_decimals` and `coin_decimals`, and no cap enforced beyond what causes `checked_pow` to overflow `u64` (i.e., an exponent of ~19-20): [3](#0-2) 

Because an unprivileged pool creator picks the coin/pc mints (and thus their decimals) when calling `Initialize2`, they can create a pool where, e.g., `pc_decimals = 0` and `coin_decimals = 19`. This makes `sys_decimal_value = 10^19`, so pc-side normalized values (`x`) get scaled up by `10^19` relative to raw balances, while coin-side normalized values (`y`) are left near their raw `u64` magnitude. `calc_take_pnl` computes `x1`/`y1` via `normalize_decimal_v2` and feeds them, along with the previously stored `target.calc_pnl_x/calc_pnl_y`, into `calc_x_power`: [4](#0-3) 

With vault balances approaching `u64::MAX` (achievable via large deposits, which is a normal unprivileged operation), the pc-scaled values (`last_x`, `current_x`) can reach on the order of `1.8e19 * 1e19 ≈ 1.8e38`. The product `last_x * last_y * current_x` can then reach roughly `1e95`, far exceeding `U256::MAX (~1.16e77)`, triggering the `.unwrap()` panic on `checked_mul` inside `calc_x_power`.

`calc_take_pnl` is called from every state-mutating path that touches pool balances: [5](#0-4) [6](#0-5) [7](#0-6) 

Once the overflow threshold is crossed, deposit, withdraw, withdrawpnl, and swap instructions that reach this code path will all panic/fail deterministically, since the stored `target.calc_pnl_x`/`calc_pnl_y` and current pool balances remain large. There is no code path to reduce these values without first executing one of these now-panicking instructions, so funds become permanently stuck in the AMM's vaults.

### Impact Explanation
This causes permanent freezing of LP and swapper funds held in the pool's coin/pc vaults: once the overflow condition is reached, `Deposit`, `Withdraw`, `SwapBaseIn`, `SwapBaseOut`, and `WithdrawPnl` all revert via panic when they reach `calc_take_pnl` → `calc_x_power`, with no available instruction to unwind the state. This matches the required bar of "permanent freezing of user or LP funds."

### Likelihood Explanation
Pool creation (`Initialize2`) is permissionless and accepts arbitrary SPL mints, so an attacker or even an ordinary pool creator can pick highly asymmetric decimals (e.g., 0 and 19) for the coin/pc mints. A single large deposit (an SPL mint can have supply approaching `u64::MAX`) is sufficient to push the normalized values into the overflow range — no sustained trading volume is required, making this reachable in a small number of straightforward, unprivileged transactions (pool creation + one or two large deposits).

### Recommendation
- Bound the allowable delta between `pc_decimals` and `coin_decimals` (or cap `sys_decimal_value`) at `AmmInfo::initialize` time to prevent extreme scaling asymmetries.
- Replace the panicking `.unwrap()` calls in `calc_x_power` (and related `checked_pow`/`checked_mul` chains in `math.rs`/`state.rs`) with proper `Result`-returning error handling (e.g., `ok_or(AmmError::CalcPnlError)`), so an overflow degrades to a recoverable instruction error rather than an unrecoverable, permanently-repeating panic.
- Consider computing `calc_x_power` using a wider intermediate representation or restructuring the formula to avoid multiplying two full-magnitude 128-bit-scale values together before dividing.

### Proof of Concept
1. Attacker calls `Initialize2` with a coin mint of decimals `19` and a pc mint of decimals `0` (or another combination near the `10^19` boundary allowed by `AmmInfo::initialize`'s `checked_pow`).
2. Attacker performs a `Deposit` (or several) that brings `total_pc_without_take_pnl` and/or `total_coin_without_take_pnl` close to `u64::MAX`, which is possible since SPL mints can be minted with very large supply and no protocol-level cap exists on deposit size besides `u64` range.
3. On this or a subsequent `Deposit`/`Withdraw`/`Swap`/`WithdrawPnl` call, `calc_take_pnl` computes `x1`/`y1` via `normalize_decimal_v2` (program/src/processor.rs:1155-1164) and calls `calc_x_power` (program/src/math.rs:50-59) with values whose product exceeds `U256::MAX`.
4. `checked_mul(...).unwrap()` panics, aborting the transaction. Because the underlying vault balances and `target.calc_pnl_x`/`calc_pnl_y` remain in this overflowing range, every subsequent instruction touching `calc_take_pnl` fails identically, permanently freezing all funds held in the pool's `coin_vault`/`pc_vault`.

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

**File:** program/src/state.rs (L733-745)
```rust
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

**File:** program/src/processor.rs (L1166-1173)
```rust
        let (delta_x, delta_y) = Self::calc_take_pnl(
            &target_orders,
            &mut amm,
            &mut total_pc_without_take_pnl,
            &mut total_coin_without_take_pnl,
            x1.as_u128().into(),
            y1.as_u128().into(),
        )?;
```

**File:** program/src/processor.rs (L1494-1502)
```rust
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

**File:** program/src/processor.rs (L1740-1749)
```rust
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
