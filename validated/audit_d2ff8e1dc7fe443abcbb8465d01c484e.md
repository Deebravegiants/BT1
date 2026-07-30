### Title
Direct NEAR transfer ("donation") to a staking-pool contract lets an attacker inflate `total_staked_balance`/share price via `internal_ping()` - (File: staking-pool/src/internal.rs)

### Summary
`internal_ping()` determines "staking rewards" purely by diffing the raw NEAR balance of the contract (`env::account_locked_balance() + env::account_balance()`) against the previously recorded `last_total_balance`, and then mints/attributes that entire delta to `total_staked_balance` (i.e., the share price) [1](#0-0) . This is structurally identical to the Aerodrome `sync()` donation issue: reserves/price are derived from a raw, unguarded on-chain balance that anyone can inflate with a plain value transfer, rather than from balances that are only mutated through accounted entry points.

### Finding Description
`deposit`, `deposit_and_stake`, `stake`, `unstake`, `withdraw`, and the public, unauthenticated `ping()` method all call `internal_ping()` before doing their accounting [2](#0-1) . `internal_ping()` computes:
```
total_balance = account_locked_balance() + account_balance() - attached_deposit()
total_reward  = total_balance - last_total_balance
```
and treats `total_reward` as validator staking rewards, adding it to `total_staked_balance` (thereby increasing `staked_amount_from_num_shares_*` for every existing "stake" share) and minting extra owner shares from the fee portion [3](#0-2) .

Because `env::account_balance()` reflects the plain NEAR balance of the account, any unprivileged user can send a bare NEAR transfer (a `Transfer` action, not a function call, so it bypasses `deposit()`'s accounting) directly to the staking-pool contract's account ID. The next call to `ping()` (which anyone can invoke) will count that donated amount as legitimate "reward," permanently baking it into `total_staked_balance` and thus into the "stake" share price (`staked_amount_from_num_shares_rounded_down/up` in `staking-pool/src/internal.rs:292-321`). This is the direct analog of donating tokens to an Aerodrome pool and calling `sync()` to inflate reserves without a matching trade/deposit.

### Impact Explanation
An attacker who has previously staked (owns a large fraction of "stake" shares in the pool) can donate NEAR directly to the pool and call `ping()` to convert that donation into an artificial, permanent increase of `total_staked_balance` attributed pro-rata to existing shareholders, most of it to themselves. This:
- Inflates `get_account_staked_balance` / `get_account_total_balance` / `get_total_staked_balance`, which are the values other on-chain and off-chain consumers rely on to represent legitimately earned validator rewards, letting the attacker present manipulated/self-funded "rewards" as protocol-earned value.
- Because the lockup contract's `refresh_staking_pool_balance` / `on_get_account_total_balance` flow trusts the staking pool's reported total balance to compute the lockup owner's withdrawable ("known deposited") balance [4](#0-3) , a lockup owner who points their delegation at a staking-pool instance they control (or collude with) can use this donation trick to fabricate "staking rewards" and pull them into the lockup account's liquid balance, which is not subject to the vesting/lockup release schedule the same way principal is.

This matches the in-scope High-severity class: "Share, reward, vesting, refund, whitelist, or balance-accounting divergence that lets an unprivileged user over-credit value, bypass fees or limits."

### Likelihood Explanation
The attack requires only (a) staking some amount into the target pool to obtain shares, (b) sending a plain NEAR transfer to the pool's account, and (c) calling the public `ping()` method — all fully permissionless, requiring no privileged role. The pool contract already documents at initialization that the initial balance is used specifically "to prevent inflating the price of the share too much" [5](#0-4) , which confirms the developers were aware share-price inflation via balance manipulation is a real concern, but the mitigation only covers the initialization case, not ongoing donations.

### Recommendation
Do not derive `total_reward` from the raw `env::account_balance()` delta. Instead, only recognize rewards from validator staking (`env::account_locked_balance()` delta) and separately track deposits/withdrawals through the accounted `deposit`/`withdraw` paths, ignoring unaccounted balance increases from direct transfers, or require that any unaccounted balance increase be swept to a designated pool-wide fund rather than being attributed as per-share reward.

### Proof of Concept
1. Attacker calls `deposit_and_stake` on `StakingContract`, obtaining `stake_shares` for `amount` NEAR.
2. Attacker sends a plain NEAR `Transfer` action (not a `deposit()` function call) of `D` NEAR directly to the staking-pool contract account.
3. Attacker (or anyone) calls `ping()`. `internal_ping()` computes `total_balance = locked + account_balance() - 0`, sees `total_reward = D`, and adds `D` (minus owner fee) to `self.total_staked_balance`, permanently increasing the "stake" share price [6](#0-5) .
4. `get_account_staked_balance`/`get_account_total_balance` for the attacker's account now reports an inflated value proportional to the attacker's share of `total_stake_shares`, funded largely by their own donation, with no corresponding real validator reward having been earned.

### Citations

**File:** staking-pool/src/internal.rs (L192-246)
```rust
    /// Distributes rewards after the new epoch. It's automatically called before every action.
    /// Returns true if the current epoch height is different from the last epoch height.
    pub(crate) fn internal_ping(&mut self) -> bool {
        let epoch_height = env::epoch_height();
        if self.last_epoch_height == epoch_height {
            return false;
        }
        self.last_epoch_height = epoch_height;

        // New total amount (both locked and unlocked balances).
        // NOTE: We need to subtract `attached_deposit` in case `ping` called from `deposit` call
        // since the attached deposit gets included in the `account_balance`, and we have not
        // accounted it yet.
        let total_balance =
            env::account_locked_balance() + env::account_balance() - env::attached_deposit();

        assert!(
            total_balance >= self.last_total_balance,
            "The new total balance should not be less than the old total balance"
        );
        let total_reward = total_balance - self.last_total_balance;
        if total_reward > 0 {
            // The validation fee that the contract owner takes.
            let owners_fee = self.reward_fee_fraction.multiply(total_reward);

            // Distributing the remaining reward to the delegators first.
            let remaining_reward = total_reward - owners_fee;
            self.total_staked_balance += remaining_reward;

            // Now buying "stake" shares for the contract owner at the new share price.
            let num_shares = self.num_shares_from_staked_amount_rounded_down(owners_fee);
            if num_shares > 0 {
                // Updating owner's inner account
                let owner_id = self.owner_id.clone();
                let mut account = self.internal_get_account(&owner_id);
                account.stake_shares += num_shares;
                self.internal_save_account(&owner_id, &account);
                // Increasing the total amount of "stake" shares.
                self.total_stake_shares += num_shares;
            }
            // Increasing the total staked balance by the owners fee, no matter whether the owner
            // received any shares or not.
            self.total_staked_balance += owners_fee;

            env::log(
                format!(
                    "Epoch {}: Contract received total rewards of {} tokens. New total staked balance is {}. Total number of shares {}",
                    epoch_height, total_reward, self.total_staked_balance, self.total_stake_shares,
                )
                    .as_bytes(),
            );
            if num_shares > 0 {
                env::log(format!("Total rewards fee is {} stake shares.", num_shares).as_bytes());
            }
        }
```

**File:** staking-pool/src/lib.rs (L168-172)
```rust
    /// curve) and initial reward fee fraction that owner charges for the validation work.
    ///
    /// The entire current balance of this contract will be used to stake. This allows contract to
    /// always maintain staking shares that can't be unstaked or withdrawn.
    /// It prevents inflating the price of the share too much.
```

**File:** staking-pool/src/lib.rs (L209-236)
```rust
    pub fn ping(&mut self) {
        if self.internal_ping() {
            self.internal_restake();
        }
    }

    /// Deposits the attached amount into the inner account of the predecessor.
    #[payable]
    pub fn deposit(&mut self) {
        let need_to_restake = self.internal_ping();

        self.internal_deposit();

        if need_to_restake {
            self.internal_restake();
        }
    }

    /// Deposits the attached amount into the inner account of the predecessor and stakes it.
    #[payable]
    pub fn deposit_and_stake(&mut self) {
        self.internal_ping();

        let amount = self.internal_deposit();
        self.internal_stake(amount);

        self.internal_restake();
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
