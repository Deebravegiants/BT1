## Verified: This is a real logic bug in `staking_contract.move`

Tracing the code confirms the exact mechanism described. The root cause is in `switch_operator` at [1](#0-0) , combined with `distribute_internal`'s recipient-resolution check at [2](#0-1) .

### Title
Stale `old_operator` shares in `distribution_pool` bypass `beneficiary_for_operator` redirection on subsequent `distribute` calls — ([File: aptos-move/framework/aptos-framework/sources/staking_contract.move])

### Summary
`distribute_internal` only redirects a payout to a beneficiary when `recipient == operator` (the operator argument passed into the current call) [3](#0-2) . `switch_operator` can leave stale, unredeemed shares for `old_operator` in the `distribution_pool` after the switch completes, because it calls `distribute_internal` (which empties the pool) and only *afterward* calls `request_commission_internal`, which re-adds a fresh distribution share keyed to `old_operator` for any newly-unlockable commission [4](#0-3) [5](#0-4) . Once the operator key is switched to `new_operator`, any later unprivileged call to `distribute(staker, new_operator)` iterates over all shareholders in the pool, including the leftover `old_operator` entry, but the beneficiary check only compares against the *current* `operator` parameter (`new_operator`), so `old_operator != new_operator` and the stale share is paid straight to `old_operator`'s address, bypassing `beneficiary_for_operator(old_operator)`.

### Finding Description
`distribute` is a fully public, unprivileged entry function: "Allow anyone to distribute already unlocked funds" [6](#0-5) . When it is invoked for `(staker, new_operator)`, `distribute_internal` walks every shareholder currently in `staking_contract.distribution_pool`, not just ones related to `new_operator`. The beneficiary substitution is applied via a single equality check against the operator parameter passed in, not against the recipient's own beneficiary record:

```
if (recipient == operator) {
    recipient = beneficiary_for_operator(operator);
};
```

Because `switch_operator` performs `distribute_internal` + `request_commission_internal` (which itself re-populates the pool with an `old_operator`-keyed share for commission unlocked at switch time) *before* re-keying the map to `new_operator`, that `old_operator` share persists in the pool across the switch. The framework's own documentation acknowledges that "the previous operator may still have a non-zero pending attribution" post-switch [7](#0-6) , but the beneficiary-redirection logic in `distribute_internal` was never extended to check a *stale* recipient's own beneficiary record — it only checks the beneficiary of the operator argument that was passed in for the current call.

### Impact Explanation
If `old_operator` calls `set_beneficiary_for_operator` to delegate commission receipt to a beneficiary address [8](#0-7) , and stale shares remain in the pool from before/around a `switch_operator` call, any unprivileged caller triggering `distribute(staker, new_operator)` will pay that stale commission directly to `old_operator`'s address instead of to the configured beneficiary. This violates the documented invariant that beneficiary redirection governs all operator-originated commission payouts, misrouting funds away from the party entitled to receive them under `old_operator`'s beneficiary delegation.

### Likelihood Explanation
This requires a specific but plausible real-world sequence: a staker switches operators while there is unpaid/newly-unlocked commission for the old operator, and the old operator has configured (or later configures) a beneficiary. Given `distribute` is callable by anyone, no cooperation from a malicious actor is needed to trigger the misrouted payout — any routine caller of `distribute` (including automated bots that regularly flush distributions) will do so.

### Recommendation
In `distribute_internal`, resolve the beneficiary based on the shareholder recipient's own address rather than solely the `operator` parameter passed into the call — e.g., check `beneficiary_for_operator(recipient)` for any recipient that is a registered operator/beneficiary owner, not just when `recipient == operator`. Alternatively, ensure `switch_operator` fully drains and pays out `old_operator`'s distribution shares (including beneficiary resolution) before re-keying the staking contract to `new_operator`, so no operator-associated shares can survive the switch under the old key.

### Proof of Concept
1. Staker `S` creates a staking contract with `operator = A`, commission 10%.
2. Rewards accrue and become inactive/unlockable.
3. `A` calls `set_beneficiary_for_operator(B)`.
4. `S` calls `switch_operator_with_same_commission(S, A, C)` (switch from `A` to new operator `C`). Internally: `distribute_internal` flushes the pool, then `request_commission_internal` re-adds a share for `A` for any commission unlocked at that moment, then the contract is re-keyed to `C`.
5. Anyone (unprivileged) calls `distribute(S, C)`.
6. In `distribute_internal(S, C, staking_contract)`, the loop iterates the pool; when it reaches the stale `A` recipient, `recipient == operator` compares `A == C`, which is false, so `A` is paid directly instead of being redirected to `B`.
7. Assert: `B`'s balance is unchanged, and `A`'s balance increased by the stale commission amount, demonstrating the beneficiary redirection was bypassed. [9](#0-8)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L393-397)
```text
    /// USAGE NOTES:
    /// - To query the staker's pending amount, pass `account = staker`.
    /// - To query the operator's pending commission, pass `account = operator`.
    /// - In operator-switch scenarios, the previous operator may still have a
    ///   non-zero pending attribution; in that case, pass `account = old_operator`.
```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L637-658)
```text
    fun request_commission_internal(
        operator: address,
        staking_contract: &mut StakingContract,
    ): u64 {
        // Unlock just the commission portion from the stake pool.
        let (total_active_stake, accumulated_rewards, commission_amount) =
            get_staking_contract_amounts_internal(staking_contract);
        staking_contract.principal = total_active_stake - commission_amount;

        // Short-circuit if there's no commission to pay.
        if (commission_amount == 0) {
            return 0
        };

        // Add a distribution for the operator.
        add_distribution(
            operator,
            staking_contract,
            operator,
            commission_amount
        );

```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L783-805)
```text
        let (_, staking_contract) = staking_contracts.remove(&old_operator);
        // Force distribution of any already inactive stake.
        distribute_internal(
            staker_address,
            old_operator,
            &mut staking_contract,
        );

        // For simplicity, we request commission to be paid out first. This avoids having to ensure to staker doesn't
        // withdraw into the commission portion.
        request_commission_internal(
            old_operator,
            &mut staking_contract,
        );

        // Update the staking contract's commission rate and stake pool's operator.
        stake::set_operator_with_cap(&staking_contract.owner_cap, new_operator);
        staking_contract.commission_percentage = new_commission_percentage;

        let pool_address = staking_contract.pool_address;
        staking_contracts.add(new_operator, staking_contract);
        emit(SwitchOperator { pool_address, old_operator, new_operator });
    }
```

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

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L856-920)
```text
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
