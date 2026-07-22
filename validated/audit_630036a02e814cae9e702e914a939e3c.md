### Title
Batcher Computes Wrong `state_diff_commitment` and `block_hash` for Blocks Containing DeclareV1 (Cairo-0) Transactions — (`crates/blockifier/src/state/cached_state.rs`)

---

### Summary

`CommitmentStateDiff` has no field for deprecated (Cairo-0) declared classes. The conversion `From<CommitmentStateDiff> for ThinStateDiff` hardcodes `deprecated_declared_classes: Vec::new()`. Because `calculate_state_diff_hash` explicitly chains `deprecated_declared_classes` into the Poseidon hash, any block containing a DeclareV1 transaction will have a wrong `StateDiffCommitment`, wrong `concatenated_counts`, and wrong `block_hash`.

---

### Finding Description

`CommitmentStateDiff` tracks only four fields — `address_to_class_hash`, `address_to_nonce`, `storage_updates`, and `class_hash_to_compiled_class_hash` — with no field for deprecated (Cairo-0) declared classes: [1](#0-0) 

The conversion to `ThinStateDiff` therefore always produces an empty `deprecated_declared_classes`: [2](#0-1) 

This converted `ThinStateDiff` is passed directly to `calculate_block_commitments` in the batcher: [3](#0-2) 

`calculate_block_commitments` calls `calculate_state_diff_hash`, which explicitly chains `deprecated_declared_classes` into the Poseidon hash: [4](#0-3) 

Specifically, `chain_deprecated_declared_classes` chains the count and each class hash: [5](#0-4) 

The resulting `state_diff_commitment` is then chained into the block hash: [6](#0-5) 

Additionally, `state_diff.len()` (which counts `deprecated_declared_classes` entries) feeds into `concatenated_counts`, also part of the block hash: [7](#0-6) 

`ThinStateDiff` defines `deprecated_declared_classes` as `Vec<ClassHash>`: [8](#0-7) 

---

### Impact Explanation

An unprivileged user submits a DeclareV1 transaction via the public RPC/gateway. The transaction is accepted and executed. The batcher's `BlockExecutionArtifacts::new` produces a `ThinStateDiff` with `deprecated_declared_classes: Vec::new()` regardless of how many Cairo-0 classes were declared. `calculate_state_diff_hash` computes a `StateDiffCommitment` that omits the declared class hash(es). The resulting `block_hash` is wrong compared to any implementation that correctly includes the deprecated class hash in the state diff hash. This is a **Critical** impact: wrong block hash and wrong state diff commitment for accepted, executed transactions.

---

### Likelihood Explanation

DeclareV1 (Cairo-0) transactions are still valid Starknet transactions. Any user who submits one triggers the bug deterministically. No special privileges are required — only a valid DeclareV1 transaction submitted to the public gateway.

---

### Recommendation

Add a `deprecated_declared_classes` field to `CommitmentStateDiff` and populate it from `StateMaps` (which already tracks `declared_contracts`). Update `From<CommitmentStateDiff> for ThinStateDiff` to copy this field instead of hardcoding `Vec::new()`. Ensure `From<StateMaps> for CommitmentStateDiff` maps `declared_contracts` to the new field.

---

### Proof of Concept

1. Execute a DeclareV1 transaction through the batcher.
2. Capture `BlockExecutionArtifacts::thin_state_diff()`.
3. Assert `thin_state_diff.deprecated_declared_classes.is_empty()` — this will pass, demonstrating the bug.
4. Compute `calculate_state_diff_hash(&batcher_thin_state_diff)` → `commitment_A`.
5. Construct a corrected `ThinStateDiff` with the declared class hash in `deprecated_declared_classes`.
6. Compute `calculate_state_diff_hash(&correct_thin_state_diff)` → `commitment_B`.
7. Assert `commitment_A != commitment_B` — this will pass, proving the block hash divergence.

### Citations

**File:** crates/blockifier/src/state/cached_state.rs (L701-710)
```rust
#[derive(Clone, Debug, Default, Eq, PartialEq)]
pub struct CommitmentStateDiff {
    // Contract instance attributes (per address).
    pub address_to_class_hash: IndexMap<ContractAddress, ClassHash>,
    pub address_to_nonce: IndexMap<ContractAddress, Nonce>,
    pub storage_updates: IndexMap<ContractAddress, IndexMap<StorageKey, Felt>>,

    // Global attributes.
    pub class_hash_to_compiled_class_hash: IndexMap<ClassHash, CompiledClassHash>,
}
```

**File:** crates/blockifier/src/state/cached_state.rs (L756-767)
```rust
impl From<CommitmentStateDiff> for ThinStateDiff {
    fn from(commitment_state_diff: CommitmentStateDiff) -> Self {
        Self {
            deployed_contracts: commitment_state_diff.address_to_class_hash,
            storage_diffs: commitment_state_diff.storage_updates,
            class_hash_to_compiled_class_hash: commitment_state_diff
                .class_hash_to_compiled_class_hash,
            nonces: commitment_state_diff.address_to_nonce,
            // TODO(AlonH): Remove this when the structure of storage diffs changes.
            deprecated_declared_classes: Vec::new(),
        }
    }
```

**File:** crates/apollo_batcher/src/block_builder.rs (L170-176)
```rust
        let (header_commitments, measurements) = calculate_block_commitments(
            &transactions_data,
            ThinStateDiff::from(commitment_state_diff.clone()),
            l1_da_mode,
            &block_info.starknet_version,
        )
        .await;
```

**File:** crates/starknet_api/src/block_hash/state_diff_hash.rs (L30-42)
```rust
pub fn calculate_state_diff_hash(state_diff: &ThinStateDiff) -> StateDiffCommitment {
    let mut hash_chain = HashChain::new();
    hash_chain = hash_chain.chain(&STARKNET_STATE_DIFF0);
    hash_chain = chain_deployed_contracts(&state_diff.deployed_contracts, hash_chain);
    hash_chain = chain_declared_classes(&state_diff.class_hash_to_compiled_class_hash, hash_chain);
    hash_chain =
        chain_deprecated_declared_classes(&state_diff.deprecated_declared_classes, hash_chain);
    hash_chain = hash_chain.chain(&Felt::ONE) // placeholder.
        .chain(&Felt::ZERO); // placeholder.
    hash_chain = chain_storage_diffs(&state_diff.storage_diffs, hash_chain);
    hash_chain = chain_nonces(&state_diff.nonces, hash_chain);
    StateDiffCommitment(PoseidonHash(hash_chain.get_poseidon_hash()))
}
```

**File:** crates/starknet_api/src/block_hash/state_diff_hash.rs (L71-80)
```rust
fn chain_deprecated_declared_classes(
    deprecated_declared_classes: &[ClassHash],
    hash_chain: HashChain,
) -> HashChain {
    let mut sorted_deprecated_declared_classes = deprecated_declared_classes.to_vec();
    sorted_deprecated_declared_classes.sort_unstable();
    hash_chain
        .chain(&sorted_deprecated_declared_classes.len().into())
        .chain_iter(sorted_deprecated_declared_classes.iter().map(|class_hash| &class_hash.0))
}
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L253-261)
```rust
    Ok(BlockHash(
        HashChain::new()
            .chain(&block_hash_version.clone().into())
            .chain(&partial_block_hash_components.block_number.0.into())
            .chain(&state_root.0)
            .chain(&partial_block_hash_components.sequencer.0)
            .chain(&partial_block_hash_components.timestamp.0.into())
            .chain(&block_commitments.concatenated_counts)
            .chain(&block_commitments.state_diff_commitment.0.0)
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L318-323)
```rust
    let concatenated_counts = concat_counts(
        transactions_data.len(),
        event_leaf_elements.len(),
        state_diff.len(),
        l1_da_mode,
    );
```

**File:** crates/starknet_api/src/state.rs (L67-76)
```rust
#[derive(Debug, Default, Clone, Eq, PartialEq, Deserialize, Serialize)]
pub struct ThinStateDiff {
    pub deployed_contracts: IndexMap<ContractAddress, ClassHash>,
    pub storage_diffs: IndexMap<ContractAddress, IndexMap<StorageKey, Felt>>,
    // class hash to compiled class hash is affected by both declared_classes and
    // migrated_compiled_classes.
    pub class_hash_to_compiled_class_hash: IndexMap<ClassHash, CompiledClassHash>,
    pub deprecated_declared_classes: Vec<ClassHash>,
    pub nonces: IndexMap<ContractAddress, Nonce>,
}
```
