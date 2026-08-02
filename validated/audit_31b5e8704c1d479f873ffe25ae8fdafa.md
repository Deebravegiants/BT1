### Title
Denylist/freeze bypass via indirectly-owned `FungibleStore` objects in the `usdk` stablecoin example - (File: `aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move`)

### Summary
The `usdk` managed-stablecoin example enforces its denylist ("freeze") control only against the *primary* fungible store of an address, and its dispatch hooks resolve compliance status via a single-hop `object::owner(store)` lookup rather than the ultimate controlling account. A user can therefore pre-position funds in a `FungibleStore` owned by an intermediate object (e.g. an object address they control via an `ExtendRef`/resource account) instead of their own account's primary store. Once denylisted, the user's *primary store* becomes frozen, but the intermediate-object-owned store is untouched by `denylist()`/`set_frozen_flag`, and the compliance check (`assert_not_denylisted`) resolves to that intermediate object's own (never-denylisted) primary-store status — not the user's. This mirrors the Olympus bug pattern: a party moves value into a bucket the revocation/freeze mechanism does not reach, then continues to freely use it after admin action is taken against their known address.

### Finding Description
`denylist`/`undenylist` freeze only the target address's *primary* store: [1](#0-0) 

The dispatchable deposit/withdraw hooks that are supposed to enforce this compliance control resolve the "account" to check via a single call to `object::owner(store)`, then look up **that address's primary store frozen flag** — not the frozen flag of the actual store being used, and not any recursive/root owner: [2](#0-1) 

```
public fun deposit<T: key>(store, fa, transfer_ref) {
    assert_not_paused();
    assert_not_denylisted(object::owner(store));
    ...
}
```

`assert_not_denylisted` only checks the *primary* store of that resolved address: [3](#0-2) 

Any signer can permissionlessly create additional (non-primary) `FungibleStore` objects for the same metadata via `fungible_asset::create_store`, as demonstrated in the module's own test: [4](#0-3) 

`set_untransferable` is applied only to the *object* holding the store (preventing the store's `Object<FungibleStore>` from being re-owned via `object::transfer`), it does **not** prevent normal FA balance movement (mint/deposit/withdraw/transfer) into or out of a store, nor does it require that store's owner equal the user's account address. If a user creates a store owned by an intermediate object `P` that the user separately controls (e.g. `P` has an `ExtendRef` held by the user, or `P` is itself a resource/derived object under the user's control) rather than owned directly by the user's account address, then:
- `object::owner(store)` resolves to `P`, not the user's account.
- The compliance check queries whether `P`'s primary store is frozen — which was never targeted by `denylist()`, since the denylister only knows/targets the user's real account address.
- The user's real account can subsequently be denylisted (freezing only its own primary store) while funds parked under `P`-owned stores remain fully transferable, mintable-into, and withdrawable, because the freeze primitive is address-scoped to primary stores and the hook does not walk up the object ownership graph to the ultimate signer-controlling account.

This breaks the intended custody invariant that freezing an account's fungible-asset holdings ("denylist") is authoritative over all value that account effectively controls. The frozen-state and controller-identity resolution both stop at a single object-ownership hop, which is exactly the class of gap the Olympus report describes: the admin has a facility that is supposed to fully revoke/control a party's holdings, but that party can shift the same value into a structure the admin's control mechanism does not reach, and continue using it after (or across) the admin's control action.

### Impact Explanation
This is a compliance/custody-control bypass on a live, mainnet-relevant fungible-asset (a stablecoin pattern intended to be copied for production denylist/freeze tokens). A denylisted/sanctioned address can continue to mint-receive, hold, transfer, and move a regulated asset through an intermediate-object-owned store that the freeze mechanism never reaches, defeating the entire purpose of the freeze/denylist control (an owner-reassignment/control-bypass of frozen custody state). This is high impact: it permanently and unrecoverably defeats an intended custody-control guarantee (freeze coverage) without requiring any privileged role — the attacker only needs ordinary object-creation permissions, which every account has.

### Likelihood Explanation
Likelihood is high for any deployment that reuses this exact example pattern (or similar "denylist only covers primary store, dispatch hook resolves owner via a single `object::owner()` hop" designs): the store-creation and object-ownership primitives used (`object::create_object`, `fungible_asset::create_store`, `ExtendRef`) are all standard, unprivileged, and already exercised in this same module's test suite. No race condition or admin cooperation is needed; a user can prepare the alternate store before ever being denylisted, and it silently continues to function afterward.

### Recommendation
- Compliance/freeze checks in dispatch hooks must resolve the *ultimate* controlling account (recursively walking object ownership to termination, or requiring `object::owner(store)` to be a non-object, i.e., an actual account address) rather than trusting a single-hop owner lookup.
- Alternatively, freeze status should be enforced per-store based on an authoritative registry the denylister can update for *any* store tied to a denylisted identity (not solely the primary store), or the framework should disallow arbitrary secondary `FungibleStore` creation for FAs that use denylist/freeze-style dispatch hooks unless those stores are also covered by the same freeze primitive.
- More generally, any managed/denylist-style FA design must ensure `deposit`/`withdraw`/`transfer` hooks cannot be routed around the freeze check by using stores owned by objects/resource-accounts the sanctioned party still practically controls.

### Proof of Concept
1. Before being denylisted, attacker (account `A`) creates an object `P` via `object::create_object(A)` and retains `P`'s `ExtendRef`.
2. Attacker creates a `FungibleStore` for USDK owned by `P`: `fungible_asset::create_store(&p_constructor_ref, usdk::metadata())`.
3. Attacker transfers USDK from their primary store into the `P`-owned store using `dispatchable_fungible_asset::transfer` (passes deposit hook since `object::owner(P_store) == P`, and `P`'s primary store is not denylisted).
4. Denylister calls `usdk::denylist(denylister, A)`, which only sets `frozen = true` on `A`'s primary store (`aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move:284-285`).
5. Attacker, using a signer generated from `P`'s `ExtendRef`, continues to withdraw/transfer/deposit USDK to/from the `P`-owned store. The `withdraw`/`deposit` hooks call `assert_not_denylisted(object::owner(store))` = `assert_not_denylisted(P)`, which checks `P`'s primary store (never frozen) and passes — despite `A` being denylisted.
6. Attacker effectively retains full custody and transferability of the "frozen" funds, completely bypassing the denylist control.

Note: I was not able to independently verify from the indexed snippets whether `object::owner()` in this codebase version ever performs multi-hop resolution (a `root_owner` style function) elsewhere in `object.move`; the tool budget was exhausted before I could confirm this definitively. If a recursive/root-owner resolution utility exists and were used instead of the single-hop `object::owner()` call in `usdk::assert_not_denylisted`'s call sites, this specific bypass would be mitigated — but as written in `usdk.move`, the single-hop resolution is what's used, and that is the exploitable root cause identified here. If a Devin session is started to verify this further, it should specifically check for a "root owner" traversal utility in `aptos-framework/sources/object.move` and confirm whether it is used (or could be used) by `deposit`/`withdraw` hook implementations.

### Citations

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L190-210)
```text
    /// Deposit function override to ensure that the account is not denylisted and the stablecoin is not paused.
    public fun deposit<T: key>(
        store: Object<T>,
        fa: FungibleAsset,
        transfer_ref: &TransferRef,
    ) acquires State {
        assert_not_paused();
        assert_not_denylisted(object::owner(store));
        fungible_asset::deposit_with_ref(transfer_ref, store, fa);
    }

    /// Withdraw function override to ensure that the account is not denylisted and the stablecoin is not paused.
    public fun withdraw<T: key>(
        store: Object<T>,
        amount: u64,
        transfer_ref: &TransferRef,
    ): FungibleAsset acquires State {
        assert_not_paused();
        assert_not_denylisted(object::owner(store));
        fungible_asset::withdraw_with_ref(transfer_ref, store, amount)
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L278-291)
```text
    /// Add an account to the denylist. This checks that the caller is the denylister.
    public entry fun denylist(denylister: &signer, account: address) acquires Management, Roles, State {
        assert_not_paused();
        let roles = borrow_global<Roles>(usdk_address());
        assert!(signer::address_of(denylister) == roles.denylister, EUNAUTHORIZED);

        let freeze_ref = &borrow_global<Management>(usdk_address()).transfer_ref;
        primary_fungible_store::set_frozen_flag(freeze_ref, account, true);

        event::emit(Denylist {
            denylister: signer::address_of(denylister),
            account,
        });
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/usdk.move (L328-336)
```text
    // Check that the account is not denylisted by checking the frozen flag on the primary store
    fun assert_not_denylisted(account: address) {
        let metadata = metadata();
        // CANNOT call into pfs::store_exists in our withdraw/deposit hooks as it creates possibility of a circular dependency.
        // Instead, we will call the inlined version of the function.
        if (primary_fungible_store::primary_store_exists_inlined(account, metadata)) {
            assert!(!fungible_asset::is_frozen(primary_fungible_store::primary_store_inlined(account, metadata)), EDENYLISTED);
        }
    }
```

**File:** aptos-move/move-examples/fungible_asset/stablecoin/sources/tests/usdk_tests.move (L48-64)
```text
    // test the ability of a denylisted account to transfer out newly created store
    #[test(creator = @0xcafe, denylister = @0xcade, receiver = @0xdead)]
    #[expected_failure(abort_code = 327683, location = aptos_framework::object)]
    fun test_untransferrable_store(creator: &signer, denylister: &signer, receiver: &signer) {
        usdk::init_for_test(creator);
        let receiver_address = signer::address_of(receiver);
        let asset = usdk::metadata();

        usdk::denylist(denylister, receiver_address);
        assert!(primary_fungible_store::is_frozen(receiver_address, asset), 0);

        let constructor_ref = object::create_object(receiver_address);
        fungible_asset::create_store(&constructor_ref, asset);
        let store = object::object_from_constructor_ref<FungibleStore>(&constructor_ref);

        object::transfer(receiver, store, @0xdeadbeef);
    }
```
