## Title
Operator-controlled beneficiary can permanently DoS `staking_contract::distribute`, freezing all staker funds in the resource-account-controlled stake pool - (File: `aptos-move/framework/aptos-framework/sources/staking_contract.move`)

### Summary
`staking_contract::distribute_internal` pushes coins to every shareholder of a `distribution_pool` in a single atomic loop, redirecting the operator's payout to an address the operator fully controls (`beneficiary_for_operator`). If a deposit to any one recipient in that loop aborts, the *entire* transaction reverts — including the staker's own payout redemption — exactly the push-payment DoS pattern from the external report (`FeeHandler.handleFee()` reverting on one blacklisted/failing recipient blocks all other payouts).

### Finding Description
`distribute_internal` withdraws all inactive/pending-inactive stake from the pool-owning resource account and then iterates over the distribution pool's shareholders, redeeming shares and pushing coins via `aptos_account::deposit_coins`: [1](#0-0) 

Shareholders are only ever the `staker` and the `operator`; the operator's payout is explicitly rerouted to `beneficiary_for_operator(operator)`: [2](#0-1) 

The operator can set this beneficiary to any address at will, with no restriction and no requirement that they control or can later fix the address: [3](#0-2) 

`aptos_account::deposit_coins` aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS` when the target is an *existing* account that is not registered for the `CoinType` and has explicitly opted out of unregistered/direct transfers via `DirectTransferConfig`: [4](#0-3) [5](#0-4) 

Because `distribute`/`distribute_internal` is the *only* code path that moves unlocked/inactive stake out of a `staking_contract`-managed stake pool (called from `distribute`, `request_commission`, `unlock_stake`, `unlock_rewards`, `switch_operator`, `update_commision`), a single permanently-reverting recipient in the shareholder loop blocks every one of these entry points: [6](#0-5) [7](#0-6) 

The custody invariant broken: an unprivileged participant of a two-party financial arrangement (the operator, who is not the staker/asset owner) can unilaterally choose a payout destination that will forever revert, and because the loop is atomic and processes both parties' payouts together, this blocks the *other* party's (the staker's) legitimate, unrelated withdrawal permanently — even though the staker owns the underlying stake and did nothing wrong.

### Impact Explanation
This satisfies "Permanent lock or non-recoverable loss of ... resource-account-held value": the stake pool behind a `staking_contract` is held by a resource account whose signer capability is exclusively controlled by `staking_contract`'s `distribute_internal`/`OwnerCapability` flow. Once an operator sets a beneficiary that permanently reverts, `stake::withdraw_with_cap` extracts real coins from the pool inside `distribute_internal`, but since the whole transaction aborts on the failing deposit, those coins are never released and can never be released again through any code path, because every future call to `distribute`, `unlock_stake`, `unlock_rewards`, `request_commission`, `switch_operator`, or `update_commision` re-triggers the same failing `distribute_internal` call first. This freezes the staker's entire inactive/pending-inactive stake indefinitely, with no admin override or recovery function in this module.

### Likelihood Explanation
Setting up the grief requires only that the operator (a normal, unprivileged party under `staking_contract`, not the staker/asset owner and not governance) call `set_beneficiary_for_operator` with an address that has previously called `aptos_account::set_allow_direct_coin_transfers(false)` and is not registered for `AptosCoin`/the relevant coin type — both of which are ordinary, permissionless, low-cost actions any account can pre-arrange. No special privileges, timing races, or governance assumptions are needed, making this practically exploitable by any malicious or careless operator against any staker who delegates to them.

### Recommendation
- Do not let a single failing recipient block payouts to other shareholders: process each shareholder's payout independently (e.g., isolate each transfer in its own sub-call and use a pull-based claim/withdrawal balance per shareholder instead of pushing in a shared loop), or `try/catch`-style isolate the deposit so failure for one recipient doesn't revert the whole distribution.
- Alternatively, disallow setting `beneficiary_for_operator` to an address that is currently unable to receive the coin (validate `can_receive_direct_coin_transfers`/registration at set-time as a sanity check, though this is a weak mitigation since the beneficiary can opt out afterward) — the pull-pattern fix is the robust solution.
- Add a governance/staker-triggerable recovery path to force-skip or redirect a stuck payout to an escrow address if a specific recipient's deposit repeatedly fails.

### Proof of Concept
1. Staker `S` creates a staking contract with operator `O` via `create_staking_contract`, non-zero commission.
2. `O` calls `aptos_account::set_allow_direct_coin_transfers(false)` from an address `X` that `O` controls but which is *not* registered for `AptosCoin` (a normal, freshly created but never-coin-registered account).
3. `O` calls `staking_contract::set_beneficiary_for_operator(O, X)`.
4. Time passes, rewards accumulate, lockup expires so inactive stake becomes available.
5. `S` calls `staking_contract::unlock_stake(S, O, amount)` (or `distribute`, `unlock_rewards`, etc.). This internally calls `distribute_internal`, which loops over shareholders `{S, O}`, redeems `O`'s commission shares, redirects to `beneficiary_for_operator(O) == X`, and calls `aptos_account::deposit_coins(X, ...)`.
6. Because `X` is registered with `DirectTransferConfig{allow_arbitrary_coin_transfers:false}` and is not registered for `AptosCoin`, `deposit_coins` aborts with `EACCOUNT_DOES_NOT_ACCEPT_DIRECT_COIN_TRANSFERS`.
7. The entire transaction reverts, including `S`'s share redemption and payout. Every subsequent call to any withdrawal-related entry point in `staking_contract.move` for this `(S, O)` pair repeats the same failure, permanently freezing `S`'s already-unlocked stake inside the resource-account-owned stake pool.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L622-635)
```text
        if (staking_contract.commission_percentage == 0) { return };

        // Force distribution of any already inactive stake.
        distribute_internal(
            staker,
            operator,
            staking_contract,
        );

        request_commission_internal(
            operator,
            staking_contract,
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L811-838)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L840-853)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/aptos_account.move (L226-231)
```text
    public fun can_receive_direct_coin_transfers(
        account: address
    ): bool acquires DirectTransferConfig {
        !exists<DirectTransferConfig>(account)
            || borrow_global<DirectTransferConfig>(account).allow_arbitrary_coin_transfers
    }
```
