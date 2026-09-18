No vulnerability found for this question.

Raydium's AMM v4 program computes swap and withdrawal pricing entirely from its own on-chain vault reserves via the constant-product formula in `Calculator::calc_total_without_take_pnl_no_orderbook` and the swap processors [1](#0-0) , rather than from any externally-committed price oracle. There is no analog to Pyth's `PythOracle.commit()` mechanism — no instruction accepts a user-supplied timestamp/price pair that gets validated against a "previous commit" and then used to value collateral or positions. `AmmInfo` state only tracks vault balances, LP amounts, and fee/status fields [2](#0-1) , and swap instructions derive price purely from real-time vault token balances read via `unpack_token_account` at execution time [3](#0-2) . Since there's no out-of-band oracle commit path that can be manipulated with a stale, attacker-chosen timestamp to create a mismatch between "recorded" and "live" market price, the reported bug class (arbitrary historical oracle-version commit enabling profit extraction from collateral operations) has no reachable equivalent in this AMM's account-bound, reserve-based pricing model.

### Citations

**File:** program/src/processor.rs (L2321-2327)
```rust
        let amm_coin_vault =
            Self::unpack_token_account(&amm_coin_vault_info, spl_token_program_id)?;
        let amm_pc_vault = Self::unpack_token_account(&amm_pc_vault_info, spl_token_program_id)?;

        let user_source = Self::unpack_token_account(&user_source_info, spl_token_program_id)?;
        let user_destination =
            Self::unpack_token_account(&user_destination_info, spl_token_program_id)?;
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

**File:** program/src/state.rs (L717-766)
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

        self.min_size = 0;

        self.vol_max_cut_ratio = 500; // TEN_THOUSAND as denominator
        self.amount_wave = self
            .sys_decimal_value
            .checked_mul(5)
            .unwrap()
            .checked_div(1000)
            .unwrap();
        self.coin_lot_size = 0;
        self.pc_lot_size = 0;
        self.min_price_multiplier = 1;
        self.max_price_multiplier = 1000000000;
        self.client_order_id = 0;
        self.padding1 = Zeroable::zeroed();
        self.recent_epoch = get_recent_epoch().unwrap();
        self.padding2 = Zeroable::zeroed();

        Ok(())
    }
```
