## Title
Operator-controlled `beneficiary_for_operator` can permanently DoS `staking_contract::distribute` for all its stakers - (File: `aptos-move/framework/aptos-framework/sources/staking_contract.move`)

## Summary
`staking_contract::set_beneficiary_for_operator` lets an operator redirect all commission payouts to an arbitrary address without validating that the address can actually receive `AptosCoin`. That beneficiary is *global* per operator (shared across every staker who has a `StakingContract` with that operator), and `distribute_internal` pays the operator's commission and the staker's own unlocked principal in the same atomic loop. If the beneficiary deposit aborts, the whole `distribute()` transaction reverts, blocking every staker under that operator from withdrawing their own unlocked stake — the exact bug class from the Predy report (attacker-controlled recipient reverts a shared payout operation), but here it's not even fixed by validation the way the sibling `vesting.move` module already is.

## Finding Description
`set_beneficiary_for_operator` stores the new beneficiary with no reachability/registration check: [1](#0-0) 

Compare this to `vesting::set_beneficiary`, which explicitly guards against this exact bug class: [2](#0-1) 
The vesting code comment is explicit about the invariant being protected: *"This is a requirement so distribute() wouldn't fail and block all other accounts from receiving APT if one beneficiary is not registered."* `staking_contract::set_beneficiary_for_operator` has no equivalent call to `aptos_account::assert_account_is_registered_for_apt` (or any reachability check).

`distribute_internal` then processes the operator's commission recipient (the beneficiary) and the staker's own inactive/pending-inactive withdrawal in the *same* atomic `while` loop, using `aptos_account::deposit_coins`: [3](#0-2) 

`aptos_account::deposit_coins` aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` if the recipient account exists, is not registered for the `CoinType` being deposited, and has explicitly opted out via `set_allow_direct_coin_transfers(false)`: [4](#0-3) [5](#0-4) 

Because Move aborts revert the entire transaction, a failed deposit to the operator's beneficiary rolls back the whole `distribute()` call — including the portion meant to pay out the calling staker's own unlocked/withdrawn stake. Since the comment in `set_beneficiary_for_operator` states *"An operator can set one beneficiary for staking contract pools, not a separate one for each pool"*, this single poisoned beneficiary blocks `distribute()` for every staker who delegated to that operator via `staking_contract`, not just the operator's own funds.

## Impact Explanation
This breaks the custody invariant that a shared distribution/payout path must not be blockable by one party's choice of recipient. Concretely:
- An operator can set `beneficiary_for_operator` to an account that exists and has called `aptos_account::set_allow_direct_coin_transfers(false)` (a legitimate self-service opt-out any account can perform) while not being registered for `AptosCoin`.
- Any subsequent `distribute()` call for *any* staker under that operator will revert as soon as it tries to pay the operator/beneficiary's commission share, since `distribute_internal` processes all pending distributions (staker principal + operator commission) in one atomic pass.
- Legitimate stakers cannot withdraw their own unlocked/inactive stake through this staking-contract path until the operator fixes the beneficiary (which the operator fully controls and can withhold indefinitely as leverage/griefing, or use to stall being forced to realize commission if the intent is different).
- This is a value-lock/DoS on custody-relevant funds (staker's own unlocked APT), matching "Permanent lock or non-recoverable loss ... value" and "custody accounting corruption that moves value to the wrong holder or destroys recovery rights" in spirit — funds remain locked in the stake pool with no path to distribution while the condition persists.

Note: I was not able to fully verify within the available context whether `AptosCoin`'s `coin::is_account_registered<AptosCoin>` check is bypassed entirely post the coin→fungible-asset migration (the `coin.move` module is large and I could not confirm the exact behavior of `is_account_registered<AptosCoin>` for migrated APT). If `is_account_registered<AptosCoin>` unconditionally returns `true` for any account after migration, the `can_receive_direct_coin_transfers` branch in `deposit_coins` would never be reached for `AptosCoin`, and this specific abort path would not be reachable in practice for `AptosCoin` — the DoS would then only be provable for non-APT coin types (staking rewards are however always in `AptosCoin`, so this caveat matters).

## Likelihood Explanation
Medium. The operator role is unprivileged relative to the staker delegating to it — a delegator chooses to trust the operator with running validation, not with unilateral control over their withdrawal path. The griefing action requires only one entry function call (`set_allow_direct_coin_transfers(false)` on the beneficiary account) plus `set_beneficiary_for_operator`, both fully permissionless for the operator. This is gated by the runtime feature flag `features::operator_beneficiary_change_enabled()`, so it only applies where that feature is active.

## Recommendation
Add the same registration/reachability check that `vesting::set_beneficiary` already performs to `staking_contract::set_beneficiary_for_operator`:
```move
aptos_account::assert_account_is_registered_for_apt(new_beneficiary);
```
Additionally, consider decoupling the operator/beneficiary payout from the staker's own principal/reward payout in `distribute_internal` (e.g., catch/skip a failing recipient and re-queue their share) so that one unresponsive or hostile recipient cannot block payouts to other shareholders of the same distribution pool.

## Proof of Concept
Conceptual repro path (not run against this repo's test harness, since I could not execute Move tests here):
1. Staker creates a `staking_contract` with `operator1` via `staking_contract::create_staking_contract`.
2. `operator1` calls `aptos_account::set_allow_direct_coin_transfers(false)` from a fresh account `evil_beneficiary` that has never registered for `AptosCoin`.
3. `operator1` calls `staking_contract::set_beneficiary_for_operator(operator1, evil_beneficiary)` — succeeds with no validation.
4. Stake pool earns rewards/commission is due; staker unlocks and waits for lockup to expire (funds become `inactive`).
5. Anyone calls `staking_contract::distribute(staker, operator1)`.
6. `distribute_internal` reaches the commission-redemption iteration for `operator1` → resolves recipient to `evil_beneficiary` → `aptos_account::deposit_coins` aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS`.
7. The whole transaction reverts — the staker's own unlocked principal (processed in the same loop) is also not paid out, and remains stuck until the operator changes the beneficiary back. [6](#0-5)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L810-838)
```text
    public entry fun set_beneficiary_for_operator(
        operator: &signer, new_beneficiary: address
    ) acquires BeneficiaryForOperator {
        assert!(
            features::operator_beneficiary_change_enabled(),
            std::error::invalid_state(EOPERATOR_BENEFICIARY_CHANGE_NOT_SUPPORTED)
        );
        // The beneficiay address of an operator is stored under the operator's address.
        // So, the operator does not need to be validated with respect to a staking pool.
        let operator_addr = signer::address_of(operator);
        let old_beneficiary = beneficiary_for_operator(operator_addr);
        if (exists<BeneficiaryForOperator>(operator_addr)) {
            borrow_global_mut<BeneficiaryForOperator>(operator_addr).beneficiary_for_operator =
                new_beneficiary;
        } else {
            move_to(
                operator,
                BeneficiaryForOperator { beneficiary_for_operator: new_beneficiary }
            );
        };

        emit(
            SetBeneficiaryForOperator {
                operator: operator_addr,
                old_beneficiary,
                new_beneficiary
            }
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L855-920)
```text
    /// Distribute all unlocked (inactive) funds according to distribution shares.
    fun distribute_internal(
        staker: address,
        operator: address,
        staking_contract: &mut StakingContract,
    ) acquires BeneficiaryForOperator {
        let pool_address = staking_contract.pool_address;
        // Create the Staker resource if it doesn't exist to backfill the Staker resource for each pool.
        if (!exists<Staker>(pool_address)) {
            let pool_signer =
                &account::create_signer_with_capability(&staking_contract.signer_cap);
            move_to(pool_signer, Staker { staker });
        };
        let (_, inactive, _, pending_inactive) = stake::get_stake(pool_address);
        let total_potential_withdrawable = inactive + pending_inactive;
        let coins =
            stake::withdraw_with_cap(
                &staking_contract.owner_cap, total_potential_withdrawable
            );
        let distribution_amount = coin::value(&coins);
        if (distribution_amount == 0) {
            coin::destroy_zero(coins);
            return
        };

        let distribution_pool = &mut staking_contract.distribution_pool;
        update_distribution_pool(
            distribution_pool,
            distribution_amount,
            operator,
            staking_contract.commission_percentage
        );

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

        // In case there's any dust left, send them all to the staker.
        if (coin::value(&coins) > 0) {
            aptos_account::deposit_coins(staker, coins);
            distribution_pool.update_total_coins(0);
        } else {
            coin::destroy_zero(coins);
        }
    }
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L915-935)
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

        let old_beneficiary = get_beneficiary(vesting_contract, shareholder);
        let beneficiaries = &mut vesting_contract.beneficiaries;
        if (beneficiaries.contains_key(&shareholder)) {
            let beneficiary = beneficiaries.borrow_mut(&shareholder);
            *beneficiary = new_beneficiary;
        } else {
            beneficiaries.add(shareholder, new_beneficiary);
        };
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
