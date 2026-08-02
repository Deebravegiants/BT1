## Custody Analog Finding

### Title
Object-layer `transfer` bypasses dispatchable `FungibleStore` withdraw/deposit hooks (pause, denylist, permissioned-withdraw) - ([File: aptos-move/framework/aptos-framework/sources/fungible_asset.move])

### Summary
The Malt bug worked because a business-logic gate ("buy block") could be routed around by using a different, whitelisted state-mutation path (`addLiquidity`/`removeLiquidity`) that did not itself enforce the gate. The Aptos custody analog is structurally identical: a `FungibleAsset` issuer can attach custom withdraw/deposit business logic (pause flags, denylists, permissioned withdraw) via `dispatchable_fungible_asset::register_dispatch_functions`, but that logic is only invoked through `dispatchable_fungible_asset::withdraw/deposit/transfer`. The underlying `FungibleStore` is still an ordinary Aptos `Object`, and Aptos objects are transferable-by-default (`allow_ungated_transfer = true`). Unless the issuer *also* opts in to `fungible_asset::set_untransferable` on the metadata, any store holder can call the generic `object::transfer` entry function directly on the store's object address, moving the entire balance to any address while completely skipping the custom withdraw/deposit dispatch hooks and the `frozen` check tied to them.

### Finding Description
`FungibleStore` is defined as a normal object resource with a `frozen` flag and, optionally, custom dispatch hooks stored in `DispatchFunctionStore`: [1](#0-0) 

Custom hooks are only consulted by `dispatchable_fungible_asset::withdraw`/`deposit`, which call `fungible_asset::withdraw_sanity_check`/`deposit_sanity_check` and then the registered function: [2](#0-1) 

Real-world hook implementations use this to enforce custody-relevant controls — e.g. FACoin's pause/denylist: [3](#0-2) 

and the bonding-curve launchpad's "global freezing effect" permissioned withdraw: [4](#0-3) 

Nowhere in this hook path is the object-layer `owner`/`allow_ungated_transfer` field touched. Ownership of the `FungibleStore` object is governed exclusively by `object::transfer`/`transfer_raw`, which only checks `ObjectCore.allow_ungated_transfer` and that the caller is the current owner — it has no knowledge of `FungibleStore.frozen` or `DispatchFunctionStore`: [5](#0-4) 

By default, new objects (including `FungibleStore` objects created via `fungible_asset::create_store`) are created with `allow_ungated_transfer = true`: [6](#0-5) 

The only mechanism that prevents raw object transfer of a `FungibleStore` is `fungible_asset::set_untransferable`, which is an **opt-in** call the metadata creator must make at initialization time: [7](#0-6) 

None of the dispatchable-FA reference implementations found in the repo (`FACoin.move`, `bonding_curve_launchpad.move`, `simple_token.move`, `clamped_token.move`) call `set_untransferable` during initialization: [8](#0-7) [9](#0-8) 

This mirrors the Malt pattern exactly: a privileged, security-critical gate (buy-block / pause / denylist / permissioned-withdraw) is enforced only on one code path (swap / `dispatchable_fungible_asset::withdraw`), while an orthogonal, unprivileged, whitelisted-by-default path (add/remove liquidity / `object::transfer`) achieves the same value movement without the gate.

### Impact Explanation
Any holder of a dispatchable `FungibleStore` (not just primary stores — any store created via `fungible_asset::create_store`, which is `public` and used directly by protocols such as `managed_fungible_asset.move`) can move their entire balance to an arbitrary address by transferring the container object instead of calling `transfer`/`withdraw`. This:
- Defeats denylist/freeze/pause controls that issuers rely on for regulatory or security custody guarantees (e.g., FACoin's `paused` state, `freeze_account`).
- Defeats "permissioned withdraw" style controls used as a global circuit-breaker (bonding-curve launchpad's comment explicitly calls this "a conditionally global freezing effect").
- Allows a frozen store's balance to still change hands: `frozen` blocks `dispatchable_fungible_asset::withdraw/deposit`, but not `object::transfer` of the store itself, so a frozen account can still transfer out its whole balance by moving store ownership.

This is a custody/asset-control bypass with direct mainnet relevance to any token issuer using dispatchable hooks without also calling `set_untransferable`.

### Likelihood Explanation
High for any project that copies the reference dispatchable-FA patterns in this repo (FACoin, bonding-curve launchpad, or similar) without independently learning to call `fungible_asset::set_untransferable`. The vulnerability requires no special privilege — only that the attacker already owns (or is given, even temporarily) a `FungibleStore` object for the asset, and knows the object's address, both of which are always available to a normal holder. I was not able to fully verify within this investigation whether `primary_fungible_store::create_primary_store` unconditionally forces `set_untransferable` on primary stores regardless of the metadata-level opt-in (the source for `ensure_primary_store_exists`/`create_primary_store` internals was not reached before the tool budget ran out); if it does not, the bug also affects the much more common primary-store flow, which would raise likelihood/impact further. This should be verified directly against `primary_fungible_store.move`'s store-creation function before finalizing severity.

### Recommendation
- Make `Untransferable` the default for all `FungibleStore` objects (both primary and secondary), requiring an explicit opt-out only for legitimate use cases (if any), rather than requiring issuers to opt in.
- Alternatively, have `object::transfer`/`transfer_raw` refuse to move any object that carries a `FungibleStore` resource unless the metadata has explicitly allowed store transfers, closing the gap between the two independent ownership models (object ownership vs. fungible-asset custody control).
- Audit all dispatchable-FA examples/templates in the repo (FACoin, bonding_curve_launchpad, clamped_token, simple_token) to add `fungible_asset::set_untransferable` calls, since these are used as copy-paste templates by external developers.

### Proof of Concept
1. Issuer deploys a dispatchable FA (e.g., FACoin pattern) and calls `dispatchable_fungible_asset::register_dispatch_functions` with a custom `withdraw`/`deposit` that checks `assert_not_paused()`, but does **not** call `fungible_asset::set_untransferable` on the metadata's `ConstructorRef`.
2. Issuer calls `set_pause(true)` (or `freeze_account`) intending to prevent all transfers of a flagged account's tokens.
3. The flagged holder calls `fungible_asset::create_store` — or already owns a non-primary `FungibleStore` object holding their balance — and instead of calling `fungible_asset::transfer`/`dispatchable_fungible_asset::transfer` (which would hit `assert_not_paused()`/`is_frozen` and abort), calls `aptos_framework::object::transfer<FungibleStore>(holder, store_object, attacker_address)`.
4. `object::transfer_raw` only checks `ObjectCore.allow_ungated_transfer` (true by default) and `owner == signer`; it never touches `FungibleStore.frozen` or `DispatchFunctionStore`, so the transfer succeeds and the entire balance (the whole `FungibleStore.balance` field) moves to `attacker_address`, bypassing pause/denylist/freeze entirely.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L145-161)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    /// The store object that holds fungible assets of a specific type associated with an account.
    struct FungibleStore has key {
        /// The address of the base metadata object.
        metadata: Object<Metadata>,
        /// The balance of the fungible metadata.
        balance: u64,
        /// If true, owner transfer is disabled that only `TransferRef` can move in/out from this store.
        frozen: bool
    }

    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    struct DispatchFunctionStore has key {
        withdraw_function: Option<FunctionInfo>,
        deposit_function: Option<FunctionInfo>,
        derived_balance_function: Option<FunctionInfo>
    }
```

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L352-367)
```text
    /// Set that only untransferable stores can be created for this fungible asset.
    public fun set_untransferable(constructor_ref: &ConstructorRef) {
        let metadata_addr = constructor_ref.address_from_constructor_ref();
        assert!(
            exists<Metadata>(metadata_addr),
            error::not_found(EFUNGIBLE_METADATA_EXISTENCE)
        );
        let metadata_signer = &constructor_ref.generate_signer();
        move_to(metadata_signer, Untransferable {});
    }

    #[view]
    /// Returns true if the FA is untransferable.
    public fun is_untransferable<T: key>(metadata: Object<T>): bool {
        exists<Untransferable>(metadata.object_address())
    }
```

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L72-119)
```text
    public fun withdraw<T: key>(
        owner: &signer,
        store: Object<T>,
        amount: u64,
    ): FungibleAsset acquires TransferRefStore {
        fungible_asset::withdraw_sanity_check(owner, store, false);
        let func_opt = fungible_asset::withdraw_dispatch_function(store);
        if (func_opt.is_some()) {
            let func = func_opt.borrow();
            if (features::is_function_value_dispatch_enabled()) {
                dispatch_withdraw_hook(store, amount, borrow_transfer_ref(store), func)
            } else {
                function_info::load_module_from_function(func);
                dispatchable_withdraw(
                    store,
                    amount,
                    borrow_transfer_ref(store),
                    func,
                )
            }
        } else {
            fungible_asset::unchecked_withdraw(store.object_address(), amount)
        }
    }

    /// Deposit `amount` of the fungible asset to `store`.
    ///
    /// The semantics of deposit will be governed by the function specified in DispatchFunctionStore.
    public fun deposit<T: key>(store: Object<T>, fa: FungibleAsset) acquires TransferRefStore {
        fungible_asset::deposit_sanity_check(store, false);
        let func_opt = fungible_asset::deposit_dispatch_function(store);
        if (func_opt.is_some()) {
            let func = func_opt.borrow();
            if (features::is_function_value_dispatch_enabled()) {
                dispatch_deposit_hook(store, fa, borrow_transfer_ref(store), func)
            } else {
                function_info::load_module_from_function(func);
                dispatchable_deposit(
                    store,
                    fa,
                    borrow_transfer_ref(store),
                    func
                )
            }
        } else {
            fungible_asset::unchecked_deposit(store.object_address(), fa)
        }
    }
```

**File:** aptos-move/move-examples/fungible_asset/fa_coin/sources/FACoin.move (L61-87)
```text
        // Create a global state to pause the FA coin and move to Metadata object.
        move_to(
            &metadata_object_signer,
            State { paused: false, }
        );

        // Override the deposit and withdraw functions which mean overriding transfer.
        // This ensures all transfer will call withdraw and deposit functions in this module
        // and perform the necessary checks.
        // This is OPTIONAL. It is an advanced feature and we don't NEED a global state to pause the FA coin.
        let deposit = function_info::new_function_info(
            admin,
            string::utf8(b"fa_coin"),
            string::utf8(b"deposit"),
        );
        let withdraw = function_info::new_function_info(
            admin,
            string::utf8(b"fa_coin"),
            string::utf8(b"withdraw"),
        );
        dispatchable_fungible_asset::register_dispatch_functions(
            constructor_ref,
            option::some(withdraw),
            option::some(deposit),
            option::none(),
        );
    }
```

**File:** aptos-move/move-examples/fungible_asset/fa_coin/sources/FACoin.move (L96-116)
```text
    /// Deposit function override to ensure that the account is not denylisted and the FA coin is not paused.
    /// OPTIONAL
    public fun deposit<T: key>(
        store: Object<T>,
        fa: FungibleAsset,
        transfer_ref: &TransferRef,
    ) acquires State {
        assert_not_paused();
        fungible_asset::deposit_with_ref(transfer_ref, store, fa);
    }

    /// Withdraw function override to ensure that the account is not denylisted and the FA coin is not paused.
    /// OPTIONAL
    public fun withdraw<T: key>(
        store: Object<T>,
        amount: u64,
        transfer_ref: &TransferRef,
    ): FungibleAsset acquires State {
        assert_not_paused();
        fungible_asset::withdraw_with_ref(transfer_ref, store, amount)
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/bonding_curve_launchpad.move (L221-237)
```text
        let mint_ref = fungible_asset::generate_mint_ref(fa_obj_constructor_ref);
        let transfer_ref = fungible_asset::generate_transfer_ref(fa_obj_constructor_ref);
        let fa_minted = fungible_asset::mint(&mint_ref, (max_supply as u64));
        // Define the dispatchable FA's withdraw as a conditionally global freezing effect.
        dispatchable_fungible_asset::register_dispatch_functions(
            fa_obj_constructor_ref,
            option::some(launchpad.permissioned_withdraw),
            option::none(),
            option::none()
        );
        // Store `transfer_ref` for later usage, within the FA's object.
        // `tranfer_ref` will be required to allow the smart contract's modules to ignore the dispatchable
        // withdraw's frozen status for each swap of an FA on `liquidity_pair`.
        move_to(
            &fa_obj_signer,
            FAController { transfer_ref }
        );
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L558-594)
```text
    /// Transfers ownership of the object (and all associated resources) at the specified address
    /// for Object<T> to the "to" address.
    public entry fun transfer<T: key>(
        owner: &signer,
        object: Object<T>,
        to: address,
    ) {
        transfer_raw(owner, object.inner, to)
    }

    /// Attempts to transfer using addresses only. Transfers the given object if
    /// allow_ungated_transfer is set true. Note, that this allows the owner of a nested object to
    /// transfer that object, so long as allow_ungated_transfer is enabled at each stage in the
    /// hierarchy.
    public fun transfer_raw(
        owner: &signer,
        object: address,
        to: address,
    ) {
        let owner_address = signer::address_of(owner);
        verify_ungated_and_descendant(owner_address, object);
        transfer_raw_inner(object, to);
    }

    inline fun transfer_raw_inner(object: address, to: address) {
        let object_core = borrow_global_mut<ObjectCore>(object);
        if (object_core.owner != to) {
            event::emit(
                Transfer {
                    object,
                    from: object_core.owner,
                    to,
                },
            );
            object_core.owner = to;
        };
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.spec.move (L67-88)
```text
    spec create_object(owner_address: address): ConstructorRef {
        pragma aborts_if_is_partial;

        let unique_address = transaction_context::spec_generate_unique_address();
        aborts_if exists<ObjectCore>(unique_address);

        ensures exists<ObjectCore>(unique_address);
        ensures global<ObjectCore>(unique_address) == ObjectCore {
            guid_creation_num: INIT_GUID_CREATION_NUM + 1,
            owner: owner_address,
            allow_ungated_transfer: true,
            transfer_events: event::EventHandle {
                counter: 0,
                guid: guid::GUID {
                    id: guid::ID {
                        creation_num: INIT_GUID_CREATION_NUM,
                        addr: unique_address,
                    }
                }
            }
        };
        ensures result == ConstructorRef { self: unique_address, can_delete: true };
```

**File:** aptos-move/framework/aptos-framework/tests/simple_dispatchable_token.move (L12-33)
```text
    public fun initialize(account: &signer, constructor_ref: &ConstructorRef) {
        assert!(signer::address_of(account) == @aptos_framework, 1);

        let withdraw = function_info::new_function_info(
            account,
            string::utf8(b"simple_token"),
            string::utf8(b"withdraw"),
        );

        let deposit = function_info::new_function_info(
            account,
            string::utf8(b"simple_token"),
            string::utf8(b"deposit"),
        );

        dispatchable_fungible_asset::register_dispatch_functions(
            constructor_ref,
            option::some(withdraw),
            option::some(deposit),
            option::none()
        );
    }
```
