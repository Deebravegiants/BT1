### Title
Unvalidated `builder` Address in `ProposalInit` Allows Proposer to Redirect Sequencer Fees — (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

---

### Summary

The `builder` field of `ProposalInit` is never checked against any expected value during proposal validation. A malicious-but-legitimately-selected proposer can set `builder` to an arbitrary address. Validators re-execute the block using the proposer-supplied `builder` as `sequencer_address`, so the resulting `partial_block_hash` and `ProposalCommitment` match the proposer's fin, and the proposal is accepted. All transaction fees for that block are paid to the attacker-controlled address.

---

### Finding Description

`ProposalInit` carries a `builder` field (proto field 6) that `convert_to_sn_api_block_info` maps directly to `sequencer_address` in `BlockInfo`:

```rust
sequencer_address: init.builder,
``` [1](#0-0) 

The proposer sets this field from its own static config:

```rust
builder_address: self.config.static_config.builder_address,
``` [2](#0-1) 

The `ProposalInitValidation` struct — the sole source of reference values used by `is_proposal_init_valid` — contains no `builder` field: [3](#0-2) 

`is_proposal_init_valid` validates `height`, `l1_da_mode`, `l2_gas_price_fri`, all four L1 gas prices, `starknet_version`, `version_constant_commitment`, `timestamp`, and `fee_proposal_fri`, but never `builder`: [4](#0-3) 

The only other field-level check in the manager validates `init.proposer` against the committee-derived proposer identity — not `init.builder`: [5](#0-4) 

After `is_proposal_init_valid` passes, `initiate_validation` calls `convert_to_sn_api_block_info(init)` and passes the resulting `BlockInfo` (containing the attacker's `sequencer_address`) to the batcher: [6](#0-5) 

The batcher executes all transactions with the attacker's address as `sequencer_address`. The resulting `partial_block_hash` is then wrapped into a `ProposalCommitment` via `proposal_commitment_from`: [7](#0-6) 

Because the validator used the proposer's own `builder` value throughout, the validator's commitment equals the proposer's fin commitment, so the final check passes: [8](#0-7) 

The TODO comment in the proposer path acknowledges that `builder_address` should eventually come from the committee but currently does not: [2](#0-1) 

---

### Impact Explanation

`sequencer_address` in Starknet's execution model is the address that receives all transaction fees and is returned by the `get_sequencer_address` syscall. By setting `builder` to an attacker-controlled address, the malicious proposer:

1. Diverts all fee payments for the block to their address — a direct, quantifiable economic loss.
2. Causes `get_sequencer_address` to return the wrong address, corrupting any contract logic that branches on it.
3. Persists the wrong `sequencer_address` in the block header committed to L1.

This matches the allowed impact: **Critical — incorrect fee/balance effect with economic impact**.

---

### Likelihood Explanation

The attack requires being selected as the round proposer, which is a normal, unprivileged event for any validator in the committee. No special access beyond committee membership is needed. The proposer simply sets `builder` to a different address before calling `propose_block`; no signature forgery or network interception is required.

---

### Recommendation

Add `builder` (or an equivalent `expected_builder_address`) to `ProposalInitValidation` and reject any proposal whose `init.builder` does not equal the locally-configured or committee-derived expected value, analogous to how `l1_da_mode` and `l2_gas_price_fri` are already enforced:

```rust
if init_proposed.builder != proposal_init_validation.expected_builder {
    return Err(ValidateProposalError::InvalidProposalInit(
        init_proposed.clone(),
        proposal_init_validation.clone(),
        format!("builder mismatch: expected={:?}, proposed={:?}",
            proposal_init_validation.expected_builder, init_proposed.builder),
    ));
}
```

The expected value should be sourced from the committee once available (as the existing TODO notes), or from `ContextStaticConfig::builder_address` in the interim.

---

### Proof of Concept

1. Attacker is legitimately selected as proposer for height `H`, round `R`.
2. Attacker modifies `initiate_build` (or intercepts the outbound `ProposalInit`) to set `builder = ATTACKER_ADDR`.
3. Attacker calls `propose_block` with `block_info.sequencer_address = ATTACKER_ADDR`; the batcher executes all transactions, paying fees to `ATTACKER_ADDR`, and returns `partial_block_hash = H_attack`.
4. Attacker sends `ProposalPart::Init` with `builder = ATTACKER_ADDR` and `ProposalPart::Fin` with `proposal_commitment = proposal_commitment_from(H_attack, fee_proposal)`.
5. Each validator calls `is_proposal_init_valid` — no check on `builder` — then `initiate_validation` → `convert_to_sn_api_block_info(init)` → `sequencer_address = ATTACKER_ADDR`.
6. Each validator's batcher executes with `ATTACKER_ADDR`, produces the same `H_attack`, and returns the same `ProposalCommitment`.
7. The commitment check `built_block != received_fin.proposal_commitment` passes.
8. Consensus reaches decision; all fees for block `H` are credited to `ATTACKER_ADDR`; the block header persists `sequencer_address = ATTACKER_ADDR` on-chain.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-333)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
        gas_prices: GasPrices {
```

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L806-808)
```rust
            // TODO(Asmaa): Get it from committee once we have it.
            builder_address: self.config.static_config.builder_address,
            cancel_token,
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L244-247)
```rust
    if built_block != received_fin.proposal_commitment {
        CONSENSUS_PROPOSAL_FIN_MISMATCH.increment(1);
        return Err(ValidateProposalError::ProposalFinMismatch);
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

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L455-474)
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
    debug!("Initiating validate proposal: input={input:?}");
    batcher.validate_block(input.clone()).await.map_err(|err| {
        ValidateProposalError::Batcher(
            format!("Failed to initiate validate proposal {input:?}."),
            err,
        )
    })?;
```

**File:** crates/apollo_consensus/src/manager.rs (L860-866)
```rust
                if proposer != init.proposer {
                    warn!(
                        "Invalid proposer for height {} and round {}: expected {:?}, got {:?}",
                        init.height.0, init.round, proposer, init.proposer
                    );
                    return Ok(VecDeque::new());
                }
```

**File:** crates/apollo_consensus_orchestrator/src/dynamic_gas_price/mod.rs (L163-171)
```rust
pub(crate) fn proposal_commitment_from(
    partial: PartialBlockHash,
    fee_proposal: Option<GasPrice>,
) -> ProposalCommitment {
    let Some(fee_proposal) = fee_proposal else {
        return ProposalCommitment(partial.0);
    };
    ProposalCommitment(Poseidon::hash_array(&[partial.0, Felt::from(fee_proposal.0)]))
}
```
