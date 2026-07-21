### Title
Unvalidated `builder` Field in `ProposalInit` Allows Malicious Proposer to Redirect Block Fees to Arbitrary Address - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

`is_proposal_init_valid` validates many fields of `ProposalInit` but never checks `init.builder`. The `builder` field is passed directly to `convert_to_sn_api_block_info` as `sequencer_address`, which is the address that receives all transaction fees in the block. A Byzantine proposer can set `builder` to any address, causing the validator to accept the proposal and commit a block whose `sequencer_address` — and therefore all fee receipts — belongs to the attacker.

### Finding Description

`ProposalInit` carries two identity fields:

- `proposer: ContractAddress` — the consensus participant who proposes the block
- `builder: ContractAddress` — the node that builds/sequences the block; becomes `sequencer_address` in `BlockInfo` [1](#0-0) 

`is_proposal_init_valid` validates `height`, `l1_da_mode`, `l2_gas_price_fri`, `starknet_version`, `version_constant_commitment`, all four L1 gas price fields, `timestamp`, and `fee_proposal_fri`. It does **not** validate `builder`. [2](#0-1) 

`ProposalInitValidation` — the struct that carries the validator's reference values — has no `builder` field, so there is no reference value to check against: [3](#0-2) 

After `is_proposal_init_valid` passes, `initiate_validation` calls `convert_to_sn_api_block_info(&init)` which maps `init.builder` directly to `sequencer_address`: [4](#0-3) 

The resulting `BlockInfo` (with the attacker-controlled `sequencer_address`) is forwarded to the batcher via `ValidateBlockInput.block_info`. The batcher executes all transactions under that `sequencer_address`, collects fees to it, and computes `PartialBlockHash` from it. Because both proposer and validator use the same `init.builder` to compute the hash, the `ProposalCommitment` matches and the final check passes: [5](#0-4) 

The block is then committed with the attacker's address as `sequencer_address`.

The legitimate proposer sets `builder` from a configured `builder_address`: [6](#0-5) 

But nothing prevents a Byzantine proposer from substituting any address in that field before broadcasting.

### Impact Explanation

All transaction fees in the block are transferred to `sequencer_address` (i.e., `init.builder`). A Byzantine proposer who wins a round can set `builder` to an attacker-controlled address, stealing 100% of fees for that block. Additionally, `sequencer_address` is part of the block header and feeds into the block hash / state commitment, so the committed state is permanently wrong for that block. This matches the **Critical** impact: "Incorrect fee, gas, bouncer, resource accounting, refund, balance, or L1 gas price effect with economic impact."

### Likelihood Explanation

Any consensus participant who is elected proposer for a round can trigger this. In a BFT system tolerating up to `f < n/3` Byzantine nodes, a Byzantine proposer can act on every round it is elected. No special privilege beyond being the current-round proposer is required; the attack is a single-field substitution in the outgoing `ProposalInit` message.

### Recommendation

Add a `builder: ContractAddress` field to `ProposalInitValidation` and check it in `is_proposal_init_valid`:

```rust
if init_proposed.builder != proposal_init_validation.builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!(
            "builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.builder, init_proposed.builder
        ),
    ));
}
```

The validator's `builder` reference value should be populated from the node's own configured `builder_address` when constructing `ProposalInitValidation` in `validate_current_round_proposal`. [7](#0-6) 

### Proof of Concept

1. Byzantine node wins proposer election for round R at height H.
2. In `initiate_build`, it substitutes `builder: attacker_address` instead of its configured `builder_address`.
3. It broadcasts `ProposalPart::Init(init)` with the tampered `builder`.
4. Honest validators call `validate_proposal` → `is_proposal_init_valid`. No check on `builder` exists; validation passes.
5. `initiate_validation` calls `convert_to_sn_api_block_info(&init)` → `sequencer_address = attacker_address`.
6. The batcher executes all transactions with `sequencer_address = attacker_address`, collecting fees there.
7. `PartialBlockHash` is computed from the block header containing `attacker_address`; both proposer and validator agree on this hash.
8. `built_block == received_fin.proposal_commitment` → proposal accepted.
9. `decision_reached` commits the block; `attacker_address` permanently holds all fees from block H.

### Citations

**File:** crates/apollo_protobuf/src/consensus.rs (L102-107)
```rust
    /// Address of the one who proposed the block in consensus.
    pub proposer: ContractAddress,
    /// Block timestamp.
    pub timestamp: u64,
    /// Address of the one who builds/sequences the block.
    pub builder: ContractAddress,
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L74-85)
```rust
#[derive(Clone, Debug)]
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L243-247)
```rust
    // TODO(matan): Switch to signature validation.
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
    }
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L252-321)
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
    }
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-333)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
```

**File:** crates/apollo_consensus_orchestrator/src/build_proposal.rs (L169-175)
```rust
    let init = ProposalInit {
        height: args.build_param.height,
        round: args.build_param.round,
        valid_round: args.build_param.valid_round,
        proposer: args.build_param.proposer,
        builder: args.builder_address,
        timestamp,
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1213-1244)
```rust
    async fn validate_current_round_proposal(
        &mut self,
        init: ProposalInit,
        proposal_init_validation: ProposalInitValidation,
        timeout: Duration,
        batcher_timeout_margin: Duration,
        content_receiver: mpsc::Receiver<ProposalPart>,
        fin_sender: oneshot::Sender<ProposalCommitment>,
    ) {
        let proposal_id = ProposalId(self.proposal_id);
        self.proposal_id += 1;
        info!(?timeout, %proposal_id, proposer=%init.proposer, round=self.current_round, "Start validating proposal");

        let cancel_token = CancellationToken::new();
        let cancel_token_clone = cancel_token.clone();
        let gas_price_params = make_gas_price_params(&self.config.dynamic_config);
        let args = ProposalValidateArguments {
            deps: self.deps.clone(),
            init,
            proposal_init_validation,
            proposal_id,
            timeout,
            batcher_timeout_margin,
            valid_proposals: Arc::clone(&self.valid_proposals),
            content_receiver,
            gas_price_params,
            cancel_token: cancel_token_clone,
            compare_retrospective_block_hash: self
                .config
                .dynamic_config
                .compare_retrospective_block_hash,
        };
```
