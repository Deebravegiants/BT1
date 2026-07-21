The two grep searches confirm zero occurrences of `verify_block_signature`, `calculate_block_hash`, or any state-root verification anywhere inside `crates/apollo_p2p_sync/`. The vulnerability is real.

---

### Title
Unauthenticated P2P Peer Can Inject Arbitrary `state_root` into Stored Block Header — (`crates/apollo_p2p_sync/src/client/header.rs`)

### Summary
`HeaderStreamBuilder::parse_data_for_block` accepts a `SignedBlockHeader` from any unauthenticated p2p peer and forwards it to `write_to_storage` → `append_header` after performing only two structural checks: block-number ordering and signature-vector length. Neither the `block_hash` field nor the `state_root` field inside `BlockHeaderWithoutHash` is verified against any cryptographic proof or recomputed value. A malicious peer can therefore store an arbitrary `GlobalRoot` as the canonical state root for any block.

### Finding Description

`parse_data_for_block` performs exactly two checks before accepting a `SignedBlockHeader`: [1](#0-0) 

1. The embedded `block_number` matches the expected sequence position.
2. The `signatures` vector has length 1.

No call to `verify_block_signature` (which hashes `(block_hash, state_diff_commitment)` and checks the sequencer ECDSA key) is made anywhere in the p2p sync client: [2](#0-1) 

No call to `calculate_block_hash` is made to recompute the hash from the received fields and compare it to the peer-supplied `block_hash`. The accepted `SignedBlockHeader` is passed directly to `write_to_storage`: [3](#0-2) 

`state_root` lives inside `BlockHeaderWithoutHash`: [4](#0-3) 

and is persisted verbatim into `StorageBlockHeader`: [5](#0-4) 

The RPC layer then reads this field directly from storage and returns it as `new_root` in `starknet_getStateUpdate` responses, as confirmed by the RPC test fixture: [6](#0-5) 

`state_root` is the second element hashed into the block hash (after `block_hash_version` and `block_number`), so a corrupted stored value also means the stored `block_hash` is inconsistent with the actual Patricia trie root: [7](#0-6) 

### Impact Explanation
Any unauthenticated p2p peer can cause the syncing node to permanently store an arbitrary `state_root` (and an arbitrary `block_hash`) for any block. The node then serves these corrupted values as authoritative via RPC (`starknet_getStateUpdate` `new_root`, `starknet_getBlockWithTxHashes` `state_root`, etc.). Downstream consumers — wallets, bridges, provers — that rely on the node's state-root view receive a wrong value with no indication of corruption. This is a concrete High-impact RPC-authority corruption reachable from a zero-privilege network position.

### Likelihood Explanation
Any peer that can establish a p2p connection to the node can trigger this. The only prerequisite is that the node is running in p2p-sync mode (i.e., `internal_block_receiver` is `None` for the header stream, so the network path is taken). No key material, stake, or operator access is required.

### Recommendation
Before calling `write_to_storage`, `parse_data_for_block` must:
1. Recompute `block_hash` from the received header fields using `calculate_block_hash` and assert it equals `signed_block_header.block_header.block_hash`.
2. Verify the ECDSA signature over `(block_hash, state_diff_commitment)` against the known sequencer public key using `verify_block_signature`.

Both checks must pass before the header is yielded for storage. The existing `verify_block_signature` utility already implements step 2: [8](#0-7) 

### Proof of Concept
```
1. Connect a peer to the p2p sync client.
2. Respond to the header query for block N with a SignedBlockHeader where:
     state_root = GlobalRoot(Felt::from(0xfeed_u64))
     block_hash = <any felt>
     block_number = N
     signatures = [<any single BlockSignature>]
3. Observe that parse_data_for_block returns Ok(Some(...)) — no error.
4. Observe that append_header stores the header.
5. Call starknet_getStateUpdate(block_id=N) via RPC.
6. Assert response.new_root == 0xfeed.
7. Independently compute the real block hash using the actual Patricia trie root.
8. Assert stored block_hash != real block hash.
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

**File:** crates/apollo_p2p_sync/src/client/header.rs (L104-119)
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
```

**File:** crates/starknet_api/src/block.rs (L232-248)
```rust
pub struct BlockHeaderWithoutHash {
    pub parent_hash: BlockHash,
    pub block_number: BlockNumber,
    pub l1_gas_price: GasPricePerToken,
    pub l1_data_gas_price: GasPricePerToken,
    pub l2_gas_price: GasPricePerToken,
    pub l2_gas_consumed: GasAmount,
    pub next_l2_gas_price: GasPrice,
    pub state_root: GlobalRoot,
    pub sequencer: SequencerContractAddress,
    pub timestamp: BlockTimestamp,
    pub l1_da_mode: L1DataAvailabilityMode,
    pub starknet_version: StarknetVersion,
    // TODO(AndrewL): Add this field into the block hash.
    /// Proposer's oracle-derived recommended L2 gas fee. `None` for pre-V0_14_3 blocks.
    pub fee_proposal_fri: Option<GasPrice>,
}
```

**File:** crates/starknet_api/src/block.rs (L721-734)
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
```

**File:** crates/apollo_storage/src/header.rs (L91-91)
```rust
    pub state_root: GlobalRoot,
```

**File:** crates/apollo_rpc/src/v0_8/api/test.rs (L2734-2734)
```rust
        new_root: header.block_header_without_hash.state_root,
```

**File:** crates/apollo_starknet_os_program/src/cairo/starkware/starknet/core/os/block_hash.cairo (L32-34)
```text
        hash_update_single(BLOCK_HASH_VERSION);
        hash_update_single(block_info.block_number);
        hash_update_single(state_root);
```
