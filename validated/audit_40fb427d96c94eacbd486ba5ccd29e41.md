### Title
Missing `state_diff_commitment` Hash Verification in P2P Sync Allows Malicious Peer to Corrupt Stored State Diffs — (`crates/apollo_p2p_sync/src/client/state_diff.rs`)

---

### Summary

`parse_data_for_block` in `StateDiffStreamBuilder` validates only the *length* of received state diff chunks against `header.state_diff_length`, but never computes `calculate_state_diff_hash` on the assembled `ThinStateDiff` and compares it against the `state_diff_commitment` already stored in the block header. Any unauthenticated p2p peer can therefore supply length-correct but content-wrong `StateDiffChunk` messages that pass all existing checks and are committed verbatim to the `state_diffs_table` storage column.

---

### Finding Description

`parse_data_for_block` reads `target_state_diff_len` from the stored header: [1](#0-0) 

It then loops, accumulating chunks until `current_state_diff_len == target_state_diff_len`: [2](#0-1) 

After the loop, the only additional check is for duplicate deprecated declared classes: [3](#0-2) 

The assembled `ThinStateDiff` is then written directly to storage: [4](#0-3) 

The block header **does** carry a `state_diff_commitment` field (populated during header sync): [5](#0-4) 

`calculate_state_diff_hash` exists and is used elsewhere (e.g., in the committer and block hash calculator): [6](#0-5) 

But it is **never called** inside `parse_data_for_block`. A peer that sends `N` length-units of `ContractDiff` chunks with arbitrary storage values satisfies the only guard (`current_state_diff_len == target_state_diff_len`) and causes the wrong diff to be committed.

---

### Impact Explanation

The corrupted `ThinStateDiff` is stored in the `state_diffs_table` column and served by `starknet_getStateUpdate`. Any client querying that RPC endpoint receives an authoritative-looking but incorrect state update — wrong storage values, wrong nonces, wrong deployed contracts — for the affected block. This falls under **High: RPC returns an authoritative-looking wrong value**.

---

### Likelihood Explanation

The attack requires only that the victim node connects to a malicious p2p peer during state diff sync (i.e., while `state_marker < header_marker`). P2P peers are unauthenticated. The attacker needs to know the correct `state_diff_length` for the target block (publicly available) and send that many length-units of crafted chunks. No privileged access is required.

---

### Recommendation

After the loop in `parse_data_for_block`, read `header.state_diff_commitment` from storage and assert:

```rust
let expected_commitment = storage_reader
    .begin_ro_txn()?
    .get_block_header(block_number)?
    .expect("...")
    .state_diff_commitment
    .ok_or(P2pSyncClientError::OldHeaderInStorage { ... })?;

let actual_commitment = calculate_state_diff_hash(&result);
if actual_commitment != expected_commitment {
    return Err(ParseDataError::BadPeer(BadPeerError::InvalidStateDiffHash { ... }));
}
```

This mirrors the pattern already used in `apollo_committer`: [7](#0-6) 

---

### Proof of Concept

Using the existing `run_test`/`Action` harness in `crates/apollo_p2p_sync/src/client/test.rs`:

1. Inject a `SignedBlockHeader` for block 0 with `state_diff_length = 1` and `state_diff_commitment = calculate_state_diff_hash(&correct_diff)`.
2. Send one `ContractDiff` chunk of length 1 with a **different** storage value (wrong content, correct length).
3. Send `Fin`.
4. Assert the state diff is committed (no error returned).
5. Read back the stored diff and assert `calculate_state_diff_hash(&stored_diff) != expected_commitment`.

Steps 4 and 5 both succeed with the current code, confirming the missing validation.

### Citations

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

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L72-104)
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

            if current_state_diff_len != target_state_diff_len {
                return Err(ParseDataError::BadPeer(BadPeerError::WrongStateDiffLength {
                    expected_length: target_state_diff_len,
                    possible_lengths: vec![prev_result_len, current_state_diff_len],
                }));
            }
```

**File:** crates/apollo_p2p_sync/src/client/state_diff.rs (L106-107)
```rust
            validate_deprecated_declared_classes_non_conflicting(&result)?;
            Ok(Some((result, block_number)))
```

**File:** crates/apollo_p2p_sync/src/client/header.rs (L146-147)
```rust
                state_diff_commitment: Some(header_commitments.state_diff_commitment),
                state_diff_length: Some(sync_block.state_diff.len()),
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

**File:** crates/apollo_committer/src/committer.rs (L267-275)
```rust
                if self.config.verify_state_diff_hash {
                    let calculated_commitment = calculate_state_diff_hash(state_diff);
                    if commitment != calculated_commitment {
                        return Err(CommitterError::StateDiffHashMismatch {
                            provided_commitment: commitment,
                            calculated_commitment,
                            height,
                        });
                    }
```
