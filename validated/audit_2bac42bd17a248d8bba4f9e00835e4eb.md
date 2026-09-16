### Title
Missing lower-bound check on `challengePeriod` lets a zero value permanently disable the fisherman veto window - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.updateHostParamsInternal` validates several `HostParams` fields (host manager, handler, consensus client, `hyperbridge` id, state machine list length, and enforces `unStakingPeriod >= 1 days`) but never checks that `challengePeriod` is non-zero. A `challengePeriod` of `0` is treated by the delay-check logic as "delay has already elapsed," permanently disabling the fisherman veto/dispute window that is supposed to protect every state commitment. This mirrors the RocketJoe finding exactly: a governance-configurable economic/security parameter that must always be greater than zero has no such floor enforced at the point it is set, so a single omission or mistake (not necessarily malicious intent) zeroes out the protection.

### Finding Description
`updateHostParamsInternal` in `evm/src/core/EvmHost.sol` performs several sanity checks on incoming `HostParams` before committing them, including a hard floor on `unStakingPeriod`: [1](#0-0) 

Notably, `_hostParams.challengePeriod = params.challengePeriod;` is assigned with **no validation whatsoever** — unlike `unStakingPeriod`, which reverts with `InvalidUnstakingPeriod` if set below `1 days`, there is no `InvalidChallengePeriod` guard preventing `challengePeriod == 0`.

The `challengePeriod` is the security-critical delay during which fishermen can detect and veto a fraudulent state commitment before it becomes usable for message delivery: [2](#0-1) 

The consensus/ISMP-core delay-check function that gates request/response/timeout processing explicitly treats a zero challenge period as "already elapsed," bypassing the wait entirely: [3](#0-2) 

This is corroborated by the test suite, which documents the intended behavior of the challenge-period gate and by the protocol docs describing the same fisherman-veto mechanism this delay exists to support: [4](#0-3) [5](#0-4) 

Because `updateHostParams` is the only governance entry point that mutates `challengePeriod`, and it applies no floor, a `SetHostParam` governance payload that (accidentally or through a copy/paste of one field) sets `challengePeriod` to `0` will be accepted and immediately take effect, permanently removing the window fishermen rely on to veto fraudulent L2 state before it is trusted for proof verification.

### Impact Explanation
With `challengePeriod == 0`, `verify_delay_passed`/`validate_state_machine` (and the equivalent EVM-side handler checks) will treat every freshly stored state commitment as immediately final. Relayers and applications can submit request/response/timeout proofs against that state commitment the instant it is stored, with zero time for the fishermen watch process to detect and veto a fraudulent commitment (e.g., a compromised or buggy consensus client anchoring an incorrect L2 state). This directly undermines the "unsound state commitment" protection the challenge-period/fisherman-veto design exists to provide, and can enable forged proof delivery or draining of applications that trust the fraudulently anchored state, exactly the class of risk the original RocketJoe report describes for zero-value economic-penalty parameters.

### Likelihood Explanation
`updateHostParams` is restricted to cross-chain governance (`restrict(_hostParams.hostManager)`), so triggering this requires a governance-approved `SetHostParam` action. However, unlike the other fields that are defensively checked (`hostManager`, `handler`, `consensusClient`, `stateMachines`, `unStakingPeriod`), `challengePeriod` has no floor at all, so the failure mode is a single missing validation line, not a deliberate abuse of governance privilege — the same "unlikely but possible, by mistake or intentionally" framing the original report used for zero withdrawal penalties. Given `unStakingPeriod` was deliberately given a `1 days` floor by the same function, the omission for `challengePeriod` looks like a genuine gap rather than an intentional design choice.

### Recommendation
Add an explicit floor check in `updateHostParamsInternal`, e.g. `if (params.challengePeriod == 0) revert InvalidChallengePeriod();` (or enforce a sane minimum matching the expected fisherman detection latency), mirroring the existing `InvalidUnstakingPeriod` check for `unStakingPeriod`.

### Proof of Concept
1. Governance (via `HostManager.onAccept` → `IHostManager(_params.host).updateHostParams`) submits a `SetHostParam` payload with `challengePeriod = 0` and otherwise-valid fields.
2. `updateHostParamsInternal` in `evm/src/core/EvmHost.sol:581-645` passes all its checks (none of them cover `challengePeriod`) and stores `_hostParams.challengePeriod = 0`.
3. Any subsequent `storeStateMachineCommitment` sets `_stateCommitmentsUpdateTime[...] = block.timestamp`.
4. On the ISMP-core / handler side, `verify_delay_passed` (`modules/ismp/core/src/handlers.rs:103-114`) returns `true` unconditionally because `delay_period.as_secs() == 0`, so `validate_state_machine` never returns `ChallengePeriodNotElapsed`.
5. A relayer can immediately submit request/response/timeout proofs against the just-stored (and potentially fraudulent) state commitment, with no window left for a fisherman to call `veto_state_commitment` (`modules/pallets/fishermen/src/lib.rs:167-193`) before it is trusted.

### Citations

**File:** evm/src/core/EvmHost.sol (L581-636)
```text
    function updateHostParamsInternal(HostParams memory params) internal {
        // check the params to prevent the host from getting bricked.
        if (
            params.hostManager == address(0) || address(params.hostManager).code.length == 0
                || !IERC165(params.hostManager).supportsInterface(type(IApp).interfaceId)
        ) {
            // otherwise cannot process new cross-chain governance requests
            revert InvalidHostManager();
        }

        if (
            params.handler == address(0) || address(params.handler).code.length == 0
                || !IERC165(params.handler).supportsInterface(type(IHandlerV2).interfaceId)
        ) {
            // otherwise cannot process new datagrams
            revert InvalidHandler();
        }

        if (
            params.consensusClient == address(0) || address(params.consensusClient).code.length == 0
                || !IERC165(params.consensusClient).supportsInterface(type(IConsensusV2).interfaceId)
        ) {
            // otherwise cannot process new consensus datagrams
            revert InvalidConsensusClient();
        }

        // otherwise cannot process new cross-chain governance requests
        if (keccak256(params.hyperbridge) == keccak256(bytes(""))) revert InvalidHyperbridgeId();

        // otherwise cannot process new datagrams
        uint256 stateMachinesLen = params.stateMachines.length;
        if (stateMachinesLen == 0) revert InvalidStateMachinesLength();

        // otherwise cannot process new datagrams
        if (1 days > params.unStakingPeriod) revert InvalidUnstakingPeriod();

        address oldFeeToken = feeToken();
        if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
            uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
            if (balance != 0) revert CannotChangeFeeToken();
        }

        // safe to emit here because invariants have already been checked
        // and don't want to store a temp variable for the old params
        emit HostParamsUpdated({oldParams: _hostParams, newParams: params});

        _hostParams.feeToken = params.feeToken;
        _hostParams.admin = params.admin;
        _hostParams.handler = params.handler;
        _hostParams.hostManager = params.hostManager;
        _hostParams.uniswapV2 = params.uniswapV2;
        _hostParams.unStakingPeriod = params.unStakingPeriod;
        _hostParams.challengePeriod = params.challengePeriod;
        _hostParams.consensusClient = params.consensusClient;
        _hostParams.stateMachines = params.stateMachines;
        _hostParams.hyperbridge = params.hyperbridge;
```

**File:** docs/content/developers/explore/fishermen.mdx (L6-20)
```text
# Fishermen

Every collator on Hyperbridge doubles as a fisherman. The fisherman task runs inside the collator binary and watches each connected L2 across multiple independent RPC providers. When those providers reach a supermajority agreeing on an L2 state that contradicts what Hyperbridge is about to commit to its state trie, the fisherman submits a `veto_state_commitment` extrinsic signed by the collator's AURA key. This veto prevents the fraudulent commitment from being finalised on Hyperbridge, protecting every application that relies on cross-chain state proofs.

Collators are compensated 2 `$BRIDGE` per block produced. This reward covers both block production and the ongoing cost of operating a high-quality fisherman setup — running premium RPC endpoints across multiple independent providers is part of the job, and the block reward is sized to make that sustainable.

## What a Fisherman Can Do

A fisherman holding a seat in the active collator set can:

- **Veto a state commitment** by calling `pallet-fishermen.veto_state_commitment` with a specific `StateMachineHeight`. The veto is accepted without requiring a cryptographic proof — the fisherman's inclusion in the collator set is the trust anchor.
- **Block cross-chain message delivery** for the vetoed height. Because a state commitment is an accumulator, messages from a vetoed height will still be included in a later commitment once the correct state is finalised. A veto delays processing; it cannot censor a specific message permanently.
- **Prevent a compromised or faulty consensus client** from anchoring fraudulent L2 state on Hyperbridge, which would otherwise let attackers fabricate state proofs and drain applications of funds.

A fisherman cannot selectively censor individual messages. The veto operates at the state commitment level — either the entire state at a given height is accepted or it is rejected.
```

**File:** modules/ismp/core/src/handlers.rs (L103-114)
```rust
/// for the state machine has elasped.
pub fn verify_delay_passed<H>(host: &H, proof_height: &StateMachineHeight) -> Result<bool, Error>
where
	H: IsmpHost,
{
	let update_time = host.state_machine_update_time(*proof_height)?;
	let delay_period = host
		.challenge_period(proof_height.id)
		.ok_or(Error::ChallengePeriodNotConfigured { state_machine: proof_height.id })?;
	let current_timestamp = host.timestamp();
	Ok(delay_period.as_secs() == 0 || current_timestamp.saturating_sub(update_time) > delay_period)
}
```

**File:** modules/ismp/testsuite/src/lib.rs (L110-152)
```rust
/// Ensure challenge period rules are followed in all handlers
pub fn check_challenge_period<H: IsmpHost>(host: &H) -> Result<(), &'static str> {
	let intermediate_state = setup_mock_client(host);
	// Set the previous update time
	let challenge_period = host.challenge_period(intermediate_state.height.id).unwrap();
	let previous_update_time = host.timestamp() - (challenge_period / 2);
	host.store_consensus_update_time(mock_consensus_state_id(), previous_update_time)
		.unwrap();
	host.store_state_machine_update_time(intermediate_state.height, previous_update_time)
		.unwrap();

	let post = PostRequest {
		source: intermediate_state.height.id.state_id,
		dest: host.host_state_machine(),
		nonce: 0,
		from: vec![0u8; 32],
		to: vec![0u8; 32],
		timeout_timestamp: 0,
		body: vec![0u8; 64],
	};

	let (signature, ..) = create_relayer_signer(vec![post.clone()].encode(), &[1u8; 32]);

	// Request message handling check
	let request_message = Message::Request(RequestMessage {
		requests: vec![post.clone()],
		proof: Proof { height: intermediate_state.height, proof: vec![] },
		signer: signature,
	});

	let res = handle_incoming_message(host, request_message).map_err(|e| e.downcast().unwrap());

	assert!(matches!(res, Err(ismp::error::Error::ChallengePeriodNotElapsed { .. })));

	// Timeout mesaage handling check
	let timeout_message = Message::Timeout(TimeoutMessage::Post {
		requests: vec![post],
		timeout_proof: Proof { height: intermediate_state.height, proof: vec![] },
	});

	let res = handle_incoming_message(host, timeout_message).map_err(|e| e.downcast().unwrap());
	assert!(matches!(res, Err(ismp::error::Error::ChallengePeriodNotElapsed { .. })));
	Ok(())
```

**File:** docs/content/protocol/ismp/consensus.mdx (L206-232)
```text
### `StateMachineUpdated`

```rust showLineNumbers
/// Emitted when a state machine is successfully updated to a new height
struct StateMachineUpdated {
    /// State machine height
    state_machine_id: StateMachineId,
    /// State machine latest height
    latest_height: u64,
}
```

A `StateMachineUpdated` event is emitted to notify network participants (both relayers and fishermen) of some newly available `StateCommitment`s for a given state machine. Relayers will wait for the configured `challenge_period` before attempting to transmit new requests & responses. While fishermen will check if these pending `StateCommitment`s describe valid states on the counterparty network. If the `challenge_period` elapses without any fraud proofs being presented, we can safely conclude that the provided `StateCommitment`s are indeed canonical.

### `StateCommitmentVetoed`

```rust showLineNumbers
/// Emitted when a `StateCommitment` has been successfully vetoed by a fisherman
pub struct StateCommitmentVetoed {
    /// The state commitment identifier
    pub height: StateMachineHeight,
    /// The account responsible
    pub fisherman: Vec<u8>,
}
```

A `StateCommitmentVetoed` event is emitted after a fisherman successfully vetoes a `StateCommitment` that is still within its challenge period. This instructs relayers to discard any pending requests/responses whose proofs rely on the vetoed commitment.
```
