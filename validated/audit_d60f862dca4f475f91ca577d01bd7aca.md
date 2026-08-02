## Title
`maybe_convert_to_fungible_store()` silently discards the `frozen` flag when the legacy `CoinStore` balance is zero, letting a frozen account escape freeze control on migration - ([File: aptos-move/framework/aptos-framework/sources/coin.move])

### Summary
`coin::maybe_convert_to_fungible_store()` (invoked from the permissionless `migrate_to_fungible_store` / `migrate_coin_store_to_fungible_store` entry functions) only propagates a legacy `CoinStore.frozen` flag to the new/target `FungibleStore` inside the `is_coin_initialized<CoinType>() && coin.value > 0` branch. When a `CoinStore<CoinType>` has `frozen == true` but `coin.value == 0`, execution falls into the `else` branch, which simply calls `destroy_zero(coin)` and drops the whole `CoinStore` resource — including its `frozen` bit — without ever writing that state anywhere else. [1](#0-0) 

### Finding Description
`maybe_convert_to_fungible_store` moves out the `CoinStore<CoinType>` resource (`coin`, `frozen`, event handles) and then branches on whether the coin has a positive balance:

```
fun maybe_convert_to_fungible_store<CoinType>(account: address) ... {
    if (exists<CoinStore<CoinType>>(account)) {
        let CoinStore<CoinType> { coin, frozen, deposit_events, withdraw_events } = move_from<CoinStore<CoinType>>(account);
        if (is_coin_initialized<CoinType>() && coin.value > 0) {
            ... primary_fungible_store::ensure_primary_store_exists ...
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
``` [1](#0-0) 

The `frozen` field is only consulted (and copied onto a `FungibleStore` via `fungible_asset::set_frozen_flag_internal`) inside the `coin.value > 0` branch. If balance is `0` — which is exactly the state a compliance/freeze authority would use when preemptively freezing an account that has not yet received `CoinType` — the function takes the `else` path, destroys the zero-value `Coin<CoinType>`, and discards `frozen` entirely. No `FungibleStore` is created, and critically, no record of the freeze state survives. This is called from the fully permissionless entry points `migrate_to_fungible_store` and `migrate_coin_store_to_fungible_store`, callable by the frozen account holder (or anyone, for the batch variant) at any time. [2](#0-1) 

Once the `CoinStore` is destroyed this way, any subsequent interaction that creates a `FungibleStore` for that account/metadata (e.g. `primary_fungible_store::deposit`, `ensure_primary_store_exists`) starts from `frozen == false` by default, since `fungible_asset::create_store` always initializes `frozen: false`. [3](#0-2) 

This breaks the custody invariant that "Fungible asset metadata, primary and secondary stores ... and freeze state must preserve supply and holder identity" across store-creation/migration paths: the freeze authority's control over the account is silently voided by an action the frozen party itself can trigger.

### Impact Explanation
Freeze functionality in Aptos coin/FA is the mechanism used by issuers/compliance modules to block a specific account from moving a given asset (e.g., sanctioned addresses, exploit-recovery addresses). This bug allows the frozen party to permanently and unilaterally erase that restriction by calling a public, unprivileged entry function (`migrate_to_fungible_store`) whenever their legacy `CoinStore` balance happens to be zero. After migration, the account can freely receive and transfer the paired FA with no freeze enforcement, even though the freeze authority never un-froze them. This is a custody/authority-control bypass (unauthorized removal of freeze control) rather than a benign accounting error, and for compliance-critical or exploit-mitigation freezes on mainnet assets this is a high-impact issue.

### Likelihood Explanation
The trigger requires only: (1) a `CoinType` with `AptosFramework`-migration enabled (`ensure_paired_metadata`), (2) the target account holding a `CoinStore<CoinType>` with `frozen == true` and `coin.value == 0`, and (3) a call to the permissionless `migrate_to_fungible_store`. Freezing a zero-balance account is a normal compliance action (freeze first, before/without ever crediting funds, or after balance is fully swept to zero by other means), so this is a realistic, low-effort trigger requiring no special privileges from the caller.

### Recommendation
In `maybe_convert_to_fungible_store`, always propagate the `frozen` flag regardless of `coin.value`. Specifically, when the balance is zero, still ensure a `FungibleStore` exists (or otherwise persist the frozen bit) via `primary_fungible_store::ensure_primary_store_exists` and apply `fungible_asset::set_frozen_flag_internal(store, frozen)` before discarding the (zero-valued) `Coin`, instead of only doing so under the `coin.value > 0` branch.

### Proof of Concept
1. Freeze/compliance authority calls the freeze capability to set `frozen = true` on a `CoinStore<CoinType>` for `victim` while `victim`'s `coin.value == 0` (e.g., freeze applied pre-emptively, or balance later drained to zero through normal spending prior to being frozen).
2. `victim` (or anyone, via `migrate_coin_store_to_fungible_store`) calls `coin::migrate_to_fungible_store<CoinType>(victim_signer)`.
3. Inside `maybe_convert_to_fungible_store`, `coin.value == 0` so the `else` branch executes: `destroy_zero(coin)` runs, `frozen` is dropped, and no `FungibleStore`/frozen flag is persisted.
4. `victim` (or anyone) later calls `primary_fungible_store::deposit`/transfer for the paired FA metadata; `ensure_primary_store_exists` creates a fresh `FungibleStore` with `frozen: false`.
5. `victim` now transfers/receives the asset freely, despite never having been un-frozen by the freeze authority — confirming the freeze-control bypass.

Note: I was not able to fully load the surrounding `coin.move` freeze-setter functions (`fungible_asset::set_frozen_flag_internal`, `coin::freeze`/equivalent) in this session due to search/tool limitations on this final iteration, so exact call sites that set `CoinStore.frozen = true` on a zero-balance account should be re-verified directly in the repository (a Devin session with full file access would confirm this precisely) before treating this as fully proven; the code shown above for `maybe_convert_to_fungible_store` and `fungible_asset::create_store` was directly read and is accurate.

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

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L892-917)
```text
    /// Allow an object to hold a store for fungible assets.
    /// Applications can use this to create multiple stores for isolating fungible assets for different purposes.
    public fun create_store<T: key>(
        constructor_ref: &ConstructorRef, metadata: Object<T>
    ): Object<FungibleStore> {
        let store_obj = &constructor_ref.generate_signer();
        move_to(
            store_obj,
            FungibleStore { metadata: metadata.convert(), balance: 0, frozen: false }
        );

        if (is_untransferable(metadata)) {
            constructor_ref.set_untransferable();
        };

        if (default_to_concurrent_fungible_balance()) {
            move_to(
                store_obj,
                ConcurrentFungibleBalance {
                    balance: aggregator_v2::create_unbounded_aggregator()
                }
            );
        };

        constructor_ref.object_from_constructor_ref<FungibleStore>()
    }
```
