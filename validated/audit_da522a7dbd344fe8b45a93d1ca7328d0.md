### Title
Missing Lower-Bound Wall-Clock Check on `ProposalInit.timestamp` Allows Past-Dated Block Timestamps — (`crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

`is_proposal_init_valid` enforces an upper bound (`timestamp ≤ now + window`) but has **no symmetric lower bound against `now`**. The only lower bound is `timestamp ≥ last_block_timestamp`. A selected proposer can therefore set `ProposalInit.timestamp` to any value from `last_block_timestamp` (which is `0` at genesis) up to `now + 1 s`, causing the committed block to carry an arbitrarily stale timestamp. Every validator accepts the proposal, the batcher executes it with that timestamp as `BlockInfo.block_timestamp`, and the wrong value is permanently committed to the chain.

---

### Finding Description

In `is_proposal_init_valid`, the full timestamp gate is:

```rust
// lower bound — only against the previous block, NOT against now
if init_proposed.timestamp < last_block_timestamp {
    return Err(InvalidProposalInit(..., "Timestamp is too old: ..."));
}
// upper bound — against now + window
if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds {
    return Err(InvalidProposalInit(..., "Timestamp is in the future: ..."));
}
``` [1](#0-0) 

`last_block_timestamp` is derived from `previous_proposal_init`:

```rust
let last_block_timestamp =
    proposal_init_validation.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
``` [2](#0-1) 

When `previous_proposal_init` is `None` (first block / genesis), `last_block_timestamp = 0`, so the accepted range is `[0, now + 1]`. A proposer can legally set `timestamp = 1` (Unix epoch + 1 s). Even in steady-state operation the proposer can set `timestamp = last_block_timestamp` (the previous block's timestamp), causing zero time progression between consecutive blocks.

The production deployment configures `block_timestamp_window_seconds = 1`: [3](#0-2) 

The default in code is also `1`: [4](#0-3) 

The accepted `init_proposed.timestamp` is then forwarded verbatim to the batcher as `BlockInfo.block_timestamp` via `convert_to_sn_api_block_info`: [5](#0-4) 

The batcher executes all transactions in the block with this `BlockInfo`, which is the value returned by the `get_block_timestamp()` syscall inside every contract.

Additionally, the L1 gas price is looked up **at `init_proposed.timestamp`**, not at `now`: [6](#0-5) 

A past timestamp can map to a materially different L1 gas price, causing incorrect fee charging for all transactions in the block.

The same missing lower-bound gap exists in `try_sync`, which validates synced blocks: [7](#0-6) 

---

### Impact Explanation

**Critical — Wrong execution result from syscall logic for accepted input.**

Every contract that calls `get_block_timestamp()` during execution of the affected block receives the proposer-supplied stale value. Time-sensitive contracts (vesting, auctions, rate-limiters, TWAP oracles, deadline checks) will compute incorrect results. Because the timestamp is part of `PartialBlockHashComponents`, the wrong value is permanently committed to the block hash and the state root.

**Critical — Incorrect fee / L1 gas price effect with economic impact.**

The L1 gas price oracle is queried at `init_proposed.timestamp`. A past timestamp (potentially outside the `max_time_gap_seconds = 900` window) returns a stale or fallback price. All transactions in the block are charged fees derived from that stale price rather than the current market price.

---

### Likelihood Explanation

Any validator that is legitimately selected as proposer by the committee can trigger this. No special privilege beyond normal proposer selection is required. The near-genesis window (`last_block_timestamp = 0`) is the most severe case and is reachable on every fresh chain deployment or after a chain reset. In steady-state, the window is bounded by the inter-block interval (~6 s), but the proposer can still suppress time progression entirely by setting `timestamp = last_block_timestamp`.

---

### Recommendation

Add a symmetric lower-bound check anchored to `now` inside `is_proposal_init_valid`:

```rust
// Reject timestamps that are too far in the past relative to wall-clock time.
if now > proposal_init_validation.block_timestamp_window_seconds
    && init_proposed.timestamp < now - proposal_init_validation.block_timestamp_window_seconds
{
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "Timestamp is too far in the past: now={}, block_timestamp_window_seconds={}, \
             proposed={}",
            now,
            proposal_init_validation.block_timestamp_window_seconds,
            init_proposed.timestamp
        ),
    ));
}
```

Apply the same guard in `try_sync`. Consider widening `block_timestamp_window_seconds` slightly (e.g., to the expected maximum block interval) so that legitimate slow rounds are not rejected, while still bounding how far in the past a timestamp can be.

---

### Proof of Concept

1. Chain starts fresh; `previous_proposal_init = None` → `last_block_timestamp = 0`.
2. The selected proposer constructs `ProposalInit { timestamp: 1, .. }` (Unix epoch + 1 s).
3. `is_proposal_init_valid` checks:
   - `1 >= 0` ✓ (lower bound passes)
   - `1 <= now + 1` ✓ (upper bound passes, `now` ≈ 1.7 × 10⁹)
4. `initiate_validation` calls `batcher.validate_block(ValidateBlockInput { block_info: BlockInfo { block_timestamp: BlockTimestamp(1), .. }, .. })`.
5. All transactions execute with `get_block_timestamp() == 1`.
6. A contract checking `assert(get_block_timestamp() > deadline)` where `deadline = 1_000_000` (year 1970) would incorrectly fail, or a contract checking `assert(get_block_timestamp() < expiry)` where `expiry = 1_000` would incorrectly pass.
7. The L1 gas price oracle is queried at timestamp `1`; the gap from `now` (~1.7 × 10⁹ s) far exceeds `max_time_gap_seconds = 900`, returning a stale/fallback price used to charge all transaction fees.
8. `ProposalFin` is accepted; the block is committed with `block_timestamp = 1` permanently in the chain state.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L260-285)
```rust
    let now: u64 = clock.unix_now();
    let last_block_timestamp =
        proposal_init_validation.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
    if init_proposed.timestamp < last_block_timestamp {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "Timestamp is too old: last_block_timestamp={}, proposed={}",
                last_block_timestamp, init_proposed.timestamp
            ),
        ));
    }
    if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "Timestamp is in the future: now={}, block_timestamp_window_seconds={}, \
                 proposed={}",
                now,
                proposal_init_validation.block_timestamp_window_seconds,
                init_proposed.timestamp
            ),
        ));
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L322-328)
```rust
    let (l1_gas_prices_fri, l1_gas_prices_wei) = get_l1_prices_in_fri_and_wei(
        l1_gas_price_provider,
        init_proposed.timestamp,
        proposal_init_validation.previous_proposal_init.as_ref(),
        gas_price_params,
    )
    .await;
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-467)
```rust
    let input = ValidateBlockInput {
        proposal_id,
        deadline: clock.now() + chrono_timeout,
        retrospective_block_hash: retrospective_block_hash(
            batcher.clone(),
            state_sync_client,
            init,
            compare_retrospective_block_hash,
        )
        .await
        .map_err(ValidateProposalError::from)?,
        block_info: convert_to_sn_api_block_info(init)?,
    };
```

**File:** crates/apollo_deployments/resources/app_configs/consensus_manager_config.json (L36-36)
```json
  "consensus_manager_config.context_config.static_config.block_timestamp_window_seconds": 1,
```

**File:** crates/apollo_consensus_orchestrator_config/src/config.rs (L253-253)
```rust
            block_timestamp_window_seconds: 1,
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1067-1070)
```rust
        if !(block_number == height
            && timestamp.0 >= last_block_timestamp
            && timestamp.0 <= now + self.config.static_config.block_timestamp_window_seconds)
        {
```
