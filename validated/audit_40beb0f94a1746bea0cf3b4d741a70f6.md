## Custody Path Analysis

**Reduced invariant:** the external bug is fundamentally about a *balance-authority desync* — one subsystem (the vault) trusts a raw quantity as unconditionally durable while a second subsystem (Lido) can silently mutate the underlying accounting, and an unprivileged actor can straddle both subsystems to convert a loss meant for them into a loss for the pool.

**Candidates generated internally:**
1. `delegation_pool.move` share-pool sandwich around `synchronize_delegation_pool` — rejected: every entry point (`add_stake`, `unlock`, `reactivate_stake`, `withdraw`) calls `synchronize_delegation_pool` first and uses `pool_u64_unbound` share math, so gains/losses are already baked into the exchange rate before any buy-in/redeem; this is the correct fix pattern for the Lybra bug, not a repeat of it.
2. `dispatchable_fungible_asset` rebase hooks — rejected as a *framework* bug: any balance/value mismatch would live entirely in application-defined `withdraw`/`deposit`/`derived_balance` hook code, not in `aptos_framework` itself.
3. `fungible_asset.move` `ConcurrentFungibleBalance`/aggregator upgrade paths — rejected: balance moves are atomic within a single transaction, no cross-subsystem desync exists.
4. `coin::maybe_convert_to_fungible_store` frozen-flag reconciliation during Coin→FA migration — **kept**. This is the direct analog: two independently-authoritative "frozen" custody fields (`CoinStore.frozen` and the primary `FungibleStore`'s frozen flag) that can diverge, and the migration path blindly overwrites the fungible store's authoritative freeze state with the legacy, unprivileged one.

### Title
Compliance-freeze bypass via stale `CoinStore.frozen` silently overwriting an admin-frozen `FungibleStore` during Coin→FA migration - (`aptos-move/framework/aptos-framework/sources/coin.move`)

### Summary
`coin::maybe_convert_to_fungible_store` reconciles the `frozen` flag of a legacy `CoinStore<CoinType>` with the primary `FungibleStore` it migrates into by simply overwriting the FA store's frozen state whenever they differ, with no check on *which direction* the difference goes or *who* set it.

### Finding Description
`maybe_convert_to_fungible_store` moves out `CoinStore<CoinType> { coin, frozen, .. }`, deposits the coin balance into the primary fungible store, then does: [1](#0-0) 
```
if (frozen != fungible_asset::is_frozen(store)) {
    fungible_asset::set_frozen_flag_internal(store, frozen)
}
```
This copies the CoinStore's `frozen` boolean onto the FA store unconditionally, regardless of which flag was set more recently or by whom. `CoinStore.frozen` defaults to `false` for every ordinary account and is normally only mutated by whoever holds `FreezeCapability<CoinType>` (a legacy, capability-based, admin-controlled path). The primary `FungibleStore.frozen` flag is the field an issuer relies on today for compliance freezes via `TransferRef` (`fungible_asset::set_frozen_flag` / `set_frozen_flag_internal`) — this is the authoritative custody control after AIP-73-style FA migration.

Because migration is triggered by **the account owner themselves** — `migrate_to_fungible_store` is a plain `entry fun` taking only `account: &signer` — and because `migrate_coin_store_to_fungible_store` takes an arbitrary `accounts: vector<address>` with **no ownership check on those addresses at all**: [2](#0-1) 

any account that (a) has been frozen on its primary FA store by the issuer for compliance reasons, but (b) still has a nonzero, non-frozen legacy `CoinStore<CoinType>` balance (e.g. dust never migrated, or freshly received via a plain `coin::transfer`), can call `migrate_to_fungible_store` on itself — or *anyone* can call `migrate_coin_store_to_fungible_store` on that address — and the reconciliation branch will set `FungibleStore.frozen = false`, silently lifting the issuer's freeze.

### Impact Explanation
This breaks the "Fungible asset metadata, primary and secondary stores, dispatchable hooks, and freeze state must preserve supply and holder identity" custody invariant and the "Multisig-owned assets, resource accounts, and code objects must not leak upgrade, freeze, or transfer authority to unprivileged callers" invariant: an unprivileged holder can unilaterally revoke an issuer's `TransferRef`-based freeze on their own primary fungible store, which is the sole custody control stablecoin/regulated-asset issuers have over an already-migrated FA. Once unfrozen, the holder can withdraw/transfer funds that were meant to be locked, defeating sanctions/compliance freezes tied to live, mainnet asset custody.

### Likelihood Explanation
Any coin type that has been migrated to the Coin↔FA pairing (all of them, since `create_coin_conversion_map`/`ensure_paired_metadata` are core framework flows) and that also uses `TransferRef`-based freezing on the FA side is exposed. The precondition — a nonzero, non-frozen `CoinStore` balance coexisting with a frozen `FungibleStore` — is trivially achievable: an attacker can receive a small `coin::transfer` (which creates/uses a `CoinStore`, independent from the FA freeze) after being frozen, then call the migration entry function. No privileged role or race condition is needed; this is a plain logic error reachable by any signer.

### Recommendation
Never let migration silently *lower* the frozen state of an already-existing `FungibleStore`. At minimum: 1) only propagate `CoinStore.frozen == true` onto the FA store (one-directional escalation), never `false`; 2) never downgrade an FA store's frozen state via a self-service/unprivileged migration path — only via the same `TransferRef`/capability holder that set it; and 3) require `migrate_coin_store_to_fungible_store` to verify caller authority over each address in `accounts`, or restrict it to a governance/framework-privileged caller.

### Proof of Concept
1. Issuer creates `CoinType` with `FreezeCapability`, migrates to paired FA (`create_pairing`/`ensure_paired_metadata`), and users hold balances in `primary_fungible_store`.
2. Attacker's primary `FungibleStore` for `CoinType`'s metadata is frozen by issuer via `fungible_asset::set_frozen_flag` (using `TransferRef`) for compliance reasons.
3. Attacker (or anyone) causes attacker's address to receive `1` unit via legacy `coin::transfer<CoinType>(sender, attacker_addr, 1)`, creating `CoinStore<CoinType>{ coin: 1, frozen: false, .. }` at attacker's address (CoinStore freeze was never separately applied).
4. Attacker calls `coin::migrate_to_fungible_store<CoinType>(attacker_signer)` (or any third party calls `coin::migrate_coin_store_to_fungible_store<CoinType>(vector[attacker_addr])`).
5. Inside `maybe_convert_to_fungible_store`, `frozen` (from CoinStore) = `false` ≠ `fungible_asset::is_frozen(store)` = `true`, so `set_frozen_flag_internal(store, false)` executes, unfreezing the primary store.
6. Attacker's previously frozen FA balance is now transferable, bypassing the issuer's compliance freeze. [3](#0-2) [2](#0-1)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/coin.move (L670-721)
```text
    fun maybe_convert_to_fungible_store<CoinType>(
        account: address
    ) acquires CoinStore, CoinConversionMap, CoinInfo {
        if (exists<CoinStore<CoinType>>(account)) {
            let CoinStore<CoinType> { coin, frozen, deposit_events, withdraw_events } =
                move_from<CoinStore<CoinType>>(account);
            if (is_coin_initialized<CoinType>() && coin.value > 0) {
                let metadata = ensure_paired_metadata<CoinType>();
                let store =
                    primary_fungible_store::ensure_primary_store_exists(
                        account, metadata
                    );

                event::emit(
                    CoinStoreDeletion {
                        coin_type: type_info::type_name<CoinType>(),
                        event_handle_creation_address: guid::creator_address(
                            event::guid(&deposit_events)
                        ),
                        deleted_deposit_event_handle_creation_number: guid::creation_num(
                            event::guid(&deposit_events)
                        ),
                        deleted_withdraw_event_handle_creation_number: guid::creation_num(
                            event::guid(&withdraw_events)
                        )
                    }
                );

                if (coin.value == 0) {
                    destroy_zero(coin);
                } else {
                    fungible_asset::unchecked_deposit_with_no_events(
                        store.object_address(),
                        coin_to_fungible_asset(coin)
                    );
                };

                // Note:
                // It is possible the primary fungible store may already exist before this function call.
                // In this case, if the account owns a frozen CoinStore and an unfrozen primary fungible store, this
                // function would convert and deposit the rest coin into the primary store and freeze it to make the
                // `frozen` semantic as consistent as possible.
                if (frozen != fungible_asset::is_frozen(store)) {
                    fungible_asset::set_frozen_flag_internal(store, frozen);
                }
            } else {
                destroy_zero(coin);
            };
            event::destroy_handle(deposit_events);
            event::destroy_handle(withdraw_events);
        };
    }
```

**File:** aptos-move/framework/aptos-framework/sources/coin.move (L723-738)
```text
    /// Voluntarily migrate to fungible store for `CoinType` if not yet.
    public entry fun migrate_to_fungible_store<CoinType>(
        account: &signer
    ) acquires CoinStore, CoinConversionMap, CoinInfo {
        let account_addr = signer::address_of(account);
        maybe_convert_to_fungible_store<CoinType>(account_addr);
    }

    /// Migrate to fungible store for `CoinType` if not yet.
    public entry fun migrate_coin_store_to_fungible_store<CoinType>(
        accounts: vector<address>
    ) acquires CoinStore, CoinConversionMap, CoinInfo {
        accounts.for_each(|account| {
                maybe_convert_to_fungible_store<CoinType>(account);
            });
    }
```
