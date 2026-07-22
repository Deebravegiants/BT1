### Title
Missing `event_commitment` Validation in P2P Sync Allows Fabricated Events to Corrupt Stored Block Body and Poison RPC Event Responses — (`crates/apollo_p2p_sync/src/client/transaction.rs`)

---

### Summary

`TransactionStreamFactory::parse_data_for_block` accepts `TransactionOutput` objects (including their `events` fields) from an unauthenticated SQMR peer and writes them directly to storage with no verification against the `event_commitment` stored in the block header. A malicious peer can inject arbitrary fabricated events into a syncing node's persistent storage, causing every downstream RPC call that reads those events (`starknet_getEvents`, `starknet_getTransactionReceipt`) to return authoritative-looking wrong values.

---

### Finding Description

`parse_data_for_block` loops over peer-supplied `FullTransaction` messages and pushes each `transaction_output` (which carries the `events` vec) straight into `block_body.transaction_outputs`:

```rust
block_body.transaction_outputs.push(transaction_output);
``` [1](#0-0) 

The only guard applied is a count check against `header.n_transactions`:

```rust
while current_transaction_len < target_transaction_len { … }
``` [2](#0-1) 

There is no step that recomputes `calculate_event_commitment` over the received outputs and compares it to `header.event_commitment`. The developers themselves flag the analogous hash gap with a TODO:

```rust
// TODO(eitan): Validate transaction hash from untrusted sources
block_body.transaction_hashes.push(transaction_hash);
``` [3](#0-2) 

`write_to_storage` then calls `append_body`, which writes every event from every `TransactionOutput` into the persistent events table and the transaction-output file store with no further checks: [4](#0-3) [5](#0-4) 

`calculate_block_commitments` — the function that would recompute `event_commitment` from `TransactionHashingData.transaction_output.events` — is only invoked in the batcher/block-builder path, never in the P2P sync client path: [6](#0-5) 

The header (with the authoritative `event_commitment`) is stored separately by `HeaderStreamBuilder` before the body arrives. There is no cross-check between the two at any point in the sync pipeline. [7](#0-6) 

---

### Impact Explanation

After a malicious peer delivers fabricated `TransactionOutput::Invoke` messages with synthetic events:

1. The events are written verbatim to the node's persistent storage via `write_events` / `append_transaction_output`.
2. `get_transaction_output` and `get_block_transaction_outputs` read them back without any integrity check.
3. Every RPC handler that calls these storage accessors — `starknet_getEvents`, `starknet_getTransactionReceipt`, `starknet_simulateTransactions` (pending-state event replay) — returns the fabricated events as authoritative chain data.
4. The stored body is permanently inconsistent with `header.event_commitment`; any later attempt to verify block integrity by recomputing commitments from stored outputs will produce a diverging value.

This maps directly to the allowed High impact: **"RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value."**

---

### Likelihood Explanation

The attacker needs only to be a reachable P2P peer — no authentication, no stake, no operator privilege. The SQMR protocol is open to any peer the node connects to. The node will accept the fabricated body as long as the transaction count matches `header.n_transactions`, which the attacker can satisfy trivially by sending the correct number of `FullTransaction` messages with arbitrary event payloads.

---

### Recommendation

After collecting all `transaction_output` values for a block, recompute `event_commitment` from the assembled outputs and compare it to `header.event_commitment` before calling `write_to_storage`. If the values diverge, return `ParseDataError::BadPeer` (which already triggers peer reporting and query retry via `client_response_manager.report_peer()`).

The same check should be applied to `transaction_commitment` and `receipt_commitment` for completeness, consistent with the existing TODO at line 88.

---

### Proof of Concept

```rust
// In an integration test harness (mirroring transaction_test.rs):
// 1. Store a header for block 0 with a known event_commitment (e.g., the empty-tree root).
// 2. Act as the SQMR peer; send one FullTransaction whose TransactionOutput::Invoke
//    contains a synthetic event with arbitrary keys/data.
// 3. Let parse_data_for_block accept it (transaction count == header.n_transactions == 1).
// 4. After write_to_storage completes, read back the stored TransactionOutput.
// 5. Recompute event_commitment from the stored output using calculate_event_commitment.
// 6. Assert it equals header.event_commitment — this assertion FAILS, proving the invariant
//    is violated and fabricated events are now in persistent storage.
let stored_outputs = txn.get_block_transaction_outputs(BlockNumber(0)).unwrap().unwrap();
let event_leaves: Vec<EventLeafElement> = stored_outputs.iter().zip(tx_hashes.iter())
    .flat_map(|(out, hash)| out.events().iter().map(|e| EventLeafElement {
        event: e.clone(), transaction_hash: *hash,
    }).collect::<Vec<_>>())
    .collect();
let recomputed = calculate_event_commitment::<Poseidon>(&event_leaves);
assert_eq!(recomputed, header.event_commitment); // FAILS — fabricated events accepted
```

### Citations

**File:** crates/apollo_p2p_sync/src/client/transaction.rs (L36-36)
```rust
            storage_writer.begin_rw_txn()?.append_body(self.1, self.0)?.commit()?;
```

**File:** crates/apollo_p2p_sync/src/client/transaction.rs (L67-67)
```rust
            while current_transaction_len < target_transaction_len {
```

**File:** crates/apollo_p2p_sync/src/client/transaction.rs (L86-90)
```rust
                block_body.transactions.push(transaction);
                block_body.transaction_outputs.push(transaction_output);
                // TODO(eitan): Validate transaction hash from untrusted sources
                block_body.transaction_hashes.push(transaction_hash);
                current_transaction_len += 1;
```

**File:** crates/apollo_storage/src/body/mod.rs (L619-621)
```rust
        let tx_location = file_handlers.append_transaction(tx);
        let tx_output_location = file_handlers.append_transaction_output(tx_output);
        write_events(tx_output, txn, events_table, transaction_index)?;
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

**File:** crates/apollo_p2p_sync/src/client/header.rs (L148-150)
```rust
                transaction_commitment: Some(header_commitments.transaction_commitment),
                event_commitment: Some(header_commitments.event_commitment),
                n_transactions: sync_block.account_transaction_hashes.len()
```
