### Title
Credit-mode self-liquidation lets a stale account copy overwrite the debited position map, resurrecting seized collateral - (File: contracts/controller/src/positions/liquidation/mod.rs)

### Summary
`process_liquidation` loads the liquidated `Account` and, for `SeizeMode::Credit`, a second independently-loaded `Account` for the receiver. Both are mutated in memory and persisted sequentially. If the receiver resolves to the same `account_id` as the liquidated account, the receiver's supply-position write at `finalize_position_flow` clobbers the already-persisted seizure debits — a use-after-free analog: two live copies of one storage object, the stale copy's write landing after the authoritative copy's.

### Finding Description
- `liquidate` loads `account` once (`mod.rs:46`), then `resolve_seize_receiver` loads `receiver` separately (`mod.rs:53-55`).
- Repayments and seizure debits are applied to `account` (`apply.rs:177-179`, `mod.rs:68-93`), while share credits are applied to `receiving_account.supply_positions` (`apply.rs:227-235`). The only cross-account check is `receiver.spoke_id == account.spoke_id` (`apply.rs:165-169`); no visible check enforces `receiver_id != account_id`.
- Persistence is ordered: the liquidated account's maps are written first (`mod.rs:114-121`), then `record_share_credit_updates` + `finalize_position_flow(.., receiver_id, receiving_account, PositionSides::Supply, false)` writes the receiver's supply map (`mod.rs:123-133`).
- If both ids are equal, the second write contains the receiver's *pre-liquidation* supply map plus credited `liquidator_scaled` shares (`credit_supply_shares` read at `apply.rs:227` happens before debits on the other copy are persisted), silently restoring every seized position.

### Impact Explanation
The liquidator transfers real repayment tokens to the pool (`transfer_amount_measured`, `apply.rs:58-65`), the debt is burned, yet the account's collateral is fully restored from the stale map. Result: theft of the liquidator's repayment funds credited to the account owner, and divergent controller/pool accounting (spoke usage exits at `apply.rs:192-197` are not re-entered). This is direct theft of user funds.

### Likelihood Explanation
Reachable by any unprivileged liquidator via `liquidate(liquidator, account_id, debt_payments, SeizeMode::Credit(account_id))` — a single transaction, no oracle or timing dependence. The critical unverified gate is `resolve_seize_receiver` (`mod.rs:53-55`): if it rejects `receiver_id == account_id` (its signature takes both `account_id` and `&account`, which suggests it may), the analog collapses. I could not read that function body to confirm; if it only verifies NFT ownership/position limits, the bug is fully reachable. Rated High if reachable.

### Recommendation
Reject `SeizeMode::Credit(id)` where `id == account_id` in `resolve_seize_receiver` or `apply_liquidation_share_credit`, and/or assert the receiver and target are distinct persistent objects before any writeback.

### Proof of Concept
1. Victim account `A` supplies collateral and borrows until HF < 1.
2. Attacker (or colluding owner) calls `liquidate(attacker, A, [debt_payments], SeizeMode::Credit(A))`.
3. `apply_liquidation_share_credit` debits seized shares from `account` copy, credits `liquidator_scaled` into `receiving_account` copy (same `A`, loaded fresh).
4. `finalize_position_flow(A, account)` persists reduced supply map; `finalize_position_flow(A, receiving_account)` overwrites it with the stale full map plus credited shares.
5. Debt is repaid from attacker's tokens; `A`'s collateral is intact — attacker loses the repayment, `A`'s owner gains it. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

Note: full verification requires the body of `resolve_seize_receiver`, which was not read; if it enforces `receiver_id != account_id`, this finding does not stand.

### Citations

**File:** contracts/controller/src/positions/liquidation/mod.rs (L53-55)
```rust
    let mut receiver = resolve_seize_receiver(
        env, liquidator, account_id, &account, seize_mode, &mut cache,
    );
```

**File:** contracts/controller/src/positions/liquidation/mod.rs (L114-133)
```rust
    finalize_position_flow(
        env,
        account_id,
        &account,
        &mut cache,
        PositionSides::Both,
        false,
    );

    if let Some((receiver_id, receiving_account)) = &receiver {
        apply::record_share_credit_updates(env, receiving_account, &seized, &mut cache);
        finalize_position_flow(
            env,
            *receiver_id,
            receiving_account,
            &mut cache,
            PositionSides::Supply,
            false,
        );
    }
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L165-179)
```rust
        assert_with_error!(
            env,
            receiver.spoke_id == account.spoke_id,
            SpokeError::SpokeMismatch
        );
        assert_with_error!(
            env,
            seized_scaled.checked_sub(env, liquidator_scaled) == fee_scaled,
            GenericError::InternalError
        );

        // Checked subtraction prevents over-seizure; liquidation preserves risk stamps.
        let mut position = get_supply_position_or_panic(env, account, &entry.hub_asset);
        position.scaled_amount = position.scaled_amount.checked_sub(env, seized_scaled);
        update_or_remove_supply_position(account, &entry.hub_asset, &position);
```

**File:** contracts/controller/src/positions/liquidation/apply.rs (L227-235)
```rust
    let mut position = match receiver.supply_positions.get(hub_asset.clone()) {
        Some(raw) => AccountPosition::from(&raw),
        None => {
            let config = cache.require_spoke_asset(receiver.spoke_id, hub_asset);
            receiver.get_or_create_supply_position(hub_asset, &config)
        }
    };
    position.scaled_amount = position.scaled_amount.checked_add(env, scaled);
    update_or_remove_supply_position(receiver, hub_asset, &position);
```
