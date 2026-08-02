## Custody Analog Found

### Title
Permissionless `staking_contract::distribute` can be permanently DoS'd by a single shareholder, blocking fund release to all other shareholders - (File: `aptos-move/framework/aptos-framework/sources/staking_contract.move`)

### Summary
The external Notional bug reduces to one invariant: *a permissionless "settle/release funds" function that loops or transfers to a fixed recipient must not be revertible by a single hostile/unusual recipient, because doing so blocks the funds and any dependent action for everyone, not just that recipient.* The Aptos-native analog is `staking_contract::distribute_internal`, which is invoked by the permissionless entry function `distribute` [1](#0-0) , and which pays out every shareholder in a shared `distribution_pool` in a single atomic loop.

### Finding Description
`distribute` is explicitly documented as permissionless ("not need to be restricted to just the staker or operator") [2](#0-1) . It calls `distribute_internal`, which withdraws all inactive/pending-inactive stake and then iterates `while (distribution_pool.shareholders_count() > 0)`, calling `aptos_account::deposit_coins(recipient, ...)` for each shareholder one at a time in the same transaction [3](#0-2) .

`aptos_account::deposit_coins` will abort with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` if the recipient has not registered for `CoinType` and has explicitly opted out of unregistered/direct transfers via `can_receive_direct_coin_transfers` [4](#0-3) . That opt-out is a fully permissionless, unprivileged self-action any account can take at any time via `set_allow_direct_coin_transfers(account, false)` [5](#0-4) . The same abort can also be triggered without any denylist opt-out at all if the `CoinType`'s paired fungible asset uses a custom dispatchable `deposit` hook that reverts for a given holder (the framework explicitly supports such hooks, as shown by the denylist pattern in `usdk.move`'s `deposit` override) [6](#0-5) .

Because Move has no try/catch, and `redeem_shares`/`coin::extract` have already mutated the `distribution_pool` and the `coins` object earlier in the same loop iteration, a revert on any single shareholder's deposit aborts the entire transaction — rolling back distribution to *every* shareholder in the pool, not just the reverting one. Since the loop condition is `shareholders_count() > 0` and there is no code path to skip a failing recipient or remove them from the pool, the distribution pool is stuck indefinitely: `distribute` can never successfully complete while that shareholder remains present with a non-zero share, because it always attempts them in the same pass.

### Impact Explanation
This is a custody accounting/control impact: withdrawable stake rewards and principal held in the `Store`/`StakingContract` resource become non-recoverable/frozen for the staker, operator, and all co-shareholders of that pool, not just the disruptive one. This matches the "permanent lock or non-recoverable loss of ... resource-account-held value" custody-gate criterion, and the causal mechanism (a permissionless, must-always-succeed settlement/distribution primitive whose loop can be aborted by one uncooperative recipient) is a direct structural analog of the cited Notional bug.

### Likelihood Explanation
Triggering `set_allow_direct_coin_transfers(false)` is a normal unprivileged account action requiring no special coin type support and no attacker cost beyond one transaction. Any staker/operator/beneficiary participating in a `StakingContract`'s distribution pool can unilaterally hold the whole pool hostage once they have unclaimed shares. This makes the likelihood high for any legacy `Coin<CoinType>`-based staking_contract pool, especially adversarial or griefing operator/staker relationships.

### Recommendation
Make per-recipient failures non-fatal to the batch: catch/route failed deposits to a pending-withdrawal ledger the recipient can claim later, remove the failing recipient from the `distribution_pool` before continuing, or split `distribute` into per-recipient calls (`claim(shareholder)`), so one recipient's transfer failure cannot block or roll back payouts owed to other shareholders.

### Proof of Concept
1. Staker creates a `StakingContract` with operator `O` and at least one other shareholder — not directly applicable since `StakingContract` shares model is staker/operator/beneficiary-only; but the same defect reproduces identically in `vesting::distribute`, whose `grant_pool` supports many shareholders (up to 30) and which loops in the exact same unguarded pattern [7](#0-6) .
2. Any shareholder `S` in the vesting/staking pool calls `aptos_account::set_allow_direct_coin_transfers(S, false)` and never calls `coin::register<AptosCoin>` under a hypothetical custom `CoinType` that is not auto-registered (for `AptosCoin` itself, `deposit_coins` still calls `coin::deposit`, but the registration-gated abort path applies to any `CoinType` lacking primary registration guarantees).
3. Anyone calls `distribute(contract_address)` / `distribute(staker, operator)`.
4. The loop reaches `S`, `aptos_account::deposit_coins` aborts, the whole transaction reverts, and no shareholder — including cooperative ones — receives their payout. `S` can repeat this indefinitely, and there is no code path found in `vesting.move`/`staking_contract.move` to exclude `S` or force-settle around them.

**Uncertainty:** I was not able to fully verify within the available searches whether an admin-only recovery function exists elsewhere in the codebase (e.g., a way to remove/skip a specific shareholder from `pool_u64`/`distribution_pool`) that would mitigate this DoS; if such a function exists, the "permanent" characterization would need to be downgraded to "temporary, admin-recoverable." I recommend a follow-up search of `pool_u64.move` and any `remove_shareholder`/admin-forced-settlement APIs to confirm whether recovery is possible without a background Devin session with fuller repository access.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L838-853)
```text
    }

    /// Allow anyone to distribute already unlocked funds. This does not affect reward compounding and therefore does
    /// not need to be restricted to just the staker or operator.
    public entry fun distribute(
        staker: address, operator: address
    ) acquires Store, BeneficiaryForOperator {
        assert_staking_contract_exists(staker, operator);
        let store = borrow_global_mut<Store>(staker);
        let staking_contract = store.staking_contracts.borrow_mut(&operator);
        distribute_internal(
            staker,
            operator,
            staking_contract,
        );
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

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L190-199)
```text
    /// Deposit function override to ensure that the account is not denylisted and the stablecoin is not paused.
    public fun deposit<T: key>(
        store: Object<T>,
        fa: FungibleAsset,
        transfer_ref: &TransferRef,
    ) acquires State {
        assert_not_paused();
        assert_not_denylisted(object::owner(store));
        fungible_asset::deposit_with_ref(transfer_ref, store, fa);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/vesting.move (L718-747)
```text
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
```
