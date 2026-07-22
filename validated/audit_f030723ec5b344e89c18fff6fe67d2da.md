### Title
P2P Sync Stores Peer-Supplied `block_hash` Verbatim Without Verification, Corrupting `block_hash_to_number` Mapping and RPC Responses — (`crates/apollo_p2p_sync/src/client/header.rs`)

---

### Summary

The p2p sync client accepts a `SignedBlockHeader` from any unauthenticated peer and writes the peer-supplied `block_hash` directly to storage without recomputing it from the header fields or cryptographically verifying the block signature. This corrupts the `block_hash_to_number` index, causing `starknet_getBlockByHash` to return authoritative-looking wrong values.

---

### Finding Description

**Entrypoint — `parse_data_for_block`**

`HeaderStreamBuilder::parse_data_for_block` in `crates/apollo_p2p_sync/src/client/header.rs` performs only two checks on the incoming `SignedBlockHeader`:

1. Block number ordering (lines 104–113)
2. Signature vector length equals `ALLOWED_SIGNATURES_LENGTH` (lines 115–118) [1](#0-0) 

There is no cryptographic verification of the signature against the `block_hash`, and no recomputation of `block_hash` from the header fields. The `verify_block_signature` function that exists in `starknet_api/src/block.rs` (lines 722–734) is never called in this path. [2](#0-1) 

**Storage write — `write_to_storage`**

`SignedBlockHeader::write_to_storage` passes `&self.block_header` (including the peer-supplied `block_hash`) directly to `append_header`: [3](#0-2) 

**Verbatim storage — `append_header`**

`HeaderStorageWriter::append_header` constructs a `StorageBlockHeader` using `block_header.block_hash` verbatim (line 309) and then calls `update_hash_mapping`, which inserts the peer-supplied hash into the `block_hash_to_number` table: [4](#0-3) 

**No parent-hash check either**

The code even has an explicit TODO acknowledging the missing parent-hash consistency check: [5](#0-4) 

---

### Impact Explanation

After a malicious peer injects a `SignedBlockHeader` for block N with `block_hash = X` (where X ≠ correct hash H):

- `block_hash_to_number[X] = N` is stored; `H` is never indexed.
- `starknet_getBlockByHash(H)` → "not found" (authoritative-looking wrong value).
- `starknet_getBlockByHash(X)` → returns block N (wrong hash, correct data).
- Because the p2p sync also lacks a parent-hash check, the attacker can chain further blocks with `parent_hash = X`, propagating the corruption across the entire synced chain segment.

This matches the allowed impact: **High — RPC returns an authoritative-looking wrong value**.

---

### Likelihood Explanation

Any node that can establish a p2p connection to the victim (unauthenticated, public network) can send a crafted `SignedBlockHeader`. The only guards are block-number ordering and signature-vector length — both trivially satisfied. No cryptographic material controlled by a privileged party is required.

---

### Recommendation

1. **Recompute and verify `block_hash`** inside `parse_data_for_block` (or `write_to_storage`) using `calculate_block_hash` over the received header fields before accepting the message.
2. **Cryptographically verify the block signature** using `verify_block_signature` against the known sequencer public key before storing.
3. **Implement the parent-hash consistency check** noted in the existing TODO comment.

---

### Proof of Concept

```rust
// In an integration test, inject a SignedBlockHeader via the mock p2p channel
// with block_number=0 but block_hash set to an arbitrary wrong value.
mock_header_responses_manager
    .send_response(DataOrFin(Some(SignedBlockHeader {
        block_header: BlockHeader {
            block_hash: BlockHash(felt!("0xdeadbeef")), // wrong hash
            block_header_without_hash: BlockHeaderWithoutHash {
                block_number: BlockNumber(0),
                ..Default::default()
            },
            state_diff_length: Some(0),
            ..Default::default()
        },
        signatures: vec![BlockSignature::default()], // length=1, not verified
    })))
    .await
    .unwrap();

// After sync advances:
let txn = storage_reader.begin_ro_txn().unwrap();
// Correct hash is NOT found:
assert_eq!(txn.get_block_number_by_hash(&correct_hash).unwrap(), None);
// Wrong hash IS found:
assert_eq!(
    txn.get_block_number_by_hash(&BlockHash(felt!("0xdeadbeef"))).unwrap(),
    Some(BlockNumber(0))
);
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

**File:** crates/apollo_p2p_sync/src/client/header.rs (L102-120)
```rust
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
```

**File:** crates/starknet_api/src/block.rs (L722-734)
```rust
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

**File:** crates/apollo_storage/src/header.rs (L308-338)
```rust
        let storage_block_header = StorageBlockHeader {
            block_hash: block_header.block_hash,
            parent_hash: block_header.block_header_without_hash.parent_hash,
            block_number: block_header.block_header_without_hash.block_number,
            l1_gas_price: block_header.block_header_without_hash.l1_gas_price,
            l1_data_gas_price: block_header.block_header_without_hash.l1_data_gas_price,
            l2_gas_price: block_header.block_header_without_hash.l2_gas_price,
            l2_gas_consumed: block_header.block_header_without_hash.l2_gas_consumed,
            next_l2_gas_price: block_header.block_header_without_hash.next_l2_gas_price,
            state_root: block_header.block_header_without_hash.state_root,
            sequencer: block_header.block_header_without_hash.sequencer,
            timestamp: block_header.block_header_without_hash.timestamp,
            l1_da_mode: block_header.block_header_without_hash.l1_da_mode,
            state_diff_commitment: block_header.state_diff_commitment,
            transaction_commitment: block_header.transaction_commitment,
            event_commitment: block_header.event_commitment,
            receipt_commitment: block_header.receipt_commitment,
            state_diff_length: block_header.state_diff_length,
            n_transactions: block_header.n_transactions,
            n_events: block_header.n_events,
            fee_proposal_fri: block_header.block_header_without_hash.fee_proposal_fri,
        };

        headers_table.append(self.txn(), &block_number, &storage_block_header)?;

        update_hash_mapping(
            self.txn(),
            &block_hash_to_number_table,
            &storage_block_header,
            block_number,
        )?;
```
