### Title
Global `challengePeriod` is applied retroactively, re-locking messages whose delay had already elapsed - ([File: evm/src/core/HandlerV2.sol])

### Summary
`HandlerV2` computes message deliverability by comparing `block.timestamp - stateMachineCommitmentUpdateTime` against the **current, live** `challengePeriod` value read from `EvmHost` at verification time, rather than the value that was in force when the state commitment was recorded. If governance legitimately raises `challengePeriod` via `updateHostParams` while state commitments/requests are already in flight and past their old delay, those previously-deliverable messages become undeliverable again until the new, larger delay also elapses — the same "unvest → re-lock" pattern as the reported `ContinuousVesting.setVestingConfig()` issue, but applied to message delivery instead of token vesting.

### Finding Description
`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` all gate on the delay elapsed since the state commitment was stored, checked against the *current* host-wide challenge period: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

The `challengePeriod` used in each check is `host.challengePeriod()`, which reads the single, mutable `_hostParams.challengePeriod` field: [5](#0-4) 

That field is overwritten wholesale by `updateHostParamsInternal`, with no accounting for state commitments already stored under the old value and no grandfathering of in-flight messages: [6](#0-5) 

The Substrate side of the protocol has the identical pattern: `verify_delay_passed` reads whatever `challenge_period` is *currently* configured for the state machine, not the value active when the commitment/update time was recorded: [7](#0-6) 

and this value can be changed post-hoc via `update_consensus_state`: [8](#0-7) 

Because the delay check is re-evaluated against the live parameter every time a relayer calls `handlePostRequests`/`handleGetResponses`/timeout handlers, a routine (non-malicious) `updateHostParams`/`update_consensus_state` governance action that raises the challenge period retroactively re-arms `ChallengePeriodNotElapsed` for state commitments and requests that had already cleared the delay under the previous configuration — exactly mirroring the vesting bug's "already-vested tokens become locked again" pattern, here applied to "already-deliverable messages become undeliverable again."

### Impact Explanation
Requests/responses that were ready for delivery can be pushed past their `timeout()`/`timeout_timestamp` while waiting out the newly-extended challenge period, since `handlePostRequests` independently enforces `MessageTimedOut` against `leaf.request.timeout()`: [9](#0-8) 

If the extended wait exceeds the remaining time-to-timeout, the message can never be delivered through the normal path and is instead forced into the timeout/refund path (or becomes permanently stuck if timeout has already passed on the destination but the challenge period hasn't cleared to prove it), constituting a route that becomes unable to deliver a legitimately in-flight message — a liveness/fund-availability regression for relayers and end users who already paid fees expecting delivery.

### Likelihood Explanation
This requires only a normal, non-adversarial governance parameter update to `challengePeriod`/`challenge_periods` (an expected periodic operational action, e.g., in response to changing finality assumptions) occurring while any request/response is in the window between "delay elapsed under old period" and "delivered". Given `challengePeriod` changes are a documented governance capability (`HostParamsUpdated`/`update_host_params`) rather than an exotic edge case, and every in-flight message during the transition is affected simultaneously, likelihood is moderate rather than rare.

### Recommendation
Snapshot the challenge period effective at the time a state commitment is stored (per `StateMachineHeight`) and use that stored value for all subsequent delay checks against that commitment, instead of re-reading the live `challengePeriod`/`challenge_period` value. Alternatively, when increasing the challenge period, apply the new value only to state commitments recorded after the change, leaving already-elapsed delays honored for prior commitments.

### Proof of Concept
1. Governance calls `updateHostParams` (via `HostManager`) raising `_hostParams.challengePeriod` from `T1` to `T2` (`T2 > T1`), applied via `updateHostParamsInternal` (`evm/src/core/EvmHost.sol:573-636`).
2. A state commitment at height `H` was stored at time `t0`; at time `t0 + T1 + 1` (before the update) it satisfied `delay > challengePeriod` and any queued Post request anchored at `H` was deliverable.
3. Governance's update lands at `t0 + T1 + 2`, before a relayer submits `handlePostRequests` for that batch.
4. The relayer's call to `handlePostRequests(host, request)` now computes `delay = block.timestamp - updateTime` and compares it against the new `challengePeriod = T2`; if `block.timestamp < t0 + T2`, the call reverts with `ChallengePeriodNotElapsed()` (`evm/src/core/HandlerV2.sol:181-186`) even though the message was deliverable moments earlier.
5. If the request's `timeout()` falls between `t0+T1` and `t0+T2`, the request now hits `MessageTimedOut()` on any future retry once `T2` elapses, and can only be resolved via the timeout path — the intended cross-chain action is permanently lost even though the sender's message had already cleared its original delay requirement.

### Citations

**File:** evm/src/core/HandlerV2.sol (L181-186)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

```

**File:** evm/src/core/HandlerV2.sol (L187-196)
```text
        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
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

**File:** evm/src/core/EvmHost.sol (L56-66)
```text
    // The unstaking period of Polkadot's validators. In order to prevent long-range attacks
    uint256 unStakingPeriod;
    // Minimum challenge period for state commitments in seconds;
    uint256 challengePeriod;
    // The consensus client contract which handles consensus proof verification
    address consensusClient;
    // State machines whose state commitments are accepted
    uint256[] stateMachines;
    // The state machine identifier for hyperbridge
    bytes hyperbridge;
}
```

**File:** evm/src/core/EvmHost.sol (L573-636)
```text
    function updateHostParams(HostParams memory params) external virtual restrict(_hostParams.hostManager) {
        updateHostParamsInternal(params);
    }

    /**
     * @dev Updates the HostParams. Will reset all fishermen accounts and initialize any new state machines.
     * @param params, the new host params.
     */
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

**File:** modules/pallets/ismp/src/lib.rs (L410-437)
```rust
		/// Modify the unbonding period and challenge period for a consensus state.
		/// The dispatch origin for this call must be `T::AdminOrigin`.
		///
		/// - `message`: `UpdateConsensusState` struct.
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().writes(2))]
		#[pallet::call_index(3)]
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
