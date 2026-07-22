The code path is real and traceable. Here is the full analysis:

---

## Code Path Trace

**1. `pending_data` is never updated in P2P mode.**

In `StateSyncRunner::new`, when `p2p_sync_client_config=Some, central_sync_client_config=None`, the `pending_data` Arc is passed only to `spawn_rpc_server`, not to the P2P sync client: [1](#0-0) 

The central sync path (lines 334–351) does pass `pending_data` to the sync client, but the P2P path does not. So `pending_data` stays permanently initialized with `GENESIS_PARENT_HASH`: [2](#0-1) 

**2. `read_pending_data` falls through to the synthetic block on every call in P2P mode.**

Since `pending_data.block.parent_block_hash()` is always `GENESIS_PARENT_HASH` and the latest stored header's `block_hash` is never that value after block 0, the condition at line 1570 is always false, and the synthetic `DeprecatedPendingBlock` is always returned: [3](#0-2) 

The synthetic block copies `l1_gas_price.price_in_wei` and `l1_gas_price.price_in_fri` directly from the latest stored header.

**3. P2P sync stores headers with no gas-price validation.**

`parse_data_for_block` in the header stream builder only checks block number ordering and signature vector length. There is no cryptographic verification of the block hash against header fields, and no range check on gas prices. The comment at line 102 explicitly acknowledges the missing parent-hash check: [4](#0-3) 

`write_to_storage` then calls `append_header` directly with the peer-supplied header: [5](#0-4) 

**4. Fee estimation with `BlockId::Tag(Tag::Pending)` uses the synthetic block's gas prices.**

`estimate_fee` calls `read_pending_data` when the block tag is `Pending` and passes the result to `exec_estimate_fee`: [6](#0-5) 

`exec_estimate_fee` builds the `BlockContext` using `l1_gas_price` from the pending data: [7](#0-6) 

---

## Verdict

**The vulnerability is real and reachable.**

The full chain is:

1. Attacker runs a P2P node and connects to the victim.
2. Attacker sends a `SignedBlockHeader` with an extreme `l1_gas_price` (e.g., `u128::MAX`). The P2P client accepts it — only block number and signature-vector length are checked; the signature is not cryptographically verified and gas prices are not range-checked.
3. The header is written to storage via `append_header`.
4. Any unauthenticated RPC client calls `starknet_estimateFee` (or `starknet_getBlockWithTxs`) with `BlockId::Tag(Tag::Pending)`.
5. `read_pending_data` detects the hash mismatch, constructs the synthetic `DeprecatedPendingBlock` from the attacker-supplied header's `l1_gas_price`, and returns it.
6. Fee estimation executes with the attacker-controlled gas price, returning a fabricated fee to the caller.

The impact matches **High — RPC fee estimation returns an authoritative-looking wrong value** driven by unauthenticated P2P data.

---

### Title
P2P-Supplied Header Gas Prices Reflected in Pending-Block Fee Estimation — (`crates/apollo_p2p_sync/src/client/header.rs`, `crates/apollo_rpc/src/v0_8/api/api_impl.rs`)

### Summary
In P2P-only sync mode, block headers received from peers are stored without validating gas prices or verifying the block hash against header fields. Because `pending_data` is never updated by the P2P path, `read_pending_data` always falls through to a synthetic `DeprecatedPendingBlock` whose `l1_gas_price` is copied from the latest stored (peer-supplied) header. Any RPC caller using `BlockId::Tag(Tag::Pending)` for fee estimation or block queries receives results computed from attacker-controlled gas prices.

### Finding Description
`HeaderStreamBuilder::parse_data_for_block` accepts a `SignedBlockHeader` from a peer after checking only that the block number matches the expected value and that exactly one signature is present. No cryptographic verification of the block hash against header fields (including gas prices) is performed, and no range or sanity check is applied to `l1_gas_price`. The accepted header is written directly to storage. In P2P mode, `pending_data` is initialized with `GENESIS_PARENT_HASH` and never updated, so `read_pending_data` always constructs a synthetic pending block whose `eth_l1_gas_price`/`strk_l1_gas_price` are taken from the latest stored header. This synthetic block is used by `estimate_fee`, `estimate_message_fee`, `simulate_transactions`, and `get_block` when called with `BlockId::Tag(Tag::Pending)`.

### Impact Explanation
An attacker who is a P2P peer (achievable by running any Starknet-compatible node) can inject a header with an arbitrarily large or small `l1_gas_price`. Every subsequent call to `starknet_estimateFee` with `block_id = "pending"` will return a fee computed from that price. Users relying on pending-block fee estimates to set `max_fee` or `resource_bounds` will receive systematically wrong values, potentially causing transactions to be under-priced (rejected on-chain) or over-priced (economic loss).

### Likelihood Explanation
The P2P network is open; any node can connect and serve headers. The missing block-hash-vs-fields verification is acknowledged in a TODO comment in the source. The attack requires no privileged access and no special timing.

### Recommendation
1. In `parse_data_for_block`, recompute the block hash from the received header fields and reject the header if it does not match `signed_block_header.block_header.block_hash`.
2. Cryptographically verify the block signature against the block hash before storing the header.
3. In `StateSyncRunner::new` for the P2P path, either update `pending_data` from the latest stored header after each write, or document and enforce that pending-block RPC endpoints are disabled in P2P-only mode.

### Proof of Concept
```
1. Start a victim node in P2P-only mode.
2. Connect an attacker node; respond to the victim's header query with a SignedBlockHeader
   for block N containing l1_gas_price = { price_in_wei: u128::MAX, price_in_fri: u128::MAX }
   and a dummy (all-zero) signature.
3. The victim stores the header (parse_data_for_block accepts it).
4. Call starknet_estimateFee on the victim's RPC with block_id = "pending".
5. Observe that the returned l1_gas_price equals u128::MAX and overall_fee is u128::MAX-scaled.
```

### Citations

**File:** crates/apollo_state_sync/src/runner/mod.rs (L163-171)
```rust
        let pending_data = Arc::new(RwLock::new(PendingData {
            // The pending data might change later to DeprecatedPendingBlock, depending on the
            // response from the feeder gateway.
            block: PendingBlockOrDeprecated::Current(PendingBlock {
                parent_block_hash: BlockHash::GENESIS_PARENT_HASH,
                ..Default::default()
            }),
            ..Default::default()
        }));
```

**File:** crates/apollo_state_sync/src/runner/mod.rs (L311-333)
```rust
        let (p2p_sync_client_future, central_sync_client_future, new_block_dev_null_future) =
            match (p2p_sync_client_config, central_sync_client_config) {
                (Some(p2p_sync_client_config), None) => {
                    debug!("State sync runner creating peer-to-peer sync client.");
                    // TODO(noamsp): Add this check to the config validation.
                    let network_manager = maybe_network_manager
                        .as_mut()
                        .expect("Network manager should be present if p2p sync client is present");

                    let p2p_sync_client = Self::new_p2p_state_sync_client(
                        storage_reader.clone(),
                        storage_writer,
                        p2p_sync_client_config,
                        network_manager,
                        new_block_receiver,
                        class_manager_client.clone(),
                    );

                    let p2p_sync_client_future = p2p_sync_client.run().boxed();
                    let central_sync_client_future = future::pending().boxed();
                    let new_block_dev_null_future = future::pending().boxed();
                    (p2p_sync_client_future, central_sync_client_future, new_block_dev_null_future)
                }
```

**File:** crates/apollo_rpc/src/v0_8/api/api_impl.rs (L1009-1016)
```rust
        let maybe_pending_data = if let BlockId::Tag(Tag::Pending) = block_id {
            Some(client_pending_data_to_execution_pending_data(
                read_pending_data(&self.pending_data, &storage_txn).await?,
                self.pending_classes.read().await.clone(),
            ))
        } else {
            None
        };
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

**File:** crates/apollo_p2p_sync/src/client/header.rs (L28-50)
```rust
    fn write_to_storage<'a>(
        self: Box<Self>,
        storage_writer: &'a mut StorageWriter,
        _class_manager_client: &'a mut SharedClassManagerClient,
    ) -> BoxFuture<'a, Result<(), P2pSyncClientError>> {
        async move {
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

**File:** crates/apollo_p2p_sync/src/client/header.rs (L99-120)
```rust
            let Some(signed_block_header) = maybe_signed_header?.0 else {
                return Ok(None);
            };
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

**File:** crates/apollo_rpc_execution/src/lib.rs (L341-366)
```rust
        Some(pending_data) => (
            block_context_number.unchecked_next(),
            pending_data.timestamp,
            pending_data.l1_gas_price,
            pending_data.l1_data_gas_price,
            pending_data.l2_gas_price,
            pending_data.sequencer,
            pending_data.l1_da_mode,
        ),
        None => {
            let header = storage_reader
                .begin_ro_txn()?
                .get_block_header(block_context_number)?
                .expect("Should have block header.")
                .block_header_without_hash;
            (
                header.block_number,
                header.timestamp,
                header.l1_gas_price,
                header.l1_data_gas_price,
                header.l2_gas_price,
                header.sequencer,
                header.l1_da_mode,
            )
        }
    };
```
