## Analysis

The MixBytes bug pattern is: **a balance-affecting event syncs derived/dependent state only along one code path (withdrawal), never the other (pure balance increase), leaving stale/inconsistent state that erodes an invariant (full stake delegation) the system is supposed to maintain.**

The Aptos-native analog is in the Coin→FungibleAsset migration logic in `coin.move`, specifically `maybe_convert_to_fungible_store`, which only propagates the CoinStore's `frozen` flag to the new `FungibleStore` *when the coin balance is non‑zero*. When the balance is zero, the freeze state is silently dropped, and the function is reachable by **any unprivileged caller** for **any target account** via `migrate_coin_store_to_fungible_store`.

### Title
Freeze-flag loss on zero-balance `CoinStore` migration allows unprivileged compliance-freeze bypass - (File: `aptos-move/framework/aptos-framework/sources/coin.move`)

### Summary
`maybe_convert_to_fungible_store` only migrates the `frozen` bit of a `CoinStore<CoinType>` into the corresponding `FungibleStore` inside the `coin.value > 0` branch. When `coin.value == 0`, the function destroys the zero coin and drops the `CoinStore` (including its `frozen: bool`) without creating a `FungibleStore` or otherwise recording the freeze state. Because the public entry point that triggers this path, `migrate_coin_store_to_fungible_store`, takes no signer and no authorization check, any account can force this conversion for any target address, erasing that account's freeze status for the given `CoinType` before any fungible-asset store material exists.

### Finding Description
`maybe_convert_to_fungible_store` is implemented as: [1](#0-0) 

The relevant branch is:
```
if (is_coin_initialized<CoinType>() && coin.value > 0) {
    ... primary_fungible_store::ensure_primary_store_exists(...) ...
    if (frozen != fungible_asset::is_frozen(store)) {
        fungible_asset::set_frozen_flag_internal(store, frozen);
    }
} else {
    destroy_zero(coin);
};
``` [2](#0-1) 

Only the `coin.value > 0` branch ensures a `FungibleStore` exists and copies over `frozen`. The `else` branch (`coin.value == 0`) simply calls `destroy_zero(coin)`; the local `frozen` variable destructured from `CoinStore<CoinType>` is discarded, and no `FungibleStore` is created to carry the freeze state forward.

This function is reachable without any authorization from either of two entry points: [3](#0-2) 

`migrate_to_fungible_store` requires the account's own signer, but `migrate_coin_store_to_fungible_store<CoinType>(accounts: vector<address>)` takes **no signer parameter at all** — it can be invoked by any sender for an arbitrary list of target addresses.

Root cause / broken invariant: the intended custody invariant is that a `frozen` `CoinStore` (used for compliance/blacklist enforcement via `FreezeCapability`) must remain frozen (or have its freeze state preserved) through any representation migration. This invariant only holds conditionally on `coin.value > 0`, so it is broken whenever the frozen account happens to hold a zero balance of that coin at migration time.

### Impact Explanation
An account that has been frozen by the coin issuer (via `FreezeCapability`/`CoinStore.frozen`) for compliance reasons, but currently holds a zero balance, can have its freeze state permanently erased by anyone calling `coin::migrate_coin_store_to_fungible_store<CoinType>(vector[victim])`. After this call:
- The `CoinStore<CoinType>` (and its `frozen = true` flag) is deleted.
- No `FungibleStore` is created (since balance was zero), so no frozen state exists anywhere for that account/asset pair.
- The next time value flows to that account for `CoinType` (e.g., via `primary_fungible_store::deposit`, `coin::deposit`, or a plain transfer), `ensure_primary_store_exists` creates a brand-new, **unfrozen** `FungibleStore`.

This is a freeze-control bypass performed by an unprivileged third party, not the asset issuer — it directly matches the custody-gate category "Unauthorized takeover of ... freeze control ... tied to live assets." It defeats issuer-level compliance/blacklist controls for any `CoinType` still using the legacy `CoinStore` freeze mechanism paired with the FA migration path (this includes AptosCoin and any managed coin using `coin::freeze/coin::FreezeCapability`).

### Likelihood Explanation
High likelihood of triggerability: `migrate_coin_store_to_fungible_store` is a `public entry fun` with no access control, callable in a single transaction by any account, targeting any address list. The only precondition is that the target's `CoinStore<CoinType>` exists, is frozen, and currently has zero balance — a state that is easy to arrange or wait for (e.g., an issuer freezes a wallet after it has already been drained, or freezes proactively before crediting it). No governance or admin privilege is required to execute the bypass.

### Recommendation
Preserve freeze semantics unconditionally, independent of the migrated balance:
- In `maybe_convert_to_fungible_store`, always call `primary_fungible_store::ensure_primary_store_exists` (or an equivalent lightweight store-creation path) and apply the `frozen` flag when the CoinStore is deleted, regardless of `coin.value`.
- Alternatively, disallow migration/deletion of a frozen zero-balance `CoinStore` unless the freeze state is first transferred to a `FungibleStore`, and/or restrict `migrate_coin_store_to_fungible_store` to require some authorization (e.g., only the account owner, or the coin's freeze-capability holder) rather than being fully permissionless for arbitrary target lists.

### Proof of Concept
1. Coin issuer freezes `victim`'s `CoinStore<CoinType>` via `coin::freeze_coin_store` while `victim`'s balance is `0` (either freeze happens before any deposit, or after the balance has been fully withdrawn).
2. Attacker (any account) submits `coin::migrate_coin_store_to_fungible_store<CoinType>(vector[victim])`.
3. Inside `maybe_convert_to_fungible_store`, `coin.value == 0` so the `else` branch executes: `CoinStore<CoinType>` (with `frozen = true`) is dropped via `destroy_zero(coin)`, and no `FungibleStore` is created — freeze state is lost.
4. Later, `victim` (or anyone) receives `CoinType` value through `primary_fungible_store::deposit`/`coin::deposit`, which calls `ensure_primary_store_exists`, creating a new, unfrozen `FungibleStore`.
5. `victim` can now freely transfer/withdraw the asset despite the issuer's original freeze decision, with no compliance control in effect for that `CoinType`.

Note: I was unable to further trace `coin::freeze_coin_store`/`FreezeCapability` call sites or confirm production usage (e.g., which real mainnet `CoinType`s rely on `CoinStore.frozen` post-FA-migration) due to running out of search iterations; a Devin session with full repo access could verify usage of `FreezeCapability` and `coin::freeze_coin_store` across the codebase/ecosystem to confirm real-world exposure before treating this as confirmed-exploitable in production.

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
