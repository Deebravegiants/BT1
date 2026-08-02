No vulnerability found for this question.

**Reasoning:**

The premise conflates object-code-deployment addresses with the fixed framework address `aptos_token = 0x3`. This distinction breaks every step of the proposed attack chain:

1. **Object code deployment never produces the address `0x3`.** `object_code_deployment::publish` derives the new module's address deterministically from the *publisher's account address* and *sequence number* via `object::create_named_object` and `object_seed`, and this happens entirely under the publisher's own address space — it never targets or collides with a pre-existing, unrelated address like `0x3`. [1](#0-0) [2](#0-1) 

2. **`aptos_token` (and `token_event_store`) is not an object-deployed package at all.** It is a standard named-address framework module compiled with `aptos_token = "0x3"` in its `Move.toml`, i.e. a reserved framework address set at genesis, not an object address that any user's `code::publish_package_txn` / `object_code_deployment::publish` invocation could ever land on. [3](#0-2) [4](#0-3) 

3. **Republishing at address `0x3` itself requires a signer for `0x3`.** `code::publish_package` / `publish_package_txn` simply take whatever `&signer` is passed and operate on `signer::address_of(owner)` — there is no bypass that lets a signer at some other (attacker-controlled or object) address write into another address's `PackageRegistry`. [5](#0-4) [6](#0-5) 
An unprivileged attacker has no way to obtain a signer for the `0x3` account, since that address is a framework-reserved account whose upgrade/authorization is governed by Aptos governance, not by an object-ownership transfer.

4. **`friend` visibility is fixed in the compiled module and only changes if the module at that exact address is republished.** `friend aptos_token::token;` in `token_event_store.move` is compiled into the bytecode deployed at `0x3`, and since (2)+(3) show no unprivileged path exists to republish code at `0x3`, this declaration cannot be altered or "gained" by an attacker's object. [7](#0-6) 

5. Additionally, `object_code_deployment::upgrade` / `freeze_code_object` correctly gate on `object::is_owner(code_object, publisher_address)`, so even within the object-code-deployment subsystem, ownership transfer of a *different* code object could not let an attacker author code that runs under the `0x3` friend list. [8](#0-7) 

Since there is no unprivileged path that lets an attacker's code become part of the `0x3::token` module or acquire the `friend` grant, `emit_token_royalty_mutate_event` / `emit_default_property_mutate_event` remain uncallable by attacker code. Furthermore, even if this were somehow possible, the stated impact ("corrupted mapping in the event stream") is explicitly excluded under the Decision Standard as an event-level mismatch with no custody-boundary crossing (no change to who owns/mints/burns/freezes/upgrades any asset). Both the technical premise and the impact fail the review gate.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object_code_deployment.move (L80-96)
```text
    public entry fun publish(
        publisher: &signer,
        metadata_serialized: vector<u8>,
        code: vector<vector<u8>>,
    ) {
        let publisher_address = signer::address_of(publisher);
        let object_seed = object_seed(publisher_address);
        let constructor_ref = &object::create_named_object(publisher, object_seed);
        let code_signer = &constructor_ref.generate_signer();
        code::publish_package_txn(code_signer, metadata_serialized, code);

        event::emit(Publish { object_address: signer::address_of(code_signer), });

        move_to(code_signer, ManagingRefs {
            extend_ref: constructor_ref.generate_extend_ref(),
        });
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object_code_deployment.move (L98-104)
```text
    inline fun object_seed(publisher: address): vector<u8> {
        let sequence_number = account::get_sequence_number(publisher) + 1;
        let seeds = vector[];
        seeds.append(bcs::to_bytes(&OBJECT_CODE_DEPLOYMENT_DOMAIN_SEPARATOR));
        seeds.append(bcs::to_bytes(&sequence_number));
        seeds
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object_code_deployment.move (L113-133)
```text
    public entry fun upgrade(
        publisher: &signer,
        metadata_serialized: vector<u8>,
        code: vector<vector<u8>>,
        code_object: Object<PackageRegistry>,
    ) {
        let publisher_address = signer::address_of(publisher);
        assert!(
            object::is_owner(code_object, publisher_address),
            error::permission_denied(ENOT_CODE_OBJECT_OWNER),
        );

        let code_object_address = code_object.object_address();
        assert!(exists<ManagingRefs>(code_object_address), error::not_found(ECODE_OBJECT_DOES_NOT_EXIST));

        let extend_ref = &borrow_global<ManagingRefs>(code_object_address).extend_ref;
        let code_signer = &extend_ref.generate_signer_for_extending();
        code::publish_package_txn(code_signer, metadata_serialized, code);

        event::emit(Upgrade { object_address: signer::address_of(code_signer), });
    }
```

**File:** aptos-move/framework/aptos-token/Move.toml (L1-12)
```text
[package]
name = "AptosToken"
version = "1.0.0"

[addresses]
std = "0x1"
aptos_framework = "0x1"
aptos_token = "0x3"

[dependencies]
MoveStdlib = { local = "../move-stdlib" }
AptosFramework = { local = "../aptos-framework"}
```

**File:** aptos-move/framework/aptos-token/sources/token_event_store.move (L1-11)
```text
/// This module provides utils to add and emit new token events that are not in token.move
module aptos_token::token_event_store {
    use std::string::String;
    use std::signer;
    use aptos_framework::event::{Self, EventHandle};
    use aptos_framework::account;
    use std::option::Option;
    use aptos_std::any::Any;
    use aptos_token::property_map::PropertyValue;

    friend aptos_token::token;
```

**File:** aptos-move/framework/aptos-framework/sources/code.move (L157-169)
```text
    /// Publishes a package at the given signer's address. The caller must provide package metadata describing the
    /// package.
    public fun publish_package(owner: &signer, pack: PackageMetadata, code: vector<vector<u8>>) acquires PackageRegistry {
        // Disallow incompatible upgrade mode. Governance can decide later if this should be reconsidered.
        assert!(
            pack.upgrade_policy.policy > upgrade_policy_arbitrary().policy,
            error::invalid_argument(EINCOMPATIBLE_POLICY_DISABLED),
        );

        let addr = signer::address_of(owner);
        if (!exists<PackageRegistry>(addr)) {
            move_to(owner, PackageRegistry { packages: vector::empty() })
        };
```

**File:** aptos-move/framework/aptos-framework/sources/code.move (L256-261)
```text
    /// Same as `publish_package` but as an entry function which can be called as a transaction. Because
    /// of current restrictions for txn parameters, the metadata needs to be passed in serialized form.
    public entry fun publish_package_txn(owner: &signer, metadata_serialized: vector<u8>, code: vector<vector<u8>>)
    acquires PackageRegistry {
        publish_package(owner, util::from_bytes<PackageMetadata>(metadata_serialized), code)
    }
```
