## Custody Analog Found: Commission-rounding evasion in `staking_contract::update_distribution_pool`

### Title
Repeated small stake operations round `unpaid_commission` to 0 shares, permanently diverting operator commission to the staker - ([File: aptos-move/framework/aptos-framework/sources/staking_contract.move])

### Summary
The external report's custody invariant is: *"a value/shares conversion that rounds an amount down to zero silently defeats the value-transfer the protocol intends to enforce, and the lost value is not recoverable."* The Aptos-native analog is in `aptos_framework::staking_contract`, where `update_distribution_pool` converts an accrued reward slice into a number of `distribution_pool` shares to transfer from a staker to the operator as commission. Because the amount→shares conversion floors (`pool_u64::amount_to_shares_with_total_coins` → `math64::mul_div`), and `pool_u64::transfer_shares` is a no-op when the computed share count is `0`, any accrued-reward slice smaller than the current share price is silently dropped rather than carried forward — permanently moving value that should go to the operator to the staker instead.

### Finding Description
`update_distribution_pool` is called on every event that changes the stake pool's total coin balance (add_stake, unlock_stake, request_commission, switch_operator, etc.), and is the sole mechanism that charges commission on rewards accrued since the pool's last update: [1](#0-0) 

For each shareholder it computes:
```
unpaid_commission = (current_worth - previous_worth) * commission_percentage / 100
shares_to_transfer = amount_to_shares_with_total_coins(distribution_pool, unpaid_commission, updated_total_coins)
transfer_shares(distribution_pool, shareholder, operator, shares_to_transfer)
```
then unconditionally calls `distribution_pool.update_total_coins(updated_total_coins)` at the end, regardless of whether the transfer actually moved any shares.

`amount_to_shares_with_total_coins` floors via `mul_div`: [2](#0-1) 

`pool_u64::transfer_shares` short-circuits entirely when the computed share amount is `0`: [3](#0-2) 

Because `distribution_pool.update_total_coins(updated_total_coins)` is called every time regardless of whether `shares_to_transfer` was `0`, the "baseline" (`previous_worth`) used for the *next* call is reset to reflect the new, higher `total_coins` — the un-transferred reward slice is not carried into the next computation. There is no accumulator or dust-tracking for the shareholder-side commission calculation (unlike `distribute_internal`/`vesting::distribute`, which do send leftover dust to a recovery address after the fact). The loss here is structural per-call, not leftover dust after a single settlement — repeating the call keeps re-triggering the same floor-to-zero condition.

As the distribution pool matures (rewards accumulate while `total_shares` stays fixed unless new stake is bought in), the coins-per-share price rises, so the reward slice needed to buy even a single share of commission grows too. A staker who calls state-changing entry functions (e.g. `unlock_stake`) in many small increments in rapid succession (each triggering `update_distribution_pool` with a tiny `updated_total_coins` delta) can keep each call's `unpaid_commission` below one share's worth, causing `shares_to_transfer == 0` on every call. The commission owed to the operator for that reward slice is never collected on that call, and the baseline moves on — so it is not merely deferred, it is permanently lost from the operator's side of the accounting and effectively stays with the staker.

### Impact Explanation
This is a custody/accounting-corruption bug tied to a live, resource-account-controlled asset flow: `staking_contract` stake pools are hosted in dedicated resource accounts whose `OwnerCapability` is held by the contract specifically to enforce the staker/operator commission split described in the module's own docstring: [4](#0-3) 

By repeatedly triggering `update_distribution_pool` with sub-share-price increments, a staker can systematically evade the operator's commission on reward accrual, corrupting the intended supply/custody split and redirecting value from the operator (the intended recipient of commission) to themselves without authorization. This matches "Supply or custody accounting corruption that moves value to the wrong holder" from the custody impact gate.

### Likelihood Explanation
Likelihood is Medium: the staker already has full authority to call `unlock_stake`/`add_stake` on their own contract at any cadence, and Aptos gas costs are low enough that issuing many small calls to keep each reward slice under one share's rounding threshold is economically realistic, especially for mature, high-value pools where the coins-per-share price is large. The staker does not need any privileged access beyond their existing role in the staking contract.

### Recommendation
Track and carry forward rounding remainders in `update_distribution_pool` instead of resetting the shareholder's baseline unconditionally: either (a) accumulate an un-transferred "pending commission" per shareholder that is added to the next `unpaid_commission` calculation, or (b) only advance `distribution_pool`'s recorded baseline/`update_total_coins` for the fraction of value that was actually converted into shares, leaving the un-collected remainder attributable to a future call. Alternatively, revert/skip advancing the shareholder-specific baseline whenever `shares_to_transfer == 0`, so the shortfall compounds until it crosses the share-price threshold and is correctly collected.

### Proof of Concept
1. Staker and operator set up a staking contract with `commission_percentage = 10`, `create_staking_contract(staker, operator, 100 * ONE_APT, 10, seed)`.
2. Let the pool run several epochs so it accumulates meaningful rewards, growing the coins-per-share price of `distribution_pool` (e.g., 1.5x).
3. Instead of calling `unlock_stake` once for a large amount, the staker calls `unlock_stake` many times with amounts small enough that each call's `(current_worth - previous_worth) * 10 / 100` is smaller than one share's coin value at the current price.
4. Each call passes through `update_distribution_pool`; `amount_to_shares_with_total_coins` floors to `0`, `transfer_shares` no-ops, yet `distribution_pool.update_total_coins(updated_total_coins)` still advances the baseline.
5. After the loop, sum the total commission actually transferred to the operator vs. the commission that would have been charged had the staker made a single `unlock_stake` call for the full amount — the operator receives strictly less, and the difference is unrecoverable since no dust/remainder tracking exists for this per-call commission path.

Note: I was not able to inspect the full `request_commission_internal`/`unlock_stake` bodies in this pass (only `add_distribution`, `distribute_internal`, and `update_distribution_pool` were retrieved), so exact call-frequency thresholds and any indirect protections elsewhere in those functions could not be fully confirmed from the index; a Devin session with full file access is recommended to verify the exact minimum-call-interval economics and confirm no additional guard exists between `unlock_stake` and `update_distribution_pool`.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L1-26)
```text
/// Allow stakers and operators to enter a staking contract with reward sharing.
/// The main accounting logic in a staking contract consists of 2 parts:
/// 1. Tracks how much commission needs to be paid out to the operator. This is tracked with an increasing principal
/// amount that's updated every time the operator requests commission, the staker withdraws funds, or the staker
/// switches operators.
/// 2. Distributions of funds to operators (commissions) and stakers (stake withdrawals) use the shares model provided
/// by the pool_u64 to track shares that increase in price as the stake pool accumulates rewards.
///
/// Example flow:
/// 1. A staker creates a staking contract with an operator by calling create_staking_contract() with 100 coins of
/// initial stake and commission = 10%. This means the operator will receive 10% of any accumulated rewards. A new stake
/// pool will be created and hosted in a separate account that's controlled by the staking contract.
/// 2. The operator sets up a validator node and, once ready, joins the validator set by calling stake::join_validator_set
/// 3. After some time, the stake pool gains rewards and now has 150 coins.
/// 4. Operator can now call request_commission. 10% of (150 - 100) = 5 coins will be unlocked from the stake pool. The
/// staker's principal is now updated from 100 to 145 (150 coins - 5 coins of commission). The pending distribution pool
/// has 5 coins total and the operator owns all 5 shares of it.
/// 5. Some more time has passed. The pool now has 50 more coins in rewards and a total balance of 195. The operator
/// calls request_commission again. Since the previous 5 coins have now become withdrawable, it'll be deposited into the
/// operator's account first. Their new commission will be 10% of (195 coins - 145 principal) = 5 coins. Principal is
/// updated to be 190 (195 - 5). Pending distribution pool has 5 coins and operator owns all 5 shares.
/// 6. Staker calls unlock_stake to unlock 50 coins of stake, which gets added to the pending distribution pool. Based
/// on shares math, staker will be owning 50 shares and operator still owns 5 shares of the 55-coin pending distribution
/// pool.
/// 7. Some time passes and the 55 coins become fully withdrawable from the stake pool. Due to accumulated rewards, the
/// 55 coins become 70 coins. Calling distribute() distributes 6 coins to the operator and 64 coins to the validator.
```

**File:** aptos-move/framework/aptos-framework/sources/staking_contract.move (L1001-1039)
```text
    fun update_distribution_pool(
        distribution_pool: &mut Pool,
        updated_total_coins: u64,
        operator: address,
        commission_percentage: u64
    ) {
        // Short-circuit and do nothing if the pool's total value has not changed.
        if (distribution_pool.total_coins() == updated_total_coins) { return };

        // Charge all stakeholders (except for the operator themselves) commission on any rewards earnt relatively to the
        // previous value of the distribution pool.
        let shareholders = &distribution_pool.shareholders();
        shareholders.for_each_ref(
            |shareholder| {
                let shareholder: address = *shareholder;
                if (shareholder != operator) {
                    let shares = pool_u64::shares(distribution_pool, shareholder);
                    let previous_worth = pool_u64::balance(distribution_pool, shareholder);
                    let current_worth =
                        pool_u64::shares_to_amount_with_total_coins(
                            distribution_pool, shares, updated_total_coins
                        );
                    let unpaid_commission =
                        (current_worth - previous_worth) * commission_percentage / 100;
                    // Transfer shares from current shareholder to the operator as payment.
                    // The value of the shares should use the updated pool's total value.
                    let shares_to_transfer =
                        pool_u64::amount_to_shares_with_total_coins(
                            distribution_pool, unpaid_commission, updated_total_coins
                        );
                    pool_u64::transfer_shares(
                        distribution_pool, shareholder, operator, shares_to_transfer
                    );
                };
            }
        );

        distribution_pool.update_total_coins(updated_total_coins);
    }
```

**File:** aptos-move/framework/aptos-stdlib/sources/pool_u64.move (L187-199)
```text
    public fun transfer_shares(
        self: &mut Pool,
        shareholder_1: address,
        shareholder_2: address,
        shares_to_transfer: u64,
    ) {
        assert!(self.contains(shareholder_1), error::invalid_argument(ESHAREHOLDER_NOT_FOUND));
        assert!(self.shares(shareholder_1) >= shares_to_transfer, error::invalid_argument(EINSUFFICIENT_SHARES));
        if (shares_to_transfer == 0) return;

        self.deduct_shares(shareholder_1, shares_to_transfer);
        self.add_shares(shareholder_2, shares_to_transfer);
    }
```

**File:** aptos-move/framework/aptos-stdlib/sources/pool_u64.move (L226-240)
```text
    /// Return the number of new shares `coins_amount` can buy in `self` with a custom total coins number.
    /// `amount` needs to big enough to avoid rounding number.
    public fun amount_to_shares_with_total_coins(self: &Pool, coins_amount: u64, total_coins: u64): u64 {
        // No shares yet so amount is worth the same number of shares.
        if (self.total_coins == 0 || self.total_shares == 0) {
            // Multiply by scaling factor to minimize rounding errors during internal calculations for buy ins/redeems.
            // This can overflow but scaling factor is expected to be chosen carefully so this would not overflow.
            coins_amount * self.scaling_factor
        } else {
            // Shares price = total_coins / total existing shares.
            // New number of shares = new_amount / shares_price = new_amount * existing_shares / total_amount.
            // We rearrange the calc and do multiplication first to avoid rounding errors.
            self.multiply_then_divide(coins_amount, self.total_shares, total_coins)
        }
    }
```
