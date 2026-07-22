The code is clear. Let me trace the exact execution path.

The code confirms the vulnerability. Here is the complete analysis:

---

### Title
Unauthenticated P2P Peer Can Inject `state_diff_length=0` Header to Persist Empty State Diff, Corrupting Node Storage — (`crates/apollo_p2p_sync/src/client/state_diff.rs`, `crates/apollo_p2p_sync/src/client/header.rs`)

### Summary

`HeaderStreamBuilder::parse_data_for_block` accepts a `SignedBlockHeader` from an unauthenticated p2p peer with no cryptographic verification of the block hash, `state_diff_commitment`, or signature content. If the peer sets `state_diff_length=0`, `StateDiffStreamBuilder::parse_data_for_block` reads that value as `target_state_diff_len`, the accumulation loop is never entered, and `ThinStateDiff::default()` (an empty diff) is immediately committed to storage for that block number — silently discarding all actual storage writes, nonce updates, and contract deployments.

### Finding Description

**Step 1 — Header acceptance without commitment verification.**

`HeaderStreamBuilder::parse_data_for_block` performs exactly two checks on the peer-supplied `SignedBlockHeader`: [1](#0-0) 

- Block number matches the expected value.
- `signatures.len() == ALLOWED_SIGNATURES_LENGTH` (count only; no cryptographic verification of the signature bytes, no block-hash recomputation, no `state_diff_commitment` cross-check).

The `_storage_reader` parameter is explicitly unused. `verify_block_signature` (which exists in `starknet_api/src/block.rs` and signs over `block_hash ‖ state_diff_commitment`) is never called here. [2](#0-1) 

The header — including the attacker-controlled `state_diff_length` field — is then written verbatim to storage: [3](#0-2) 

**Step 2 — State diff loop gated entirely on the stored `state_diff_length`.**

`StateDiffStreamBuilder::parse_data_for_block` reads `target_state_diff_len` directly from the header that was just stored: [4](#0-3) 

The accumulation loop is: [5](#0-4) 

When `target_state_diff_len = 0`, the condition `0 < 0` is immediately false; the loop body never executes and no `StateDiffChunk` messages are consumed.

**Step 3 — Post-loop length check passes trivially.** [6](#0-5) 

`current_state_diff_len (0) != target_state_diff_len (0)` is false, so no error is raised. `validate_deprecated_declared_classes_non_conflicting` trivially passes on an empty diff. The function returns `Ok(Some((ThinStateDiff::default(), block_number)))`.

**Step 4 — Empty diff committed to storage.** [7](#0-6) 

`append_state_diff` is called with the empty `ThinStateDiff`. No verification against the `state_diff_commitment` field stored in the header is performed at any point in this path.

### Impact Explanation

Any node syncing via the p2p client (full nodes, sequencers in catch-up mode) that connects to a malicious peer will store an empty `ThinStateDiff` for the targeted block. All storage writes, nonce increments, contract deployments, and class declarations for that block are silently dropped. Subsequent RPC calls (`starknet_getStorageAt`, `starknet_getNonce`, `starknet_getClassAt`, etc.) return authoritative-looking wrong values. The state marker advances normally, so the node continues syncing subsequent blocks on top of a corrupted state root, compounding the corruption indefinitely.

This matches: **High — RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value**, and also **High — sync/storage corruption with no detection**.

### Likelihood Explanation

Any party that can establish a p2p connection to the victim node can execute this attack. No validator, operator, or sequencer privilege is required. The attacker only needs to supply a `SignedBlockHeader` with the correct block number, any single `BlockSignature` value (the count check passes), and `state_diff_length = 0`. The victim node has no mechanism to detect or recover from the resulting corruption.

### Recommendation

1. **Verify the block hash**: Recompute the block hash from the received header fields and compare it against the `block_hash` field before storing. This binds `state_diff_commitment` (and thus `state_diff_length`) to the hash.
2. **Verify the signature cryptographically**: Call `verify_block_signature` (already present in `starknet_api::block`) against a known sequencer public key before accepting any `SignedBlockHeader` from a p2p peer.
3. **Verify the state diff against `state_diff_commitment`**: After collecting all `StateDiffChunk` messages, compute `calculate_state_diff_hash(&result)` and compare it against the `state_diff_commitment` stored in the header. The infrastructure for this already exists in `apollo_committer`.

### Proof of Concept

```
1. Attacker node connects to victim via p2p.
2. Victim sends a BlockHeadersRequest for block N.
3. Attacker responds with:
     SignedBlockHeader {
         block_header: BlockHeader {
             block_number: N,
             state_diff_length: Some(0),   // attacker-controlled
             state_diff_commitment: <any>, // not verified
             block_hash: <any>,            // not verified
             ...
         },
         signatures: vec![BlockSignature::default()], // count == 1, passes
     }
4. HeaderStreamBuilder::parse_data_for_block accepts it (block_number matches, signatures.len()==1).
5. Header is written to storage with state_diff_length = 0.
6. StateDiffStreamBuilder::parse_data_for_block reads target_state_diff_len = 0.
7. while 0 < 0 { } — loop body never executes.
8. 0 != 0 — false, no error.
9. Ok(Some((ThinStateDiff::default(), N))) returned.
10. append_state_diff(N, ThinStateDiff::default()) committed to storage.
11. All actual storage writes / nonces / deployments for block N are lost.
12. starknet_getStorageAt / starknet_getNonce return wrong (zero/default) values for all
    contracts modified in block N.
```

### Citations

**File:** crates/apollo_p2p_sync/src/client/header.rs (L34-50)
```rust
            storage_writer
                .begin_rw_txn()?
                .append_header(
                    self.block_header.block_header_without_hash.block_number,
                    &self.block_header,
                )?
                .append_block_signature(
                    self.block_header.block_header_without_hash.block_number,
                    self
                    .signatures
                    // In the future we will support multiple signatures.
                    .first()
                    // The verification that the size of the vector is 1 is done in the data
                    // verification.
                    .expect("Vec::first should return a value on a vector of size 1"),
                )?
                .commit()?;
```

**File:** crates/apollo_p2p_sync/src/client/header.rs (L82-123)
```rust
    fn parse_data_for_block<'a>(
        signed_headers_response_manager: &'a mut ClientResponsesManager<
            DataOrFin<SignedBlockHeader>,
        >,
        block_number: BlockNumber,
        _storage_reader: &'a StorageReader,
    ) -> BoxFuture<'a, Result<Option<Self::Output>, ParseDataError>> {
        async move {
            // TODO(noamsp): investigate and remove this timeout.
            let maybe_signed_header =
                timeout(Duration::from_secs(15), signed_headers_response_manager.next())
                    .await
                    .ok()
                    .flatten()
                    .ok_or(ParseDataError::BadPeer(BadPeerError::SessionEndedWithoutFin {
                        type_description: Self::TYPE_DESCRIPTION,
                    }))?;
            let Some(signed_block_header) = maybe_signed_header?.0 else {
                return Ok(None);
            };
            // TODO(shahak): Check that parent_hash is the same as the previous block's hash
            // and handle reverts.
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
        }
        .boxed()
    }
```

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L33-35)
```rust
        async move {
            storage_writer.begin_rw_txn()?.append_state_diff(self.1, self.0)?.commit()?;
            STATE_SYNC_STATE_MARKER.set_lossy(self.1.unchecked_next().0);
```

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L62-70)
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
```

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L72-97)
```rust
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
```

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L99-107)
```rust
            if current_state_diff_len != target_state_diff_len {
                return Err(ParseDataError::BadPeer(BadPeerError::WrongStateDiffLength {
                    expected_length: target_state_diff_len,
                    possible_lengths: vec![prev_result_len, current_state_diff_len],
                }));
            }

            validate_deprecated_declared_classes_non_conflicting(&result)?;
            Ok(Some((result, block_number)))
```
