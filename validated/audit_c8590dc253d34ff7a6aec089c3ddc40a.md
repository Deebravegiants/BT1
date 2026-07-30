[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** lockup/src/foundation_callbacks.rs (L143-158)
```rust
    pub fn on_staking_pool_withdraw_for_termination(&mut self, amount: WrappedBalance) -> bool {
        assert_self();

        let withdraw_succeeded = is_promise_success();
        self.set_staking_pool_status(TransactionStatus::Idle);

        if withdraw_succeeded {
            self.set_termination_status(TerminationStatus::ReadyToWithdraw);
            {
                let staking_information = self.staking_information.as_mut().unwrap();
                // Due to staking rewards the deposit amount can become negative.
                staking_information.deposit_amount.0 = staking_information
                    .deposit_amount
                    .0
                    .saturating_sub(amount.0);
            }
```

**File:** lockup/src/owner.rs (L12-41)
```rust
    pub fn select_staking_pool(&mut self, staking_pool_account_id: AccountId) -> Promise {
        self.assert_owner();
        assert!(
            env::is_valid_account_id(staking_pool_account_id.as_bytes()),
            "The staking pool account ID is invalid"
        );
        self.assert_staking_pool_is_not_selected();
        self.assert_no_termination();

        env::log(
            format!(
                "Selecting staking pool @{}. Going to check whitelist first.",
                staking_pool_account_id
            )
            .as_bytes(),
        );

        ext_whitelist::is_whitelisted(
            staking_pool_account_id.clone(),
            &self.staking_pool_whitelist_account_id,
            NO_DEPOSIT,
            gas::whitelist::IS_WHITELISTED,
        )
        .then(ext_self_owner::on_whitelist_is_whitelisted(
            staking_pool_account_id,
            &env::current_account_id(),
            NO_DEPOSIT,
            gas::owner_callbacks::ON_WHITELIST_IS_WHITELISTED,
        ))
    }
```

**File:** lockup/src/owner.rs (L176-209)
```rust
    pub fn refresh_staking_pool_balance(&mut self) -> Promise {
        self.assert_owner();
        self.assert_staking_pool_is_idle();
        self.assert_no_termination();

        env::log(
            format!(
                "Fetching total balance from the staking pool @{}",
                self.staking_information
                    .as_ref()
                    .unwrap()
                    .staking_pool_account_id
            )
            .as_bytes(),
        );

        self.set_staking_pool_status(TransactionStatus::Busy);

        ext_staking_pool::get_account_total_balance(
            env::current_account_id(),
            &self
                .staking_information
                .as_ref()
                .unwrap()
                .staking_pool_account_id,
            NO_DEPOSIT,
            gas::staking_pool::GET_ACCOUNT_TOTAL_BALANCE,
        )
        .then(ext_self_owner::on_get_account_total_balance(
            &env::current_account_id(),
            NO_DEPOSIT,
            gas::owner_callbacks::ON_GET_ACCOUNT_TOTAL_BALANCE,
        ))
    }
```

**File:** lockup/src/getters.rs (L163-178)
```rust
    pub fn get_owners_balance(&self) -> WrappedBalance {
        (env::account_balance() + self.get_known_deposited_balance().0)
            .saturating_sub(self.get_locked_amount().0)
            .into()
    }

    /// Returns total balance of the account including tokens deposited to the staking pool.
    pub fn get_balance(&self) -> WrappedBalance {
        (env::account_balance() + self.get_known_deposited_balance().0).into()
    }

    /// Returns the amount of tokens the owner can transfer from the account.
    /// Transfers have to be enabled.
    pub fn get_liquid_owners_balance(&self) -> WrappedBalance {
        std::cmp::min(self.get_owners_balance().0, self.get_account_balance().0).into()
    }
```
