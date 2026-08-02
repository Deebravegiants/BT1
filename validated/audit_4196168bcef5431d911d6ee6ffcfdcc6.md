No vulnerability found for this question.

**Why this doesn't qualify:**

The V1 `UriMutation` event can only be emitted through `token_event_store::emit_token_uri_mutate_event`, which is a `friend fun` called exclusively from `token.move::mutate_tokendata_uri`, which itself requires a `creator: &signer` argument, checks `assert_tokendata_exists(creator, token_data_id)`, and requires `token_data.mutability_config.uri` to be set for that specific token data. [1](#0-0) [2](#0-1)  An attacker without the creator signer cannot invoke this path at all — Move events are emitted as part of validated transaction execution, not arbitrary user-supplied data, so there is no way to "forge" the event without actually holding the required signer capability, which the review's decision standard excludes ("Reject anything that needs pre-existing permissions").

Separately, even granting the premise, the V1/V2 `UriMutation`/`Mutation` events only carry descriptive strings (creator, collection, token name, old/new uri) and are purely observational — they do not touch `object::ObjectCore` ownership, `MutatorRef`/`ExtendRef`/`TransferRef` capabilities, or any resource controlling the actual token object's custody. [3](#0-2)  The indexer's V1↔V2 translation logic (`event_v2_translator.rs`) resolves event sequence numbers/keys strictly from the emitting account's own on-chain resource (e.g., `TokenEventStoreV1` under the `creator` address in the event), not by fuzzy string matching against unrelated token objects, so there's no cross-token conflation mechanism in the core translator itself. [4](#0-3)  Any downstream indexer/API that chose to key metadata resolution by "collection/token name string" rather than by object address or account+creation-number would be an indexer-side data-modeling issue, not a core custody vulnerability, and falls under the explicitly excluded category of "event-only mismatches."

Since no unprivileged path bypasses signer/mutability checks to emit the event, and no actual owner, `MutatorRef`, royalty payee resource, or object ownership state is altered, this does not cross a custody boundary per the review's decision standard.

### Citations

**File:** aptos-move/framework/aptos-token/sources/token.move (L800-813)
```text
    public fun mutate_tokendata_uri(
        creator: &signer,
        token_data_id: TokenDataId,
        uri: String
    ) acquires Collections {
        assert!(uri.length() <= MAX_URI_LENGTH, error::invalid_argument(EURI_TOO_LONG));
        assert_tokendata_exists(creator, token_data_id);

        let all_token_data = &mut Collections[token_data_id.creator].token_data;
        let token_data = all_token_data.borrow_mut(token_data_id);
        assert!(token_data.mutability_config.uri, error::permission_denied(EFIELD_NOT_MUTABLE));
        token_event_store::emit_token_uri_mutate_event(creator, token_data_id.collection, token_data_id.name, token_data.uri ,uri);
        token_data.uri = uri;
    }
```

**File:** aptos-move/framework/aptos-token/sources/token_event_store.move (L273-286)
```text
    /// Emit URI mutation event
    friend fun emit_token_uri_mutate_event(
        creator: &signer,
        collection: String,
        token: String,
        old_uri: String,
        new_uri: String
    ) {
        let creator_addr = signer::address_of(creator);

        event::emit(
            UriMutation { creator: creator_addr, collection, token, old_uri, new_uri }
        );
    }
```

**File:** aptos-move/framework/aptos-token-objects/sources/token.move (L810-820)
```text
    public fun set_uri(mutator_ref: &MutatorRef, uri: String) acquires Token {
        assert!(uri.length() <= MAX_URI_LENGTH, error::out_of_range(EURI_TOO_LONG));
        let token = borrow_mut(mutator_ref);
        event::emit(Mutation {
            token_address: mutator_ref.self,
            mutated_field_name: string::utf8(b"uri"),
            old_value: token.uri,
            new_value: uri,
        });
        token.uri = uri;
    }
```

**File:** storage/indexer/src/event_v2_translator.rs (L1120-1143)
```rust
struct UriMutationTranslator;
impl EventV2Translator for UriMutationTranslator {
    fn translate_event_v2_to_v1(
        &self,
        v2: &ContractEventV2,
        engine: &EventV2TranslationEngine,
    ) -> Result<ContractEventV1> {
        let uri_mutation = UriMutation::try_from_bytes(v2.event_data())?;
        let struct_tag = StructTag::from_str("0x3::token_event_store::TokenEventStoreV1")?;
        let (key, sequence_number) = if let Some(state_value_bytes) =
            engine.get_state_value_bytes_for_resource(uri_mutation.creator(), &struct_tag)?
        {
            let object_resource: TokenEventStoreV1Resource = bcs::from_bytes(&state_value_bytes)?;
            let key = *object_resource.uri_mutate_events().key();
            let sequence_number = engine
                .get_next_sequence_number(&key, object_resource.uri_mutate_events().count())?;
            (key, sequence_number)
        } else {
            // If the TokenEventStoreV1 resource is not found, we skip the event translation to
            // avoid panic because the creation number cannot be decided.
            return Err(AptosDbError::from(anyhow::format_err!(
                "TokenEventStoreV1 resource not found"
            )));
        };
```
