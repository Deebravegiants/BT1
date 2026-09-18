No vulnerability found for this question.

The reported bug is about a hardcoded decimal-precision constant (`TELLOR_DIGITS`) that incorrectly assumes all Tellor price feeds use 6 decimals when newer feeds use 18, causing price misinterpretation. This bug class requires an external price oracle whose reported value's decimal precision is baked into the contract as a fixed constant.

Raydium AMM has no analogous dependency. Token decimals are read dynamically from the actual SPL mint accounts at pool initialization (`coin_mint.decimals`, `pc_mint.decimals`) and stored in `AmmInfo.coin_decimals`/`AmmInfo.pc_decimals`, with `sys_decimal_value` derived from whichever is larger [1](#0-0) . All later normalization calls (`normalize_decimal`, `normalize_decimal_v2`, `restore_decimal`, `convert_in_pc_lot_size`, `convert_out_pc_lot_size`, etc.) consistently take these stored per-pool decimal values as parameters rather than any hardcoded digit constant [2](#0-1) [3](#0-2) . Since there is no external oracle report being parsed with an assumed fixed number of decimals, the "wrong decimals constant for newer feeds" bug class has no reachable analog in the in-scope swap/deposit/withdraw/initialize instruction paths.

### Citations

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

**File:** program/src/math.rs (L80-116)
```rust
    pub fn normalize_decimal(val: u64, native_decimal: u64, sys_decimal_value: u64) -> u64 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**9) -> (1.23*10**6)
        //let ret:u64 = val.checked_mul(amm.sys_decimal_value).unwrap().checked_div((10 as u64).pow(native_decimal.into())).unwrap();
        let ret_mut = (U128::from(val))
            .checked_mul(sys_decimal_value.into())
            .unwrap();
        let ret = Self::to_u64(
            ret_mut
                .checked_div(U128::from(10).checked_pow(native_decimal.into()).unwrap())
                .unwrap()
                .as_u128(),
        )
        .unwrap();
        ret
    }

    pub fn restore_decimal(val: U128, native_decimal: u64, sys_decimal_value: u64) -> U128 {
        // e.g., amm.sys_decimal_value is 10**6, native_decimal is 10**9, price is 1.23, this function will convert (1.23*10**6) -> (1.23*10**9)
        // let ret:u64 = val.checked_mul((10 as u64).pow(native_decimal.into())).unwrap().checked_div(amm.sys_decimal_value).unwrap();
        let ret_mut = val
            .checked_mul(U128::from(10).checked_pow(native_decimal.into()).unwrap())
            .unwrap();
        let ret = ret_mut.checked_div(sys_decimal_value.into()).unwrap();
        ret
    }

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

**File:** program/src/math.rs (L142-186)
```rust
    // convert internal pc_lot_size -> srm pc_lot_size
    pub fn convert_out_pc_lot_size(
        pc_decimals: u8,
        coin_decimals: u8,
        pc_lot_size: u64,
        coin_lot_size: u64,
        sys_decimal_value: u64,
    ) -> u64 {
        let native_lot_size = Self::to_u64(
            ((U128::from(pc_lot_size)
                * U128::from(coin_lot_size)
                * (U128::from(10).checked_pow(pc_decimals.into()).unwrap()))
                / (U128::from(sys_decimal_value)
                    * (U128::from(10).checked_pow(coin_decimals.into()).unwrap())))
            .as_u128(),
        )
        .unwrap();
        native_lot_size
    }

    // convert srm pc_lot_size -> internal pc_lot_size
    pub fn convert_in_pc_lot_size(
        pc_decimals: u8,
        coin_decimals: u8,
        pc_lot_size: u64,
        coin_lot_size: u64,
        sys_decimal_value: u64,
    ) -> u64 {
        let native_lot_size = Self::to_u64(
            (U128::from(pc_lot_size)
                .checked_mul(sys_decimal_value.into())
                .unwrap()
                .checked_mul(U128::from(10).checked_pow(coin_decimals.into()).unwrap())
                .unwrap())
            .checked_div(
                U128::from(coin_lot_size)
                    .checked_mul(U128::from(10).checked_pow(pc_decimals.into()).unwrap())
                    .unwrap(),
            )
            .unwrap()
            .as_u128(),
        )
        .unwrap();
        native_lot_size
    }
```
