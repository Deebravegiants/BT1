Based on my research, I found a plausible custody-accounting analog in `swap::liquidity_pool`, but I was unable to fully verify one precondition before running out of iterations (see the caveat in "Likelihood Explanation"). I present it with that explicit limitation.

### Title
Stale per-address fee checkpoints in `liquidity_pool::update_claimable_fees` allow fee-accounting corruption if LP token transfer bypasses the wrapper - (File: aptos-move/move-examples/swap/sources/liquidity_pool.move)

### Summary
The `swap::liquidity_pool` module tracks each address's entitlement to swap fees using a per-address "last claimed" checkpoint (`total_fees_at_last_claim_1/2`) that is only updated when LP token movements go through the module's own `mint`, `burn`, `transfer`, or `claim_fees`/`update_claimable_fees` functions [1](#0-0) . The module explicitly documents that raw `fungible_asset::transfer`/`primary_fungible_store::transfer` of LP tokens are "not supported" and that all transfers must go through `liquidity_pool::transfer` to keep this checkpoint consistent [2](#0-1) . This is the same invariant class as the Sablier bug: an off-chain-enforced (rather than protocol-enforced) link between a transferable balance and a per-holder accounting record, which can desynchronize if the balance moves outside the code path that maintains the record.

### Finding Description
`update_claimable_fees` computes an LP's claimable fee delta as `current_total_fees - total_fees_at_last_claim[lp]`, scaled by the LP's *current* balance, and then unconditionally overwrites the checkpoint to `current_total_fees` [3](#0-2) . This checkpoint is address-keyed and is never invalidated when the underlying LP token balance for that address changes through a channel other than `mint`/`burn`/`transfer` in this module. If an address's balance can change without going through this module (e.g., a stale address that previously held LP tokens, had its checkpoint set, later reduced its balance to zero, and then received a *fresh* transfer of LP tokens through a path that does not call `update_claimable_fees`), the next call to `update_claimable_fees`/`claim_fees` will compute the fee delta over the *entire* stale interval — including time the address held zero tokens — and apply it to the newly-received balance. Since `claimable_1/2` are paid out of the finite `fees_store_1/2` [4](#0-3) , this inflated claim diverts fee custody away from the LPs who actually held tokens during that interval — a supply/custody accounting corruption that moves value to the wrong holder, matching the "Custody Accounting Corruption" impact category.

### Impact Explanation
If exploitable, an attacker could recycle a previously-used LP address (or any address with a stale, low checkpoint) to claim a share of pool fees disproportionate to actual holding time, draining `fees_store_1`/`fees_store_2` value that rightfully belongs to genuine liquidity providers. This is a direct custody/value-diversion impact on fungible-asset-held value in an object-based vault (the `LiquidityPool` object and its `FeesAccounting` resource).

### Likelihood Explanation
**This finding is not fully confirmed.** The exploit's precondition — that LP tokens can actually be moved into/out of an address via a path other than `liquidity_pool::mint`/`burn`/`transfer` (e.g., raw `primary_fungible_store::transfer` or `fungible_asset::transfer`) — depends on whether `create_lp_token`/`create_lp_token_refs`/`create_token_store` register dispatch hooks or disable ungated transfer on the LP token's fungible store to enforce the "must use this module" comment at the protocol level. I located these function definitions via `grep_search` but ran out of tool-call budget before reading their bodies, so I cannot confirm whether the restriction is code-enforced (in which case this finding does not hold) or merely documented/convention-based (in which case the finding holds as described). If the restriction is enforced (e.g. via `object::disable_ungated_transfer` combined with `dispatchable_fungible_asset` withdraw/deposit hooks that route through the module), this specific analog does not independently hold and should be discarded.

### Recommendation
- Confirm (or add, if missing) an enforced transfer restriction on LP token fungible stores, e.g. `object::disable_ungated_transfer` on the LP token's `TransferRef` plus `dispatchable_fungible_asset::register_dispatch_functions` routing all withdraw/deposit through `liquidity_pool::transfer`'s fee-checkpoint logic, so no path exists to move LP token balance without updating `total_fees_at_last_claim`.
- Alternatively, redesign the fee-accounting model to use a reward-per-share accumulator pattern where each store's entitlement is derived purely from its own historical balance-weighted contribution (e.g., checkpointing at token mint time to current global accumulator value, and deleting/reinitializing checkpoints whenever a store's balance transitions from zero), removing any implicit trust that balance changes are always intermediated by this module.

### Proof of Concept
Not verified end-to-end due to the unresolved precondition above. Conceptually:
1. Address A mints LP tokens, pool accrues fees over time (`total_fees_1` increases).
2. A calls `claim_fees`/`update_claimable_fees`, setting `total_fees_at_last_claim_1[A]` to the current total.
3. A withdraws/burns all LP tokens (balance → 0), but `total_fees_at_last_claim_1[A]` entry is not deleted and remains at the old checkpoint.
4. Time passes and `total_fees_1` grows substantially while A holds zero tokens.
5. A receives a fresh transfer of LP tokens into the same address via a path that bypasses `liquidity_pool::transfer` (unverified whether this is possible).
6. A calls `update_claimable_fees`: `delta_1 = total_fees_1 (now) - total_fees_at_last_claim_1[A] (stale)`, credited against A's freshly-acquired balance — granting A fee credit for a period during which A held no LP tokens.

Because step 5 could not be confirmed as feasible within the remaining investigation budget, this should be treated as a candidate requiring further code review of `create_lp_token`, `create_token_store`, and `create_lp_token_refs` in `aptos-move/move-examples/swap/sources/liquidity_pool.move` before being considered a confirmed vulnerability.

### Citations

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L11-14)
```text
///
/// Another important thing to note is that all transfers of the LP tokens have to call via this module. This is
/// required so that fees are correctly updated for LPs. fungible_asset::transfer and primary_fungible_store::transfer
/// are not supported
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L91-99)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    struct FeesAccounting has key {
        total_fees_1: u128,
        total_fees_2: u128,
        total_fees_at_last_claim_1: SmartTable<address, u128>,
        total_fees_at_last_claim_2: SmartTable<address, u128>,
        claimable_1: SmartTable<address, u128>,
        claimable_2: SmartTable<address, u128>,
    }
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L515-541)
```text
    public entry fun update_claimable_fees(lp: address, pool: Object<LiquidityPool>) acquires FeesAccounting {
        let fees_accounting = unchecked_mut_fees_accounting(&pool);
        let current_total_fees_1 = fees_accounting.total_fees_1;
        let current_total_fees_2 = fees_accounting.total_fees_2;
        let lp_balance = (primary_fungible_store::balance(lp, pool) as u128);
        let lp_token_total_supply = lp_token_supply(pool);
        // Calculate and update the amount of fees this LP token store is entitled to, taking into account the last
        // time they claimed.
        if (lp_balance > 0) {
            let last_total_fees_1 = *smart_table::borrow(&fees_accounting.total_fees_at_last_claim_1, lp);
            let last_total_fees_2 = *smart_table::borrow(&fees_accounting.total_fees_at_last_claim_2, lp);
            let delta_1 = current_total_fees_1 - last_total_fees_1;
            let delta_2 = current_total_fees_2 - last_total_fees_2;
            let claimable_1 = math128::mul_div(delta_1, lp_balance, lp_token_total_supply);
            let claimable_2 = math128::mul_div(delta_2, lp_balance, lp_token_total_supply);
            if (claimable_1 > 0) {
                let old_claimable_1 = smart_table::borrow_mut_with_default(&mut fees_accounting.claimable_1, lp, 0);
                *old_claimable_1 = *old_claimable_1 + claimable_1;
            };
            if (claimable_2 > 0) {
                let old_claimable_2 = smart_table::borrow_mut_with_default(&mut fees_accounting.claimable_2, lp, 0);
                *old_claimable_2 = *old_claimable_2 + claimable_2;
            };
        };

        smart_table::upsert(&mut fees_accounting.total_fees_at_last_claim_1, lp, current_total_fees_1);
        smart_table::upsert(&mut fees_accounting.total_fees_at_last_claim_2, lp, current_total_fees_2);
```

**File:** aptos-move/move-examples/swap/sources/liquidity_pool.move (L547-571)
```text
    public(friend) fun claim_fees(
        lp: &signer,
        pool: Object<LiquidityPool>,
    ): (FungibleAsset, FungibleAsset) acquires FeesAccounting, LiquidityPool {
        let lp_address = signer::address_of(lp);
        update_claimable_fees(lp_address, pool);

        let pool_data = liquidity_pool_data(&pool);
        let fees_accounting = unchecked_mut_fees_accounting(&pool);
        let claimable_1 = if (smart_table::contains(&fees_accounting.claimable_1, lp_address)) {
            smart_table::remove(&mut fees_accounting.claimable_1, lp_address)
        } else {
            0
        };
        let claimable_2 = if (smart_table::contains(&fees_accounting.claimable_2, lp_address)) {
            smart_table::remove(&mut fees_accounting.claimable_2, lp_address)
        } else {
            0
        };
        let swap_signer = &package_manager::get_signer();
        let fees_1 = if (claimable_1 > 0) {
            fungible_asset::withdraw(swap_signer, pool_data.fees_store_1, (claimable_1 as u64))
        } else {
            fungible_asset::zero(fungible_asset::store_metadata(pool_data.fees_store_1))
        };
```
