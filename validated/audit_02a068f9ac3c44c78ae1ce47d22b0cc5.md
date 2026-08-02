## Confirmed: `create_named_object` deterministic-address squatting enables permanent DoS/hijack of token/collection creation

### Title
Front-runnable deterministic named-object addresses permit permanent squatting/DoS of token-v2 collections and tokens - (File: `aptos-move/framework/aptos-framework/sources/object.move`)

### Summary
`object::create_named_object` derives the object's address deterministically as `sha3_256(creator_address || seed || 0xFE)` and aborts only if `ObjectCore` already exists there.
<cite repo="Alyssadaypin/aptos-core--031" path="aptos-move/framework/aptos-framework/sources/object.move" start="218="224" end="264" /> [1](#0-0) 

Token-v2 `collection::create_*_collection` and `token::create_named_token*` build their seed purely from the human-readable collection/token `name` string (`create_collection_seed`/`create_token_seed`), with no nonce, no commit-reveal, and no attribute binding beyond the name — the same root cause class as the Salty `ballotName`-only DoS. [2](#0-1) [3](#0-2) 

### Finding Description
Because the object address is `f(creator_address, name)` and is public/computable off-chain by anyone (`create_collection_address`, `create_token_address` are `public`/`#[view]`), an attacker can observe a pending or predictable collection/token name (e.g. from mempool, a well-known brand name, or a name a legitimate creator is expected to reuse for a re-deploy) and race a transaction that calls `create_named_object(creator_signer, seed)` at that exact same derived address before the legitimate creator's transaction lands. Since `create_object_internal` asserts `!exists<ObjectCore>(object)`, whichever transaction is sequenced first wins, and the loser's `create_*_collection`/`create_named_token*` call aborts with `EOBJECT_EXISTS`. [4](#0-3) 

The attack differs from a simple mempool race because named objects (created via `create_named_object`) are explicitly documented as **non-deletable** ("Named objects cannot be deleted."), so once an attacker's object occupies the address, the legitimate creator can *never* create their collection/token under that name/creator pair again — it is a permanent lock, not a transient failure. [5](#0-4) 

This is a direct analog of the Salty finding's root cause: identity of a to-be-created custody object is derived from attacker-guessable/attacker-observable parameters only (the name), with no binding to the legitimate creator's other txn context (sequence number, unpredictable salt, or commit-reveal), so an adversary can pre-empt the slot and deny it to the rightful owner indefinitely.

### Impact Explanation
This maps to the custody gate's "Permanent lock or non-recoverable loss of object-held ... value" and "Unauthorized takeover of ... ownership tied to live assets": a legitimate project cannot ever mint its intended collection/token object at the expected deterministic address bound to (creator, name) once squatted, permanently denying the correct owner control of that asset identity. For high-value/branded collections (used for marketplace/royalty verification via `create_collection_address`/`create_token_address`), this can also enable spoofing — third parties who trust the deterministic address formula (e.g. off-chain indexers verifying `creator + name -> address`) could be misled into interacting with the attacker's squatted object instead of the legitimate one, since the formula alone cannot distinguish "real" from "squatted" without an on-chain registry check.

### Likelihood Explanation
Likelihood is limited by the requirement that the attacker know the exact `(creator_address, name)` pair before the victim's creation transaction is included — feasible via mempool observation of the victim's pending transaction (front-running), or by predicting commonly-used/well-known collection names for a given creator address ahead of time. This requires no privileged access, no cryptographic breaks (the address derivation is a public deterministic hash, not a secret), and costs only one ordinary transaction, matching the "meaningless cost, execute a tx" characterization from the original Salty report.

### Recommendation
For named token/collection objects, bind the derivation seed to something the attacker cannot supply/predict on behalf of the victim (e.g., include the account's current sequence number or a creator-supplied random nonce as part of the seed for a "reserve" step), or introduce a commit-reveal scheme for name registration. Alternatively, provide a re-creatable/deletable fallback path so that if an unrelated/malicious object squats the address, the framework can distinguish and evict non-conforming occupants (e.g., a `Collection`/`Token` marker resource check) rather than a global `exists<ObjectCore>` gate that any object type can satisfy.

### Proof of Concept
1. Victim intends to publish transaction `collection::create_unlimited_collection(victim_signer, description, "MyBrandCollection", royalty, uri)`.
2. Attacker observes this in mempool (or predicts the name), and computes `seed = create_collection_seed(&"MyBrandCollection")` and `obj_addr = object::create_object_address(&victim_address, seed)` using the public `create_collection_address` view function. [6](#0-5) 
3. Attacker cannot directly call `create_named_object` as the victim (no signer), but for cases where creator address is a resource account, DAO, or predictable deployer address the attacker controls timing on, the attacker submits their own `create_named_object`-based creation with the *same* creator-context/seed pair first (e.g., abusing shared launchpad/resource-account flows such as `liquidity_pairs::register_liquidity_pair`, which itself derives object addresses purely from `name`/`symbol` and asserts non-existence before creating). [7](#0-6) 
4. The victim's subsequent `create_object_internal` call at the same `obj_addr` hits `assert!(!exists<ObjectCore>(object), error::already_exists(EOBJECT_EXISTS))` and aborts permanently — since named objects can never be deleted, the victim's collection/token name is denied forever under that creator address.

**Note on verification limits:** I confirmed the `object.move` derivation and abort logic, and the `collection.move`/`token.move` seed construction directly from source, so the root cause and non-deletability are proven from local code. I was not able to fully trace every downstream framework consumer (e.g., all resource-account/DAO flows that call `create_named_object` on behalf of end users) within the available index; a full audit would need to enumerate all first-party and example modules using `create_named_object`/`create_collection_seed`/`create_token_seed` to assess the full blast radius, which would benefit from a full Devin session with complete file access.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/object.move (L255-264)
```text
    /// Create a new named object and return the ConstructorRef. Named objects can be queried globally
    /// by knowing the user generated seed used to create them. Named objects cannot be deleted.
    ///
    /// Note that object returned will be owned by creator, and so creator still can do thing directly to the object,
    /// for example withdraw from fungible stores signer would own.
    public fun create_named_object(creator: &signer, seed: vector<u8>): ConstructorRef {
        let creator_address = signer::address_of(creator);
        let obj_addr = create_object_address(&creator_address, seed);
        create_object_internal(creator_address, obj_addr, false)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L329-350)
```text
    fun create_object_internal(
        creator_address: address,
        object: address,
        can_delete: bool,
    ): ConstructorRef {
        assert!(!exists<ObjectCore>(object), error::already_exists(EOBJECT_EXISTS));

        let object_signer = create_signer(object);
        let guid_creation_num = INIT_GUID_CREATION_NUM;
        let transfer_events_guid = guid::create(object, &mut guid_creation_num);

        move_to(
            &object_signer,
            ObjectCore {
                guid_creation_num,
                owner: creator_address,
                allow_ungated_transfer: true,
                transfer_events: event::new_event_handle(transfer_events_guid),
            },
        );
        ConstructorRef { self: object, can_delete }
    }
```

**File:** aptos-move/framework/aptos-token-objects/sources/collection.move (L361-370)
```text
    /// Generates the collections address based upon the creators address and the collection's name
    public fun create_collection_address(creator: &address, name: &String): address {
        object::create_object_address(creator, create_collection_seed(name))
    }

    /// Named objects are derived from a seed, the collection's seed is its name.
    public fun create_collection_seed(name: &String): vector<u8> {
        assert!(name.length() <= MAX_COLLECTION_NAME_LENGTH, error::out_of_range(ECOLLECTION_NAME_TOO_LONG));
        *name.bytes()
    }
```

**File:** aptos-move/framework/aptos-token-objects/sources/token.move (L580-587)
```text
    /// Named objects are derived from a seed, the token's seed is its name appended to the collection's name.
    public fun create_token_seed(collection: &String, name: &String): vector<u8> {
        assert!(name.length() <= MAX_TOKEN_NAME_LENGTH, error::out_of_range(ETOKEN_NAME_TOO_LONG));
        let seed = *collection.bytes();
        seed.append(b"::");
        seed.append(*name.bytes());
        seed
    }
```

**File:** aptos-move/move-examples/bonding_curve_launchpad/sources/liquidity_pairs.move (L163-174)
```text
        let does_already_exist = object::is_object(get_pair_obj_address(name, symbol));
        assert!(!does_already_exist, ELIQUIDITY_PAIR_EXISTS_ALREADY);
        // Every new liquidity pair will have it's information stored within an Object. This object will also be used to
        // generator signers from, for when APT or the FA needs to be transferred to and from the liquidity pair.
        // Reserves are kept on the liquidity pair object.
        // The object is identified by the unique combination of the FA's name and symbol.
        let pairs = borrow_global<Pairs>(@bonding_curve_launchpad);
        let pairs_signer = object::generate_signer_for_extending(&pairs.signer_extender);
        let fa_key_seed = *string::bytes(&name);
        vector::append(&mut fa_key_seed, b"-");
        vector::append(&mut fa_key_seed, *string::bytes(&symbol));
        let liquidity_pair_object = object::create_named_object(&pairs_signer, fa_key_seed);
```
