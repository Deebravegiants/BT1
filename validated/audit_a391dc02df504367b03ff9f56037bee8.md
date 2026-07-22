### Title
Unauthenticated SQMR Peer Can Inject Arbitrary `TransactionHash` Bound to Any Transaction Body During Sync — (`crates/apollo_p2p_sync/src/client/transaction.rs`)

---

### Summary

The `TryFrom<protobuf::TransactionInBlock> for (Transaction, TransactionHash)` converter blindly trusts the `transaction_hash` field from the wire without recomputing it from the deserialized `Transaction` body. The p2p sync client's `parse_data_for_block` then stores this unverified hash directly into the node's `BlockBody`. An unauthenticated SQMR peer can therefore bind any arbitrary `TransactionHash` to any transaction body, permanently corrupting the node's stored transaction-hash mapping.

---

### Finding Description

In `converters/transaction.rs` lines 137–142, `tx_hash` is extracted directly from the protobuf field:

```rust
let tx_hash = value
    .transaction_hash
    .clone()
    .ok_or(missing("Transaction::transaction_hash"))?
    .try_into()
    .map(TransactionHash)?;
``` [1](#0-0) 

No recomputation from the deserialized `Transaction` fields is performed. The resulting `(Transaction, TransactionHash)` pair is returned with whatever hash the peer supplied.

In `parse_data_for_block`, the `FullTransaction` is destructured and the hash is pushed directly to `block_body.transaction_hashes`. The developer-acknowledged TODO confirms no validation occurs:

```rust
// TODO(eitan): Validate transaction hash from untrusted sources
block_body.transaction_hashes.push(transaction_hash);
``` [2](#0-1) 

The `BlockBody` is then committed to storage unconditionally:

```rust
storage_writer.begin_rw_txn()?.append_body(self.1, self.0)?.commit()?;
``` [3](#0-2) 

---

### Impact Explanation

Once the corrupted `BlockBody` is in storage, `apollo_state_sync`'s `get_block` reads `block_transactions_with_hash` from storage and propagates the attacker-controlled hashes into `SyncBlock.account_transaction_hashes` / `l1_transaction_hashes`:

```rust
for (tx, tx_hash) in block_transactions_with_hash {
    match tx {
        Transaction::L1Handler(_) => l1_transaction_hashes.push(tx_hash),
        _ => account_transaction_hashes.push(tx_hash),
    }
}
``` [4](#0-3) 

These hashes feed into `calculate_block_commitments` as `TransactionHashingData.transaction_hash`, which is used to compute `transaction_commitment`, `event_commitment` (events are keyed by `transaction_hash`), and `receipt_commitment`: [5](#0-4) 

A peer-injected hash therefore corrupts:
- The node's authoritative RPC view of every affected transaction (wrong hash ↔ wrong body mapping).
- Any downstream block commitment recomputation that reads stored transaction hashes.

This squarely matches the allowed High impact: **"Transaction conversion or signature/hash logic binds the wrong signer, hash, type, or executable payload."**

---

### Likelihood Explanation

- **Precondition**: the node is syncing any block via SQMR — the normal operating state of any non-genesis full node.
- **Attacker privilege**: none. Any peer that can respond to a `TransactionQuery` SQMR session can supply the malformed message.
- **No existing guard**: the TODO comment is the only acknowledgment; there is zero runtime check.
- **Persistence**: the corrupted hash is written to durable storage and never re-validated.

---

### Recommendation

After deserializing the `Transaction` from the protobuf body, recompute the canonical hash using the chain-id-aware hasher and reject (disconnect peer / return `BadPeerError`) if it does not match `value.transaction_hash`. This should replace the `// TODO(eitan): Validate transaction hash from untrusted sources` placeholder at `client/transaction.rs:88`.

---

### Proof of Concept

```rust
// Construct a valid InvokeV1 body but supply a completely different hash.
let real_tx = build_invoke_v1_protobuf(/* ... */);
let fake_hash = protobuf::Felt252 { elements: vec![0xde, 0xad, /* ... */] };

let tampered = protobuf::TransactionInBlock {
    txn: Some(protobuf::transaction_in_block::Txn::InvokeV1(real_tx)),
    transaction_hash: Some(fake_hash.clone()),
};

let (tx, stored_hash) =
    <(Transaction, TransactionHash)>::try_from(tampered).unwrap();

// Recompute the canonical hash from the deserialized transaction body.
let canonical_hash = compute_transaction_hash(&tx, &chain_id);

// This assertion FAILS — stored_hash == fake_hash != canonical_hash.
assert_eq!(stored_hash, canonical_hash,
    "Peer-supplied hash accepted without verification");
```

The node will persist `fake_hash` in `BlockBody.transaction_hashes`, causing all subsequent RPC lookups and block-commitment calculations that read from storage to operate on the attacker-chosen value.

### Citations

**File:** crates/apollo_protobuf/src/converters/transaction.rs (L134-143)
```rust
impl TryFrom<protobuf::TransactionInBlock> for (Transaction, TransactionHash) {
    type Error = ProtobufConversionError;
    fn try_from(value: protobuf::TransactionInBlock) -> Result<Self, Self::Error> {
        let tx_hash = value
            .transaction_hash
            .clone()
            .ok_or(missing("Transaction::transaction_hash"))?
            .try_into()
            .map(TransactionHash)?;
        let txn = value.txn.ok_or(missing("Transaction::txn"))?;
```

**File:** crates/apollo_p2p_sync/src/client/transaction.rs (L36-36)
```rust
            storage_writer.begin_rw_txn()?.append_body(self.1, self.0)?.commit()?;
```

**File:** crates/apollo_p2p_sync/src/client/transaction.rs (L86-90)
```rust
                block_body.transactions.push(transaction);
                block_body.transaction_outputs.push(transaction_output);
                // TODO(eitan): Validate transaction hash from untrusted sources
                block_body.transaction_hashes.push(transaction_hash);
                current_transaction_len += 1;
```

**File:** crates/apollo_state_sync/src/lib.rs (L195-200)
```rust
        for (tx, tx_hash) in block_transactions_with_hash {
            match tx {
                Transaction::L1Handler(_) => l1_transaction_hashes.push(tx_hash),
                _ => account_transaction_hashes.push(tx_hash),
            }
        }
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L284-316)
```rust
/// Calculates the commitments of the transactions data for the block hash.
pub async fn calculate_block_commitments(
    transactions_data: &[TransactionHashingData],
    state_diff: ThinStateDiff,
    l1_da_mode: L1DataAvailabilityMode,
    starknet_version: &StarknetVersion,
) -> (BlockHeaderCommitments, BlockCommitmentsMeasurements) {
    let transaction_leaf_elements: Vec<TransactionLeafElement> = transactions_data
        .iter()
        .map(|tx_leaf| {
            let mut tx_leaf_element = TransactionLeafElement::from(tx_leaf);
            if starknet_version < &BlockHashVersion::V0_13_4.into()
                && tx_leaf.transaction_signature.0.is_empty()
            {
                tx_leaf_element.transaction_signature =
                    TransactionSignature(vec![Felt::ZERO].into());
            }
            tx_leaf_element
        })
        .collect();

    let event_leaf_elements: Vec<EventLeafElement> = transactions_data
        .iter()
        .flat_map(|transaction_data| {
            transaction_data.transaction_output.events.iter().map(|event| EventLeafElement {
                event: event.clone(),
                transaction_hash: transaction_data.transaction_hash,
            })
        })
        .collect();

    let receipt_elements: Vec<ReceiptElement> =
        transactions_data.iter().map(ReceiptElement::from).collect();
```
