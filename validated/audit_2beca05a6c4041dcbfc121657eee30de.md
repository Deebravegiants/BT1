### Title
Unsanitized `collection::name` concatenation in `create_token_seed` allows named-object address collisions and permanent token/collection address squatting - (File: `aptos-move/framework/aptos-token-objects/sources/token.move`)

### Summary
`token::create_token_seed` builds the seed used to derive a token's deterministic object address by naively concatenating the `collection` string, a fixed `"::"` separator, and the `name` string, with no length-prefixing of the two dynamic fields: [1](#0-0) 

This is the exact `abi.encodePacked`-with-two-dynamic-types collision pattern described in the source report: because `String` values are attacker-controlled and may themselves contain the `"::"` separator, two different `(collection, name)` pairs can serialize to the identical byte string and therefore the identical derived object address via `object::create_object_address`.

### Finding Description
`create_object_address` hashes `source_addr || seed || 0xFE`; the only entropy differentiating two tokens from the same creator is the `seed` bytes: [2](#0-1) 

`create_token_seed` builds that seed as `collection_bytes || "::" || name_bytes`: [1](#0-0) 

Because `collection` and `name` are arbitrary UTF-8 strings (only length-checked, not content-restricted) and `"::"` is not a reserved/escaped character, the following two distinct logical identities hash to the same byte sequence and thus the same object address:
- `collection = "a"`, `name = "b::c"` → seed bytes `"a" || "::" || "b::c"` = `a::b::c`
- `collection = "a::b"`, `name = "c"` → seed bytes `"a::b" || "::" || "c"` = `a::b::c`

`create_named_token` and `create_named_token_as_collection_owner` feed this colliding seed straight into `object::create_named_object`: [3](#0-2) 

`create_named_object` derives the address from the seed and calls `create_object_internal`, which asserts the address does not already hold an `ObjectCore`: [4](#0-3) [5](#0-4) 

Named objects are explicitly documented as **non-deletable**: [6](#0-5) 

**Broken invariant:** the protocol assumes `(creator, collection, name)` uniquely and collision-freely maps to one object address, and that whoever legitimately owns that `(collection, name)` combination can always mint the corresponding named token object. The unprefixed packed concatenation breaks that uniqueness guarantee.

**Attack path:** an attacker who knows (or predicts) a victim's intended `(collection, name)` pair for a future token mint (e.g., a well-known upcoming collection/token launch, or a name/collection pair advertised off-chain) computes the colliding pair (e.g., inserting the `"::"` separator earlier) and calls `create_named_token` first from their own creator account address that equals the victim's (this requires the same `source` address; note `create_token_address(creator, collection, name)` is keyed by `creator` too, so the collision must be exploited by the same creator account, or by any code path that derives the object address from creator-supplied `collection`/`name` without further creator-address separation, such as `create_named_token_as_collection_owner`, which lets *any* signer create the token as long as they pass the `Object<Collection>`. In `create_named_token_as_collection_owner`, the *creator signer* need not be the collection owner's original account for the seed derivation; the seed only depends on `collection::name(collection)` and the attacker-chosen `name`. Combined with `object::create_named_object(creator, seed)`, which derives the address from `signer::address_of(creator)`, the effective “creator address” in the address derivation is still the caller of the entry function — so the practical collision-exploiting attacker must be the account that will also legitimately create the victim token later (i.e., front-running its own account with a syntactically different name) or a delegated auto-minting flow using the same creator account across untrusted names/collections. This narrows exploitation to scenarios where an untrusted party can pick and submit `collection_name`/`name` strings on behalf of a creator account (e.g., marketplaces, dynamic minting contracts) before the intended pair is minted).

Once the colliding address is claimed, the legitimate `(collection, name)` mint permanently aborts with `EOBJECT_EXISTS`, and — because named objects cannot be deleted — the intended token identity is **permanently and non-recoverably** unattainable at its expected deterministic address.

### Impact Explanation
This breaks a custody-relevant invariant: the deterministic, collision-free addressing of token objects that off-chain indexers, marketplaces, and other contracts rely on to locate/verify token identity and ownership. A successful collision permanently denies the rightful creator/owner the ability to mint their intended token at its documented deterministic address (non-recoverable loss of the expected named-object slot, per the "Permanent lock or non-recoverable loss of object-held ... value" custody pivot), and can be leveraged to plant an attacker-controlled object masquerading at an address any integrator expects to correspond to a specific `(collection, name)` pair, misdirecting supply/ownership lookups.

### Likelihood Explanation
Exploitation requires the attacker to control or front-run the `collection`/`name` strings passed into `create_named_token`/`create_named_token_as_collection_owner` for a specific creator account before the legitimate mint transaction lands — realistic in marketplace/auto-minting flows where third parties supply names, or in any front-running scenario on a public mempool. It does not require any privileged role; only string crafting and normal transaction submission are needed, but it is scoped to callers who share (or can pre-empt) the intended creator address, which somewhat limits the pool of realistic attackers.

### Recommendation
Replace the ad hoc `collection || "::" || name` packed concatenation in `create_token_seed`/`create_token_name_with_seed` with a length-prefixed/BCS-encoded (`bcs::to_bytes`) construction of a struct containing `collection` and `name` (or hash each field separately, e.g. `sha3_256(collection) || sha3_256(name)`), matching the pattern used safely elsewhere (e.g., `create_object_address` and `create_resource_address`, which only ever combine one dynamic field with fixed-length data). Ensure no two distinct `(collection, name)` pairs can ever serialize identically before hashing.

### Proof of Concept
```
// Same creator account `alice`.
// Legitimate intended pair:
collection_name = "a"
token_name       = "b::c"
seed = create_token_seed(&"a".into(), &"b::c".into());
// seed bytes = b"a" ++ b"::" ++ b"b::c" = b"a::b::c"

// Attacker-crafted colliding pair (submitted first, e.g. via front-running
// or a permissive minting proxy that lets third parties choose collection/name):
collection_name' = "a::b"
token_name'       = "c"
seed' = create_token_seed(&"a::b".into(), &"c".into());
// seed' bytes = b"a::b" ++ b"::" ++ b"c" = b"a::b::c"

assert!(seed == seed');
// object::create_object_address(&alice, seed) == object::create_object_address(&alice, seed')
// Whichever create_named_token call executes second aborts with EOBJECT_EXISTS,
// and because named objects are non-deletable, the losing (collection, name)
// pair can never be minted at its documented deterministic address again.
``` [1](#0-0) [2](#0-1) [5](#0-4)

### Citations

**File:** aptos-move/framework/aptos-token-objects/sources/token.move (L450-472)
```text
    public fun create_named_token(
        creator: &signer,
        collection_name: String,
        description: String,
        name: String,
        royalty: Option<Royalty>,
        uri: String,
    ): ConstructorRef {
        let seed = create_token_seed(&collection_name, &name);

        let constructor_ref = object::create_named_object(creator, seed);
        create_common(
            creator,
            &constructor_ref,
            collection_name,
            description,
            name,
            option::none(),
            royalty,
            uri
        );
        constructor_ref
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

**File:** aptos-move/framework/aptos-framework/sources/object.move (L218-224)
```text
    /// Derives an object address from source material: sha3_256([creator address | seed | 0xFE]).
    public fun create_object_address(source: &address, seed: vector<u8>): address {
        let bytes = bcs::to_bytes(source);
        bytes.append(seed);
        bytes.push_back(OBJECT_FROM_SEED_ADDRESS_SCHEME);
        from_bcs::to_address(hash::sha3_256(bytes))
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L255-256)
```text
    /// Create a new named object and return the ConstructorRef. Named objects can be queried globally
    /// by knowing the user generated seed used to create them. Named objects cannot be deleted.
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L260-264)
```text
    public fun create_named_object(creator: &signer, seed: vector<u8>): ConstructorRef {
        let creator_address = signer::address_of(creator);
        let obj_addr = create_object_address(&creator_address, seed);
        create_object_internal(creator_address, obj_addr, false)
    }
```

**File:** aptos-move/framework/aptos-framework/sources/object.move (L329-334)
```text
    fun create_object_internal(
        creator_address: address,
        object: address,
        can_delete: bool,
    ): ConstructorRef {
        assert!(!exists<ObjectCore>(object), error::already_exists(EOBJECT_EXISTS));
```
