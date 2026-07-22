The code path is fully traceable. Let me confirm the exact lines for the RPC `new_root` derivation and the `read_pending_data` fallback path.

### Title
Unauthenticated P2P Peer Can Inject Arbitrary `state_root` into Storage, Corrupting `starknet_getStateUpdate` `new_root` and Pending State `old_root` — (`crates/apollo_p2p_sync/src/client/header.rs`)

---

### Summary

The p2p sync client accepts `SignedBlockHeader` messages from low-trust peers and writes them to storage with no cryptographic verification. The only guards in `parse_data_for_block` are a sequential block-number check and a signature-count check. No signature is verified against the block hash, and no block hash is recomputed from the header fields. As a result, a peer-supplied `state_root` (`GlobalRoot`) is stored verbatim and later served by `starknet_getStateUpdate` as the authoritative `new_root`, and by `read_pending_data` as the `old_root` for the pending state update.

---

### Finding Description

**Step 1 — Entry point: unauthenticated p2p message**

A low-trust peer sends a `BlockHeadersResponse` protobuf containing a `SignedBlockHeader` with an arbitrary `state_root` field (protobuf tag 6).

The protobuf converter in `crates/apollo_protobuf/src/converters/header.rs` maps the wire value directly into `BlockHeaderWithoutHash.state_root` with no validation: [1](#0-0) 

**Step 2 — Validation gate: only block number and signature count are checked**

`parse_data_for_block` in `header.rs` applies exactly two checks before accepting the header: [2](#0-1) 

There is no call to `verify_block_signature` anywhere in the `apollo_p2p_sync` crate (confirmed by exhaustive grep). The `block_hash` field is also peer-supplied and is never recomputed from the header fields. The comment at line 102 even acknowledges that `parent_hash` is not yet checked: [3](#0-2) 

**Step 3 — Storage write: peer-supplied `state_root` committed verbatim**

`write_to_storage` calls `append_header` unconditionally: [4](#0-3) 

`append_header` copies `block_header.block_header_without_hash.state_root` directly into `StorageBlockHeader.state_root`: [5](#0-4) 

**Step 4 — RPC `starknet_getStateUpdate` returns the injected value as `new_root`**

`get_state_update` reads the stored header and returns `header.new_root` as the authoritative global state root: [6](#0-5) 

`new_root` is mapped from `block_header_without_hash.state_root`: [7](#0-6) 

**Step 5 — `read_pending_data` uses the injected `state_root` as `old_root`**

When the cached pending block does not match the latest stored block hash, `read_pending_data` synthesizes a pending state update using the stored `state_root` as `old_root`: [8](#0-7) 

This corrupts fee estimation and all pending-block state queries for RPC clients.

---

### Impact Explanation

- `starknet_getStateUpdate` returns an attacker-controlled `new_root` as the authoritative global state root for any accepted block.
- `starknet_getStateUpdate` with `block_id = "pending"` returns an attacker-controlled `old_root`, corrupting the pending state update baseline.
- Fee estimation (`starknet_estimateFee`), simulation (`starknet_simulateTransactions`), and any RPC call that reads pending state via `read_pending_data` inherits the wrong `old_root`.
- The impact is **High**: RPC returns authoritative-looking wrong values for global state roots, directly matching the allowed impact scope.

---

### Likelihood Explanation

Any node that connects to the p2p network and uses the p2p sync client is reachable. The attacker only needs to be a peer that responds to a `BlockHeadersRequest` query. The only preconditions are that the injected `block_number` matches the expected sequential value and `signatures.len() == 1`. Both are trivially satisfied. No cryptographic material is required.

---

### Recommendation

1. **Verify the block signature cryptographically** in `parse_data_for_block` before accepting a `SignedBlockHeader`. The function `verify_block_signature` already exists in `starknet_api::block` and signs over `(block_hash, state_diff_commitment)`. It should be called here with the known sequencer public key.
2. **Recompute and verify `block_hash`** from the header fields before storage, so that a peer cannot supply a mismatched `(block_hash, state_root)` pair.
3. **Verify `parent_hash`** against the previously stored block hash (the existing TODO at line 102 of `header.rs`).

---

### Proof of Concept

```rust
// Attacker sends a SignedBlockHeader with state_root = 0xbadbeef
let injected = SignedBlockHeader {
    block_header: BlockHeader {
        block_hash: /* any value accepted by block_hash_to_number lookup */,
        block_header_without_hash: BlockHeaderWithoutHash {
            block_number: BlockNumber(N), // matches expected sequential number
            state_root: GlobalRoot(Felt::from(0xbadbeef_u64)),
            ..Default::default()
        },
        state_diff_length: Some(0),
        ..Default::default()
    },
    signatures: vec![BlockSignature::default()], // len == ALLOWED_SIGNATURES_LENGTH == 1
};
// parse_data_for_block accepts it (block_number matches, signatures.len() == 1)
// write_to_storage commits state_root = 0xbadbeef to StorageBlockHeader
// starknet_getStateUpdate(block_id=N) returns AcceptedStateUpdate { new_root: 0xbadbeef, ... }
// read_pending_data returns PendingStateUpdate { old_root: 0xbadbeef, ... }
```

### Citations

**File:** crates/apollo_protobuf/src/converters/header.rs (L197-206)
```rust
                block_header_without_hash: BlockHeaderWithoutHash {
                    parent_hash,
                    block_number: BlockNumber(value.number),
                    l1_gas_price,
                    l1_data_gas_price,
                    l2_gas_price,
                    l2_gas_consumed,
                    next_l2_gas_price,
                    state_root,
                    sequencer,
```

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

**File:** crates/apollo_p2p_sync/src/client/header.rs (L102-103)
```rust
            // TODO(shahak): Check that parent_hash is the same as the previous block's hash
            // and handle reverts.
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

**File:** crates/apollo_storage/src/header.rs (L308-317)
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
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L521-526)
```rust
        Ok(StateUpdate::AcceptedStateUpdate(AcceptedStateUpdate {
            block_hash: header.block_hash,
            new_root: header.new_root,
            old_root,
            state_diff,
        }))
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L1589-1591)
```rust
            state_update: ClientPendingStateUpdate {
                old_root: latest_header.block_header_without_hash.state_root,
                state_diff: Default::default(),
```

**File:** crates/apollo_rpc/src/v0_8/block.rs (L57-57)
```rust
            new_root: header.block_header_without_hash.state_root,
```
