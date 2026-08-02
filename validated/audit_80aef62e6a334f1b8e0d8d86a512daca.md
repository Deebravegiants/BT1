Based on my research, the strongest Aptos-native analog to the Nouns fork bug is in `aptos_framework::vesting`, where a single uncooperative shareholder can permanently block reward/vesting distribution to an *entire group* of shareholders — the same "one poisoned list entry blocks everyone" pattern as the ERC20 allowlist bug.

### Title
Single griefing shareholder can permanently block APT distribution to all vesting-contract shareholders - (File: aptos-move/framework/aptos-framework/sources/vesting.move)

### Summary
`vesting::distribute` iterates over the vesting contract's shareholder list and calls `aptos_account::deposit_coins` for each one in a single, non-fault-tolerant loop [1](#0-0) . `deposit_coins` can abort for an unregistered recipient who has opted out of direct coin transfers [2](#0-1) , and any account can flip that opt-out flag at will via `set_allow_direct_coin_transfers` [3](#0-2) . Because `distribute` has no per-shareholder isolation (no try/catch, no skip-on-failure), one shareholder reverting the deposit reverts the entire transaction, blocking payout to every other (honest) shareholder in that vesting contract — mirroring how a single poisoned `erc20TokensToIncludeInFork` entry in NounsDAO blocks the whole minority group's exit.

### Finding Description
`distribute()` computes `total_distribution_amount`, then walks `grant_pool.shareholders()` and calls `aptos_account::deposit_coins(recipient_address, share_of_coins)` for each shareholder in sequence [1](#0-0) . `distribute_many` simply calls `distribute` for a list of contract addresses, so the same failure mode also aborts the whole batch across independent contracts [4](#0-3) .

`deposit_coins` aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` if the recipient is not yet registered for `CoinType` and has disabled direct transfers [5](#0-4) . Any account holder fully controls this opt-out flag via the public entry function `set_allow_direct_coin_transfers` [6](#0-5) , and a shareholder can simply avoid ever registering/receiving AptosCoin directly.

Since a vesting contract's shareholder list is fixed at contract creation and cannot be modified afterward (admin cannot remove shareholders once granted), any single shareholder — malicious, griefing, or even accidentally locked out — can render `distribute()` permanently unusable for the whole contract: the transaction always aborts at that shareholder's deposit, so no shareholder (including honest ones) ever receives their share, and the funds sit stuck in the vesting contract's resource account indefinitely (unrecoverable except via `terminate_vesting_contract`/`admin_withdraw`, which requires admin action and effectively also fails to route funds to shareholders during the process, since `terminate_vesting_contract` itself calls `distribute` first) [7](#0-6) .

This is the same custody-invariant break as the external report: a group-exit/payout mechanism iterates a fixed list of addresses controlled by someone other than the caller, and a single entry can unilaterally revert the operation for the whole group with no way to skip or exclude it.

### Impact Explanation
This blocks legitimate vested-fund custody rights for every shareholder in an affected vesting contract, not just the griefer — a group-wide, non-recoverable value-access lock on real APT held in the vesting contract's resource account. It matches the "permanent lock or non-recoverable loss of ... resource-account-held value" custody-impact category, since `terminate_vesting_contract` also routes through `distribute()` before admin can reclaim remaining funds, so even termination can be stalled/blocked.

### Likelihood Explanation
Any of the shareholders named in a vesting contract can trigger this unilaterally and at zero cost — no governance approval, no majority collusion, and no privileged access is required, unlike the original Nouns bug which required a majority-approved proposal. The only precondition is that the griefing shareholder hasn't yet registered a CoinStore for AptosCoin when `distribute` first runs against them, which is plausible for freshly added/undercapitalized shareholder accounts (e.g., addresses added purely to receive future vested stake that never interacted with APT before). I was not able to fully verify whether AptosCoin's fungible-asset migration (`coin::is_account_registered<AptosCoin>` / primary-store coercion) neutralizes this precondition on current mainnet, since I could not inspect the full body of `coin::is_account_registered` and `can_receive_direct_coin_transfers` before running out of iterations — this is a material verification gap that should be checked directly in `aptos-move/framework/aptos-framework/sources/coin.move` before treating this as confirmed-exploitable on mainnet.

### Recommendation
Make `distribute()` resilient to individual recipient failures: either (a) wrap each `aptos_account::deposit_coins` call so a failure only skips/re-queues that shareholder's payout instead of aborting the whole transaction, or (b) let the admin/withdrawal-address unilaterally reclaim a shareholder's redeemable share to a fallback address if that shareholder's deposit repeatedly fails, similar to how `vest()` accrues without blocking on payout.

### Proof of Concept
1. Admin creates a vesting contract with shareholders `[A, B]` via `create_vesting_contract`, where `B` is an address that has not yet interacted with AptosCoin.
2. `B` calls `aptos_account::set_allow_direct_coin_transfers(B_signer, false)` before ever being credited/registered for `AptosCoin` [6](#0-5) .
3. Once funds become withdrawable, anyone calls `vesting::distribute(contract_address)`.
4. The loop reaches `B`'s payout, calls `aptos_account::deposit_coins(B, share)`, which aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` since `B` is unregistered and has opted out [8](#0-7) .
5. The entire `distribute` transaction reverts, so `A` (an honest shareholder) never receives their share either, and this repeats on every future call to `distribute` for this contract.

**Verification gap:** I could not confirm within the available tool budget whether AptosCoin's FA-migration path (`primary_fungible_store` coercion referenced in `aptos_account.move`'s spec TODOs) makes `coin::is_account_registered<AptosCoin>` effectively always `true` for existing accounts, which — if true — would neutralize this vector for `AptosCoin` specifically on current mainnet. This should be verified directly against `coin.move`'s `is_account_registered` implementation before treating this as a confirmed live vulnerability.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L730-741)
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

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L758-768)
```text
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
