### Title
Unbounded `U256` multiplication chain in `Calculator::calc_x_power` (used by `calc_take_pnl`) can overflow and panic, causing a permanent DoS/fund-freeze on `Deposit`/`Withdraw` for pools with highly asymmetric coin/pc decimals - (File: `program/src/math.rs`, `program/src/processor.rs`)

### Summary
`Calculator::calc_x_power` and the `calc_take_pnl` routine that consumes it perform three chained `checked_mul` operations on `U256` values derived from `Calculator::normalize_decimal_v2`, without ever bounding the intermediate product the way a safe `mulDiv` (divide-before-multiply / wider-intermediate) implementation would. Because Raydium normalizes both pool sides to a common `sys_decimal_value` that can be as large as `10^19` (the largest power of ten that still fits in `u64`), a pool created between a 0-decimal token and a 19-decimal token amplifies one side by up to `10^19` relative to the other before the pnl math runs. Chaining three such multiplications inside `U256` (max ≈ `1.157e77`) can then exceed the `U256` limit, causing the `.unwrap()` on `checked_mul` to panic and abort the transaction — a Denial-of-Service that is triggered on every subsequent `Deposit`/`Withdraw` call once the pool state (`total_pc_without_take_pnl`/`total_coin_without_take_pnl`, `target.calc_pnl_x`/`calc_pnl_y`) crosses the threshold, effectively freezing all LP funds in the pool.

### Finding Description
`Calculator::normalize_decimal_v2` rescales the raw vault balance to the pool's `sys_decimal_value`: [1](#0-0) 

`AmmInfo::initialize` sets `sys_decimal_value = 10^max(coin_decimals, pc_decimals)`, using `checked_pow` on a `u64`, so any decimals pair up to `19` is accepted (`10^19 < u64::MAX`, `10^20` overflows and only aborts at pool-creation time, not afterward): [2](#0-1) 

Both `process_deposit` and `process_withdraw` compute `x1`/`y1` via `normalize_decimal_v2` and immediately feed them into `Self::calc_take_pnl`: [3](#0-2) [4](#0-3) 

Inside `calc_take_pnl`, `Calculator::calc_x_power` chains three `U256` multiplications with no intermediate range check other than `.unwrap()`-based panics: [5](#0-4) [6](#0-5) 

For a pool where `pc_decimals = 0` and `coin_decimals = 19` (a valid, non-privileged pool configuration through `Initialize2`), `x1 = normalize_decimal_v2(total_pc, 0, 1e19) = total_pc * 1e19` while `y1 = normalize_decimal_v2(total_coin, 19, 1e19) = total_coin`. With realistic (attacker- or LP-controlled) vault balances approaching `u64::MAX` (~1.84e19), `x1` reaches ~`1.84e38`, still within `U128`, but `calc_x_power`'s `last_x.checked_mul(last_y).checked_mul(current_x)` reaches roughly `(1.84e38) * (1.84e19) * (1.84e38) ≈ 6.2e95`, which exceeds `U256::MAX` (~`1.157e77`) by many orders of magnitude. The `.unwrap()` on the second `checked_mul` then panics, aborting the instruction.

This directly mirrors the referenced Solidity finding's root cause: raw `mul`/`div` chains without an overflow-safe `mulDiv`-style implementation, applied to a protocol that (like the Solidity target) permits pools/tokens with widely varying decimal configurations rather than enforcing a narrow decimals range.

### Impact Explanation
Once a pool's normalized balances (which grow with legitimate deposits/swaps over time) cross the threshold that overflows `U256` inside `calc_x_power`, every subsequent `Deposit` and `Withdraw` call — both reachable by any unprivileged liquidity provider — will panic and revert. Because `Withdraw` is the only path for LPs to redeem their share of the pool, this permanently freezes all coin/pc tokens locked in the AMM's vaults for that pool (loss of availability equivalent to loss of funds for depositors), matching the Medium-severity DoS/fund-freeze impact accepted in the referenced report.

### Likelihood Explanation
Reaching the overflow requires a pool created with an extreme decimals disparity (e.g., `pc_decimals = 0`, `coin_decimals = 19`) and vault balances that grow large enough in the normalized domain. Pool creation via `Initialize2` is unprivileged and does not reject such decimal combinations (only combinations producing `sys_decimal_value > u64::MAX` are rejected at creation time). Reaching balances near `u64::MAX` for a 0-decimal token is a large but not physically restricted supply (SPL token mint supply is itself a `u64`), so a token/pool deliberately structured this way, or one that organically accumulates large balances over time, can trigger the panic. This is a narrower reachability window than the original ERC-20 report (bounded by `sys_decimal_value`'s `u64` cap versus Solidity's unbounded decimals), but it remains reachable without any privileged action, consistent with the accepted precedent that decimal-driven overflow classes are valid even for less common decimal configurations.

### Recommendation
Replace the raw chained `checked_mul`/`checked_div` in `Calculator::calc_x_power` (and the `mul`-then-`div` patterns throughout `math.rs`/`processor.rs` that operate on values derived from `normalize_decimal_v2`) with an overflow-safe wide-multiply-then-divide implementation (analogous to `Math::mulDiv`), e.g., promoting to `U512` for the intermediate product before dividing back down, or restructuring the pnl formula to divide before multiplying where mathematically valid. Additionally, consider bounding the accepted `coin_decimals`/`pc_decimals` disparity at `Initialize2` time to a range that is provably safe for all downstream `U256`/`U128` arithmetic.

### Proof of Concept
1. Create two SPL mints: `MintA` with `decimals = 0`, `MintB` with `decimals = 19`.
2. Call `Initialize2` to create an AMM pool with `coin_mint = MintB` (19 decimals) and `pc_mint = MintA` (0 decimals). `AmmInfo::initialize` sets `sys_decimal_value = 10^19` (fits `u64`), so initialization succeeds — `program/src/state.rs:717-746`.
3. Perform deposits (via `Deposit`) until `total_pc_without_take_pnl` (in raw `MintA` units) and `total_coin_without_take_pnl` (in raw `MintB` units) are large enough that, after `Calculator::normalize_decimal_v2` scaling, `x1 ≈ total_pc * 1e19` approaches `~1e38` and `y1 ≈ total_coin` approaches `~1e19`.
4. Call `Withdraw` (or another `Deposit`) that invokes `Self::calc_take_pnl` → `Calculator::calc_x_power(target.calc_pnl_x, target.calc_pnl_y, x1, y1)` — `program/src/processor.rs:1719-1748`, `program/src/math.rs:50-60`.
5. The second `checked_mul` (`last_x*last_y).checked_mul(current_x)`) exceeds `U256::MAX`, causing `.unwrap()` to panic; the transaction fails, and this failure recurs for every future `Deposit`/`Withdraw` on this pool, permanently locking LP funds in the vaults.

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

**File:** program/src/state.rs (L717-746)
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

**File:** program/src/processor.rs (L199-208)
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
```

**File:** program/src/processor.rs (L1155-1174)
```rust
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
```

**File:** program/src/processor.rs (L1719-1736)
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

```
