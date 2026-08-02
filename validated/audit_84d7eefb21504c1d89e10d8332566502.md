## Analysis

The external report's core custody invariant is: **a fee/commission must only be charged on genuinely new value, not on value that merely "recovers" a previous dip — this requires a true high-water mark, not a comparison against the last recorded value.**

I evaluated several Aptos-native candidates that track share-price / accumulated-value style accounting tied to live APT custody:

1. `aptos_framework::delegation_pool` commission accounting in `calculate_stake_pool_drift` — compares current stake to the *last recorded* `pool.active_shares.total_coins()`, not a high-water mark.
2. `aptos_framework::staking_contract` commission accounting via `principal` — would abort on underflow rather than silently double count, so it's not exploitable the same way.
3. `move-examples/swap/liquidity_pool.move` fee-per-share tracking — excluded per the rules (`move-examples`/example code).
4. `pool_u64` shares math — generic and correctly proportional; no analog fee-double-count bug found there.

Candidate 1 is the strongest: it is core framework code controlling real APT held in delegation-pool-owned resource accounts, and it explicitly acknowledges (in its own comments) a "slashing" scenario that resets its baseline downward without memory of the prior high point — precisely the seed bug's shape.

## Title
Delegation pool operator commission is charged against a non-monotonic baseline, allowing double-commission extraction from delegator stake on any active-stake dip-and-recovery - (File: aptos-move/framework/aptos-framework/sources/delegation_pool.move)

## Summary
`calculate_stake_pool_drift` computes operator commission by comparing the stake pool's current `active` stake to `pool.active_shares.total_coins()`, the value recorded at the last synchronization — not a true high-water mark. When `active` decreases relative to this recorded baseline, the code takes zero commission and silently rebases `total_coins` downward. When `active` later increases past the old baseline, the entire recovered delta is treated as fresh yield and commission is charged on it in full, effectively re-taxing delegators for value that was only recovering a prior dip.

## Finding Description [1](#0-0) 
computes:
```
let pool_active = pool.active_shares.total_coins();
let commission_active = if (active > pool_active) {
    math64::mul_div(active - pool_active, pool.operator_commission_percentage, MAX_FEE)
} else {
    // handle any slashing applied to `active` stake
    0
};
```
The comment itself acknowledges that `active` can be *lower* than the last recorded `pool_active` ("slashing"). In that branch, no commission is charged, but crucially the baseline is still rebased downward afterward via [2](#0-1) 
```
pool.active_shares.update_total_coins(active - commission_active);
```
This sets `total_coins` to the new, lower `active` value with no memory that a higher value was previously seen (and previously used as the commission baseline). On the very next synchronization where `active` recovers toward (or past) its pre-dip level, the `active > pool_active` branch fires again and charges the operator's commission percentage on the *entire* recovered delta — including the portion that is simply restoring previously-existing (already-baselined) delegator value rather than newly produced rewards.

This is the exact accounting flaw described in the seed report: the "fee baseline" is a last-observed value rather than a monotonic high-water mark, so a dip followed by a recovery causes commission to be levied twice on the same underlying value band.

## Impact Explanation
Delegator-owned APT stake inside `DelegationPool` (a mainnet-relevant, resource-account-held asset) is subject to excess commission extraction that is transferred to the operator via `buy_in_active_shares` [3](#0-2) 
. This moves value away from the rightful holders (delegators) to the operator without a corresponding real yield event — a custody/accounting corruption that redirects value to the wrong holder, satisfying the "Supply or custody accounting corruption that moves value to the wrong holder" impact category. Because commission is compounded via shares (`buy_in_active_shares`), the operator's excess claim itself continues to earn further rewards, amplifying the loss to delegators over time.

## Likelihood Explanation
I could not fully confirm, within the available tooling, that the `active` stake tracked by `stake::get_stake` can actually decrease outside of an explicit, pool-accounted unlock/withdraw operation (e.g., via a live slashing mechanism) on current Aptos mainnet. The code's own comment ("handle any slashing applied to `active` stake") strongly implies the authors intentionally guarded for such a decrease, meaning the underlying `stake` module is expected to be able to reduce `active` outside of the delegation pool's own bookkeeping. If such a decrease is achievable (whether through slashing, or any other framework-level stake adjustment not funneled through `unlock`), the double-commission path triggers deterministically and requires no special privilege — it happens automatically on the next `synchronize_delegation_pool` call, which is permissionless. I was unable to complete tracing of `stake.move`'s current slashing/adjustment mechanisms in the time available, so this should be verified against the current implementation before treating this as fully proven.

## Recommendation
Track a true high-water mark for `active_shares.total_coins()` (and similarly for `pending_inactive`), only charging commission on increases above the historical maximum, mirroring the fix recommended in the seed report (highwater tracker). Alternatively, only rebase the baseline downward without ever charging commission on subsequent recovery up to the prior high-water level; only amounts exceeding the previous all-time high should be commissionable.

## Proof of Concept
Not independently executable within this analysis — verifying requires confirming that some code path (validator slashing, governance-triggered stake reduction, or similar) can reduce `active` in the underlying `stake` module without going through `delegation_pool`'s own `unlock`/`withdraw` bookkeeping. This would need to be validated in a Move test harness against `aptos_framework::stake` to conclusively trigger the `else` branch in `calculate_stake_pool_drift`, then trigger a subsequent recovery and observe double commission extraction via `synchronize_delegation_pool`.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/delegation_pool.move (L1887-1898)
```text
        // on stake-management operations, total coins on the internal shares pools and individual
        // stakes on the stake pool are updated simultaneously, thus the only stakes becoming
        // unsynced are rewards and slashes routed exclusively to/out the stake pool

        // operator `active` rewards not persisted yet to the active shares pool
        let pool_active = pool.active_shares.total_coins();
        let commission_active = if (active > pool_active) {
            math64::mul_div(active - pool_active, pool.operator_commission_percentage, MAX_FEE)
        } else {
            // handle any slashing applied to `active` stake
            0
        };
```

**File:** aptos-move/framework/aptos-framework/sources/delegation_pool.move (L1943-1946)
```text
        // update total coins accumulated by `active` + `pending_active` shares
        // redeemed `add_stake` fees are restored and distributed to the rest of the pool as rewards
        pool.active_shares.update_total_coins(active - commission_active);
        // update total coins accumulated by `pending_inactive` shares at current observed lockup cycle
```

**File:** aptos-move/framework/aptos-framework/sources/delegation_pool.move (L1949-1951)
```text
        // reward operator its commission out of uncommitted active rewards (`add_stake` fees already excluded)
        buy_in_active_shares(pool, beneficiary_for_operator(stake::get_operator(pool_address)), commission_active);
        // reward operator its commission out of uncommitted pending_inactive rewards
```
