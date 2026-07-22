Based on my thorough analysis of the code, here is the finding:

---

### Title
P2P Sync Accepts State Diffs Without Verifying Against `state_diff_commitment`, Causing `starknet_getStateUpdate` to Return Authoritative Wrong Values — (`crates/apollo_p2p_sync/src/client/state_diff.rs`)

### Summary
The p2p sync client's `parse_data_for_block` for state diffs validates only the total entry count (`state_diff_length`) against the stored header, but never computes or compares the Poseidon hash of the assembled `ThinStateDiff` against `header.state_diff_commitment`. An unauthenticated peer can send chunks with the correct total length but arbitrary wrong content. The wrong diff is committed to storage and then served verbatim by `starknet_getStateUpdate` as an `AcceptedStateUpdate`.

### Finding Description

**Step 1 — Header sync accepts headers without cryptographic verification.**

`parse_data_for_block` in `header.rs` only checks block number ordering and that exactly one signature is present: [1](#0-0) 

There is no call to `verify_block_signature` and no L1 anchor check. The attacker can supply any `state_diff_length` and any `state_diff_commitment` value in the header, and it will be stored as-is.

**Step 2 — State diff sync validates only total length, not content hash.**

`parse_data_for_block` in `state_diff.rs` reads `state_diff_length` from the stored header and accumulates chunks until the count matches: [2](#0-1) 

The only content checks are: no duplicate keys within a chunk (`ConflictingStateDiffParts`), no empty chunks, and no duplicate deprecated class hashes. There is **no call to `calculate_state_diff_hash`** and no comparison against `header.state_diff_commitment`. A grep for `state_diff_commitment` in the entire `apollo_p2p_sync` client directory returns hits only in `test.rs` and `header.rs` (the `convert_sync_block_to_block_data` path for internally-produced blocks, not for p2p-received data).

**Step 3 — Wrong diff is committed to storage unconditionally.**

`write_to_storage` calls `append_state_diff` directly with the unverified `ThinStateDiff`: [3](#0-2) 

**Step 4 — RPC reads the stored diff without re-verification.**

`get_state_update` in `api_impl.rs` reads `txn.get_state_diff(block_number)` and wraps it in `AcceptedStateUpdate` with no check against `header.state_diff_commitment`: [4](#0-3) 

### Impact Explanation

Any RPC client calling `starknet_getStateUpdate` receives an `AcceptedStateUpdate` whose `state_diff.storage_diffs`, `state_diff.deployed_contracts`, and `state_diff.nonces` may be entirely attacker-controlled. This is an authoritative-looking wrong value served over the public JSON-RPC interface, matching the **High** impact category: *"RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value."*

### Likelihood Explanation

The p2p network is open to unauthenticated peers. Any node that connects and is selected to answer a state diff query can inject the wrong diff. The node reports the peer only for structural violations (wrong length, conflicting keys), not for wrong content. The attack requires no special privileges.

### Recommendation

After assembling the full `ThinStateDiff` in `parse_data_for_block`, compute its Poseidon hash with `calculate_state_diff_hash` and compare it against `header.state_diff_commitment`. Reject with `BadPeerError` if they differ. Additionally, verify the block signature cryptographically in the header sync path using `verify_block_signature` so that the `state_diff_commitment` embedded in the header is itself trustworthy.

### Proof of Concept

1. Run a node with p2p sync enabled.
2. Inject a malicious peer that responds to `StateDiff` queries with a `ContractDiff` chunk whose `storage_diffs` contain a fabricated key/value pair (e.g., `key=0x1 → value=0xdeadbeef`) while keeping the total `len()` equal to the `state_diff_length` in the header it previously sent.
3. Call `starknet_getStateUpdate` for that block number.
4. Assert the response contains `storage_diffs` with `value=0xdeadbeef` — confirming the wrong value is returned as authoritative.

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

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L510-526)
```rust
        // Get the block state diff.
        let mut thin_state_diff = txn
            .get_state_diff(block_number)
            .map_err(internal_server_error)?
            .ok_or_else(|| ErrorObjectOwned::from(BLOCK_NOT_FOUND))?;
        // Remove empty storage diffs. Some blocks contain empty storage diffs that must be kept for
        // the computation of state diff commitment.
        thin_state_diff.storage_diffs.retain(|_k, v| !v.is_empty());

        let state_diff =
            self.convert_thin_state_diff(thin_state_diff, block_id, block_number).await?;
        Ok(StateUpdate::AcceptedStateUpdate(AcceptedStateUpdate {
            block_hash: header.block_hash,
            new_root: header.new_root,
            old_root,
            state_diff,
        }))
```
