## Title
Unprivileged commission recipient can permanently block `staking_contract::distribute` by disabling direct coin transfers — ([File: aptos-move/framework/aptos-framework/sources/staking_contract.move])

### Summary
`staking_contract::distribute_internal` mirrors the `LineOfCredit._close()` pattern: it withdraws all withdrawable stake into a single `Coin<AptosCoin>` and then, in one atomic transaction, *pushes* payouts to every entry in the `distribution_pool` (operator/beneficiary and staker) via `aptos_account::deposit_coins`. Any recipient in that loop who has not yet registered a `CoinStore<AptosCoin>` and who has disabled direct coin transfers can make this push abort, exactly like an ERC-777/native-ETH lender rejecting a `close()` transfer.

### Finding Description
`distribute_internal` loops over all shareholders of `staking_contract.distribution_pool` and calls `aptos_account::deposit_coins` for each recipient: [1](#0-0) 

`aptos_account::deposit_coins` requires that, for any address not already registered for `CoinType`, the recipient's `DirectTransferConfig.allow_arbitrary_coin_transfers` be `true`, or it aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS`: [2](#0-1) 

`DirectTransferConfig` is a self-service, unprivileged setting any account controls for itself (opt-out of unsolicited coin transfers) — this is by design for spam protection, but it is not designed for this custody flow. In `staking_contract`, the operator's commission is (potentially) redirected to a `beneficiary_for_operator` address, and the distribution pool can contain multiple shareholders via `add_distribution`/`update_distribution_pool`: [3](#0-2) 

Because the entire withdrawal (`stake::withdraw_with_cap`) already happened before the payout loop, and the loop is a single atomic `while` over `distribution_pool.shareholders()` with no per-recipient error isolation, **one griefing recipient aborts the whole `distribute()` call** — including the payout to every *other* legitimate shareholder (e.g., the staker) — even though those other payouts would have succeeded. This is the same custody-invariant break as the seed report: a push-based settlement step can be unilaterally vetoed by one participant, blocking closure/distribution for everyone.

### Impact Explanation
- The staker cannot ever receive their share of unlocked/inactive stake once any single distribution-pool member (an operator's beneficiary, or any other shareholder added via `add_distribution`) opts out of unregistered direct transfers.
- Since `distribute()` is also invoked as part of other staking-contract lifecycle operations (e.g., before terminating/reallocating a staking contract), this can stall broader staking-contract state transitions that depend on a successful distribution, trapping already-inactive/withdrawable APT inside the resource-account-owned stake pool indefinitely (no pull-based fallback exists in this module).
- This is custody-grade because it corrupts settlement of already-earned, already-unlocked value away from its rightful holder (the staker or other shareholders) due to an unprivileged, unrelated party's account setting.

### Likelihood Explanation
Setting `allow_arbitrary_coin_transfers = false` is a one-line self-service call any account can make at any time (this is the intended anti-spam feature), and not registering a `CoinStore<AptosCoin>` beforehand is the default state for many accounts (e.g., freshly used beneficiary addresses or newly designated recipients in `add_distribution`). No privileged action or race condition is required — any operator/beneficiary/added recipient can trivially self-grief to hold the staker's funds hostage or force a specific resolution.

### Recommendation
Make the distribution loop resilient to individual recipient failures: skip/queue a recipient's payout (e.g., store it as a claimable balance) instead of aborting the whole transaction when a `deposit_coins` payout would fail, or split each recipient's transfer into its own try/catch-like isolated sub-call, or move to a pull-based claim pattern for distribution recipients (matching the report's own recommended mitigation of preferring pull over push).

### Proof of Concept
1. Staker `S` creates a staking contract with operator `O`, and `O` sets a beneficiary `B` via `set_beneficiary_for_operator` (or `S`/`O` calls `add_distribution` naming an arbitrary `recipient`).
2. `B` (or the arbitrary `recipient`), who has never registered `CoinStore<AptosCoin>`, calls `aptos_account::set_allow_direct_coin_transfers(false)` (self-service, no special privilege needed).
3. Stake becomes inactive/withdrawable; `S` or anyone calls `staking_contract::distribute(staker, operator)`.
4. `distribute_internal` withdraws all withdrawable coins, then in its payout loop reaches `B`/`recipient`: `aptos_account::deposit_coins(recipient, ...)` aborts because `coin::is_account_registered<AptosCoin>(recipient) == false` and `can_receive_direct_coin_transfers(recipient) == false`.
5. The whole `distribute()` transaction reverts — the staker gets none of their unlocked stake, and this can be repeated indefinitely by `B`/`recipient`, permanently blocking distribution.

Note: I was not able to trace every downstream caller of `distribute()`/`distribute_internal()` (e.g., whether `switch_operator`/`reset_lockup` force a distribution first) within the available search budget; a full review of `staking_contract.move`'s lifecycle functions is recommended to confirm the complete blast radius of this DoS.

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L937-957)
```text
    /// Add a new distribution for `recipient` and `amount` to the staking contract's distributions list.
    fun add_distribution(
        operator: address,
        staking_contract: &mut StakingContract,
        recipient: address,
        coins_amount: u64,
    ) {
        let distribution_pool = &mut staking_contract.distribution_pool;
        let (_, _, _, total_distribution_amount) =
            stake::get_stake(staking_contract.pool_address);
        update_distribution_pool(
            distribution_pool,
            total_distribution_amount,
            operator,
            staking_contract.commission_percentage
        );

        distribution_pool.buy_in(recipient, coins_amount);
        let pool_address = staking_contract.pool_address;
        emit(AddDistribution { operator, pool_address, amount: coins_amount });
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
