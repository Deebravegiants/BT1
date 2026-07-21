### Title
Queued Future-Round Proposals Bypass Timestamp Freshness Invariant, Enabling Stale Block Timestamps and Incorrect L1 Gas Prices - (File: crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs)

### Summary

When a `ProposalInit` arrives for a future round, `SequencerConsensusContext::validate_proposal` stores it in `queued_proposals` **without any timestamp validation**. When the round is eventually reached (potentially many seconds later), the proposal is dequeued and validated with the current clock, but `is_proposal_init_valid` only checks that the timestamp is not too far in the **future** (`timestamp <= now + window`). A stale timestamp that was valid at queue time trivially passes this check because it is now in the past. The block is then committed with a stale timestamp and L1 gas prices fetched at that stale timestamp, violating the `block_timestamp_window_seconds = 1` freshness invariant.

### Finding Description

**Queue path (no timestamp check):**

When `init.round > self.current_round`, the proposal is stored verbatim:

```rust
std::cmp::Ordering::Greater => {
    trace!("Queueing proposal for future round.");
    self.queued_proposals
        .insert(init.round, ((init, timeout, content_receiver), fin_sender));
    fin_receiver
}
``` [1](#0-0) 

No timestamp check is performed at this point.

**Dequeue path (stale timestamp accepted):**

When `set_height_and_round` advances to the queued round, the proposal is dequeued and passed to `validate_current_round_proposal`: [2](#0-1) 

**Timestamp check in `is_proposal_init_valid`:**

```rust
let now: u64 = clock.unix_now();
let last_block_timestamp =
    proposal_init_validation.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
if init_proposed.timestamp < last_block_timestamp {
    return Err(...);  // only rejects if older than previous block
}
if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds {
    return Err(...);  // only rejects if too far in the future
}
``` [3](#0-2) 

For a proposal queued at time `T_queue` with timestamp `T_queue`, when dequeued at `T_dequeue = T_queue + Δ`:
- `T_queue >= last_block_timestamp` → **passes** (same height, same previous block)
- `T_queue <= T_dequeue + 1s` → **passes** (T_queue is now in the past)

The stale timestamp is accepted unconditionally.

**L1 gas prices are fetched at the stale timestamp:**

```rust
let (l1_gas_prices_fri, l1_gas_prices_wei) = get_l1_prices_in_fri_and_wei(
    l1_gas_price_provider,
    init_proposed.timestamp,   // ← stale timestamp
    proposal_init_validation.previous_proposal_init.as_ref(),
    gas_price_params,
).await;
``` [4](#0-3) 

The validator's oracle is queried at the stale timestamp. If the oracle returns consistent historical data at that timestamp (matching what the proposer used), the margin check passes and the block is committed with L1 gas prices from the stale timestamp.

**Production window is 1 second:** [5](#0-4) 

The `block_timestamp_window_seconds = 1` is designed to ensure blocks carry fresh timestamps. This invariant is completely bypassed for queued proposals.

### Impact Explanation

A block committed with a stale timestamp carries L1 gas prices (`l1_gas_price_fri`, `l1_data_gas_price_fri`, `l1_gas_price_wei`, `l1_data_gas_price_wei`) that were valid at the stale timestamp but may differ significantly from current market prices. These prices are embedded in the block header and used for fee calculations for every transaction in the block. A proposer who knows L1 gas prices will be lower at a future time can pre-build a proposal with that favorable timestamp, queue it for a future round, and have it committed with artificially low gas prices — reducing fees collected by the network. Conversely, a proposer could lock in high gas prices from a past spike.

The corrupted values are: `init_proposed.l1_gas_price_fri`, `init_proposed.l1_data_gas_price_fri`, `init_proposed.l1_gas_price_wei`, `init_proposed.l1_data_gas_price_wei`, and `init_proposed.timestamp` in the committed block header.

This matches: **High. RPC execution, fee estimation, tracing, simulation, or pending view returns an authoritative-looking wrong value** and **Critical. Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact.**

### Likelihood Explanation

The trigger is the normal Tendermint round-advance mechanism. A proposer for round R sends its proposal early (before rounds before R complete). Validators queue it. Rounds before R time out. When round R is reached, the stale proposal is dequeued. No malicious behavior is strictly required — this is a natural protocol flow. The staleness window equals the sum of timeouts for all failed rounds before R, which can be tens of seconds to minutes in a degraded network.

### Recommendation

1. **Record the wall-clock time when a proposal is queued** and add a staleness check when dequeuing: reject proposals whose timestamp is older than `now - max_allowed_staleness` (e.g., `now - block_timestamp_window_seconds`).

2. **Re-run `is_proposal_init_valid` at dequeue time** using the current clock, not the clock at queue time. This is already done for the `l2_gas_price_fri` and `fee_actual` fields (which are re-read from `self` at dequeue time), but the timestamp freshness check uses the stale `init.timestamp` without a lower-bound freshness guard.

3. Alternatively, **add a `queued_at` field** to the queued entry and reject proposals where `now - queued_at > max_round_duration`.

### Proof of Concept

```
Round 0: Proposer P (proposer for round 3) sends ProposalInit{
    round: 3,
    timestamp: T,          // valid at T (within 1s of now)
    l1_gas_price_fri: X,   // L1 price at time T
}
→ Validators queue it in queued_proposals[round=3]

Round 0 times out (no quorum). Round 1 times out. Round 2 times out.
Elapsed time: Δ = 3 × round_timeout (e.g., 30 seconds)

Round 3 reached: set_height_and_round(height, round=3)
→ Dequeues ProposalInit{timestamp: T, l1_gas_price_fri: X}
→ is_proposal_init_valid checks:
    T >= last_block_timestamp  ✓ (same height)
    T <= (T+Δ) + 1s            ✓ (T is 30s in the past, trivially passes)
    L1 prices at T match X     ✓ (oracle returns historical data at T)
→ Block committed with timestamp T (30s stale) and L1 gas prices from T
→ All transactions in the block pay fees based on 30-second-old L1 gas prices
``` [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L868-912)
```rust
        match init.round.cmp(&self.current_round) {
            std::cmp::Ordering::Less => {
                trace!("Dropping proposal from past round");
                fin_receiver
            }
            std::cmp::Ordering::Greater => {
                trace!("Queueing proposal for future round.");
                self.queued_proposals
                    .insert(init.round, ((init, timeout, content_receiver), fin_sender));
                fin_receiver
            }
            std::cmp::Ordering::Equal => {
                let proposal_init_validation = ProposalInitValidation {
                    height: init.height,
                    block_timestamp_window_seconds: self
                        .config
                        .static_config
                        .block_timestamp_window_seconds,
                    previous_proposal_init: self.previous_proposal_init.clone(),
                    l1_da_mode: self.l1_da_mode,
                    l2_gas_price_fri: self
                        .config
                        .dynamic_config
                        .override_l2_gas_price_fri
                        .map(GasPrice)
                        .unwrap_or(self.l2_gas_price),
                    starknet_version: StarknetVersion::LATEST,
                    fee_actual: compute_fee_actual(
                        &self.fee_proposals_window,
                        init.height,
                        VersionedConstants::latest_constants().fee_proposal_window_size,
                    ),
                };
                self.validate_current_round_proposal(
                    init,
                    proposal_init_validation,
                    timeout,
                    self.config.static_config.validate_proposal_margin_millis,
                    content_receiver,
                    fin_sender,
                )
                .await;
                fin_receiver
            }
        }
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1158-1207)
```rust
        let mut to_process = None;
        while let Some(entry) = self.queued_proposals.first_entry() {
            match self.current_round.cmp(entry.key()) {
                // The queued proposal is for a past round; drop it and keep scanning.
                std::cmp::Ordering::Greater => {
                    entry.remove();
                }
                // The queued proposal is for the current round; take it and stop.
                std::cmp::Ordering::Equal => {
                    to_process = Some(entry.remove());
                    break;
                }
                // The queued proposal is for a future round; preserve it for later.
                std::cmp::Ordering::Less => break,
            }
        }
        // Validate the proposal for the current round if exists.
        let Some(((init, timeout, content), fin_sender)) = to_process else {
            return Ok(());
        };
        let proposal_init_validation = ProposalInitValidation {
            height: init.height,
            block_timestamp_window_seconds: self
                .config
                .static_config
                .block_timestamp_window_seconds,
            previous_proposal_init: self.previous_proposal_init.clone(),
            l1_da_mode: self.l1_da_mode,
            l2_gas_price_fri: self
                .config
                .dynamic_config
                .override_l2_gas_price_fri
                .map(GasPrice)
                .unwrap_or(self.l2_gas_price),
            starknet_version: StarknetVersion::LATEST,
            fee_actual: compute_fee_actual(
                &self.fee_proposals_window,
                init.height,
                VersionedConstants::latest_constants().fee_proposal_window_size,
            ),
        };
        self.validate_current_round_proposal(
            init,
            proposal_init_validation,
            timeout,
            self.config.static_config.validate_proposal_margin_millis,
            content,
            fin_sender,
        )
        .await;
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L75-85)
```rust
pub(crate) struct ProposalInitValidation {
    pub height: BlockNumber,
    pub block_timestamp_window_seconds: u64,
    pub previous_proposal_init: Option<PreviousProposalInitInfo>,
    pub l1_da_mode: L1DataAvailabilityMode,
    pub l2_gas_price_fri: GasPrice,
    pub starknet_version: StarknetVersion,
    /// fee_actual from the sliding window. `None` until the window has accumulated
    /// `fee_proposal_window_size` entries (startup / near-genesis).
    pub fee_actual: Option<GasPrice>,
}
```

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

**File:** crates/apollo_node/resources/config_schema.json (L2787-2791)
```json
  "consensus_manager_config.context_config.static_config.block_timestamp_window_seconds": {
    "description": "Maximum allowed deviation (seconds) of a proposed block's timestamp from the current time.",
    "privacy": "Public",
    "value": 1
  },
```
