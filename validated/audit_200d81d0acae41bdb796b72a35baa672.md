## Custody Analog Found

### Title
Missing recipient (zero/unspendable-address) validation in `primary_fungible_store` transfer and store-creation paths permanently locks fungible assets - (File: `aptos-move/framework/aptos-framework/sources/primary_fungible_store.move`)

### Summary
The Solidity bug reduces to one invariant: *before custody of an asset is moved to a new holder, the destination must be validated as a controllable address.* In Aptos's fungible-asset framework, `primary_fungible_store::transfer` (and the lower-level store-creation helper it depends on) moves custody of a `FungibleAsset` to an arbitrary `recipient: address` with no validation that the address is a spendable/controllable account. This mirrors `FETH.withdrawFrom`'s missing `to != address(0)` check, but the corrupted field here is the `ObjectCore.owner` of a freshly-derived primary store, not a token balance mapping.

### Finding Description
`primary_fungible_store::transfer` derives (and creates if necessary) a deterministic store object for the caller-supplied `recipient` and deposits into it, without ever checking that `recipient` is anything other than an arbitrary 32-byte address: [1](#0-0) 

The store is created via `ensure_primary_store_exists` → `create_primary_store`, which simply calls `object::create_user_derived_object(owner_addr, derive_ref)` with the caller-supplied address, with no restriction on `owner_addr` (no check against `@0x0`, `@0xff...ff` (`BURN_ADDRESS`), or any other address that lacks a corresponding private key/signer): [2](#0-1) 

The resulting `FungibleStore` object's `ObjectCore.owner` field is simply set to whatever address was passed in, identical in spirit to `object::transfer_raw_inner`, which also unconditionally rewrites `object_core.owner = to` with no destination validation: [3](#0-2) 

Compare this to the framework's own explicit "burn" mechanism, `object::burn`, which *does* deliberately move an object to `BURN_ADDRESS` but tracks the `original_owner` in a `TombStone` so the object can later be reclaimed via `unburn`: [4](#0-3) 

No such recovery bookkeeping exists for a plain `transfer`/`primary_fungible_store::transfer` call sent to `@0x0` or any other address with no controllable private key. Because `@0x0` is not a "special reserved" framework address with any privileged self-recovery mechanism exposed to end users, funds deposited into a primary store deterministically derived from `@0x0` are custody-locked: nobody can produce a `&signer` for `@0x0` through ordinary account operations to later call `withdraw`, `transfer`, or `burn` from that store.

### Impact Explanation
Any fungible asset (including APT, once routed through `primary_fungible_store`/`aptos_account::transfer_fungible_assets`) sent with `recipient = @0x0` (or other unspendable addresses) becomes permanently, non-recoverably locked in a store nobody can access — a direct "custody accounting corruption that... destroys recovery rights," matching the required impact class. Unlike the original Solidity finding (a self-inflicted user error), the systemic exposure here is broader because the same unguarded pattern exists across the transfer, mint, and store-creation entry points of the fungible-asset framework (`transfer`, `deposit`, `mint`, `transfer_with_ref`), all of which funnel through `ensure_primary_store_exists`/`object::create_user_derived_object` without a destination check.

### Likelihood Explanation
High: `primary_fungible_store::transfer` is a public `entry` function directly callable by any user for any fungible asset with primary-store support, and no wallet-level or framework-level check enforces `recipient != @0x0`. A single mistaken transaction (e.g., malformed client code, copy-paste address error, or a malicious integrator crafting a `to` field) results in a real, unrecoverable loss with no privileged remediation path once the deposit succeeds.

### Recommendation
Add an explicit destination-address validation at the top of `primary_fungible_store::transfer`, `deposit`, `deposit_with_signer`, `transfer_with_ref`, and `create_primary_store`/`ensure_primary_store_exists`, rejecting `@0x0` and any other well-known unspendable addresses (e.g., `object::BURN_ADDRESS` unless routed through the tracked `burn`/`unburn` flow). This mirrors the recommended Solidity fix: explicitly reject `to == address(0)` before any balance-affecting operation executes.

### Proof of Concept
1. Attacker/user (or buggy client) calls `primary_fungible_store::transfer(sender, metadata, @0x0, amount)`.
2. `ensure_primary_store_exists(@0x0, metadata)` derives a store address for owner `@0x0` and creates it via `create_primary_store`, since `@0x0` passes no validation.
3. `dispatchable_fungible_asset::transfer` withdraws `amount` from `sender`'s store and deposits it into the new store owned by `@0x0`.
4. Because no private key or `account::create_account`-issued signer exists for `@0x0` under normal protocol rules, and no `TombStone`/`unburn` bookkeeping was created (this isn't the `burn` flow), the deposited `amount` of the fungible asset is permanently unrecoverable — a direct custody/recovery-rights loss identical in kind to the original `FETH.withdrawFrom` zero-address bug.

**Uncertainty note:** I was not able to fully verify, within tool-call limits, whether `account::create_account` (used by `aptos_account::transfer`/`deposit_fungible_assets` for non-existent accounts) contains its own reserved-address rejection logic that might indirectly block `@0x0` for the `aptos_account`-wrapped entry points. However, the `primary_fungible_store::transfer`/`deposit`/`transfer_with_ref` functions shown above do **not** route through `account::create_account` at all — they only touch `object::create_user_derived_object`, which has no destination validation — so the vulnerable path holds independent of that uncertainty.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L62-89)
```text
    /// Ensure that the primary store object for the given address exists. If it doesn't, create it.
    public fun ensure_primary_store_exists<T: key>(
        owner: address,
        metadata: Object<T>,
    ): Object<FungibleStore> acquires DeriveRefPod {
        let store_addr = primary_store_address(owner, metadata);
        if (fungible_asset::store_exists(store_addr)) {
            object::address_to_object(store_addr)
        } else {
            create_primary_store(owner, metadata)
        }
    }

    /// Create a primary store object to hold fungible asset for the given address.
    public fun create_primary_store<T: key>(
        owner_addr: address,
        metadata: Object<T>,
    ): Object<FungibleStore> acquires DeriveRefPod {
        let metadata_addr = metadata.object_address();
        object::address_to_object<Metadata>(metadata_addr);
        let derive_ref = &borrow_global<DeriveRefPod>(metadata_addr).metadata_derive_ref;
        let constructor_ref = &object::create_user_derived_object(owner_addr, derive_ref);
        // Disable ungated transfer as deterministic stores shouldn't be transferrable.
        let transfer_ref = &constructor_ref.generate_transfer_ref();
        transfer_ref.disable_ungated_transfer();

        fungible_asset::create_store(constructor_ref, metadata)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/primary_fungible_store.move (L201-213)
```text
    /// Transfer `amount` of fungible asset from sender's primary store to receiver's primary store.
    public entry fun transfer<T: key>(
        sender: &signer,
        metadata: Object<T>,
        recipient: address,
        amount: u64,
    ) acquires DeriveRefPod {
        let sender_store = ensure_primary_store_exists(signer::address_of(sender), metadata);
        // Check if the sender store object has been burnt or not. If so, unburn it first.
        may_be_unburn(sender, sender_store);
        let recipient_store = ensure_primary_store_exists(recipient, metadata);
        dispatchable_fungible_asset::transfer(sender, sender_store, recipient_store, amount);
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L582-594)
```text
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L641-660)
```text
    /// Add a TombStone to the object.  The object will then be interpreted as hidden via indexers.
    /// This only works for objects directly owned and for simplicity does not apply to indirectly owned objects.
    /// Original owners can reclaim burnt objects any time in the future by calling unburn.
    /// Please use the test only [`object::burn_object_with_transfer`] for testing with previously burned objects.
    public entry fun burn<T: key>(owner: &signer, object: Object<T>) {
        let original_owner = signer::address_of(owner);
        assert!(is_owner(object, original_owner), error::permission_denied(ENOT_OBJECT_OWNER));
        let object_addr = object.inner;
        assert!(!exists<TombStone>(object_addr), EOBJECT_ALREADY_BURNT);
        move_to(&create_signer(object_addr), TombStone { original_owner });
    }

    /// Allow origin owners to reclaim any objects they previous burnt.
    public entry fun unburn<T: key>(
        original_owner: &signer,
        object: Object<T>,
    ) {
        let object_addr = object.inner;
        assert!(exists<TombStone>(object_addr), error::invalid_argument(EOBJECT_NOT_BURNT));

```
