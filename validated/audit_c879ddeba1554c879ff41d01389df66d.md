No vulnerability found for this question.

**Reasoning:** `register_dispatch_functions` in `dispatchable_fungible_asset.move` is not an entry function and takes no `signer` parameter — its authority gate is entirely different from a signer/owner check. It requires a `&ConstructorRef` [1](#0-0) .

`ConstructorRef` is a Move "hot potato" value: it has no `store`, `copy`, or `drop` ability, so it cannot be serialized via `bcs`, cannot be passed as a transaction/entry-function argument, and cannot be persisted in global storage. It is only produced synchronously by `object::create_object`/`create_named_object`/etc. at the moment of object creation and must be consumed (or dropped by the same transaction context) before the transaction ends [2](#0-1) .

This means:
- There is no code path by which an attacker's "forged dispatch-hook function handle" or any BCS-deserialized input can produce, replay, or forge a `ConstructorRef` for an object that already exists (i.e. for a "victim's" pre-existing metadata object). The metadata object owner never exposes or stores this capability after creation.
- `register_dispatch_functions` can therefore only ever be called by the same transaction/module invocation that is actively constructing the fungible asset's `Metadata` object (typically inside `primary_fungible_store::create_primary_store_enabled_fungible_asset` or similar issuer-controlled initialization code), not by an arbitrary later caller against an "existing metadata object" as posited by the question.
- Consequently, the described attack — "a non-owner signer attempts `register_dispatch_functions` on an existing metadata object" — is not merely blocked by an abort check; it is structurally unreachable, because there's no way for a non-privileged caller (or any caller other than the object's constructor) to even obtain the required `&ConstructorRef` argument for that object. There is no signer/ownership check being bypassed here because the capability gate (`ConstructorRef` possession) inherently cannot cross from constructor to arbitrary future caller.

Because the required precondition (attacker acquiring/forging a `ConstructorRef` for a victim's already-existing metadata object) is impossible under Move's type/ability system, this does not cross a real custody boundary and does not meet the review's decision standard.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L38-57)
```text
    public fun register_dispatch_functions(
        constructor_ref: &ConstructorRef,
        withdraw_function: Option<FunctionInfo>,
        deposit_function: Option<FunctionInfo>,
        derived_balance_function: Option<FunctionInfo>,
    ) {
        fungible_asset::register_dispatch_functions(
            constructor_ref,
            withdraw_function,
            deposit_function,
            derived_balance_function,
        );
        let store_obj = &constructor_ref.generate_signer();
        move_to<TransferRefStore>(
            store_obj,
            TransferRefStore {
                transfer_ref: fungible_asset::generate_transfer_ref(constructor_ref),
            }
        );
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L17-30)
```text
module aptos_framework::object {
    use std::bcs;
    use std::error;
    use std::hash;
    use std::signer;
    use aptos_std::from_bcs;

    use aptos_framework::account;
    use aptos_framework::transaction_context;
    use aptos_framework::create_signer::create_signer;
    use aptos_framework::event;
    use aptos_framework::guid;

    friend aptos_framework::coin;
```
