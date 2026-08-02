### Title
`vesting::distribute()` can be permanently blocked for all shareholders by any single shareholder opting out of direct coin transfers - ([File: aptos-move/framework/aptos-framework/sources/vesting.move])

### Summary
`aptos_framework::vesting::distribute()` iterates over **all** shareholders of a vesting contract in a single loop and calls `aptos_account::deposit_coins` for each one. `deposit_coins` aborts if the recipient account is not registered for `AptosCoin` **and** has disabled direct coin transfers via `aptos_account::set_allow_direct_coin_transfers(false)`. Because any shareholder (or their beneficiary) fully controls this opt-out flag on their own account and is added to the pool by the admin without any registration/opt-in check at contract creation time, a single self-griefing shareholder can make `distribute()` (and thus `terminate_vesting_contract`, which calls `distribute()`) permanently revert, locking the vested/reward funds for every other shareholder in that vesting contract.

### Finding Description
`distribute()` withdraws all currently withdrawable stake and pays every shareholder in one atomic loop: [1](#0-0) 

Each payment goes through `aptos_account::deposit_coins`: [2](#0-1) 

`deposit_coins` only auto-creates/registers the account if it doesn't exist; for an *existing* account that is not registered for `AptosCoin`, it requires `can_receive_direct_coin_transfers(to)` to be true, i.e. the account must not have opted out via `set_allow_direct_coin_transfers`: [3](#0-2) 

Crucially, `create_vesting_contract` only checks that the `withdrawal_address` is registered for APT — it never validates that the shareholders themselves are registered/able to receive APT: [4](#0-3) 

The framework authors were clearly aware of exactly this class of bug: `set_beneficiary()` explicitly requires the *new beneficiary* to be registered for APT specifically "so distribute() wouldn't fail and block all other accounts from receiving APT if one beneficiary is not registered": [5](#0-4) 

However, this guard only covers the beneficiary-update path. It does not cover:
1. The original shareholder addresses supplied at `create_vesting_contract` time (never checked for APT registration).
2. A shareholder/beneficiary who *was* registered at the time of the check but later self-revokes direct-transfer permission before ever calling `coin::register<AptosCoin>()`, or an account that is registered for a different coin type but not `AptosCoin` and disables the flag.

Since `is_account_registered<CoinType>(to)` is what gates the `can_receive_direct_coin_transfers` check, any shareholder who simply never registers for `AptosCoin` (registration is fully optional/self-controlled) and calls `set_allow_direct_coin_transfers(account, false)` on their own account will cause `deposit_coins` to abort with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` whenever `distribute()` reaches their turn in the loop. Because a Move transaction abort reverts **all** state changes made in that call (including the withdrawal from the stake pool and the `pool_u64` share redemptions for shareholders processed earlier in the same loop), the entire `distribute()` call fails — for every shareholder, not just the malicious one.

There is no per-shareholder `distribute` variant and no way to skip a failing recipient; `distribute_many()` simply calls `distribute()` once per contract address, so it doesn't help. `terminate_vesting_contract()` itself calls `distribute()` first, so termination/wind-down of the contract is blocked too: [6](#0-5) [7](#0-6) 

### Impact Explanation
This is a stronger analog than the original P2P report: in the ETH case there was an alternative selective-refund function (`refundAll(address[])`) to route around a single poisoned entry. In `vesting.move` there is **no per-shareholder distribution path** — `distribute()` (and `distribute_many`) are the only entry points that release vested APT and staking rewards, and both operate over the full shareholder set atomically. A single uncooperative/malicious shareholder can therefore indefinitely lock the vested grant and accumulated staking rewards owed to **every other shareholder** in the contract, and also block `terminate_vesting_contract`/`admin_withdraw` recovery, since termination itself calls `distribute()` first. This is a non-recoverable/permanent lock of custody-held (staked) APT value for co-shareholders, satisfying the custody-impact bar of "permanent lock or non-recoverable loss of ... resource-account-held value" (the vesting contract account holds the staked funds).

### Likelihood Explanation
Likelihood is high for any real-world multi-shareholder vesting contract: any shareholder (or an attacker who convinces/becomes a beneficiary) merely needs to avoid registering for `AptosCoin` and call the already-public, unprivileged `set_allow_direct_coin_transfers(false)` on their own account — no special permission, no admin collusion, and no cost beyond a single transaction fee. Because vesting contracts are long-lived, multi-year staking constructs with several shareholders (e.g., team/investor grants), the probability that a griefing or extortion-motivated shareholder exists over that lifetime is non-trivial.

### Recommendation
- In `create_vesting_contract`, require every shareholder address to be registered/able to receive `AptosCoin`, mirroring the check already added in `set_beneficiary`.
- In `distribute()`, do not let one recipient's failure abort the whole batch: wrap each per-shareholder deposit in a way that on failure keeps the funds in the pool (e.g., re-credit their `pool_u64` shares) instead of reverting the entire loop, or use a "pull" model where amounts are escrowed per-shareholder and each shareholder independently calls a claim function to receive their share.
- Consider disallowing shareholders whose accounts are not APT-registered from remaining shareholders indefinitely, or add an escape hatch that lets the admin skip/redirect a shareholder's payout to `withdrawal_address` if their deposit repeatedly fails.

### Proof of Concept
1. Admin creates a vesting contract via `create_vesting_contract` with shareholders `[Alice, Bob]`. Neither shareholder is required to be registered for `AptosCoin` at this point (only `withdrawal_address` is checked).
2. Bob (acting maliciously or simply following a "privacy" opt-out flow) never calls `coin::register<AptosCoin>()` and calls `aptos_account::set_allow_direct_coin_transfers(bob_signer, false)` on his own account.
3. Time passes, rewards/vested tokens accrue and become withdrawable from the stake pool.
4. Anyone calls `vesting::distribute(contract_address)`. The loop reaches Bob's turn and calls `aptos_account::deposit_coins(bob_addr, share_of_coins)`; because Bob is unregistered for `AptosCoin` and has opted out, this hits the `assert!(can_receive_direct_coin_transfers(to), ...)` and aborts.
5. The entire `distribute()` transaction reverts — Alice (and Bob) never receive their withdrawable funds, and this remains true for every future call to `distribute()`/`distribute_many()`/`terminate_vesting_contract()` for as long as Bob keeps this configuration, permanently locking the contract's withdrawable value for all shareholders.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L549-558)
```text
        assert!(
            !system_addresses::is_reserved_address(withdrawal_address),
            error::invalid_argument(EINVALID_WITHDRAWAL_ADDRESS),
        );
        assert_account_is_registered_for_apt(withdrawal_address);
        assert!(shareholders.length() > 0, error::invalid_argument(ENO_SHAREHOLDERS));
        assert!(
            buy_ins.length() == shareholders.length(),
            error::invalid_argument(ESHARES_LENGTH_MISMATCH),
        );
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L706-768)
```text
    /// Call `vest` for many vesting contracts.
    public entry fun vest_many(contract_addresses: vector<address>) acquires VestingContract {
        let len = contract_addresses.length();

        assert!(len != 0, error::invalid_argument(EVEC_EMPTY_FOR_MANY_FUNCTION));

        contract_addresses.for_each_ref(|contract_address| {
            let contract_address = *contract_address;
            vest(contract_address);
        });
    }

    /// Distribute any withdrawable stake from the stake pool.
    public entry fun distribute(contract_address: address) acquires VestingContract {
        assert_active_vesting_contract(contract_address);

        let vesting_contract = borrow_global_mut<VestingContract>(contract_address);
        let coins = withdraw_stake(vesting_contract, contract_address);
        let total_distribution_amount = coin::value(&coins);
        if (total_distribution_amount == 0) {
            coin::destroy_zero(coins);
            return
        };

        // Distribute coins to all shareholders in the vesting contract.
        let grant_pool = &vesting_contract.grant_pool;
        let shareholders = &grant_pool.shareholders();
        shareholders.for_each_ref(|shareholder| {
            let shareholder = *shareholder;
            let shares = pool_u64::shares(grant_pool, shareholder);
            let amount = pool_u64::shares_to_amount_with_total_coins(grant_pool, shares, total_distribution_amount);
            let share_of_coins = coin::extract(&mut coins, amount);
            let recipient_address = get_beneficiary(vesting_contract, shareholder);
            aptos_account::deposit_coins(recipient_address, share_of_coins);
        });

        // Send any remaining "dust" (leftover due to rounding error) to the withdrawal address.
        if (coin::value(&coins) > 0) {
            aptos_account::deposit_coins(vesting_contract.withdrawal_address, coins);
        } else {
            coin::destroy_zero(coins);
        };

        emit(
            Distribute {
                admin: vesting_contract.admin,
                vesting_contract_address: contract_address,
                amount: total_distribution_amount,
            },
        );
    }

    /// Call `distribute` for many vesting contracts.
    public entry fun distribute_many(contract_addresses: vector<address>) acquires VestingContract {
        let len = contract_addresses.length();

        assert!(len != 0, error::invalid_argument(EVEC_EMPTY_FOR_MANY_FUNCTION));

        contract_addresses.for_each_ref(|contract_address| {
            let contract_address = *contract_address;
            distribute(contract_address);
        });
    }
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L770-780)
```text
    /// Terminate the vesting contract and send all funds back to the withdrawal address.
    public entry fun terminate_vesting_contract(admin: &signer, contract_address: address) acquires VestingContract {
        assert_active_vesting_contract(contract_address);

        // Distribute all withdrawable coins, which should have been from previous rewards withdrawal or vest.
        distribute(contract_address);

        let vesting_contract = borrow_global_mut<VestingContract>(contract_address);
        verify_admin(admin, vesting_contract);
        let (active_stake, _, pending_active_stake, _) = stake::get_stake(vesting_contract.staking.pool_address);
        assert!(pending_active_stake == 0, error::invalid_state(EPENDING_STAKE_FOUND));
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L915-924)
```text
    public entry fun set_beneficiary(
        admin: &signer,
        contract_address: address,
        shareholder: address,
        new_beneficiary: address,
    ) acquires VestingContract {
        // Verify that the beneficiary account is set up to receive APT. This is a requirement so distribute() wouldn't
        // fail and block all other accounts from receiving APT if one beneficiary is not registered.
        assert_account_is_registered_for_apt(new_beneficiary);

```

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L111-131)
```text
    public fun deposit_coins<CoinType>(
        to: address, coins: Coin<CoinType>
    ) acquires DirectTransferConfig {
        if (!account::exists_at(to)) {
            create_account(to);
            spec {
                // TODO(fa_migration)
                // assert coin::spec_is_account_registered<AptosCoin>(to);
                // assume aptos_std::type_info::type_of<CoinType>() == aptos_std::type_info::type_of<AptosCoin>() ==>
                //     coin::spec_is_account_registered<CoinType>(to);
            };
        };
        if (!coin::is_account_registered<CoinType>(to)) {
            assert!(
                can_receive_direct_coin_transfers(to),
                error::permission_denied(EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS)
            );
            coin::register<CoinType>(&create_signer(to));
        };
        coin::deposit<CoinType>(to, coins)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L187-211)
```text
    /// Set whether `account` can receive direct transfers of coins that they have not explicitly registered to receive.
    public entry fun set_allow_direct_coin_transfers(
        account: &signer, allow: bool
    ) acquires DirectTransferConfig {
        let addr = signer::address_of(account);
        if (exists<DirectTransferConfig>(addr)) {
            let direct_transfer_config = borrow_global_mut<DirectTransferConfig>(addr);
            // Short-circuit to avoid emitting an event if direct transfer config is not changing.
            if (direct_transfer_config.allow_arbitrary_coin_transfers == allow) { return };

            direct_transfer_config.allow_arbitrary_coin_transfers = allow;

            emit(
                DirectCoinTransferConfigUpdated {
                    account: addr,
                    new_allow_direct_transfers: allow
                }
            );
        } else {
            let direct_transfer_config = DirectTransferConfig {
                allow_arbitrary_coin_transfers: allow,
                update_coin_transfer_events: new_event_handle<
                    DirectCoinTransferConfigUpdatedEvent>(account)
            };
            emit(
```
