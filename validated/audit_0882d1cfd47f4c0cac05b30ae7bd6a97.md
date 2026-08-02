## Custody Analog Found: Freeze-status desync between `CoinStore` and `FungibleStore` allows self-unfreeze during migration

### Title
Frozen fungible asset store can be silently un-frozen by its own (frozen) owner via stale `CoinStore.frozen` reuse during coin-to-fungible-asset migration - (File: `aptos-move/framework/aptos-framework/sources/coin.move`)

### Summary
The external report's root cause is a cached/stale status field (`isOverflow`) being blindly re-applied to a re-processed entity instead of being re-evaluated against current authoritative state, silently corrupting a control field that other participants rely on for consensus. The Aptos-native analog is `maybe_convert_to_fungible_store<CoinType>` in `coin.move`, which synchronizes a `FungibleStore`'s `frozen` flag from the legacy `CoinStore<CoinType>.frozen` value whenever a user migrates leftover coin balance — without checking who last set the `FungibleStore`'s frozen bit or why.

### Finding Description
`maybe_convert_to_fungible_store` moves out an account's `CoinStore<CoinType>`, and if it still holds value, deposits the leftover coins into the account's fungible-asset primary store and then reconciles the frozen flags: [1](#0-0) 

The critical logic is:
```
if (frozen != fungible_asset::is_frozen(store)) {
    fungible_asset::set_frozen_flag_internal(store, frozen);
}
``` [2](#0-1) 

`CoinStore.frozen` reflects only the legacy, coin-specific freeze mechanism (set/unset by the `FreezeCapability<CoinType>` holder). `FungibleStore.frozen` is an independent control field that can be set by a completely different authority — the fungible-asset issuer's `TransferRef` (`fungible_asset::set_frozen_flag`/`set_frozen_flag_internal`), which is the primary freeze mechanism for the migrated/native fungible-asset world (e.g. compliance freezes, sanctions lists, dispatchable-hook-gated assets).

This function is exposed as a self-service, unprivileged entry point: [3](#0-2) 

Because the reconciliation is unconditional ("make the frozen semantic as consistent as possible" per the inline comment) and only compares the two flags rather than checking which freeze authority is authoritative or more recent, a store that was legitimately frozen at the fungible-asset level can have that freeze silently cleared merely because the account's old, never-frozen `CoinStore<CoinType>` still holds non-zero value.

This is structurally identical to the external bug: a control status computed under one context (BTC block height / CoinType-level freeze) is blindly reused to overwrite the authoritative status computed under a different, more current context (post-reorg overflow state / FA-level freeze), because the re-evaluation path assumes the cached value is still valid.

### Impact Explanation
An account frozen by a fungible-asset issuer (via `TransferRef`) for compliance/security reasons can unilaterally restore its own ability to transfer/withdraw funds by calling the unprivileged `migrate_to_fungible_store<CoinType>` entry function, provided it retains any non-zero balance in the corresponding legacy `CoinStore<CoinType>` (trivial to arrange, since coin-level freezing of that specific `CoinType` is a separate, typically unused capability for most accounts). This is a custody-control bypass: it reassigns freeze/control authority away from the intended FA-level admin/issuer to the frozen account itself, directly matching the "unauthorized freeze/owner reassignment" and "custody accounting corruption" impact classes. Impact is High: it defeats a security control (freeze) that gates transferability of live, potentially high-value fungible-asset balances.

### Likelihood Explanation
Likelihood is Medium-High: no special privilege is required — only (1) an FA-level freeze on the target account's primary store, and (2) any nonzero residual `CoinStore<CoinType>` balance for a coin type that has been migrated/paired to that fungible asset. Since the migration function is a public entry function callable by the account itself, exploitation requires no cooperation from any other party and no race condition — it is a deterministic, repeatable bypass.

### Recommendation
Do not unconditionally propagate `CoinStore.frozen` onto an existing `FungibleStore`. At minimum:
- Only allow the sync to move the store from unfrozen → frozen (never automatically unfreeze), or
- Skip the sync entirely if the `FungibleStore` already exists (only apply it when the primary store is newly created by this same call), or
- Require the caller to hold the FA-level `TransferRef`/freeze authority to change `FungibleStore.frozen`, rather than deriving it from a legacy, unrelated freeze flag.

### Proof of Concept
1. Fungible-asset issuer freezes `alice`'s primary store for `CoinType`'s paired metadata using `TransferRef::set_frozen_flag` (store.frozen = true).
2. `alice` still has a `CoinStore<CoinType>` with `frozen = false` and `coin.value > 0` (e.g., a small leftover balance never migrated).
3. `alice` calls `coin::migrate_to_fungible_store<CoinType>(&alice)`.
4. Inside `maybe_convert_to_fungible_store`, `frozen` (from `CoinStore`, `false`) `!= fungible_asset::is_frozen(store)` (`true`), so `fungible_asset::set_frozen_flag_internal(store, false)` executes, clearing the issuer-imposed freeze.
5. `alice`'s primary store is now unfrozen and transferable, despite the issuer never having lifted the freeze.

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

**File:** aptos-move/framework/aptos-framework/sources/coin.move (L723-729)
```text
    /// Voluntarily migrate to fungible store for `CoinType` if not yet.
    public entry fun migrate_to_fungible_store<CoinType>(
        account: &signer
    ) acquires CoinStore, CoinConversionMap, CoinInfo {
        let account_addr = signer::address_of(account);
        maybe_convert_to_fungible_store<CoinType>(account_addr);
    }
```
