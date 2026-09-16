### Title
Challenge period is read live from mutable HostParams instead of being pinned to a state commitment, letting a governance parameter change retroactively shrink the veto window for already-pending commitments - (File: evm/src/core/HandlerV2.sol)

### Summary
The Bancor report's root cause was that a global protocol parameter (the bonding-curve formula) could be changed by governance mid-flight and applied to a "batch" whose price should have been fixed under the parameter in effect when the batch started. Hyperbridge has the same structural flaw with `challengePeriod`: it is stored as a single mutable value in `HostParams` and is read *live* at proof-verification time rather than being snapshotted against the specific state commitment it is supposed to protect.

### Finding Description
`HostParams.challengePeriod` [1](#0-0)  is a single global value that cross-chain governance (`hostManager`) can change at any time via `updateHostParams` → `updateHostParamsInternal`, which overwrites `_hostParams.challengePeriod` immediately with no delay or timelock relative to already-pending state commitments: [2](#0-1) [3](#0-2) 

When a state commitment (the analog of a "batch") is stored via `storeStateMachineCommitment`, only the commitment and its timestamp are persisted — the challenge period in effect at that moment is *not* captured alongside it: [4](#0-3) 

Every handler that later verifies proofs against that commitment (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`) re-reads the *current* `host.challengePeriod()` rather than the value that existed when the commitment was created, and compares it against the elapsed delay: [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

The same live-read pattern exists on the Substrate/pallet-ismp side: `verify_delay_passed` fetches `host.challenge_period(proof_height.id)` at the moment of message handling, not at the moment the state machine height was committed: [9](#0-8) [10](#0-9) 

This is exactly the Bancor bug pattern: a security-critical parameter that participants (fishermen, relayers, and users) rely on being fixed for the duration of an in-flight unit of work (here, the fraud-challenge window for a specific state commitment) is instead mutable and read dynamically, so a mid-flight parameter update changes the rules retroactively for commitments already in progress.

### Impact Explanation
Fishermen are given the currently-configured challenge period as their guaranteed window to detect and veto a fraudulent/incorrect state commitment (via `vetoStateCommitment`/`deleteStateMachineCommitment`, `evm/src/core/EvmHost.sol` around L704-720). If `hostManager` legitimately lowers `challengePeriod` (e.g., a routine parameter tuning, a misconfiguration fix, or simply a scheduled reduction) while a state commitment stored under the old, longer period is still within its original window, relayers can immediately call `handlePostRequests`/`handleGetResponses`/timeout handlers against that commitment using the new, shorter (or zero) period. This finalizes/dispatches messages before the fishermen's originally-promised veto window has actually elapsed, undermining the fraud-proof security assumption for commitments that predate the update. This maps directly to the required impact class of "unsound state commitment" / forged-message-delivery risk, since messages can be dispatched to destination apps based on a state commitment that has not actually survived its intended challenge duration.

### Likelihood Explanation
`updateHostParams` is restricted to `hostManager`, which is itself driven by legitimate cross-chain governance requests from the Hyperbridge chain (not a malicious actor abusing the mechanism) [11](#0-10) . Any ordinary, non-malicious governance action that changes `challengePeriod` — for entirely legitimate reasons (e.g. lowering an overly conservative delay, or correcting an initial misconfiguration) — triggers this issue for every commitment currently mid-challenge-window at the time of the change. Because there is no linkage between a stored commitment and the challenge period active when it was stored, the bug is triggered automatically by the normal, expected governance workflow, not by any privileged/adversarial misuse — same as the original Bancor finding.

### Recommendation
Snapshot the challenge period at the moment a state commitment is stored (e.g., add a `challengePeriodAtCommit` field alongside `_stateCommitments`/`_stateCommitmentsUpdateTime` in `EvmHost.sol`, and the analogous storage in the pallet-ismp `IsmpHost` implementation), and have `HandlerV2` and `verify_delay_passed` compare elapsed time against the pinned value for that specific height rather than the live `HostParams.challengePeriod`/`challenge_period()`. Alternatively, enforce that a `challengePeriod` reduction only applies to state commitments recorded after the update (i.e., apply the new value prospectively, analogous to "the bancor formula update should be executed in the next batch").

### Proof of Concept
1. `hostManager` (via a normal governance `updateHostParams` request) sets `challengePeriod = 7 days`.
2. A state machine height `H` is committed via `HandlerV2.handleConsensus` → `EvmHost.storeStateMachineCommitment(H, commitment)`, recording only `_stateCommitmentsUpdateTime[H] = block.timestamp` [12](#0-11) ; fishermen are relying on 7 days to inspect/veto it.
3. One hour later, `hostManager` issues another legitimate `updateHostParams` request lowering `challengePeriod` to `0`, which is applied instantly via `updateHostParamsInternal` [13](#0-12) .
4. A relayer immediately calls `HandlerV2.handlePostRequests` for height `H`; the check `challengePeriod != 0 && challengePeriod > delay` now reads the new `challengePeriod = 0` and always passes regardless of `delay` [14](#0-13) , so requests proven against commitment `H` are dispatched to destination modules only 1 hour after commitment instead of the 7 days fishermen were promised, eliminating their ability to veto in time.

### Citations

**File:** evm/src/core/EvmHost.sol (L56-60)
```text
    // The unstaking period of Polkadot's validators. In order to prevent long-range attacks
    uint256 unStakingPeriod;
    // Minimum challenge period for state commitments in seconds;
    uint256 challengePeriod;
    // The consensus client contract which handles consensus proof verification
```

**File:** evm/src/core/EvmHost.sol (L564-575)
```text
    /**
     * @dev Updates the HostParams. Only callable by cross-chain governance
     * via the configured `hostManager`. The admin has no privileges here —
     * environments that need a privileged admin override (testnets, forks)
     * should use `TestnetHost`, which extends this contract.
     *
     * Marked `virtual` so subclasses can broaden the authorization
     * @param params, the new host params.
     */
    function updateHostParams(HostParams memory params) external virtual restrict(_hostParams.hostManager) {
        updateHostParamsInternal(params);
    }
```

**File:** evm/src/core/EvmHost.sol (L630-636)
```text
        _hostParams.hostManager = params.hostManager;
        _hostParams.uniswapV2 = params.uniswapV2;
        _hostParams.unStakingPeriod = params.unStakingPeriod;
        _hostParams.challengePeriod = params.challengePeriod;
        _hostParams.consensusClient = params.consensusClient;
        _hostParams.stateMachines = params.stateMachines;
        _hostParams.hyperbridge = params.hyperbridge;
```

**File:** evm/src/core/EvmHost.sol (L687-699)
```text
    function storeStateMachineCommitment(StateMachineHeight memory height, StateCommitment memory commitment)
        external
        restrict(_hostParams.handler)
    {
        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;

        emit StateMachineUpdated({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId), 
            height: height.height
        });
    }
```

**File:** evm/src/core/HandlerV2.sol (L181-186)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

```

**File:** evm/src/core/HandlerV2.sol (L217-221)
```text
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();
```

**File:** evm/src/core/HandlerV2.sol (L254-260)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();
```

**File:** evm/src/core/HandlerV2.sol (L293-296)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();
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

**File:** modules/ismp/core/src/handlers.rs (L116-147)
```rust
/// This function does the preliminary checks for a request or response message
/// - It ensures the consensus client is not frozen
/// - Checks for frozen state machine is deprecated and malicious state machine commitment will be
///   deleted instead
/// - Checks that the delay period configured for the state machine has elapsed.
pub fn validate_state_machine<H>(
	host: &H,
	proof_height: StateMachineHeight,
) -> Result<Box<dyn StateMachineClient>, Error>
where
	H: IsmpHost,
{
	// Ensure consensus client is not frozen
	let consensus_client_id = host.consensus_client_id(proof_height.id.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized {
			consensus_state_id: proof_height.id.consensus_state_id,
		},
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	// Ensure client is not frozen
	host.is_consensus_client_frozen(proof_height.id.consensus_state_id)?;

	// Ensure delay period has elapsed
	if !verify_delay_passed(host, &proof_height)? {
		return Err(Error::ChallengePeriodNotElapsed {
			state_machine_id: proof_height.id,
			current_time: host.timestamp(),
			update_time: host.state_machine_update_time(proof_height)?,
		});
	}

	consensus_client.state_machine(proof_height.id.state_id)
```
