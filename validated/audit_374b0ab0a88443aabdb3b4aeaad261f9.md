### Title
Unprivileged opt-out from direct coin transfers permanently DoSes `vesting::distribute`/`terminate_vesting_contract`, locking staked APT in the vesting resource account - (File: `aptos-move/framework/aptos-framework/sources/vesting.move`)

### Summary
The Solidity report's core custody invariant is: *a completion step (`endAuction`) that pushes value to a fixed recipient must not be able to permanently brick the whole flow just because that one recipient cannot accept the transfer*. The Aptos analog is `vesting::distribute`, which iterates over all shareholders of a vesting contract and calls `aptos_account::deposit_coins` for each one in an unguarded loop. If any single shareholder has opted out of un-registered direct coin transfers via `aptos_account::set_allow_direct_coin_transfers(false)`, that call aborts the entire transaction — blocking distribution to *every* shareholder and preventing `terminate_vesting_contract` (which calls `distribute` first) from ever completing, permanently locking the vesting contract's staked APT in its resource account.

### Finding Description
`vesting::distribute` withdraws all currently-withdrawable stake and then loops over every shareholder, unconditionally calling `aptos_account::deposit_coins`: [1](#0-0) 

`aptos_account::deposit_coins` aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` if the destination account is not registered for the `CoinType` and has opted out of direct transfers: [2](#0-1) 

Any account holder can flip this opt-out flag on their own account at any time, with no cost or special privilege, via `set_allow_direct_coin_transfers`: [3](#0-2) 

Because a shareholder's own address can be added to a vesting contract by an admin, and that shareholder (or anyone controlling that address after being added) can later call `set_allow_direct_coin_transfers(false)` and never re-register the coin, the `for_each_ref` loop in `distribute()` has no per-recipient error isolation (no try/catch equivalent in Move) — one failing deposit aborts the whole transaction, exactly like the Solidity `transfer()` DoS pattern (a single failing recipient blocks completion for everyone).

The impact compounds because `terminate_vesting_contract` calls `distribute(contract_address)` unconditionally as its first step before transitioning state to `VESTING_POOL_TERMINATED`: [4](#0-3) 

If `distribute` cannot complete due to one poisoned shareholder, `terminate_vesting_contract` can never succeed either, so the admin can never reach the `admin_withdraw` path (which requires `state == VESTING_POOL_TERMINATED`): [5](#0-4) 

The identical unguarded-loop pattern also exists in `staking_contract::distribute_internal`, which vesting's staking layer depends on indirectly: [6](#0-5) 

### Impact Explanation
This breaks the custody invariant that value held by a resource account (the vesting contract's stake pool, funded by the admin/grantor) must remain recoverable by its rightful owners. A single unprivileged shareholder can, without colluding with anyone, permanently prevent:
- All other shareholders from receiving vested/reward distributions (`distribute`, `distribute_many`).
- The admin from ever terminating the vesting contract and reclaiming remaining funds (`terminate_vesting_contract` → `admin_withdraw`).

This is a non-recoverable, permanent lock of resource-account-held APT — no on-chain code path exists to skip a failing recipient or exclude it from the shareholder set once distribution begins.

### Likelihood Explanation
Likelihood is high: any shareholder who is a normal, unprivileged Aptos account can call `set_allow_direct_coin_transfers(false)` on their own address at zero cost, and never explicitly register `AptosCoin` (which is very plausible for a wallet controlled by a script, cold-storage flow, or someone intentionally griefing the vesting pool if they have a grudge against the admin or other shareholders). No special permission or timing race is required — one transaction from any single shareholder is sufficient to trigger the condition on the next `distribute`/`terminate_vesting_contract` call.

### Recommendation
- In `vesting::distribute` (and `staking_contract::distribute_internal`), do not let a single recipient's failed deposit abort the whole batch. Use a fallible deposit path (e.g., check `aptos_account::can_receive_direct_coin_transfers`/`coin::is_account_registered` before calling `deposit_coins`, and if the recipient cannot receive, route their share to an escrow/claimable store instead of aborting).
- Decouple `terminate_vesting_contract`'s state transition from a successful `distribute()` call, or provide an explicit "force terminate, skip stuck recipients" governance path so admin funds are never permanently trapped by one recipient's account configuration.

### Proof of Concept
1. Admin creates a vesting contract with shareholders `[A, B]` via `vesting::create_vesting_contract`.
2. Shareholder `B` calls `aptos_account::set_allow_direct_coin_transfers(&B, false)` and never calls `coin::register<AptosCoin>`.
3. Time passes; rewards/vested stake becomes withdrawable.
4. Anyone calls `vesting::distribute(contract_address)`. The loop reaches `B`, calls `aptos_account::deposit_coins(B, ...)`, which aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` since `B` is unregistered and opted out — the whole transaction reverts, so shareholder `A` also receives nothing.
5. Admin calls `vesting::terminate_vesting_contract`, which calls `distribute` internally and aborts for the same reason — the vesting contract can never be terminated, and the remaining grant/staked APT is permanently stuck in the resource account.

Note: I was unable to fully verify from the index whether any external mechanism (e.g., a later add-on module or forced-registration path) exists elsewhere in the repo that could mitigate this before mainnet deployment; this assessment is based solely on the `vesting.move`/`aptos_account.move`/`staking_contract.move` sources retrieved.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L730-748)
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

        // Send any remaining "dust" (leftover due to rounding error) to the withdrawal address.
        if (coin::value(&coins) > 0) {
            aptos_account::deposit_coins(vesting_contract.withdrawal_address, coins);
        } else {
            coin::destroy_zero(coins);
        };

```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L770-793)
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

        emit(
            Terminate {
                admin: vesting_contract.admin,
                vesting_contract_address: contract_address,
            },
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L795-821)
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
        aptos_account::deposit_coins(vesting_contract.withdrawal_address, coins);

        emit(
            AdminWithdraw {
                admin: vesting_contract.admin,
                vesting_contract_address: contract_address,
                amount,
            },
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L109-131)
```text
    /// Convenient function to deposit a custom CoinType into a recipient account that might not exist.
    /// This would create the recipient account first and register it to receive the CoinType, before transferring.
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

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L187-219)
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
```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L888-911)
```text
        // Buy all recipients out of the distribution pool.
        while (distribution_pool.shareholders_count() > 0) {
            let recipients = distribution_pool.shareholders();
            let recipient = recipients[0];
            let current_shares = distribution_pool.shares(recipient);
            let amount_to_distribute =
                distribution_pool.redeem_shares(recipient, current_shares);
            // If the recipient is the operator, send the commission to the beneficiary instead.
            if (recipient == operator) {
                recipient = beneficiary_for_operator(operator);
            };
            aptos_account::deposit_coins(
                recipient, coin::extract(&mut coins, amount_to_distribute)
            );

            emit(
                Distribute {
                    operator,
                    pool_address,
                    recipient,
                    amount: amount_to_distribute
                }
            );
        };
```
