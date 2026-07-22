### Title
Missing `parent_hash` Continuity Check in P2P Header Sync Allows Unauthenticated Chain Linkage Corruption — (`crates/apollo_p2p_sync/src/client/header.rs`)

---

### Summary

`HeaderStreamBuilder::parse_data_for_block` accepts a `SignedBlockHeader` from any unauthenticated p2p peer and writes it to storage without verifying that `parent_hash` equals the stored `block_hash` of block N-1. The missing check is explicitly acknowledged by a TODO comment in the code. The corrupted `parent_hash` is persisted verbatim and subsequently served by RPC endpoints as an authoritative value.

---

### Finding Description

In `parse_data_for_block`, the only field-level validations performed on a received `SignedBlockHeader` are:

1. `block_number` matches the expected sequence number.
2. `signatures.len() == ALLOWED_SIGNATURES_LENGTH` (exactly 1). [1](#0-0) 

The `_storage_reader` parameter is explicitly unused (underscore-prefixed), confirming no storage lookup is performed to cross-check `parent_hash` against the previously stored block's hash. The TODO at line 102 explicitly names this gap:

```
// TODO(shahak): Check that parent_hash is the same as the previous block's hash
// and handle reverts.
```

The `BlockSignature` is also not cryptographically verified against `block_hash` in this path — `verify_block_signature` exists in `starknet_api::block` but is never called here. [2](#0-1) 

After `parse_data_for_block` returns `Ok(Some(signed_block_header))`, `write_to_storage` calls `append_header` unconditionally with the peer-supplied header: [3](#0-2) 

`append_header` stores `block_header.block_header_without_hash.parent_hash` directly into the `StorageBlockHeader` without any cross-check: [4](#0-3) 

The stored `parent_hash` is then read back verbatim by `get_block_header` and returned to callers including RPC handlers: [5](#0-4) 

---

### Impact Explanation

A node syncing via p2p will store an attacker-chosen `parent_hash` for any block. This corrupts:

- **RPC responses**: `starknet_getBlockWithTxHashes` and related methods return the attacker-controlled `parent_hash` as an authoritative value — a concrete instance of "RPC returns an authoritative-looking wrong value" (High impact per scope rules).
- **Chain linkage**: The stored chain is no longer a valid linked list; any downstream consumer relying on `parent_hash` to traverse or verify the chain (e.g., block hash verification, reorg detection) operates on corrupted data.
- **P2P re-propagation**: The p2p server (`FetchBlockData for SignedBlockHeader`) reads headers from storage and re-serves them to other peers, propagating the corrupted `parent_hash` further. [6](#0-5) 

---

### Likelihood Explanation

The attacker only needs to be a peer that the syncing node connects to — no credentials, keys, or operator access required. The p2p sync protocol is designed to accept connections from arbitrary peers. The attack is deterministic: send a well-formed `SignedBlockHeader` with the correct `block_number` and exactly one signature entry (any bytes), with an arbitrary `parent_hash`. The node will accept and persist it.

---

### Recommendation

In `parse_data_for_block`, before returning `Ok(Some(...))`:

1. Read the stored `block_hash` of block `block_number - 1` from `storage_reader`.
2. Compare it against `signed_block_header.block_header.block_header_without_hash.parent_hash`.
3. Return `ParseDataError::BadPeer(...)` on mismatch (and report the peer).

The `_storage_reader` parameter is already threaded into the function signature — it just needs to be used (remove the underscore prefix and add the lookup). The TODO comment at line 102 already describes exactly this fix. [7](#0-6) 

Additionally, cryptographic signature verification (`verify_block_signature`) should be applied to the received `block_hash` and `state_diff_commitment` before storage.

---

### Proof of Concept

```
1. Node A starts p2p sync from block 0.
2. Attacker peer sends block 0 header with block_hash = H0 (legitimate).
3. Attacker peer sends block 1 header with:
     block_number = 1
     parent_hash  = 0xdeadbeef  (arbitrary, != H0)
     signatures   = [any 64-byte pair]
4. parse_data_for_block accepts it (block_number check passes, signatures.len() == 1).
5. write_to_storage persists parent_hash = 0xdeadbeef for block 1.
6. starknet_getBlockWithTxHashes(block_number=1) returns parent_hash = 0xdeadbeef.
7. Any block hash verifier or chain traversal using stored parent_hash is now operating on corrupted data.
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

**File:** crates/apollo_p2p_sync/src/client/header.rs (L82-88)
```rust
    fn parse_data_for_block<'a>(
        signed_headers_response_manager: &'a mut ClientResponsesManager<
            DataOrFin<SignedBlockHeader>,
        >,
        block_number: BlockNumber,
        _storage_reader: &'a StorageReader,
    ) -> BoxFuture<'a, Result<Option<Self::Output>, ParseDataError>> {
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

**File:** crates/apollo_storage/src/header.rs (L215-219)
```rust
        Ok(Some(BlockHeader {
            block_hash: block_header.block_hash,
            block_header_without_hash: BlockHeaderWithoutHash {
                parent_hash: block_header.parent_hash,
                block_number: block_header.block_number,
```

**File:** crates/apollo_storage/src/header.rs (L308-331)
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
```

**File:** crates/apollo_p2p_sync/src/server/mod.rs (L219-243)
```rust
impl FetchBlockData for SignedBlockHeader {
    async fn fetch_block_data(
        block_number: BlockNumber,
        txn: &StorageTxn<'_, db::RO>,
        _class_manager_client: &mut SharedClassManagerClient,
    ) -> Result<Vec<Self>, P2pSyncServerError> {
        let mut header =
            txn.get_block_header(block_number)?.ok_or(P2pSyncServerError::BlockNotFound {
                block_hash_or_number: BlockHashOrNumber::Number(block_number),
            })?;
        // TODO(shahak): Remove this once central sync fills the state_diff_length field.
        if header.state_diff_length.is_none() {
            header.state_diff_length = Some(
                txn.get_state_diff(block_number)?
                    .ok_or(P2pSyncServerError::BlockNotFound {
                        block_hash_or_number: BlockHashOrNumber::Number(block_number),
                    })?
                    .len(),
            );
        }
        let signature = txn
            .get_block_signature(block_number)?
            .ok_or(P2pSyncServerError::SignatureNotFound { block_number })?;
        Ok(vec![SignedBlockHeader { block_header: header, signatures: vec![signature] }])
    }
```
