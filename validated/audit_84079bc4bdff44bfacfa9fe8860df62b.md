### Title
Global mutable `challengePeriod` is not snapshotted per state commitment, letting governance changes retroactively shrink the fraud-proof window for already-finalized (pending-challenge) commitments - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost` stores the fraud-proof `challengePeriod` as a single mutable value in `_hostParams`, updatable at any time via governance (`setHostParams`/`HostManager`). `HandlerV2` compares this *live* value against the fixed `stateMachineCommitmentUpdateTime` recorded when a state commitment was first stored, rather than the challenge period that was in effect when the commitment was created. This mirrors the reported `BridgeExecutorBase._gracePeriod` bug class: a live governance-controlled duration is applied to a previously created object's timestamp instead of being locked in as a parameter of that object at creation time.

### Finding Description
When Hyperbridge finalizes a new `StateCommitment` for a state machine, it records `stateMachineCommitmentUpdateTime(height)` once, at commitment time [1](#0-0) . The intended invariant (documented in the protocol spec) is that relayers and application handlers must wait for the *configured* `challenge_period` to elapse before this commitment can be used to deliver requests, responses, or timeouts, giving fishermen time to veto a fraudulent commitment [2](#0-1) .

On the EVM host, this delay check is implemented by reading the *current* `challengePeriod` value at call time and comparing it to the fixed `stateMachineCommitmentUpdateTime` of the target height: [3](#0-2) [4](#0-3) [5](#0-4) 

The `challengePeriod` value itself lives in `_hostParams` and can be changed at any time by governance through `setHostParams`, which simply overwrites the stored value with no history and no linkage to already-created state commitments: [6](#0-5) 

Because `challengePeriod` is a single mutable global rather than a value captured per-commitment (analogous to storing `_gracePeriod` per-action in the referenced Aave report), any reduction of the challenge period retroactively shortens the effective waiting time for *all* commitments already stored before the change — including commitments that are still within their original, longer challenge window and have not yet had the full opportunity to be vetoed by a fisherman via `FraudProofMessage`/`StateCommitmentVetoed`. The Rust-side `IsmpHost` implementation has the identical pattern: `challenge_period(state_machine)` is looked up live and compared to the fixed `state_machine_update_time`, with no per-commitment snapshot [7](#0-6) .

### Impact Explanation
A relayer (an unprivileged actor) can call `handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, or `handleGetRequestTimeouts` on `HandlerV2` against a state commitment that was stored under a longer challenge period intended to give fishermen time to detect and veto a faulty/fraudulent consensus update. If governance subsequently lowers `challengePeriod` for legitimate operational reasons (e.g. faster relaying), every pending commitment created under the old, longer period immediately becomes actionable under the new, shorter one, even though it has not accumulated the amount of scrutiny time originally promised to fishermen. This can let a relayer deliver requests/responses/timeouts derived from a state commitment that should still be within its original challenge window and subject to veto — i.e., action on an unsound/unverified state commitment before its intended fraud-proof deadline, which can result in unauthorized minting/withdrawal or forged message delivery derived from that commitment.

### Likelihood Explanation
This does not require a malicious actor to trigger — any legitimate reduction of `challengePeriod` by governance (a routine parameter tuning action, not an attack) immediately and silently changes the security guarantee for every already-stored, not-yet-fully-challenged commitment. The exploitation step itself (calling the handler functions) is fully permissionless and requires no special privileges — any relayer holding a valid membership/non-membership proof for a commitment created just before the parameter change can act on it as soon as it clears the new, shorter delay, even though fishermen were promised the original longer window.

### Recommendation
Store the `challengePeriod` (and analogously `unbonding_period`) that was in effect at the time each `StateCommitment` is finalized as part of the commitment's own record (e.g., in the `StateCommitment`/`StateCommitmentHeight` struct or a parallel mapping keyed by height), and use that snapshotted value — not the live `_hostParams.challengePeriod` — when validating delay elapsed in `HandlerV2` (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`) and in the equivalent Rust `verify_delay_passed`/`validate_state_machine` logic. This ensures governance updates to `challengePeriod` only affect commitments created after the update, not commitments already in flight.

### Proof of Concept
1. Governance configures `challengePeriod = 24 hours` in `EvmHost`/`_hostParams`.
2. Hyperbridge's consensus client verifies a new (possibly subtly faulty) `StateCommitment` for a counterparty chain at height `H`; `stateMachineCommitmentUpdateTime(H)` is recorded as `T0`, starting the intended 24-hour fisherman review window.
3. Twelve hours later (`T0 + 12h`, well before the promised 24h window elapses and before any veto has necessarily been submitted), governance lowers `challengePeriod` to `1 hour` for an unrelated operational reason via `setHostParams`.
4. A relayer immediately calls `HandlerV2.handlePostRequests` (or `handlePostRequestTimeouts`) with a proof anchored at height `H`. The check `challengePeriod > delay` now evaluates `1h > 12h`, which is false, so the request passes and is delivered/dispatched — twelve hours ahead of the originally promised 24-hour fraud-proof window, and potentially before a fisherman who was relying on the original window has submitted a veto.

### Citations

**File:** modules/ismp/core/src/handlers/consensus.rs (L68-70)
```rust
			last_commitment_height = Some(state_height);
			host.store_state_machine_commitment(state_height, commitment_height.commitment)?;
			host.store_state_machine_update_time(state_height, host.timestamp())?;
```

**File:** docs/content/protocol/ismp/consensus.mdx (L171-174)
```text
The `update_client` method is responsible for advancing the state of the consensus client. This performs the consensus verification of new `StateCommitment`s that have been finalized by a `StateMachine`'s consensus system. The `IsmpHost` must return the concrete implementation of the associated `ConsensusClient` and a previously stored `ConsensusState`. The procedure for updating the consensus client is as follows.

- First the handler must assert that the consensus client is not frozen or expired. Consensus clients can expire if the last time the consensus client was updated has exceeded the chain's unbonding period. This effectively mitigates any potential long fork attacks that may arise due to a loss of liveness of consensus clients.
- Finally the handler may perform consensus proof verification using the concrete implementation for the consensus client using `ConsensusClient::verify_consensus`. If verifications pass, the udpated `ConsensusState` and `IntermediateState`s are persisted to storage and enter a new challenge period.
```

**File:** evm/src/core/HandlerV2.sol (L181-185)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
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

**File:** evm/src/core/EvmHost.sol (L625-634)
```text
        emit HostParamsUpdated({oldParams: _hostParams, newParams: params});

        _hostParams.feeToken = params.feeToken;
        _hostParams.admin = params.admin;
        _hostParams.handler = params.handler;
        _hostParams.hostManager = params.hostManager;
        _hostParams.uniswapV2 = params.uniswapV2;
        _hostParams.unStakingPeriod = params.unStakingPeriod;
        _hostParams.challengePeriod = params.challengePeriod;
        _hostParams.consensusClient = params.consensusClient;
```

**File:** modules/ismp/core/src/handlers.rs (L104-114)
```rust
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
