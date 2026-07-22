Let me check how the transaction commitment in the header is populated during sync (to verify whether stored hashes feed back into commitment calculation).

### Title
P2P Sync Client Accepts Peer-Supplied `transaction_hash` Without Validation, Corrupting Stored Transaction Hash Index and RPC Responses — (`crates/apollo_p2p_sync/src/client/transaction.rs`)

---

### Summary

In `TransactionStreamFactory::parse_data_for_block`, the `transaction_hash` field of a peer-supplied `FullTransaction` is pushed directly into `block_body.transaction_hashes` without verifying it matches the hash of the embedded `Transaction`. A TODO comment explicitly acknowledges this gap. The wrong hash is then persisted to storage via `append_body` → `write_transactions`, corrupting the `transaction_hash_to_idx` index and `TransactionMetadata.tx_hash` for every affected transaction. This causes RPC endpoints to serve authoritative-looking wrong transaction hashes and makes correct-hash lookups return NOT_FOUND.

---

### Finding Description

**Vulnerable code path:**

`parse_data_for_block` in `crates/apollo_p2p_sync/src/client/transaction.rs`:

```rust
let Some(FullTransaction { transaction, transaction_output, transaction_hash }) =
    maybe_transaction?.0
// ...
block_body.transactions.push(transaction);
block_body.transaction_outputs.push(transaction_output);
// TODO(eitan): Validate transaction hash from untrusted sources
block_body.transaction_hashes.push(transaction_hash);  // ← peer-controlled value, unvalidated
``` [1](#0-0) 

The `FullTransaction` struct carries `transaction`, `transaction_output`, and `transaction_hash` as independent fields. The protobuf conversion in `crates/apollo_protobuf/src/converters/transaction.rs` reads `transaction_hash` directly from the wire field without computing it from the transaction body: [2](#0-1) 

The resulting `BlockBody` is written to storage via `write_to_storage` → `append_body` → `write_transactions`:

```rust
transaction_hash_to_idx_table.insert(txn, tx_hash, &transaction_index)?;
transaction_metadata_table.append(
    txn, &transaction_index,
    &TransactionMetadata { tx_location, tx_output_location, tx_hash: *tx_hash },
)?;
``` [3](#0-2) 

The peer-controlled `tx_hash` is stored in both the hash→index lookup table and the per-transaction metadata. No validation occurs anywhere in this path.

---

### Impact Explanation

**What is corrupted:** The `transaction_hash_to_idx` table and `TransactionMetadata.tx_hash` for every transaction in any block synced from a malicious peer.

**What is NOT corrupted:** The block's `transaction_commitment` stored in the block header. The header is synced independently via `HeaderStreamBuilder`, which stores the peer-supplied `transaction_commitment` directly from the signed header. The syncing node does not recompute `transaction_commitment` from the stored body transaction hashes — `calculate_block_commitments` is a sequencer/batcher-side function, not called during p2p body sync. Therefore the specific claim of "block commitment corruption" in the question is incorrect.

**Actual RPC impact (High):**

- `get_transaction_by_hash(correct_hash)` → `TRANSACTION_HASH_NOT_FOUND` (the correct hash is not in the index)
- `get_transaction_by_hash(wrong_hash)` → returns the transaction body (wrong hash is indexed)
- `get_transaction_by_block_id_and_index` → returns `TransactionWithHash` with the wrong hash
- `get_block_w_full_transactions` → returns all transactions with wrong hashes
- `get_transaction_receipt(correct_hash)` → `TRANSACTION_HASH_NOT_FOUND` [4](#0-3) [5](#0-4) 

---

### Likelihood Explanation

- The p2p sync client is production code, active whenever a node syncs via p2p.
- Any peer that can respond to a `TransactionQuery` can inject arbitrary `transaction_hash` values — no authentication or privilege is required.
- The TODO comment confirms the developers are aware the validation is missing and have not yet implemented it.
- The `BadPeer` error path (line 181 of `block_data_stream_builder.rs`) only triggers on structural errors (wrong count, session ended early), not on hash mismatch — so the peer is not disconnected. [6](#0-5) 

---

### Recommendation

In `parse_data_for_block`, after destructuring the `FullTransaction`, compute the canonical hash of `transaction` using the chain-id-aware hash function and compare it to the peer-supplied `transaction_hash`. If they differ, return `ParseDataError::BadPeer` and report the peer. The fix belongs at line 88 of `crates/apollo_p2p_sync/src/client/transaction.rs`, replacing the TODO comment.

---

### Proof of Concept

1. Stand up a p2p sync client node with an empty database.
2. Act as a p2p server peer responding to `TransactionQuery` for block 0.
3. Construct a valid `InvokeTransactionV1` body. Compute its real hash `H_real`. Choose an arbitrary wrong hash `H_fake ≠ H_real`.
4. Send a `FullTransaction { transaction: invoke_v1_body, transaction_output: default_output, transaction_hash: H_fake }` followed by a `DataOrFin(None)` fin marker.
5. Wait for the body marker to advance past block 0.
6. Read storage: `get_block_transaction_hashes(BlockNumber(0))` returns `[H_fake]`.
7. Assert `get_transaction_idx_by_hash(H_real)` returns `None`.
8. Assert `get_transaction_idx_by_hash(H_fake)` returns `Some(TransactionIndex(BlockNumber(0), TransactionOffsetInBlock(0)))`.

This deterministically demonstrates that the wrong hash is persisted and the correct hash is unreachable via the index.

### Citations

**File:** crates/apollo_p2p_sync/src/client/transaction.rs (L73-90)
```rust
                let Some(FullTransaction { transaction, transaction_output, transaction_hash }) =
                    maybe_transaction?.0
                else {
                    if current_transaction_len == 0 {
                        return Ok(None);
                    } else {
                        return Err(ParseDataError::BadPeer(BadPeerError::NotEnoughTransactions {
                            expected: target_transaction_len,
                            actual: current_transaction_len,
                            block_number: block_number.0,
                        }));
                    }
                };
                block_body.transactions.push(transaction);
                block_body.transaction_outputs.push(transaction_output);
                // TODO(eitan): Validate transaction hash from untrusted sources
                block_body.transaction_hashes.push(transaction_hash);
                current_transaction_len += 1;
```

**File:** crates/apollo_protobuf/src/converters/transaction.rs (L109-121)
```rust
impl TryFrom<protobuf::TransactionWithReceipt> for FullTransaction {
    type Error = ProtobufConversionError;
    fn try_from(value: protobuf::TransactionWithReceipt) -> Result<Self, Self::Error> {
        let (transaction, transaction_hash) = <(Transaction, TransactionHash)>::try_from(
            value.transaction.ok_or(missing("TransactionWithReceipt::transaction"))?,
        )?;

        let transaction_output = TransactionOutput::try_from(
            value.receipt.ok_or(missing("TransactionWithReceipt::output"))?,
        )?;
        Ok(FullTransaction { transaction, transaction_output, transaction_hash })
    }
}
```

**File:** crates/apollo_storage/src/body/mod.rs (L619-627)
```rust
        let tx_location = file_handlers.append_transaction(tx);
        let tx_output_location = file_handlers.append_transaction_output(tx_output);
        write_events(tx_output, txn, events_table, transaction_index)?;
        transaction_hash_to_idx_table.insert(txn, tx_hash, &transaction_index)?;
        transaction_metadata_table.append(
            txn,
            &transaction_index,
            &TransactionMetadata { tx_location, tx_output_location, tx_hash: *tx_hash },
        )?;
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L386-403)
```rust
    #[instrument(skip(self), level = "debug", err, ret)]
    async fn get_transaction_by_hash(
        &self,
        transaction_hash: TransactionHash,
    ) -> RpcResult<TransactionWithHash> {
        verify_storage_scope(&self.storage_reader)?;

        let txn = self.storage_reader.begin_ro_txn().map_err(internal_server_error)?;

        if let Some(transaction_index) =
            txn.get_transaction_idx_by_hash(&transaction_hash).map_err(internal_server_error)?
        {
            let transaction = txn
                .get_transaction(transaction_index)
                .map_err(internal_server_error)?
                .ok_or_else(|| ErrorObjectOwned::from(TRANSACTION_HASH_NOT_FOUND))?;

            Ok(TransactionWithHash { transaction: transaction.try_into()?, transaction_hash })
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L446-463)
```rust
                let block_number = get_accepted_block_number(&txn, block_id)?;

                let tx_index = TransactionIndex(block_number, index);
                let transaction = txn
                    .get_transaction(tx_index)
                    .map_err(internal_server_error)?
                    .ok_or_else(|| ErrorObjectOwned::from(INVALID_TRANSACTION_INDEX))?;
                let transaction_hash = txn
                    .get_transaction_hash_by_idx(&tx_index)
                    .map_err(internal_server_error)?
                    .ok_or_else(|| ErrorObjectOwned::from(INVALID_TRANSACTION_INDEX))?;
                (transaction, transaction_hash)
            };

        Ok(TransactionWithHash {
            transaction: starknet_api_transaction.try_into()?,
            transaction_hash,
        })
```

**File:** crates/apollo_p2p_sync/src/client/block_data_stream_builder.rs (L181-189)
```rust
                                Err(ParseDataError::BadPeer(err)) => {
                                    warn!(
                                        "Query for {:?} on {:?} returned with bad peer error: {:?}. reporting \
                                         peer and retrying query.",
                                        Self::TYPE_DESCRIPTION, current_block_number, err
                                    );
                                    client_response_manager.report_peer();
                                    continue 'send_query_and_parse_responses;
                                },
```
