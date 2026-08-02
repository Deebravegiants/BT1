## Custody Analog Found

### Title
Unremovable Shareholder in `vesting::distribute` Causes Permanent Denial-of-Service of All Vesting Payouts and Withdrawals - (File: `aptos-move/framework/aptos-framework/sources/vesting.move`)

### Summary
`vesting::distribute` iterates over the full, on-chain, persistent list of a vesting contract's shareholders in a single, non-skippable loop, sending each shareholder's cut via `aptos_account::deposit_coins`. If any single shareholder's address is not registered to receive `AptosCoin` and that shareholder (or anyone controlling that unused address before it is ever funded) calls the unprivileged `aptos_account::set_allow_direct_coin_transfers(false)`, every future call to `distribute()` aborts on that one recipient. Because `terminate_vesting_contract` and `admin_withdraw` both depend on a successful `distribute()`, this permanently locks the entire pool's remaining grant and unlocked rewards for **every** shareholder, not just the misbehaving one. This is a structural analog to the reported USDC blacklist bug: a single unprivileged, uncooperative recipient in a persistent processing loop bricks the whole batch with no skip/retry mechanism.

### Finding Description
`distribute()` withdraws unlocked stake and then loops unconditionally over `grant_pool.shareholders()`, calling `aptos_account::deposit_coins` for each recipient: [1](#0-0) 

`aptos_account::deposit_coins` only checks `can_receive_direct_coin_transfers` (and thus can abort) when the recipient's `CoinStore<CoinType>` does not yet exist: [2](#0-1) 

`can_receive_direct_coin_transfers` returns `false` once an account has called the fully unprivileged, self-service `set_allow_direct_coin_transfers(account, false)`: [3](#0-2) 

Critically, `create_vesting_contract` validates that the `withdrawal_address` is registered for APT, but performs **no such check on the `shareholders` list**: [4](#0-3) 

By contrast, the team explicitly patched this exact class of bug for *beneficiaries* — `set_beneficiary` requires the new beneficiary to already be APT-registered, with a comment showing they understood the failure mode: [5](#0-4) 

That mitigation was never applied to the original `shareholders` vector supplied to `create_vesting_contract`, leaving the same root cause open for the initial shareholder set. Once one shareholder (an address never yet registered for `AptosCoin`) opts out of arbitrary direct transfers, `distribute()` will abort at that shareholder's turn in the loop every single time it is invoked, because the loop has no skip/try-catch/2-step semantics — exactly the pattern flagged in the referenced report (`for` loop over a persistent queue with no isolation between entries).

Downstream, this doesn't just block `distribute()`:
- `terminate_vesting_contract` calls `distribute` before it can proceed: [6](#0-5) 
- `admin_withdraw` requires `state == VESTING_POOL_TERMINATED`, which is unreachable if `terminate_vesting_contract` can never complete: [7](#0-6) 

### Impact Explanation
This is a custody-grade impact: it results in **permanent, non-recoverable loss of access** to APT held in the vesting contract's underlying stake pool for all shareholders — not just the griefing party. Vested grants, accumulated staking rewards, and even admin's ability to recover funds via `admin_withdraw` after termination are all frozen indefinitely, since every path to move value out of the pool routes through the same unconditional, unskippable shareholder loop in `distribute()`. This is a full denial of custody/withdrawal for legitimate value holders caused entirely by an unprivileged action from a single low-stake participant.

### Likelihood Explanation
The action required is trivial and fully unprivileged: any address included as a shareholder in `create_vesting_contract` (which does not validate their APT registration status, unlike `withdrawal_address` and later-set beneficiaries) can call `set_allow_direct_coin_transfers(false)` on itself before ever being registered for `AptosCoin`. No special role, capital, or governance access is needed — only inclusion as one of potentially many shareholders (up to `MAXIMUM_SHAREHOLDERS`). Note: this analysis assumes `aptos_account::deposit_coins<AptosCoin>` still performs the registration/direct-transfer check described above for the AptosCoin type as used by `vesting.move`; if AptosCoin's underlying storage has been fully migrated such that `coin::is_account_registered<AptosCoin>` always resolves true for all accounts, this specific vector would not trigger — this migration-dependent detail could not be fully verified in this review and would need confirmation in a live/current framework build.

### Recommendation
- Validate at `create_vesting_contract` time that every shareholder address is registered for APT (mirroring the existing check already applied to `withdrawal_address` and to `set_beneficiary`).
- Make `distribute()` resilient to individual recipient failures: either skip/queue failed distributions for later manual claim (pull-based per-shareholder withdrawal) rather than push-based batch iteration, or wrap each recipient's deposit so a single failure does not abort the whole loop.
- Decouple `terminate_vesting_contract`/`admin_withdraw` from requiring a fully successful `distribute()` over all shareholders.

### Proof of Concept
1. Admin calls `vesting::create_vesting_contract` with a shareholder list including address `X`, an account that exists but has never registered a `CoinStore<AptosCoin>` (`shareholders` is not validated for APT registration, per `vesting.move:549-558`).
2. `X`'s owner calls `aptos_account::set_allow_direct_coin_transfers(X_signer, false)` — a permissionless call requiring no balance or role (`aptos_account.move:187-219`).
3. Time passes; rewards/vested amounts accrue. Anyone calls `vesting::distribute(contract_address)`.
4. The loop reaches `X` and calls `aptos_account::deposit_coins(X, ...)`; since `X` has no `CoinStore<AptosCoin>` and `can_receive_direct_coin_transfers(X) == false`, this aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` (`aptos_account.move:111-131`), reverting the entire transaction.
5. Every subsequent call to `distribute`, `terminate_vesting_contract`, and `admin_withdraw` on this contract fails identically and permanently, locking the vesting pool's stake and rewards for all shareholders.

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

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L730-740)
```text
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
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L770-785)
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

        // Unlock all remaining active stake.
        vesting_contract.state = VESTING_POOL_TERMINATED;
        vesting_contract.remaining_grant = 0;
        unlock_stake(vesting_contract, active_stake);
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L795-811)
```text
    /// Withdraw all funds to the preset vesting contract's withdrawal address. This can only be called if the contract
    /// has already been terminated.
    public entry fun admin_withdraw(admin: &signer, contract_address: address) acquires VestingContract {
        let vesting_contract = borrow_global<VestingContract>(contract_address);
        assert!(
            vesting_contract.state == VESTING_POOL_TERMINATED,
            error::invalid_state(EVESTING_CONTRACT_STILL_ACTIVE)
        );

        let vesting_contract = borrow_global_mut<VestingContract>(contract_address);
        verify_admin(admin, vesting_contract);
        let coins = withdraw_stake(vesting_contract, contract_address);
        let amount = coin::value(&coins);
        if (amount == 0) {
            coin::destroy_zero(coins);
            return
        };
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L915-927)
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

        let vesting_contract = borrow_global_mut<VestingContract>(contract_address);
        verify_admin(admin, vesting_contract);

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

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L187-231)
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
                DirectCoinTransferConfigUpdated {
                    account: addr,
                    new_allow_direct_transfers: allow
                }
            );
            move_to(account, direct_transfer_config);
        };
    }

    #[view]
    /// Return true if `account` can receive direct transfers of coins that they have not explicitly registered to
    /// receive.
    ///
    /// By default, this returns true if an account has not explicitly set whether the can receive direct transfers.
    public fun can_receive_direct_coin_transfers(
        account: address
    ): bool acquires DirectTransferConfig {
        !exists<DirectTransferConfig>(account)
            || borrow_global<DirectTransferConfig>(account).allow_arbitrary_coin_transfers
    }
```
