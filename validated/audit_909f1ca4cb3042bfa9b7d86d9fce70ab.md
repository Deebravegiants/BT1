No vulnerability found for this question.

**Reasoning:**

The `RoyaltyMutate::creator` field cannot be arbitrarily set by an attacker in any way that reaches on-chain custody state. It is populated exclusively by the Move framework via `emit_token_royalty_mutate_event`, which derives it from `signer::address_of(creator)` of the actual transaction signer [1](#0-0) . That signer is validated upstream by `assert_tokendata_exists(creator, token_data_id)` in `mutate_tokendata_royalty`, which enforces that the caller is the legitimate creator of the given `token_data_id` before the royalty mutation and event emission occur [2](#0-1) . There is no code path where an unprivileged caller can submit a "crafted event blob" that gets accepted as a genuine on-chain `RoyaltyMutate` event with a mismatched creator — the `creator` field is derived from the authenticated signer, not attacker-supplied input.

The `RoyaltyMutate::try_from_bytes` deserializer in `types/src/account_config/events/royalty_mutate.rs` [3](#0-2)  and the `RoyaltyMutateTranslator` in `storage/indexer/src/event_v2_translator.rs` [4](#0-3)  both operate on already-emitted, chain-validated event bytes — the translator even independently looks up the `TokenEventStoreV1` resource keyed by `royalty_mutation.creator()` to determine the event key/sequence number, and fails safely if that resource lookup doesn't succeed, rather than trusting an arbitrary creator field for custody purposes.

The scenario described (constructing two standalone `RoyaltyMutate` blobs off-chain with matching collection/token strings but different creator fields, and feeding them into a hypothetical external ledger keyed only by `(collection, token)`) is:
1. Not a real transaction/API/bytecode entry point into Aptos custody logic — it's purely a hypothetical property of a third-party indexer design, not of Aptos core.
2. Explicitly excluded by the review's decision standard, which states to "reject anything that... only produces cosmetic or event-level mismatch," and the required-impacts section explicitly excludes "event-only mismatches."
3. Not a custody boundary at all — royalty payee address custody state lives in `TokenData.royalty.payee_address` inside the actual `Collections` resource, gated by the real creator's signer authority, not in any downstream event-keyed ledger.

No unprivileged path crosses a real custody boundary here.

### Citations

**File:** aptos-move/framework/aptos-token/sources/token_event_store.move (L333-359)
```text
    friend fun emit_token_royalty_mutate_event(
        creator: &signer,
        collection: String,
        token: String,
        old_royalty_numerator: u64,
        old_royalty_denominator: u64,
        old_royalty_payee_addr: address,
        new_royalty_numerator: u64,
        new_royalty_denominator: u64,
        new_royalty_payee_addr: address
    ) {
        let creator_addr = signer::address_of(creator);

        event::emit(
            RoyaltyMutate {
                creator: creator_addr,
                collection,
                token,
                old_royalty_numerator,
                old_royalty_denominator,
                old_royalty_payee_addr,
                new_royalty_numerator,
                new_royalty_denominator,
                new_royalty_payee_addr
            }
        );
    }
```

**File:** aptos-move/framework/aptos-token/sources/token.move (L815-833)
```text
    public fun mutate_tokendata_royalty(creator: &signer, token_data_id: TokenDataId, royalty: Royalty) acquires Collections {
        assert_tokendata_exists(creator, token_data_id);

        let all_token_data = &mut Collections[token_data_id.creator].token_data;
        let token_data = all_token_data.borrow_mut(token_data_id);
        assert!(token_data.mutability_config.royalty, error::permission_denied(EFIELD_NOT_MUTABLE));

        token_event_store::emit_token_royalty_mutate_event(
            creator,
            token_data_id.collection,
            token_data_id.name,
            token_data.royalty.royalty_points_numerator,
            token_data.royalty.royalty_points_denominator,
            token_data.royalty.payee_address,
            royalty.royalty_points_numerator,
            royalty.royalty_points_denominator,
            royalty.payee_address
        );
        token_data.royalty = royalty;
```

**File:** types/src/account_config/events/royalty_mutate.rs (L54-56)
```rust
    pub fn try_from_bytes(bytes: &[u8]) -> Result<Self> {
        bcs::from_bytes(bytes).map_err(Into::into)
    }
```

**File:** storage/indexer/src/event_v2_translator.rs (L1245-1287)
```rust
struct RoyaltyMutateTranslator;
impl EventV2Translator for RoyaltyMutateTranslator {
    fn translate_event_v2_to_v1(
        &self,
        v2: &ContractEventV2,
        engine: &EventV2TranslationEngine,
    ) -> Result<ContractEventV1> {
        let royalty_mutation = RoyaltyMutate::try_from_bytes(v2.event_data())?;
        let struct_tag = StructTag::from_str("0x3::token_event_store::TokenEventStoreV1")?;
        let (key, sequence_number) = if let Some(state_value_bytes) =
            engine.get_state_value_bytes_for_resource(royalty_mutation.creator(), &struct_tag)?
        {
            let object_resource: TokenEventStoreV1Resource = bcs::from_bytes(&state_value_bytes)?;
            let key = *object_resource.royalty_mutate_events().key();
            let sequence_number = engine
                .get_next_sequence_number(&key, object_resource.royalty_mutate_events().count())?;
            (key, sequence_number)
        } else {
            // If the TokenEventStoreV1 resource is not found, we skip the event translation to
            // avoid panic because the creation number cannot be decided.
            return Err(AptosDbError::from(anyhow::format_err!(
                "TokenEventStoreV1 resource not found"
            )));
        };
        let royalty_mutation_event = RoyaltyMutateEvent::new(
            *royalty_mutation.creator(),
            royalty_mutation.collection().clone(),
            royalty_mutation.token().clone(),
            *royalty_mutation.old_royalty_numerator(),
            *royalty_mutation.old_royalty_denominator(),
            *royalty_mutation.old_royalty_payee_addr(),
            *royalty_mutation.new_royalty_numerator(),
            *royalty_mutation.new_royalty_denominator(),
            *royalty_mutation.new_royalty_payee_addr(),
        );
        Ok(ContractEventV1::new(
            key,
            sequence_number,
            ROYALTY_MUTATE_EVENT_TYPE.clone(),
            bcs::to_bytes(&royalty_mutation_event)?,
        )?)
    }
}
```
