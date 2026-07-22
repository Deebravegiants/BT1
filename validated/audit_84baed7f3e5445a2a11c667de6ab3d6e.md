### Title
`starknet_version` Uninitialized in `update_state_sync_with_new_block` Produces Authoritative-Looking Wrong RPC Block Headers — (`crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs`)

---

### Summary

`update_state_sync_with_new_block` constructs a `BlockHeaderWithoutHash` for every decided block and pushes it to state-sync. The `starknet_version` field is never assigned; it silently falls through to `..Default::default()`. Because `init.starknet_version` (always `StarknetVersion::LATEST`) is available in scope but unused, every block header stored by the sequencer carries the wrong protocol version. RPC endpoints that serve this header return an authoritative-looking but incorrect `starknet_version`, and the `has_partial_block_hash_components()` predicate derived from that field returns `false` for blocks that should return `true`.

---

### Finding Description

In `finalize_decision` → `update_state_sync_with_new_block`, the `BlockHeaderWithoutHash` is built as:

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
    // TODO(guy.f): Figure out where/if to get the values below from and fill