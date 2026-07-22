### Title
Missing lower-bound timestamp enforcement in `is_proposal_init_valid` allows proposer to commit blocks with arbitrarily stale timestamps — (`File: crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` enforces only a one-sided time window on `ProposalInit.timestamp`: it rejects timestamps that are too far **in the future** but applies no lower bound relative to `now`. A malicious proposer can set a block timestamp arbitrarily far in the past (bounded only by the previous block's timestamp), causing every validator to accept and execute the block with a stale timestamp. This corrupts the value returned by the `get_block_timestamp()` syscall for all transactions in that block and causes L1 gas prices to be derived from a historical oracle reading rather than the current one.

### Finding Description

`is_proposal_init_valid` in `validate_proposal.rs` performs two timestamp checks:

```rust
// Lower bound: monotonicity only
if init_proposed.timestamp < last_block_timestamp { ... }

// Upper bound: not too far in the future
if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds { ... }
``` [1](#0-0) 

The configuration parameter `block_timestamp_window_seconds` is documented as "Maximum allowed deviation (seconds) of a proposed block's timestamp from the current time," implying a symmetric window, but only the upper half is enforced. [2](#0-1) 

There is no check of the form `init_proposed.timestamp >= now - block_timestamp_window_seconds`. A proposer can therefore set `init_proposed.timestamp` to any value ≥ `last_block_timestamp`, which may be seconds, hours, or years in the past.

The same one-sided pattern appears in `try_sync`: [3](#0-2) 

After `is_proposal_init_valid` passes, `initiate_validation` forwards the stale timestamp directly to the batcher as `block_info.block_timestamp`: [4](#0-3) 

The batcher then executes all transactions in the block with that stale timestamp, so every `get_block_timestamp()` syscall returns the proposer-chosen past value.

Additionally, the L1 gas price oracle is queried **at the proposed timestamp**: [5](#0-4) 

Because the validator queries the oracle at `init_proposed.timestamp` (not at `now`), the margin check is internally consistent even for a stale timestamp. This means the proposer can legitimately propose historical L1 gas prices that may differ substantially from current market prices, and every validator will accept them.

### Impact Explanation

**High/Critical.** Two concrete corruptions result:

1. **Wrong syscall result**: Every transaction in the block that calls `get_block_timestamp()` receives the proposer-chosen stale value. Time-locked contracts, expiry checks, and any protocol logic that depends on block time will execute against the wrong time, potentially unlocking funds early, bypassing expiry guards, or producing incorrect state transitions. This matches the impact category "Wrong state … or revert result from blockifier/syscall/execution logic for accepted input."

2. **Incorrect L1 gas price / fee accounting**: Because the oracle is queried at the stale timestamp, the L1 gas prices embedded in the block header and used for fee calculation reflect historical market conditions. Users may be over- or under-charged relative to current L1 costs. This matches "Incorrect fee, gas … or L1 gas price effect with economic impact."

### Likelihood Explanation

**Medium.** Any validator that wins a proposer slot can trigger this. In the current single-sequencer deployment the risk is low, but the codebase is explicitly designed for decentralized multi-validator consensus (Tendermint). Once multiple validators are live, any one of them can exploit this on every round they are selected as proposer.

### Recommendation

Add a symmetric lower-bound check in `is_proposal_init_valid`:

```rust
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

Apply the same fix to the `try_sync` timestamp validation in `sequencer_consensus_context.rs`. [6](#0-5) 

### Proof of Concept

1. A validator wins a proposer slot for height H.
2. It constructs a `ProposalInit` with `timestamp = last_block_timestamp` (the minimum allowed value, which may be many seconds/hours/years in the past).
3. It streams the proposal to all validators.
4. Each validator calls `is_proposal_init_valid`:
   - `timestamp >= last_block_timestamp` → **passes** (equality)
   - `timestamp <= now + window` → **passes** (past timestamp is always ≤ now + window)
   - All other checks (height, l1_da_mode, l2_gas_price_fri, starknet_version, L1 gas prices) pass because the oracle is queried at the stale timestamp, making the margin check self-consistent.
5. `initiate_validation` sends `block_info` with the stale timestamp to the batcher.
6. All transactions execute with `get_block_timestamp()` returning the stale value.
7. The block is committed with the stale timestamp embedded in the block hash and all receipts. [7](#0-6) [8](#0-7)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-285)
```rust
#[instrument(level = "warn", skip_all, fields(?proposal_init_validation, ?init_proposed))]
async fn is_proposal_init_valid(
    proposal_init_validation: &ProposalInitValidation,
    init_proposed: &ProposalInit,
    clock: &dyn Clock,
    l1_gas_price_provider: Arc<dyn L1GasPriceProviderClient>,
    gas_price_params: &GasPriceParams,
) -> ValidateProposalResult<()> {
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L443-476)
```rust
async fn initiate_validation(
    batcher: Arc<dyn BatcherClient>,
    state_sync_client: SharedStateSyncClient,
    init: &ProposalInit,
    proposal_id: ProposalId,
    timeout_plus_margin: Duration,
    clock: &dyn Clock,
    compare_retrospective_block_hash: bool,
) -> ValidateProposalResult<()> {
    let chrono_timeout = chrono::Duration::from_std(timeout_plus_margin)
        .expect("Can't convert timeout to chrono::Duration");

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
    debug!("Initiating validate proposal: input={input:?}");
    batcher.validate_block(input.clone()).await.map_err(|err| {
        ValidateProposalError::Batcher(
            format!("Failed to initiate validate proposal {input:?}."),
            err,
        )
    })?;
    Ok(())
}
```

**File:** crates/apollo_consensus_orchestrator_config/src/config.rs (L160-161)
```rust
    /// Maximum allowed deviation (seconds) of a proposed block's timestamp from the current time.
    pub block_timestamp_window_seconds: u64,
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1064-1080)
```rust
        let last_block_timestamp =
            self.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
        let now: u64 = self.deps.clock.unix_now();
        if !(block_number == height
            && timestamp.0 >= last_block_timestamp
            && timestamp.0 <= now + self.config.static_config.block_timestamp_window_seconds)
        {
            warn!(
                "Invalid block info: expected block number {}, got {}, expected timestamp range \
                 [{}, {}], got {}",
                height,
                block_number,
                last_block_timestamp,
                now + self.config.static_config.block_timestamp_window_seconds,
                timestamp.0,
            );
            return false;
```
