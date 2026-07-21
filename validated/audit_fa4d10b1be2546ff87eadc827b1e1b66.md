### Title
`BlockHeaderWithoutHash` Constructed with `..Default::default()` Silently Zeroes `starknet_version`, `parent_hash`, and `state_root` in `SyncBlock` Sent to State Sync — (`File: crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs`)

### Summary

After every consensus decision, `update_state_sync_with_new_block` builds a `BlockHeaderWithoutHash` using a partial struct literal with `..Default::default()`. Three fields that are never assigned — `starknet_version`, `parent_hash`, and `state_root` — are silently zeroed. The resulting `SyncBlock` is forwarded to the state-sync layer. In P2P-sync mode this block is stored and served to syncing peers; those peers' batchers then use the zeroed `starknet_version` to decide the storage-commitment block-hash path, and the zeroed `parent_hash` as the actual commitment value, producing a wrong committed block hash and a wrong state root in every RPC view of that block.

### Finding Description

In `update_state_sync_with_new_block`:

```rust
let block_header_without_hash = BlockHeaderWithoutHash {
    block_number: height,
    l1_gas_price,
    l1_data_gas_price,
    l2_gas_price,
    l2_gas_consumed: l2_gas_used,
    next_l2_gas_price: self.l2_gas_price,
    sequencer,
    timestamp: BlockTimestamp(init.timestamp),
    l1_da_mode: init.l1_da_mode,
    fee_proposal_fri: init.fee_proposal_fri,
    // TODO(guy.f): Figure out where/if to get the values below from and fill them.
    ..Default::default()   // ← zeroes starknet_version, parent_hash, state_root
};
``` [1](#0-0) 

`BlockHeaderWithoutHash` derives `Default`, so the three unset fields become:

| Field | Default value |
|---|---|
| `starknet_version` | `StarknetVersion::default()` (earliest version, pre-partial-block-hash) |
| `parent_hash` | `BlockHash(Felt::ZERO)` |
| `state_root` | `GlobalRoot(Felt::ZERO)` | [2](#0-1) 

The `SyncBlock` carrying this header is then passed to `state_sync_client.add_new_block`. [3](#0-2) 

In the batcher's `add_sync_block` (the path taken by any node that syncs this block from the state-sync layer), the zeroed `starknet_version` causes `has_partial_block_hash_components()` to return `false`, so the code falls into the `else` branch and uses `block_header_without_hash.parent_hash` — which is `Felt::ZERO` — as the `StorageCommitmentBlockHash`:

```rust
let storage_commitment_block_hash = if block_header_without_hash
    .starknet_version
    .has_partial_block_hash_components()
{
    StorageCommitmentBlockHash::Partial(PartialBlockHashComponents { … })
} else {
    StorageCommitmentBlockHash::ParentHash(block_header_without_hash.parent_hash)
    //                                     ^^^ zero
};
``` [4](#0-3) 

Additionally, the zeroed `state_root` is stored in the block header served by the state-sync layer, so any RPC call that reads `new_root` / `old_root` for that block returns `0x0`.

### Impact Explanation

Any node that learns a consensus-produced block through the P2P state-sync path (i.e., not through its own batcher's `decision_reached`) will:

1. Commit the block with `StorageCommitmentBlockHash::ParentHash(Felt::ZERO)` instead of the correct partial block hash, producing a wrong on-chain block hash.
2. Store `state_root = Felt::ZERO`, causing `starknet_getStateUpdate`, `starknet_getBlockWithTxs`, and related RPC methods to return an authoritative-looking but incorrect state root.

This matches: **High — RPC execution / pending view returns an authoritative-looking wrong value**, and potentially **Critical — wrong state/receipt/storage value from execution logic**.

In Central Sync mode the `SyncBlock` from consensus is discarded (state-sync storage is populated only from the Feeder Gateway), so the impact is currently limited to deployments running P2P sync. The TODO comment at line 410 confirms the developers have not yet resolved which values to supply.

### Likelihood Explanation

The bug fires on every block committed via consensus in P2P-sync mode — no special attacker action is required. Any validator node that serves blocks to syncing peers will propagate the corrupted header automatically.

### Recommendation

Populate all three fields before constructing the `SyncBlock`:

- `starknet_version`: use `starknet_api::block::StarknetVersion::LATEST` (already used in `initiate_build`) or derive it from the `ProposalInit`.
- `parent_hash`: retrieve the previous block's hash from the batcher or state-sync client (it is already available as `retrospective_block_hash` or via `get_block_hash`).
- `state_root`: read the committed state root from the batcher's `DecisionReachedResponse` or from storage after `decision_reached` returns.

Remove the `..Default::default()` fallback once all fields are explicitly assigned, so future additions to `BlockHeaderWithoutHash` produce a compile error rather than a silent zero.

### Proof of Concept

1. Run two nodes in P2P-sync mode; Node A proposes and commits block N via consensus.
2. Node A calls `update_state_sync_with_new_block`; the `SyncBlock` for block N has `starknet_version = StarknetVersion::default()`, `parent_hash = Felt::ZERO`, `state_root = Felt::ZERO`.
3. Node B syncs block N from Node A's state-sync layer.
4. Node B's batcher calls `add_sync_block`; `has_partial_block_hash_components()` returns `false`; the block is committed with `StorageCommitmentBlockHash::ParentHash(Felt::ZERO)`.
5. `starknet_getStateUpdate(block_number=N)` on Node B returns `new_root: "0x0"` — a wrong, authoritative-looking value.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L399-412)
```rust
        let block_header_without_hash = BlockHeaderWithoutHash {
            block_number: height,
            l1_gas_price,
            l1_data_gas_price,
            l2_gas_price,
            l2_gas_consumed: l2_gas_used,
            next_l2_gas_price: self.l2_gas_price,
            sequencer,
            timestamp: BlockTimestamp(init.timestamp),
            l1_da_mode: init.l1_da_mode,
            fee_proposal_fri: init.fee_proposal_fri,
            // TODO(guy.f): Figure out where/if to get the values below from and fill them.
            ..Default::default()
        };
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L414-422)
```rust
        let sync_block = SyncBlock {
            state_diff: state_diff.clone(),
            account_transaction_hashes,
            l1_transaction_hashes,
            block_header_without_hash,
            block_header_commitments: Some(block_header_commitments),
        };

        self.deps.state_sync_client.add_new_block(sync_block).await
```

**File:** crates/starknet_api/src/block.rs (L231-248)
```rust
#[derive(Debug, Default, Clone, Eq, PartialEq, Hash, Deserialize, Serialize, PartialOrd, Ord)]
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

**File:** crates/apollo_batcher/src/batcher.rs (L849-892)
```rust
        let storage_commitment_block_hash = if block_header_without_hash
            .starknet_version
            .has_partial_block_hash_components()
        {
            self.maybe_handle_first_block_with_partial_block_hash(
                block_header_without_hash.parent_hash,
                block_number,
            )
            .map_err(|err| {
                error!("Error handling block number {block_number} with partial block hash: {err}");
                BatcherError::InternalError
            })?;
            match block_header_commitments {
                Some(header_commitments) => {
                    StorageCommitmentBlockHash::Partial(PartialBlockHashComponents {
                        header_commitments,
                        block_number,
                        l1_gas_price: block_header_without_hash.l1_gas_price,
                        l1_data_gas_price: block_header_without_hash.l1_data_gas_price,
                        l2_gas_price: block_header_without_hash.l2_gas_price,
                        sequencer: block_header_without_hash.sequencer,
                        timestamp: block_header_without_hash.timestamp,
                        starknet_version: block_header_without_hash.starknet_version,
                    })
                }
                None => return Err(BatcherError::MissingHeaderCommitments { block_number }),
            }
        } else {
            let first_block_with_partial_block_hash_number = self
                .config
                .static_config
                .first_block_with_partial_block_hash
                .as_ref()
                .expect(
                    "Since an old block was learned via sync, first block with partial block hash \
                     components should be configured.",
                )
                .block_number;
            assert!(
                height < first_block_with_partial_block_hash_number,
                "Height {height} is at least the first block configured to include a partial hash \
                 ({first_block_with_partial_block_hash_number}) but does not include one.",
            );
            StorageCommitmentBlockHash::ParentHash(block_header_without_hash.parent_hash)
```
