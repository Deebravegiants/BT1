## Finding

### Title
Unvalidated destination address in `object::transfer`/`transfer_raw`/`transfer_call` allows permanent, non-recoverable loss of object-held assets — ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
Aptos objects (which back fungible-asset stores, NFTs, and other custody-relevant resources) can be transferred to *any* raw `address` via `object::transfer`, `object::transfer_call`, and `object::transfer_raw`. None of these functions validate the destination address. Unlike the module's own `burn()` flow — which intentionally moves ownership to `BURN_ADDRESS` (`0xfff...ff`) while attaching a `TombStone` that allows recovery via `unburn()` — a direct transfer to `@vm_reserved` (`0x0`) or any other address that can never obtain a valid `signer` produces the exact same "assets gone forever" outcome as the Gearbox `to = address(0)` bug, but with **no recovery path at all**.

### Finding Description
`transfer_raw_inner` unconditionally overwrites the object's owner field with the caller-supplied `to` address: [1](#0-0) 

The only validation performed is `verify_ungated_and_descendant(owner_address, object)`, which checks that the *object being moved* is owned by the caller and ungated for transfer — it never inspects or validates the *destination* `to` address: [2](#0-1) 

Compare this to the framework's deliberate, recoverable burn design, where transferring to the reserved `BURN_ADDRESS` is paired with a `TombStone` resource specifically so the original owner can reclaim the object later via `unburn`: [3](#0-2) 

Separately, `account.move` confirms that `@vm_reserved` (address `0x0`) is a permanently unusable address for account/signer purposes — `create_account` and `create_account_if_does_not_exist` explicitly forbid creating an `Account`/signer at `@vm_reserved`: [4](#0-3) 

Because no one can ever produce a `signer` for `@vm_reserved`, once `ObjectCore.owner` is set to that address via `transfer`/`transfer_call`/`transfer_raw`, there is no `owner: &signer` that can ever again call `transfer`, `burn`, or any owner-gated function on that object — including any `FungibleStore`, token, or other resource-bearing object nested under it. This is strictly worse than accidental burn, since burn at least tags a `TombStone` allowing later recovery.

### Impact Explanation
Any object owner — including custody-relevant flows such as fungible-asset `FungibleStore` objects (holding APT/FA balances), primary/secondary token stores, or code objects — can, via a single mistaken parameter to a public entry function (`object::transfer`, `transfer_call`), irreversibly and permanently lock all resources held by that object. This satisfies the custody-impact gate: "Permanent lock or non-recoverable loss of object-held ... value," directly analogous to the Gearbox `to = address(0)` liquidator-loses-all-assets bug, and reachable by any ordinary, unprivileged object owner without any admin/governance assumption.

### Likelihood Explanation
Likelihood is non-trivial: `transfer`, `transfer_call`, and `transfer_raw` are all `public`/`public entry` functions intended for everyday, permissionless use by object owners (wallets, dApps, scripts constructing raw transfer calls). A single fat-fingered address argument, an off-by-one in address construction, or a malformed/zero recipient computed by client-side tooling results in the same class of unrecoverable mistake described in the external report — no malicious actor is required, only unprivileged, ordinary usage error.

### Recommendation
Add an explicit destination-address check in `transfer_raw` (and therefore `transfer`/`transfer_call`) rejecting known-unusable destinations, at minimum `to != @vm_reserved` (and ideally `to != @0x0` generally, mirroring the existing reserved-address checks already used in `account::create_account`). Alternatively/additionally, route "burn-like" destinations through the existing `TombStone`/`unburn` mechanism so any transfer to a non-recoverable address is required to go through `burn()`.

### Proof of Concept
1. Owner `A` creates/holds an `Object<FungibleStore>` (or any object) with `A` as owner.
2. `A` mistakenly (or via a buggy client) calls `object::transfer_call(A, object_addr, @0x0)` (or `object::transfer(A, obj, @0x0)`).
3. `transfer_raw` passes `verify_ungated_and_descendant` (checks only that `A` owns `object_addr` and it's ungated) and calls `transfer_raw_inner(object_addr, @0x0)`, setting `ObjectCore.owner = @0x0`.
4. No `TombStone` is created (unlike `burn()`), and no signer for `@0x0` can ever be produced per `account::create_account`'s reserved-address checks.
5. All resources under `object_addr` (e.g., a `FungibleStore` balance) are now permanently inaccessible — no owner-gated function (`transfer`, `withdraw`, `burn`) can ever be called again on this object.

### Citations

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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L641-676)
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

        // The new owner of the object can always unburn it, but if it's the burn address, we go to the old functionality
        let object_core = borrow_global<ObjectCore>(object_addr);
        if (object_core.owner == signer::address_of(original_owner)) {
            let TombStone { original_owner: _ } = move_from<TombStone>(object_addr);
        } else if (object_core.owner == BURN_ADDRESS) {
            // The old functionality
            let TombStone { original_owner: original_owner_addr } = move_from<TombStone>(object_addr);
            assert!(
                original_owner_addr == signer::address_of(original_owner),
                error::permission_denied(ENOT_OBJECT_OWNER)
            );
            transfer_raw_inner(object_addr, original_owner_addr);
        } else {
            abort error::permission_denied(ENOT_OBJECT_OWNER);
        };
    }
```

**File:** aptos-move/framework/aptos-framework/sources/account/account.move (L275-301)
```text
    public fun create_account_if_does_not_exist(account_address: address) {
        if (!resource_exists_at(account_address)) {
            assert!(
                account_address != @vm_reserved && account_address != @aptos_framework && account_address != @aptos_token,
                error::invalid_argument(ECANNOT_RESERVED_ADDRESS)
            );
            create_account_unchecked(account_address);
        }
    }

    /// Publishes a new `Account` resource under `new_address`. A signer representing `new_address`
    /// is returned. This way, the caller of this function can publish additional resources under
    /// `new_address`.
    public(friend) fun create_account(new_address: address): signer {
        // there cannot be an Account resource under new_addr already.
        assert!(!exists<Account>(new_address), error::already_exists(EACCOUNT_ALREADY_EXISTS));
        // NOTE: @core_resources gets created via a `create_account` call, so we do not include it below.
        assert!(
            new_address != @vm_reserved && new_address != @aptos_framework && new_address != @aptos_token,
            error::invalid_argument(ECANNOT_RESERVED_ADDRESS)
        );
        if (features::is_default_account_resource_enabled()) {
            create_signer(new_address)
        } else {
            create_account_unchecked(new_address)
        }
    }
```
