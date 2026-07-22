Based on my thorough code analysis, this is a **real vulnerability**. Here is the full report.

---

### Title
P2P Sync Accepts Attacker-Supplied State Diff Chunks Due to Missing Signature and Commitment Verification — (`crates/apollo_p2p_sync/src/client/state_diff.rs`, `crates/apollo_p2p_sync/src/client/header.rs`)

### Summary

A malicious p2p peer can corrupt a syncing node's stored state diff by sending a `SignedBlockHeader` with an inflated `state_diff_length` value. Because the p2p sync client performs no ECDSA signature verification on the header and no `state_diff_commitment` hash verification on the assembled state diff, the node will accept and permanently store an attacker-controlled `ThinStateDiff` containing arbitrary extra storage slots, class declarations, deployed contracts, or nonces.

### Finding Description

**Step 1 — Header accepted without cryptographic verification.**

`HeaderStreamBuilder::parse_data_for_block` in `header.rs` performs only two checks before storing the header:

- The `block_number` field matches the expected value.
- `signatures.len() == ALLOWED_SIGNATURES_LENGTH` (i.e., exactly 1 element — a count check, not an ECDSA check). [1](#0-0) 

There is no call to `verify_block_signature` (which exists in `starknet_api/src/block.rs` but is never invoked in the p2p sync path), no block hash verification, and no check that `state_diff_commitment.root` is consistent with any trusted source. [2](#0-1) 

**Step 2 — `state_diff_length` is extracted from the attacker-controlled `StateDiffCommitment` proto field.**

The protobuf `StateDiffCommitment` message carries both a `state_diff_length` (u64) and a `root` (hash). The converter reads `state_diff_length` directly from the peer-supplied proto: [3](#0-2) 

The proto definition confirms both fields are peer-supplied with no binding to a trusted source: [4](#0-3) 

**Step 3 — State diff loop uses the attacker-controlled length as its termination condition.**

`StateDiffStreamBuilder::parse_data_for_block` reads `state_diff_length` from the stored header and loops until `current_state_diff_len >= target_state_diff_len`: [5](#0-4) 

If the attacker set `state_diff_length = 10` but the canonical state diff has only 2 entries, the loop will consume 8 additional attacker-supplied `StateDiffChunk` messages.

**Step 4 — No `state_diff_commitment` hash verification after assembly.**

After the loop exits, the code calls `validate_deprecated_declared_classes_non_conflicting` (a duplicate-class check) and then returns `Ok(Some((result, block_number)))`. There is no call to `calculate_state_diff_hash` to verify the assembled `ThinStateDiff` against the `state_diff_commitment.root` stored in the header. [6](#0-5) 

**Step 5 — Corrupted state diff written to storage unconditionally.**

`write_to_storage` calls `append_state_diff` directly with no commitment check: [7](#0-6) 

`append_state_diff` writes all fields of the `ThinStateDiff` (deployed contracts, storage diffs, nonces, class hashes) to the node's persistent storage without any integrity check: [8](#0-7) 

### Impact Explanation

The node permanently stores a `ThinStateDiff` containing attacker-injected entries. Every subsequent RPC call that reads contract storage, class hashes, nonces, or deployed contracts for the affected block will return attacker-controlled values. The node's view of the Starknet state is corrupted from that block number onward, satisfying the Critical impact criterion: *wrong state, class hash, or storage value stored and served*.

### Likelihood Explanation

Any unauthenticated p2p peer can trigger this. The p2p sync client connects to peers discovered via the network layer with no prior trust establishment. The attacker only needs to:
1. Connect as a p2p peer.
2. Send one `SignedBlockHeader` with an inflated `state_diff_length` and a single (arbitrary) signature element.
3. Send the corresponding number of `StateDiffChunk` messages.

No validator key, sequencer key, or operator privilege is required.

### Recommendation

Two independent fixes are needed, either of which alone would block the attack:

1. **Verify the block signature cryptographically** in `HeaderStreamBuilder::parse_data_for_block` by calling `verify_block_signature` with the known sequencer public key before storing the header. This prevents an attacker from injecting any header field, including `state_diff_length`.

2. **Verify the assembled state diff against `state_diff_commitment.root`** at the end of `StateDiffStreamBuilder::parse_data_for_block` by calling `calculate_state_diff_hash(&result)` and comparing it to the `state_diff_commitment` stored in the header. If they differ, return `ParseDataError::BadPeer`. [9](#0-8) 

### Proof of Concept

```rust
// Pseudocode for a Rust integration test
let mut mock_peer = MockP2pPeer::new();

// Step 1: send a header with state_diff_length=10 (canonical is 2)
// Signature has correct length (1 element) but is cryptographically invalid — not checked.
mock_peer.send_header(SignedBlockHeader {
    block_header: BlockHeader {
        block_number: BlockNumber(0),
        state_diff_length: Some(10),   // inflated
        state_diff_commitment: Some(real_commitment_for_2_entries),
        block_hash: BlockHash(arbitrary_felt),
        ..Default::default()
    },
    signatures: vec![BlockSignature::default()], // count==1, not verified
});
mock_peer.send_header_fin();

// Step 2: send 10 StateDiffChunk messages (2 canonical + 8 attacker-supplied)
for i in 0..10 {
    mock_peer.send_state_diff_chunk(StateDiffChunk::ContractDiff(ContractDiff {
        contract_address: ContractAddress::from(i as u64),
        storage_diffs: indexmap! { StorageKey::from(0u64) => Felt::from(0xdeadbeefu64) },
        ..Default::default()
    }));
}
mock_peer.send_state_diff_fin();

// Step 3: assert the stored state diff contains all 10 entries
let stored = storage_reader.begin_ro_txn().unwrap()
    .get_state_diff(BlockNumber(0)).unwrap().unwrap();
assert_eq!(stored.storage_diffs.len(), 10); // 8 are attacker-injected
```

The loop in `parse_data_for_block` will consume all 10 chunks because `current_state_diff_len` (10) equals `target_state_diff_len` (10), and the final equality check at line 99 passes. The assertion will succeed, confirming the corrupted state diff is stored. [10](#0-9)

### Citations

**File:** crates/apollo_p2p_sync/src/client/header.rs (L104-120)
```rust
            if block_number
                != signed_block_header.block_header.block_header_without_hash.block_number
            {
                return Err(ParseDataError::BadPeer(BadPeerError::HeadersUnordered {
                    expected_block_number: block_number,
                    actual_block_number: signed_block_header
                        .block_header
                        .block_header_without_hash
                        .block_number,
                }));
            }
            if signed_block_header.signatures.len() != ALLOWED_SIGNATURES_LENGTH {
                return Err(ParseDataError::BadPeer(BadPeerError::WrongSignaturesLength {
                    signatures: signed_block_header.signatures,
                }));
            }
            Ok(Some(signed_block_header))
```

**File:** crates/starknet_api/src/block.rs (L721-735)
```rust
/// Verifies that the the block header was signed by the expected sequencer.
pub fn verify_block_signature(
    sequencer_pub_key: &SequencerPublicKey,
    signature: &BlockSignature,
    state_diff_commitment: &GlobalRoot,
    block_hash: &BlockHash,
) -> Result<bool, BlockVerificationError> {
    let message_hash = Poseidon::hash_array(&[block_hash.0, state_diff_commitment.0]);
    verify_message_hash_signature(&message_hash, &signature.0, &sequencer_pub_key.0).map_err(
        |err| BlockVerificationError::BlockSignatureVerificationFailed {
            block_hash: *block_hash,
            error: err,
        },
    )
}
```

**File:** crates/apollo_protobuf/src/converters/header.rs (L117-122)
```rust
        let state_diff_length = value.state_diff_commitment.as_ref().map(|state_diff_commitment| {
            state_diff_commitment
                .state_diff_length
                .try_into()
                .expect("Failed converting u64 to usize")
        });
```

**File:** crates/apollo_protobuf/src/proto/p2p/proto/sync/common.proto (L6-9)
```text
message StateDiffCommitment {
    uint64 state_diff_length = 1;
    Hash root = 2;
}
```

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L33-35)
```rust
        async move {
            storage_writer.begin_rw_txn()?.append_state_diff(self.1, self.0)?.commit()?;
            STATE_SYNC_STATE_MARKER.set_lossy(self.1.unchecked_next().0);
```

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L62-107)
```rust
            let target_state_diff_len = storage_reader
                .begin_ro_txn()?
                .get_block_header(block_number)?
                .expect("A header with number lower than the header marker is missing")
                .state_diff_length
                .ok_or(P2pSyncClientError::OldHeaderInStorage {
                    block_number,
                    missing_field: "state_diff_length",
                })?;

            while current_state_diff_len < target_state_diff_len {
                let maybe_state_diff_chunk = state_diff_chunks_response_manager
                    .next()
                    .await
                    .ok_or(ParseDataError::BadPeer(BadPeerError::SessionEndedWithoutFin {
                        type_description: Self::TYPE_DESCRIPTION,
                    }))?;
                let Some(state_diff_chunk) = maybe_state_diff_chunk?.0 else {
                    if current_state_diff_len == 0 {
                        return Ok(None);
                    } else {
                        return Err(ParseDataError::BadPeer(BadPeerError::WrongStateDiffLength {
                            expected_length: target_state_diff_len,
                            possible_lengths: vec![current_state_diff_len],
                        }));
                    }
                };
                prev_result_len = current_state_diff_len;
                if state_diff_chunk.is_empty() {
                    return Err(ParseDataError::BadPeer(BadPeerError::EmptyStateDiffPart));
                }
                // It's cheaper to calculate the length of `state_diff_part` than the length of
                // `result`.
                current_state_diff_len += state_diff_chunk.len();
                unite_state_diffs(&mut result, state_diff_chunk)?;
            }

            if current_state_diff_len != target_state_diff_len {
                return Err(ParseDataError::BadPeer(BadPeerError::WrongStateDiffLength {
                    expected_length: target_state_diff_len,
                    possible_lengths: vec![prev_result_len, current_state_diff_len],
                }));
            }

            validate_deprecated_declared_classes_non_conflicting(&result)?;
            Ok(Some((result, block_number)))
```

**File:** crates/apollo_storage/src/state/mod.rs (L601-678)
```rust
impl<T: StorageTransaction<Mode = RW>> StateStorageWriter for T {
    #[sequencer_latency_histogram(STORAGE_APPEND_THIN_STATE_DIFF_LATENCY, false)]
    fn append_state_diff(
        self,
        block_number: BlockNumber,
        thin_state_diff: ThinStateDiff,
    ) -> StorageResult<Self> {
        let tables = self.tables();
        let inner_txn = self.txn();
        let file_offset_table = inner_txn.open_table(&tables.file_offsets)?;
        let markers_table = self.open_table(&tables.markers)?;
        let state_diffs_table = self.open_table(&tables.state_diffs)?;
        let nonces_table = self.open_table(&tables.nonces)?;
        let deployed_contracts_table = self.open_table(&tables.deployed_contracts)?;
        let storage_table = self.open_table(&tables.contract_storage)?;
        let declared_classes_block_table = self.open_table(&tables.declared_classes_block)?;
        let deprecated_declared_classes_block_table =
            self.open_table(&tables.deprecated_declared_classes_block)?;
        let compiled_class_hash_table = self.open_table(&tables.compiled_class_hash)?;

        // Write state.
        write_deployed_contracts(
            &thin_state_diff.deployed_contracts,
            inner_txn,
            block_number,
            &deployed_contracts_table,
            &nonces_table,
        )?;
        write_storage_diffs(
            &thin_state_diff.storage_diffs,
            inner_txn,
            block_number,
            &storage_table,
        )?;
        // Must be called after write_deployed_contracts since the nonces are updated there.
        write_nonces(&thin_state_diff.nonces, inner_txn, block_number, &nonces_table)?;

        for (class_hash, _) in &thin_state_diff.class_hash_to_compiled_class_hash {
            let not_declared = declared_classes_block_table.get(inner_txn, class_hash)?.is_none();
            if not_declared {
                declared_classes_block_table.insert(inner_txn, class_hash, &block_number)?;
            }
        }

        write_compiled_class_hashes(
            &thin_state_diff.class_hash_to_compiled_class_hash,
            inner_txn,
            block_number,
            &compiled_class_hash_table,
        )?;

        for class_hash in thin_state_diff.deprecated_declared_classes.iter() {
            // Cairo0 classes can be declared in different blocks. The first block to declare the
            // class is recorded here.
            if deprecated_declared_classes_block_table.get(inner_txn, class_hash)?.is_none() {
                deprecated_declared_classes_block_table.insert(
                    inner_txn,
                    class_hash,
                    &block_number,
                )?;
            }
        }

        // Write state diff.
        let location = self.file_handlers().append_state_diff(&thin_state_diff);
        state_diffs_table.append(inner_txn, &block_number, &location)?;
        file_offset_table.upsert(inner_txn, &OffsetKind::ThinStateDiff, &location.next_offset())?;

        update_marker_to_next_block(inner_txn, &markers_table, MarkerKind::State, block_number)?;

        advance_compiled_class_marker_over_blocks_without_classes(
            inner_txn,
            &markers_table,
            &state_diffs_table,
            self.file_handlers(),
        )?;

        Ok(self)
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
