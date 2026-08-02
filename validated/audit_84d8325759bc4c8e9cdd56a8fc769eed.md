### Title
Dispatchable withdraw/deposit hooks on `FungibleStore` can be completely bypassed via raw `object::transfer` of the store object - ([File: aptos-move/framework/aptos-framework/sources/fungible_asset.move])

### Summary
The custody invariant broken by the Solana report is: *"every value-moving operation on an asset must route through the issuer-defined hook that gates that transfer."* On Aptos, the analogous mechanism is `dispatchable_fungible_asset`, which lets an issuer register custom `withdraw`/`deposit` functions (allow-lists, pause, denylist, loyalty fees, etc.) on a `Metadata` object [1](#0-0) . These hooks are only invoked inside `fungible_asset::withdraw`/`deposit` (via `withdraw_sanity_check`/`deposit_sanity_check`) [2](#0-1) . However, a `FungibleStore` is itself a generic Aptos `Object`, and object ownership can be changed with the framework's generic `object::transfer`, which does not go through `fungible_asset::withdraw`/`deposit` at all and therefore never invokes the registered hook.

### Finding Description
`fungible_asset::create_store` only disables ungated (generic-object) transfer of the store when the **metadata** has the `Untransferable` marker resource; it does nothing to protect stores whose issuer instead relies on dispatch hooks for control (allow-list, freeze/pause, KYC denylist):

```rust
// aptos-move/framework/aptos-framework/sources/fungible_asset.move
public fun create_store<T: key>(
    constructor_ref: &ConstructorRef, metadata: Object<T>
): Object<FungibleStore> {
    ...
    if (is_untransferable(metadata)) {
        constructor_ref.set_untransferable();
    };
    ...
}
``` [3](#0-2) 

`is_untransferable` only checks a completely separate global flag on the metadata object [4](#0-3) ; it has no relationship to whether `DispatchFunctionStore` (the withdraw/deposit hook registry) is populated [5](#0-4) .

By contrast, the framework's *primary* fungible stores are explicitly protected: `primary_fungible_store::create_primary_store` disables ungated transfer on every primary store it creates, specifically because "deterministic stores shouldn't be transferrable":

```rust
// aptos-move/framework/aptos-framework/sources/primary_fungible_store.move
let transfer_ref = &constructor_ref.generate_transfer_ref();
transfer_ref.disable_ungated_transfer();
``` [6](#0-5) 

That protection exists **only** for primary stores. Any secondary store created directly via `fungible_asset::create_store` (which any FA integrator — allow-list tokens, loyalty tokens, transfer-restricted "predicated transfer" tokens per the module's own doc comment) remains a normal, ungated-transferable `Object` by default [7](#0-6) . The `withdraw`/`deposit` dispatch hooks are only consulted inside `fungible_asset::withdraw`/`deposit`/`withdraw_sanity_check`/`deposit_sanity_check` [8](#0-7)  — they are never consulted by the generic object-ownership-transfer path in `object.move`. Because a `FungibleStore`'s effective "owner" is determined purely by `Object` ownership (checked via `object::owns(store, owner_address)` in `withdraw_sanity_check_impl`) [9](#0-8) , any holder of a non-primary store can call the generic `0x1::object::transfer` entry function on the store object to reassign the entire balance-carrying object — including its full balance — to an arbitrary recipient, without ever invoking the issuer's withdraw/deposit hook and without emitting the FA-level deposit/withdraw events used for compliance tracking.

This mirrors the Solana report's root cause exactly: a hook that the issuer relies on for custody control (Transfer Hook / allow-list / freeze logic) is not enforced on every code path that moves value, because one specific path (raw CPI parameter vs. raw object transfer) hardcodes/omits the hook plumbing.

### Impact Explanation
Any fungible asset built on `dispatchable_fungible_asset` that uses dispatch hooks for compliance/custody logic (transfer allow-lists, denylists, pause-on-freeze business logic, loyalty/fee-on-transfer accounting) can have that control completely circumvented for any non-primary store: the holder transfers the whole store object to a blocked/unauthorized address, and the recipient now legitimately owns that balance-bearing object with no allow-list check, no fee deduction, and no on-chain deposit event ever having fired. This corrupts supply/custody accounting (deposit/withdraw events, and any derived-balance/fee bookkeeping the issuer's hook implements) and moves value to a holder the issuer's custody logic was designed to exclude — a direct custody/compliance bypass on live, mainnet-relevant fungible assets.

### Likelihood Explanation
Medium-to-High: no privileged action is required — any account that holds (or can be granted) a secondary `FungibleStore` object for a dispatch-hook-gated asset can invoke the standard `object::transfer` entry function themselves. The only precondition is that the issuer used a secondary (non-primary) store and relied on dispatch hooks rather than `Untransferable`, which is exactly the design pattern the `dispatchable_fungible_asset` module's own documentation recommends for allow-list/pause/loyalty tokens.

### Recommendation
- When `register_dispatch_functions` registers a non-trivial `withdraw_function`/`deposit_function` for a metadata object, require (or automatically enforce) that any `FungibleStore` created against that metadata also has ungated transfer disabled, so that the only way to move the store's value is through `fungible_asset::withdraw`/`deposit` (and hence through the hook).
- Alternatively, expose an API so issuers can mark a `Metadata` object as "hook-gated, stores must not be raw-transferable" independent of the existing `Untransferable` flag, and enforce it in `fungible_asset::create_store`.
- Document explicitly that dispatch hooks do not gate raw object-ownership transfers of `FungibleStore`, and audit/patch example modules (`fa_coin`, `bonding_curve_launchpad`, `usdk`, `managed_fungible_asset`) that assume hook-only enforcement.

### Proof of Concept
1. Issuer deploys an FA with `register_dispatch_functions` setting a `withdraw` hook that enforces an allow-list (per the documented "Transfer allowlist" use case) [10](#0-9) .
2. A non-primary `FungibleStore` is created for account `A` via `fungible_asset::create_store` (e.g., an escrow/vault-style store used by a dApp) — ungated transfer is left enabled because `is_untransferable(metadata)` is false [11](#0-10) .
3. `A` holds a non-allow-listed address `B` it wants to send funds to, which the issuer's `withdraw` hook would normally reject.
4. Instead of calling `dispatchable_fungible_asset::transfer` (which would invoke the hook and be rejected), `A` calls `0x1::object::transfer<FungibleStore>(A_signer, store_object, B)`.
5. Ownership of the store object — and its entire balance — moves to `B` with no hook invocation, no allow-list check, and no deposit/withdraw event emitted, fully bypassing the issuer's custody control.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L4-16)
```text
/// The dispatchable_fungible_asset wraps the existing fungible_asset module and adds the ability for token issuer
/// to customize the logic for withdraw and deposit operations. For example:
///
/// - Deflation token: a fixed percentage of token will be destructed upon transfer.
/// - Transfer allowlist: token can only be transfered to addresses in the allow list.
/// - Predicated transfer: transfer can only happen when some certain predicate has been met.
/// - Loyalty token: a fixed loyalty will be paid to a designated address when a fungible asset transfer happens
///
/// The api listed here intended to be an in-place replacement for defi applications that uses fungible_asset api directly
/// and is safe for non-dispatchable (aka vanilla) fungible assets as well.
///
/// See AIP-73 for further discussion
///
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L363-367)
```text
    #[view]
    /// Returns true if the FA is untransferable.
    public fun is_untransferable<T: key>(metadata: Object<T>): bool {
        exists<Untransferable>(metadata.object_address())
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L370-448)
```text
    public(friend) fun register_dispatch_functions(
        constructor_ref: &ConstructorRef,
        withdraw_function: Option<FunctionInfo>,
        deposit_function: Option<FunctionInfo>,
        derived_balance_function: Option<FunctionInfo>
    ) {
        // Verify that caller type matches callee type so wrongly typed function cannot be registered.
        withdraw_function.for_each_ref(|withdraw_function| {
                let dispatcher_withdraw_function_info =
                    function_info::new_function_info_from_address(
                        @aptos_framework,
                        string::utf8(b"dispatchable_fungible_asset"),
                        string::utf8(b"dispatchable_withdraw")
                    );

                assert!(
                    function_info::check_dispatch_type_compatibility(
                        &dispatcher_withdraw_function_info,
                        withdraw_function
                    ),
                    error::invalid_argument(EWITHDRAW_FUNCTION_SIGNATURE_MISMATCH)
                );
            });

        deposit_function.for_each_ref(|deposit_function| {
                let dispatcher_deposit_function_info =
                    function_info::new_function_info_from_address(
                        @aptos_framework,
                        string::utf8(b"dispatchable_fungible_asset"),
                        string::utf8(b"dispatchable_deposit")
                    );
                // Verify that caller type matches callee type so wrongly typed function cannot be registered.
                assert!(
                    function_info::check_dispatch_type_compatibility(
                        &dispatcher_deposit_function_info,
                        deposit_function
                    ),
                    error::invalid_argument(EDEPOSIT_FUNCTION_SIGNATURE_MISMATCH)
                );
            });

        derived_balance_function.for_each_ref(|balance_function| {
                let dispatcher_derived_balance_function_info =
                    function_info::new_function_info_from_address(
                        @aptos_framework,
                        string::utf8(b"dispatchable_fungible_asset"),
                        string::utf8(b"dispatchable_derived_balance")
                    );
                // Verify that caller type matches callee type so wrongly typed function cannot be registered.
                assert!(
                    function_info::check_dispatch_type_compatibility(
                        &dispatcher_derived_balance_function_info,
                        balance_function
                    ),
                    error::invalid_argument(
                        EDERIVED_BALANCE_FUNCTION_SIGNATURE_MISMATCH
                    )
                );
            });
        register_dispatch_function_sanity_check(constructor_ref);
        assert!(
            !exists<DispatchFunctionStore>(
                constructor_ref.address_from_constructor_ref()
            ),
            error::already_exists(EALREADY_REGISTERED)
        );

        let store_obj = &constructor_ref.generate_signer();

        // Store the overload function hook.
        move_to<DispatchFunctionStore>(
            store_obj,
            DispatchFunctionStore {
                withdraw_function,
                deposit_function,
                derived_balance_function
            }
        );
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

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L956-987)
```text
    public fun withdraw<T: key>(
        owner: &signer, store: Object<T>, amount: u64
    ): FungibleAsset acquires FungibleStore, DispatchFunctionStore, ConcurrentFungibleBalance {
        withdraw_sanity_check(owner, store, true);
        unchecked_withdraw(store.object_address(), amount)
    }

    /// Check the permission for withdraw operation.
    public(friend) fun withdraw_sanity_check<T: key>(
        owner: &signer, store: Object<T>, abort_on_dispatch: bool
    ) acquires FungibleStore, DispatchFunctionStore {
        withdraw_sanity_check_impl(
            signer::address_of(owner),
            store,
            abort_on_dispatch
        )
    }

    inline fun withdraw_sanity_check_impl<T: key>(
        owner_address: address, store: Object<T>, abort_on_dispatch: bool
    ) {
        assert!(
            object::owns(store, owner_address),
            error::permission_denied(ENOT_STORE_OWNER)
        );
        let fa_store = borrow_store_resource(&store);
        assert!(
            !abort_on_dispatch || !has_withdraw_dispatch_function(fa_store.metadata),
            error::invalid_argument(EINVALID_DISPATCHABLE_OPERATIONS)
        );
        assert!(!fa_store.frozen, error::permission_denied(ESTORE_IS_FROZEN));
    }
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L82-88)
```text
        let derive_ref = &borrow_global<DeriveRefPod>(metadata_addr).metadata_derive_ref;
        let constructor_ref = &object::create_user_derived_object(owner_addr, derive_ref);
        // Disable ungated transfer as deterministic stores shouldn't be transferrable.
        let transfer_ref = &constructor_ref.generate_transfer_ref();
        transfer_ref.disable_ungated_transfer();

        fungible_asset::create_store(constructor_ref, metadata)
```
