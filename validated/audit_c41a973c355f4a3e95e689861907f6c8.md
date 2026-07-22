### Title
Stale-Pending Fallback in `read_pending_data` Always Returns `L1DataAvailabilityMode::Calldata`, Corrupting Fee Estimation and Pending Block Headers on Blob-DA Networks — (`crates/apollo_rpc/src/v0_8/api/api_impl.rs`)

---

### Summary

When the cached pending block's parent hash does not match the latest finalized block hash, `read_pending_data` constructs a synthetic fallback `PendingBlockOrDeprecated::Deprecated(DeprecatedPendingBlock { … })`. The `DeprecatedPendingBlock` struct has no `l1_da_mode` field, and `PendingBlockOrDeprecated::l1_da_mode()` for the `Deprecated` variant unconditionally returns `L1DataAvailabilityMode::Calldata`. The latest finalized header's real `l1_da_mode` is never copied into the fallback. On any network operating in Blob mode, every RPC call that hits this fallback path receives a wrong `l1_da_mode`, causing incorrect fee estimates, wrong simulation results, and incorrect pending block headers served to clients.

---

### Finding Description

**Fallback construction — `read_pending_data`:** [1](#0-0) 

When `pending_data.block.parent_block_hash() != latest_header.block_hash`, the function builds a `DeprecatedPendingBlock` copying `eth_l1_gas_price`, `strk_l1_gas_price`, `timestamp`, `sequencer_address`, and `starknet_version` from the latest header — but **not** `l1_da_mode`. The latest header stores `l1_da_mode` in `block_header_without_hash.l1_da_mode`, which is simply ignored.

**`DeprecatedPendingBlock` has no `l1_da_mode` field:** [2](#0-1) 

**`l1_da_mode()` for `Deprecated` variant is hardcoded to `Calldata`:** [3](#0-2) 

The comment says "In older versions, all blocks were using calldata" — this is correct for historical blocks, but the fallback is also used for *current* blocks on Blob-DA networks.

**Propagation to execution context:**

`client_pending_data_to_execution_pending_data` reads `l1_da_mode` from the block: [4](#0-3) 

This feeds into `create_block_context`, which sets `use_kzg_da`: [5](#0-4) 

`use_kzg_da = false` (Calldata) instead of `true` (Blob) changes how the blockifier accounts for state-change DA costs — l1_data_gas vs l1_gas — directly affecting fee estimates.

**Affected RPC endpoints (all use `read_pending_data` with `BlockId::Tag(Tag::Pending)`):**

- `starknet_getBlockWithTxs` / `starknet_getBlockWithTxHashes` — serves wrong `l1_da_mode` in `PendingBlockHeader`: [6](#0-5) 

- `starknet_estimateFee`: [7](#0-6) 

- `starknet_simulateTransactions`: [8](#0-7) 

- `starknet_traceTransaction` / `starknet_traceBlockTransactions`: [9](#0-8) 

---

### Impact Explanation

On a Blob-DA network, the fallback path fires during every block transition (the window between a new block being finalized and the pending data being refreshed). During this window:

1. **`starknet_getBlockWithTxs` / `starknet_getBlockWithTxHashes`** return `l1_da_mode: CALLDATA` in the pending block header instead of `BLOB`. Clients relying on this field to determine DA mode receive authoritative-looking wrong data.

2. **`starknet_estimateFee`** with `BlockId::Tag(Tag::Pending)` computes fees using `use_kzg_da = false`. In Blob mode, state-change costs are charged to `l1_data_gas`; with the wrong flag they are charged to `l1_gas`. The resulting fee estimate can be significantly wrong (over- or under-estimated depending on relative gas prices), causing transactions to be submitted with insufficient or excessive fees.

3. **`starknet_simulateTransactions`** and trace endpoints return execution results computed under the wrong DA mode, producing incorrect gas vectors and fee estimations.

The `concat_counts` / block hash divergence claim in the question is overstated for the RPC path — `concat_counts` is computed by the sequencer/batcher during block finalization using the real `l1_da_mode`, not by the RPC node's pending view. However, the wrong `l1_da_mode` in fee estimation and pending block headers is a concrete, reachable impact. [10](#0-9) 

---

### Likelihood Explanation

The fallback path fires on every block transition — a normal, frequent event. Any unprivileged RPC client calling `starknet_estimateFee` or `starknet_getBlockWithTxs` with `BlockId::Tag(Tag::Pending)` during this window is affected. On Starknet mainnet (which operates in Blob mode), this is a persistent, reproducible condition.

---

### Recommendation

In the fallback branch of `read_pending_data`, copy `l1_da_mode` from the latest finalized header into the synthetic pending block. Since `DeprecatedPendingBlock` has no `l1_da_mode` field, either:

1. Use `PendingBlockOrDeprecated::Current(PendingBlock { l1_da_mode: latest_header.block_header_without_hash.l1_da_mode, … })` for the fallback, or
2. Add an `l1_da_mode` field to `DeprecatedPendingBlock` with a default, and populate it from the latest header in the fallback.

The fix is in `read_pending_data` at: [11](#0-10) 

---

### Proof of Concept

```rust
// In a test: set latest block header to l1_da_mode = Blob.
// Set pending_data.block.parent_block_hash to a different hash (stale).
// Call read_pending_data.
// Assert returned block.l1_da_mode() == L1DataAvailabilityMode::Blob.
// Actual result: L1DataAvailabilityMode::Calldata  ← BUG

let mut latest_header = BlockHeader::default();
latest_header.block_header_without_hash.l1_da_mode = L1DataAvailabilityMode::Blob;
// pending_data has a different parent hash → fallback fires
let result = read_pending_data(&pending_data, &txn).await.unwrap();
assert_eq!(result.block.l1_da_mode(), L1DataAvailabilityMode::Blob); // FAILS: returns Calldata
```

### Citations

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L1009-1013)
```rust
        let maybe_pending_data = if let BlockId::Tag(Tag::Pending) = block_id {
            Some(client_pending_data_to_execution_pending_data(
                read_pending_data(&self.pending_data, &storage_txn).await?,
                self.pending_classes.read().await.clone(),
            ))
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L1079-1083)
```rust
        let maybe_pending_data = if let BlockId::Tag(Tag::Pending) = block_id {
            Some(client_pending_data_to_execution_pending_data(
                read_pending_data(&self.pending_data, &storage_txn).await?,
                self.pending_classes.read().await.clone(),
            ))
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L1192-1192)
```rust
                l1_da_mode: pending_block.l1_da_mode(),
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L1569-1594)
```rust
    let pending_data = &pending_data.read().await;
    if pending_data.block.parent_block_hash() == latest_header.block_hash {
        Ok((*pending_data).clone())
    } else {
        Ok(PendingData {
            block: PendingBlockOrDeprecated::Deprecated(DeprecatedPendingBlock {
                parent_block_hash: latest_header.block_hash,
                eth_l1_gas_price: latest_header.block_header_without_hash.l1_gas_price.price_in_wei,
                strk_l1_gas_price: latest_header
                    .block_header_without_hash
                    .l1_gas_price
                    .price_in_fri,
                timestamp: latest_header.block_header_without_hash.timestamp,
                sequencer_address: latest_header.block_header_without_hash.sequencer,
                starknet_version: latest_header
                    .block_header_without_hash
                    .starknet_version
                    .to_string(),
                ..Default::default()
            }),
            state_update: ClientPendingStateUpdate {
                old_root: latest_header.block_header_without_hash.state_root,
                state_diff: Default::default(),
            },
        })
    }
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L1626-1626)
```rust
                l1_da_mode: block.l1_da_mode(),
```

**File:** crates/apollo_starknet_client/src/reader/objects/pending_data.rs (L169-175)
```rust
    pub fn l1_da_mode(&self) -> L1DataAvailabilityMode {
        match self {
            // In older versions, all blocks were using calldata.
            PendingBlockOrDeprecated::Deprecated(_) => L1DataAvailabilityMode::Calldata,
            PendingBlockOrDeprecated::Current(block) => block.l1_da_mode,
        }
    }
```

**File:** crates/apollo_starknet_client/src/reader/objects/pending_data.rs (L178-195)
```rust
#[derive(Debug, Default, Deserialize, Clone, Eq, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct DeprecatedPendingBlock {
    #[serde(flatten)]
    pub accepted_on_l2_extra_data: Option<AcceptedOnL2ExtraData>,
    pub parent_block_hash: BlockHash,
    pub status: BlockStatus,
    // In older versions, eth_l1_gas_price was named gas_price and there was no strk_l1_gas_price.
    #[serde(alias = "gas_price")]
    pub eth_l1_gas_price: GasPrice,
    #[serde(default)]
    pub strk_l1_gas_price: GasPrice,
    pub transactions: Vec<Transaction>,
    pub timestamp: BlockTimestamp,
    pub sequencer_address: SequencerContractAddress,
    pub transaction_receipts: Vec<TransactionReceipt>,
    pub starknet_version: String,
}
```

**File:** crates/apollo_rpc/src/pending.rs (L21-21)
```rust
        l1_da_mode: client_pending_data.block.l1_da_mode(),
```

**File:** crates/apollo_rpc_execution/src/lib.rs (L369-369)
```rust
    let use_kzg_da = if override_kzg_da_to_false { false } else { l1_da_mode.is_use_kzg_da() };
```

**File:** crates/starknet_api/src/block_hash/block_hash_calculator.rs (L374-393)
```rust
pub fn concat_counts(
    transaction_count: usize,
    event_count: usize,
    state_diff_length: usize,
    l1_data_availability_mode: L1DataAvailabilityMode,
) -> Felt {
    let l1_data_availability_byte: u8 = match l1_data_availability_mode {
        L1DataAvailabilityMode::Calldata => 0,
        L1DataAvailabilityMode::Blob => 0b10000000,
    };
    let concat_bytes = [
        to_64_bits(transaction_count).as_slice(),
        to_64_bits(event_count).as_slice(),
        to_64_bits(state_diff_length).as_slice(),
        &[l1_data_availability_byte],
        &[0_u8; 7], // zero padding
    ]
    .concat();
    Felt::from_bytes_be_slice(concat_bytes.as_slice())
}
```
