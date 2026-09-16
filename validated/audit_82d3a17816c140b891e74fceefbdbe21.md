### Title
Global `challengePeriod` is not snapshotted per state commitment, allowing governance-triggered param updates to retroactively weaken the fisherman challenge window - ([File: evm/src/core/HandlerV2.sol])

### Summary
`EvmHost` stores a single mutable `challengePeriod` value in `HostParams` that is read live, at message-verification time, for every pending state machine commitment, rather than being captured at the moment each commitment was stored. This is the same root-cause pattern as the reported vault bug: a single admin-controlled parameter is applied retroactively to both already-pending and future items instead of being frozen per-item at creation time.

### Finding Description
`EvmHost.storeStateMachineCommitment` persists a `StateCommitment` and its `_stateCommitmentsUpdateTime` but never records the `challengePeriod` that was in effect when the commitment was written [1](#0-0) . The global value lives in `_hostParams.challengePeriod` and can be changed at any time via `updateHostParams`/`updateHostParamsInternal`, which simply overwrites `_hostParams.challengePeriod` for all state machines with no distinction between commitments already pending review and future ones [2](#0-1) .

`HandlerV2` then reads this live, global value on every message-processing path — `handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` — and computes the elapsed delay against `host.stateMachineCommitmentUpdateTime(...)` compared to `host.challengePeriod()` fetched at call time, not the value in effect when the commitment was stored: [3](#0-2) [4](#0-3) [5](#0-4) 

The equivalent pallet-ismp / off-chain path has the exact same design: `challenge_period` is looked up dynamically from a `BTreeMap<StateMachine, u64>` rather than snapshotted at the height the state commitment was stored, and can be changed for already-committed heights via the `update_consensus_state` extrinsic [6](#0-5) [7](#0-6) .

This design directly parallels the reported vault issue: `unstakingPeriods[asset]` is applied globally at completion time instead of being fixed per-request at request time, causing changes to retroactively affect already-pending items.

### Impact Explanation
The `challengePeriod` exists specifically to give fishermen time to detect and veto byzantine state commitments before any state proofs derived from them are trusted (the optimistic-bridging security model) [8](#0-7) . Because the period is not snapshotted per commitment, a routine parameter update (e.g. lowering the challenge period for operational reasons, or a manager rotation that ships a smaller value) immediately and retroactively shortens the review window for state commitments that are already pending and being watched by fishermen under the old, longer period. Any relayer can then immediately submit `handlePostRequests`/`handleGetResponses`/timeout messages referencing that pending commitment as soon as the new, shorter delay is satisfied — potentially before fishermen have had the originally-promised time to submit a fraud proof — allowing forged/unsound state to be acted upon. This can result in unauthorized app actions being dispatched from messages whose underlying state commitment was never actually vetted for the full intended security window.

### Likelihood Explanation
Triggering requires only a normal `updateHostParams` governance call reducing `challengePeriod` (via `hostManager`, which is routine cross-chain governance traffic, not necessarily malicious) followed by an ordinary relayer/message-dispatcher submitting the message-handling call — a single subsequent transaction from any unprivileged relayer. No exotic conditions are needed beyond a legitimate parameter change landing while commitments are in-flight, which is a realistic operational scenario (e.g., tuning trust assumptions, or a host-manager rotation shipping updated params).

### Recommendation
Snapshot the challenge period alongside each stored state machine commitment (e.g., extend the commitment struct or a parallel mapping keyed by `StateMachineHeight` to record the `challengePeriod` in effect at `storeStateMachineCommitment` time), and have `HandlerV2` compare elapsed delay against that stored value instead of the live `host.challengePeriod()`. Apply the same fix to the pallet-ismp side by persisting the challenge period used per `StateMachineHeight`/`StateCommitmentHeight` rather than relying solely on the live `challenge_period` map in `verify_delay_passed`.

### Proof of Concept
1. Governance/hostManager calls `updateHostParams` with a lower `challengePeriod` than what was in effect when a currently-pending `StateCommitment` was stored via `storeStateMachineCommitment`.
2. `_hostParams.challengePeriod` is now smaller for all state machines, including the already-pending commitment height.
3. A relayer calls `handlePostRequests` (or `handleGetResponses`/timeout variants) referencing that commitment height; `handler.challengePeriod()` returns the new smaller value, so `challengePeriod > delay` is now false even though fishermen were promised the original longer window under which they were still actively monitoring for fraud.
4. Requests/responses tied to that commitment are dispatched to destination modules before the originally-committed challenge window elapses.

### Citations

**File:** evm/src/core/EvmHost.sol (L627-636)
```text
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

**File:** evm/src/core/EvmHost.sol (L683-691)
```text
    /**
     * @dev Store the state commitment at given state height alongside relevant metadata.
     * Assumes the state commitment is of the latest height.
     */
    function storeStateMachineCommitment(StateMachineHeight memory height, StateCommitment memory commitment)
        external
        restrict(_hostParams.handler)
    {
        _stateCommitments[height.stateMachineId][height.height] = commitment;
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

**File:** modules/pallets/ismp/src/lib.rs (L416-437)
```rust
		pub fn update_consensus_state(
			origin: OriginFor<T>,
			message: UpdateConsensusState,
		) -> DispatchResult {
			T::AdminOrigin::ensure_origin(origin)?;

			let host = Pallet::<T>::default();

			if let Some(unbonding_period) = message.unbonding_period {
				host.store_unbonding_period(message.consensus_state_id, unbonding_period)
					.map_err(|_| Error::<T>::UnbondingPeriodUpdateFailed)?;
			}

			for (state_id, period) in message.challenge_periods {
				let id =
					StateMachineId { state_id, consensus_state_id: message.consensus_state_id };
				host.store_challenge_period(id, period)
					.map_err(|_| Error::<T>::UnbondingPeriodUpdateFailed)?;
			}

			Ok(())
		}
```

**File:** docs/content/protocol/interoperability/consensus-proofs.mdx (L138-146)
```text
### Optimistic Bridging

To prevent the damage that can be done to our bridge in the event of a byzantine attack, **we must introduce a challenge window in the form of a time delay between when consensus proofs are verified by our consensus client and when state proofs associated with those headers can be used to process cross-chain messages.**

During this challenge window, consensus clients can detect byzantine attacks. Off-chain consensus clients can do this by participating in the P2P network. On-chain consensus clients, on the other hand, will need to rely on off-chain parties, which we'll call fishermen<sup>[3]</sup>, to provide the proofs of fraud to the client.

These fishermen will need some incentive to watch for byzantine attacks and report the fraud proofs which will safeguard the consensus client. As such, we will require relayers who submit consensus proofs to be staked, in the event of byzantine attacks, relayer’s stake can be used to incentivise fishermen to submit fraud proofs.

In the event of a byzantine attack, the fraud proofs will allow for the consensus client to go into a frozen state until the source chain recovers from this byzantine state, **The host chain can then unfreeze the consensus client through some kind of on-chain governance, allowing the bridge to resume operations safely and without any loss of funds ever having occurred.**
```
