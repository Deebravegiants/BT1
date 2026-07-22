### Title
Zero Timestamp Passes Proposal Validation at Genesis — Malicious Proposer Can Commit Block with `BlockTimestamp(0)` - (File: `crates/apollo_consensus_orchestrator/src/validate_proposal.rs`)

### Summary

In `is_proposal_init_valid`, the integer literal `0` is used as a sentinel to represent "no previous block exists" when `previous_proposal_init` is `None`. However, `0` is also a structurally valid `u64` timestamp that passes every timestamp guard in the function. A malicious committee proposer at genesis (or after a restart where `previous_proposal_init` is `None`) can broadcast a `ProposalInit` with `timestamp = 0`, which all honest validators will accept, causing a block with `BlockTimestamp(0)` (Unix epoch, 1 January 1970) to be committed to the chain.

### Finding Description

In `is_proposal_init_valid` the lower-bound for the proposed timestamp is derived as:

```rust
let last_block_timestamp =
    proposal_init_validation.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
if init_proposed.timestamp < last_block_timestamp { … }   // 0 < 0 → false, passes
``` [1](#0-0) 

The upper-bound check is:

```rust
if init_proposed.timestamp > now + proposal_init_validation.block_timestamp_window_seconds { … }
// 0 > ~1_700_000_000 + window → false, passes
``` [2](#0-1) 

Both guards pass for `timestamp = 0`. The same sentinel collision exists in `try_sync`:

```rust
let last_block_timestamp =
    self.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
``` [3](#0-2) 

After passing `is_proposal_init_valid`, the timestamp flows directly into `convert_to_sn_api_block_info`:

```rust
block_timestamp: BlockTimestamp(init.timestamp),   // BlockTimestamp(0)
``` [4](#0-3) 

There is no zero-timestamp guard in `convert_to_sn_api_block_info` (only zero gas-price warnings are present): [5](#0-4) 

The `BlockInfo` with `BlockTimestamp(0)` is then passed to the batcher via `ValidateBlockInput` / `ProposeBlockInput`, and the blockifier's `get_block_timestamp` syscall handler returns it verbatim to every contract executing in that block: [6](#0-5) 

The `ProposalInit` struct carries `timestamp: u64` with no non-zero invariant: [7](#0-6) 

Its `Default` implementation sets `timestamp: Default::default()` (i.e., `0`): [8](#0-7) 

### Impact Explanation

A block committed with `BlockTimestamp(0)` produces:

1. **Wrong syscall result**: every contract in the block that calls `get_block_timestamp()` receives `0` instead of the real wall-clock time. Time-locked contracts, auctions, and expiry checks all observe year 1970.
2. **Wrong block header**: the timestamp field in `BlockHeaderWithoutHash` is `0`, which propagates into the block hash computation and into `previous_proposal_init` for the next height, permanently poisoning the chain's timestamp monotonicity invariant from genesis.
3. **Wrong RPC view**: any RPC call that reads the committed block's timestamp returns `0`.

This matches the Critical impact class: *"Wrong state, receipt, event, L1 message, class hash, storage value, or revert result from blockifier/syscall/execution logic for accepted input."*

### Likelihood Explanation

The condition requires `previous_proposal_init == None`, which holds at genesis (height 0) and after any restart or revert that clears the context. The attacker must be the designated proposer for that height/round, which is a normal committee role, not a special privilege. Because all honest validators run the same `is_proposal_init_valid` logic and it passes for `timestamp = 0`, they will vote for the proposal and consensus will commit the block. No out-of-band coordination is needed.

### Recommendation

Replace the `map_or(0, …)` sentinel with an explicit lower-bound that is independent of the sentinel value. Two complementary fixes:

1. **Reject timestamp = 0 unconditionally** in `is_proposal_init_valid`:
   ```rust
   if init_proposed.timestamp == 0 {
       return Err(ValidateProposalError::InvalidProposalInit(…, "timestamp must be non-zero".into()));
   }
   ```

2. **Add a minimum reasonable timestamp** (e.g., the chain's configured genesis time) so that even a non-zero but absurdly old timestamp is rejected.

Apply the same fix to the `try_sync` timestamp validation in `sequencer_consensus_context.rs`.

### Proof of Concept

1. A committee member is the designated proposer for `height = 0, round = 0` (genesis).
2. It crafts a `ProposalInit` with all valid fields except `timestamp = 0`.
3. It broadcasts the proposal stream to all validators.
4. Each validator calls `is_proposal_init_valid`:
   - `last_block_timestamp = 0` (sentinel, `previous_proposal_init` is `None`)
   - Check 1: `0 < 0` → `false` → passes
   - Check 2: `0 > now + window` → `false` → passes
   - All other checks (height, l1_da_mode, l2_gas_price, gas price margins, version_constant_commitment) are independent of the timestamp and pass normally.
5. Each validator calls `initiate_validation` → `convert_to_sn_api_block_info` → `BlockTimestamp(0)` is passed to the batcher.
6. The batcher executes the block with `block_timestamp = 0`.
7. Any contract calling `get_block_timestamp()` receives `0`.
8. Consensus reaches quorum; `decision_reached` commits the block with `BlockTimestamp(0)` permanently.
9. `previous_proposal_init` for height 1 now carries `timestamp = 0`, which is indistinguishable from the "no previous block" sentinel, breaking monotonicity enforcement for all subsequent blocks.

### Citations

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L261-272)
```rust
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
```

**File:** crates/apollo_consensus_orchestrator/src/validate_proposal.rs (L273-285)
```rust
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

**File:** crates/apollo_consensus_orchestrator/src/sequencer_consensus_context.rs (L1064-1069)
```rust
        let last_block_timestamp =
            self.previous_proposal_init.as_ref().map_or(0, |info| info.timestamp);
        let now: u64 = self.deps.clock.unix_now();
        if !(block_number == height
            && timestamp.0 >= last_block_timestamp
            && timestamp.0 <= now + self.config.static_config.block_timestamp_window_seconds)
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L303-317)
```rust
) -> Result<starknet_api::block::BlockInfo, StarknetApiError> {
    if init.l1_gas_price_fri.0 == 0
        || init.l1_gas_price_wei.0 == 0
        || init.l1_data_gas_price_fri.0 == 0
        || init.l1_data_gas_price_wei.0 == 0
        || init.l2_gas_price_fri.0 == 0
    {
        warn!("Zero gas price detected in block info: {:?}", init);
    }

    let l1_gas_price_fri = NonzeroGasPrice::new(init.l1_gas_price_fri)?;
    let l1_data_gas_price_fri = NonzeroGasPrice::new(init.l1_data_gas_price_fri)?;
    let l1_gas_price_wei = NonzeroGasPrice::new(init.l1_gas_price_wei)?;
    let l1_data_gas_price_wei = NonzeroGasPrice::new(init.l1_data_gas_price_wei)?;
    let l2_gas_price_fri = NonzeroGasPrice::new(init.l2_gas_price_fri)?;
```

**File:** crates/apollo_consensus_orchestrator/src/utils.rs (L329-332)
```rust
    Ok(starknet_api::block::BlockInfo {
        block_number: init.height,
        block_timestamp: BlockTimestamp(init.timestamp),
        sequencer_address: init.builder,
```

**File:** crates/blockifier/src/execution/deprecated_syscalls/hint_processor.rs (L689-707)
```rust
    fn get_block_timestamp(
        _request: GetBlockTimestampRequest,
        _vm: &mut VirtualMachine,
        syscall_handler: &mut Self,
    ) -> DeprecatedSyscallResult<GetBlockTimestampResponse> {
        let versioned_constants = syscall_handler.context.versioned_constants();
        let block_timestamp = syscall_handler.get_block_info().block_timestamp;
        let block_timestamp = match syscall_handler.execution_mode() {
            ExecutionMode::Validate => {
                let validate_timestamp_rounding =
                    versioned_constants.get_validate_timestamp_rounding();
                BlockTimestamp(
                    (block_timestamp.0 / validate_timestamp_rounding) * validate_timestamp_rounding,
                )
            }
            ExecutionMode::Execute => block_timestamp,
        };
        Ok(GetBlockTimestampResponse { block_timestamp })
    }
```

**File:** crates/apollo_protobuf/src/consensus.rs (L104-106)
```rust
    /// Block timestamp.
    pub timestamp: u64,
    /// Address of the one who builds/sequences the block.
```

**File:** crates/apollo_protobuf/src/consensus.rs (L145-164)
```rust
impl Default for ProposalInit {
    fn default() -> Self {
        ProposalInit {
            height: Default::default(),
            round: Default::default(),
            valid_round: Default::default(),
            proposer: ContractAddress::from(DEFAULT_VALIDATOR_ID),
            builder: ContractAddress::from(DEFAULT_VALIDATOR_ID),
            timestamp: Default::default(),
            l1_da_mode: L1DataAvailabilityMode::Calldata,
            l2_gas_price_fri: Default::default(),
            l1_gas_price_fri: Default::default(),
            l1_data_gas_price_fri: Default::default(),
            l1_gas_price_wei: Default::default(),
            l1_data_gas_price_wei: Default::default(),
            starknet_version: starknet_api::block::StarknetVersion::LATEST,
            version_constant_commitment: Default::default(),
            fee_proposal_fri: Default::default(),
        }
    }
```
