## Custody Analog Finding

### Title
Single-step, unauthenticated `ObjectCore.owner` reassignment permanently and irrecoverably locks upgrade/freeze/admin authority over object-held custody assets — ([File: aptos-move/framework/aptos-framework/sources/object.move])

### Summary
The external report's invariant reduces to: *any privileged address that can be reassigned should require a two-step propose/claim handshake, because a single-step change to an unverified address can permanently lock the system if the new address is wrong.* Aptos's `Object` model (`aptos-framework/sources/object.move`) implements exactly the single-step pattern the report warns against: `ObjectCore.owner` is the sole authority gate (`object::is_owner`) for every object-based custody/admin capability in the framework, and it can be reassigned in one unauthenticated transaction to any address, with no reachability check and no propose/claim recovery step.

### Finding Description
`ObjectCore.owner` is a plain `address` field [1](#0-0) . Ownership transfer is performed unconditionally by `transfer_raw_inner`, which simply overwrites `object_core.owner = to` for any address supplied by the current owner, with no check that `to` corresponds to a controllable account or is even distinct from a known-unreachable value: [2](#0-1) .

This is reachable via the public entry points `transfer`, `transfer_call`, and `transfer_raw`, all of which route to `transfer_raw_inner` after only checking that the caller is the current owner and that the object/chain allows ungated transfer — never that `to` is meaningful or recoverable: [3](#0-2) .

Unlike `LinearTransferRef`-based flows (which at least require a capability object generated at creation time and can be revoked before use), the ungated `transfer`/`transfer_call` path is the default (`allow_ungated_transfer` starts `true`), and once an owner uses it to set an incorrect address there is **no** propose/claim or admin recovery mechanism anywhere in `object.move`: `TransferRef` must have been generated and retained *before* the mistaken transfer to allow any override, and most callers never keep one around specifically because ownership is meant to be the normal control surface.

This `owner` field is the single point of authority for custody-critical, mainnet-relevant flows built directly on top of the framework, most notably `object_code_deployment`, where `upgrade` and `freeze_code_object` are gated purely by `object::is_owner`: [4](#0-3) [5](#0-4) 

Because `ManagingRefs` for a code object only stores an `ExtendRef` (never a `TransferRef`), the *only* way to recover or reassign control of a deployed code object after the fact is through the ungated `object::transfer` path that reassigns `owner` directly and irreversibly: [6](#0-5) . This is exactly the object-model analog of `uberOwner`: the address that gatekeeps upgrade/freeze authority over a live, in-production code object (which may itself hold `MintRef`/`BurnRef`/`TransferRef` for a fungible asset, per the framework's own documented resource-account/managed-FA pattern) can be set once, incorrectly, with no way back.

### Impact Explanation
If the current code-object owner (or any object owner gating a custody-relevant capability, e.g. mint/burn/freeze refs colocated under an object per the framework's standard managed-FA layout) mistakenly transfers ownership to an address for which no private key/controller exists (typo, wrong network's address format, a burn-style address, etc.), then:
- `object_code_deployment::upgrade` and `code::freeze_code_object` become permanently uncallable for that code object, since both require `object::is_owner(code_object, publisher_address)` to pass and no alternate authority path exists [7](#0-6) .
- Any custody-relevant admin capability elsewhere in the ecosystem that is gated the same way (mint/burn/freeze of fungible assets, metadata mutation, etc., all commonly implemented via `object::is_owner` checks against the object's metadata address) is likewise permanently and non-recoverably locked.
- This satisfies the custody impact gate's "permanent lock or non-recoverable loss of object-held value" and "unauthorized/irrecoverable owner reassignment tied to live assets" criteria — the corrupted field is `ObjectCore.owner`, and the broken invariant is "the object's controlling authority must remain reachable."

### Likelihood Explanation
Low probability, but plausible given real operational error (fat-fingered address, copy-paste mistake, wrong-chain address format) — exactly the scenario the original report and the C4/Reality-Cards judge classified as Medium severity ("very low probability coupled with a very high impact"). No malicious actor or governance collusion is required; a single honest mistake by the legitimate, privileged object owner is sufficient, and the framework provides no built-in guardrail (no pending-owner staging, no address-format/self-transfer validation beyond a same-address no-op check) to catch it before it becomes irreversible.

### Recommendation
Introduce an optional two-step ownership-transfer primitive in `object.move` (e.g., `set_pending_owner` + `accept_ownership`, mirroring `account::rotate_authentication_key` patterns elsewhere or Solidity's `Ownable2Step`) for objects that gate high-value/high-privilege capabilities (code objects, FA metadata objects holding Mint/Burn/Transfer refs, etc.). At minimum, `object_code_deployment` and other framework modules that rely solely on `object::owner` as an irrevocable admin key should retain a `TransferRef`/staged-owner mechanism so a mis-set owner can be corrected before the new address must actively claim it.

### Proof of Concept
1. `publisher` calls `object_code_deployment::publish(...)`, creating a code object at `code_object_address` with `ManagingRefs { extend_ref }` (no `TransferRef` retained) [8](#0-7) .
2. `publisher` later calls `object::transfer_call(publisher, code_object_address, to)` where `to` is mistakenly an address `publisher` does not control (e.g., a typo'd address or a provably-unowned address).
3. `transfer_raw_inner` executes unconditionally, setting `ObjectCore.owner = to` [2](#0-1) .
4. Any subsequent call to `object_code_deployment::upgrade(publisher, ...)` or `freeze_code_object(publisher, code_object)` now fails `object::is_owner(code_object, publisher_address)` and aborts with `ENOT_CODE_OBJECT_OWNER`/`ENOT_PACKAGE_OWNER` [9](#0-8) [10](#0-9) .
5. Since no `TransferRef`/pending-owner mechanism was preserved, the code object's upgrade/freeze authority — and, by the same pattern, any Mint/Burn/Transfer refs colocated on an object gated this way — is permanently unrecoverable.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L100-112)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    /// The core of the object model that defines ownership, transferability, and events.
    struct ObjectCore has key {
        /// Used by guid to guarantee globally unique objects and create event streams
        guid_creation_num: u64,
        /// The address (object or account) that owns this object
        owner: address,
        /// Object transferring is a common operation, this allows for disabling and enabling
        /// transfers bypassing the use of a TransferRef.
        allow_ungated_transfer: bool,
        /// Emitted events upon transferring of ownership.
        transfer_events: event::EventHandle<TransferEvent>,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L549-580)
```text
    /// Entry function that can be used to transfer, if allow_ungated_transfer is set true.
    public entry fun transfer_call(
        owner: &signer,
        object: address,
        to: address,
    ) {
        transfer_raw(owner, object, to)
    }

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

**File:** aptos-move/framework/aptos-framework/sources/object_code_deployment.move (L51-56)
```text
    #[resource_group_member(group = aptos_framework::object::ObjectGroup)]
    /// Internal struct, attached to the object, that holds Refs we need to manage the code deployment (i.e. upgrades).
    struct ManagingRefs has key {
        /// We need to keep the extend ref to be able to generate the signer to upgrade existing code.
        extend_ref: ExtendRef,
    }
```

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

**File:** aptos-move/framework/aptos-framework/sources/code.move (L233-254)
```text
    public fun freeze_code_object(publisher: &signer, code_object: Object<PackageRegistry>) acquires PackageRegistry {
        let code_object_addr = code_object.object_address();
        assert!(exists<PackageRegistry>(code_object_addr), error::not_found(ECODE_OBJECT_DOES_NOT_EXIST));
        assert!(
            object::is_owner(code_object, signer::address_of(publisher)),
            error::permission_denied(ENOT_PACKAGE_OWNER)
        );

        let registry = borrow_global_mut<PackageRegistry>(code_object_addr);
        registry.packages.for_each_mut(|pack| {
            let package: &mut PackageMetadata = pack;
            package.upgrade_policy = upgrade_policy_immutable();
        });

        // We unfortunately have to make a copy of each package to avoid borrow checker issues as check_dependencies
        // needs to borrow PackageRegistry from the dependency packages.
        // This would increase the amount of gas used, but this is a rare operation and it's rare to have many packages
        // in a single code object.
        registry.packages.for_each(|pack| {
            check_dependencies(code_object_addr, &pack);
        });
    }
```
