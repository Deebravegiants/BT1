### Title
`ProposalInitValidation` Not Snapshotted at Queue Time Allows Config Drift to Corrupt Proposal Acceptance Criteria — (`crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs`)

### Summary

When a `ProposalInit` arrives for a future round it is stored raw in `queued_proposals` without capturing the validator's current `ProposalInitValidation` snapshot. The validation criteria (`l2_gas_price_fri`, `fee_actual`) are computed only later, when `set_height_and_round` advances to that round and calls `update_dynamic_config()`. If the dynamic config changes between queue time and dequeue time, the validator applies a different reference value than was in effect when the proposal was received, causing valid proposals to be rejected or proposals carrying a wrong gas price to be accepted.

### Finding Description

**Queue path (no snapshot taken):**

In `validate_proposal`, when `init.round > self.current_round`, the proposal is stored without computing `ProposalInitValidation`:

```rust
std::cmp::Ordering::Greater => {
    self.queued_proposals
        .insert(init.round, ((init, timeout, content_receiver), fin_sender));
    fin_receiver
}
``` [1](#0-0) 

**Dequeue path (snapshot computed with potentially changed state):**

When `set_height_and_round` advances to the queued round, it first calls `update_dynamic_config()` (line 1156), then builds `ProposalInitValidation` from the **post-update** state:

```rust
self.update_dynamic_config().await;
// ...
let proposal_init_validation = ProposalInitValidation {
    l2_gas_price_fri: self
        .config
        .dynamic_config
        .override_l2_gas_price_fri
        .map(GasPrice)
        .unwrap_or(self.l2_gas_price),
    fee_actual: compute_fee_actual(
        &self.fee_proposals_window, init.height, ...),
    ...
};
``` [2](#0-1) 

**Exact equality check that breaks:**

`is_proposal_init_valid` enforces an exact equality on `l2_gas_price_fri`:

```rust
if !(init_proposed.height == proposal_init_validation.height
    && init_proposed.l1_da_mode == proposal_init_validation.l1_da_mode
    && init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri)
{
    return Err(ValidateProposalError::InvalidProposalInit(...));
}
``` [3](#0-2) [4](#0-3) 

The same path is taken for the current-round case in `validate_proposal`, but there `update_dynamic_config` has not yet been called for that round, so the snapshot is consistent. The bug is exclusive to the queued-proposal dequeue path.

### Impact Explanation

Two failure modes arise:

1. **Liveness / valid proposal rejected (High):** The proposer correctly sets `l2_gas_price_fri = P` (the value in effect when the proposal was broadcast). The validator queues it. Before the round advances, an operator pushes a config update that sets `override_l2_gas_price_fri = Q ≠ P`. When the validator dequeues, it computes `proposal_init_validation.l2_gas_price_fri = Q`, the exact-equality check fails, and the proposal is rejected. Consensus must restart from a new round.

2. **Safety / wrong gas price committed (Critical):** A proposer who can anticipate the upcoming config value `Q` broadcasts a proposal with `l2_gas_price_fri = Q` while the current reference is `P`. The validator queues it. After the config update, the validator dequeues and accepts the proposal because `Q == Q`. The block is executed with gas price `Q` instead of the protocol-correct `P`, corrupting fee calculations for every transaction in the block. The wrong `l2_gas_price_fri` propagates into `convert_to_sn_api_block_info` and into the batcher's `ValidateBlockInput`, so the blockifier executes all transactions with the wrong L2 gas price. [5](#0-4) [6](#0-5) 

### Likelihood Explanation

The trigger requires two concurrent conditions: (a) a proposal arriving for a future round (normal Tendermint behavior during network delays or round skips) and (b) a dynamic config update between rounds (operator-driven, but routine during upgrades or gas-price policy changes). The liveness failure is reachable in any deployment that uses the config manager. The safety failure requires the proposer to predict the incoming config value, which is feasible when config changes are announced or when the proposer and operator are the same entity.

### Recommendation

Compute and store `ProposalInitValidation` at queue time, not at dequeue time. Change the queued-proposal storage type from `(ProposalInit, Duration, Receiver)` to `(ProposalInit, ProposalInitValidation, Duration, Receiver)`, and populate it in the `Ordering::Greater` branch of `validate_proposal` using the same logic already used in the `Ordering::Equal` branch (lines 880–900). The dequeue path in `set_height_and_round` should then use the stored snapshot rather than recomputing it after `update_dynamic_config`. [7](#0-6) 

### Proof of Concept

```
Height H, round 0:
  - self.l2_gas_price = 8_000_000_000 FRI
  - override_l2_gas_price_fri = None
  - Proposer broadcasts ProposalInit { round: 1, l2_gas_price_fri: 8_000_000_000 }
  - Validator calls validate_proposal(init_round_1) → queued (round 1 > current round 0)
  - No ProposalInitValidation is captured.

Round 0 times out → set_height_and_round(H, 1) is called:
  - update_dynamic_config() fetches new config:
      override_l2_gas_price_fri = Some(9_000_000_000)
  - Queued proposal for round 1 is dequeued.
  - ProposalInitValidation is built:
      l2_gas_price_fri = 9_000_000_000  ← new config value
  - is_proposal_init_valid checks:
      init.l2_gas_price_fri (8_000_000_000) != validation.l2_gas_price_fri (9_000_000_000)
  - → InvalidProposalInit error; valid proposal rejected; consensus stalls.
``` [8](#0-7) [9](#0-8)

### Citations

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L860-912)
```rust
    async fn validate_proposal(
        &mut self,
        init: ProposalInit,
        timeout: Duration,
        content_receiver: mpsc::Receiver<Self::ProposalPart>,
    ) -> oneshot::Receiver<ProposalCommitment> {
        assert_eq!(Some(init.height), self.current_height);
        let (fin_sender, fin_receiver) = oneshot::channel();
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1145-1209)
```rust
        if round == self.current_round {
            return Ok(());
        }
        assert!(
            round > self.current_round,
            "round {} is not greater than current round {}",
            round,
            self.current_round
        );
        self.interrupt_active_proposal().await;
        self.current_round = round;
        self.update_dynamic_config().await;

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
        Ok(())
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-320)
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
    if init_proposed.starknet_version != proposal_init_validation.starknet_version {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "starknet_version mismatch: expected={:?}, proposed={:?}",
                proposal_init_validation.starknet_version, init_proposed.starknet_version
            ),
        ));
    }
    // `version_constant_commitment` is proposer-supplied (network-derived). It is not yet a real
    // commitment (see `expected_version_constant_commitment`): the only valid value is the
    // sentinel, so reject anything else. Enforcing the same value the proposer emits keeps the two
    // sides in lockstep, so a real value cannot ship on one side without the other.
    let expected_commitment = expected_version_constant_commitment();
    if init_proposed.version_constant_commitment != expected_commitment {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            format!(
                "version_constant_commitment mismatch: expected={expected_commitment:?}, \
                 proposed={:?}",
                init_proposed.version_constant_commitment
            ),
        ));
    }
    if !(init_proposed.height == proposal_init_validation.height
        && init_proposed.l1_da_mode == proposal_init_validation.l1_da_mode
        && init_proposed.l2_gas_price_fri == proposal_init_validation.l2_gas_price_fri)
    {
        return Err(ValidateProposalError::InvalidProposalInit(
            init_proposed.clone(),
            proposal_init_validation.clone(),
            "ProposalInit validation failed".to_string(),
        ));
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

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L155-216)
```rust
async fn initiate_build(args: &mut ProposalBuildArguments) -> BuildProposalResult<ProposalInit> {
    let timestamp = get_proposal_timestamp(
        args.override_timestamp,
        args.deps.batcher.as_ref(),
        args.deps.clock.as_ref(),
    )
    .await;
    let (l1_prices_fri, l1_prices_wei) = get_l1_prices_in_fri_and_wei(
        args.deps.l1_gas_price_provider.clone(),
        timestamp,
        args.previous_proposal_init.as_ref(),
        &args.gas_price_params,
    )
    .await;
    let init = ProposalInit {
        height: args.build_param.height,
        round: args.build_param.round,
        valid_round: args.build_param.valid_round,
        proposer: args.build_param.proposer,
        builder: args.builder_address,
        timestamp,
        l1_da_mode: args.l1_da_mode,
        l2_gas_price_fri: args.l2_gas_price,
        l1_gas_price_wei: l1_prices_wei.l1_gas_price,
        l1_data_gas_price_wei: l1_prices_wei.l1_data_gas_price,
        l1_gas_price_fri: l1_prices_fri.l1_gas_price,
        l1_data_gas_price_fri: l1_prices_fri.l1_data_gas_price,
        starknet_version: starknet_api::block::StarknetVersion::LATEST,
        // TODO(Asmaa): Put the real value once we have it.
        // Sentinel until then; see `expected_version_constant_commitment` for why this is the
        // single source of truth shared with the validator.
        version_constant_commitment: expected_version_constant_commitment(),
        fee_proposal_fri: Some(args.fee_proposal),
    };

    let retrospective_block_hash = wait_for_retrospective_block_hash(
        args.deps.batcher.clone(),
        args.deps.state_sync_client.clone(),
        &init,
        args.deps.clock.as_ref(),
        args.retrospective_block_hash_deadline,
        args.retrospective_block_hash_retry_interval_millis,
        args.compare_retrospective_block_hash,
    )
    .await?;

    let build_proposal_input = ProposeBlockInput {
        proposal_id: args.proposal_id,
        deadline: args.batcher_deadline,
        retrospective_block_hash,
        block_info: convert_to_sn_api_block_info(&init)?,
        proposal_round: args.proposal_round,
    };
    debug!("Initiating build proposal: {build_proposal_input:?}");
    args.deps.batcher.propose_block(build_proposal_input.clone()).await.map_err(|err| {
        BuildProposalError::Batcher(
            format!("Failed to initiate build proposal {build_proposal_input:?}."),
            err,
        )
    })?;
    Ok(init)
}
```
