### Title
Live re-read of `challengePeriod()` lets governance retroactively shrink (or eliminate) the fisherman veto window for already-stored, not-yet-elapsed state commitments - ([File: evm/src/core/EvmHost.sol])

### Summary
`EvmHost` stores the timestamp of each state-machine commitment (`_stateCommitmentsUpdateTime`) once, at the block it is submitted, but the "how long fishermen have to veto it" delay is *not* snapshotted alongside that commitment. Instead, every place that enforces the delay (`HandlerV2.handlePostRequests`/`handleGetResponses`/timeout handlers, and the pallet-ismp equivalent `verify_delay_passed`) re-reads the *current* `hostParams.challengePeriod` at message-processing time. Governance can change `challengePeriod` via `updateHostParams` at any time, and that change applies immediately and retroactively to every commitment already sitting in the challenge window, not just to future ones. This is the exact bug class in the referenced Neobase `LendingLedger` finding: a config value that is mutated live is implicitly assumed to only affect not-yet-created state, but the code has no mechanism to freeze/lock the value that was in effect when the relevant state (here, a state-machine commitment) was created.

### Finding Description
`updateHostParamsInternal` writes `_hostParams.challengePeriod = params.challengePeriod` unconditionally and takes effect for the whole host the instant the governance message lands: [1](#0-0) 

Every enforcement point that is supposed to give fishermen time to veto a newly stored state commitment reads `host.challengePeriod()` fresh at the time a relayer submits a delivery, not the value that existed when that specific commitment was stored: [2](#0-1) [3](#0-2) [4](#0-3) 

The Rust/pallet-ismp side has the identical pattern — `verify_delay_passed` reads `host.challenge_period(proof_height.id)` (current value) against the fixed `state_machine_update_time`: [5](#0-4) 

Meanwhile the update *timestamp* for a commitment is written once, permanently, when the commitment is stored: [6](#0-5) 

Because the delay length and the update timestamp live in two independently-mutable places, any governance-initiated reduction of `challengePeriod` (a routine parameter tune, e.g. to lower latency) instantly shortens — or with `challengePeriod = 0`, completely removes — the remaining veto window for every state-machine height that was stored under the old (longer) period and is still inside it. Fishermen who were relying on the originally-configured window to detect and veto a bad/malicious state commitment via `vetoStateCommitment` lose that time without warning, exactly mirroring the LendingLedger flaw where `setBlockTimeParameters`/`setRewards` retroactively mutate values for markets/epochs that have not yet been "settled" (there: `update_market`; here: challenge-period elapsed + delivery).

### Impact Explanation
This directly undermines the fisherman/veto security model that state-machine-commitment consumers (HandlerV2, GET-response and timeout handlers, and pallet-ismp) rely on. A commitment that a fisherman has not yet had the intended time to review and veto can immediately become deliverable the moment governance drops the challenge period, allowing an unsound/forged state commitment already in flight to be consumed and its embedded requests/responses/timeouts dispatched to modules before it could be vetoed — i.e., an "unsound state commitment" / forged-message-delivery outcome, one of the accepted impact classes. This can lead to acceptance of state that should have been rejected, and downstream token/intent/escrow logic (which trusts `dispatchIncoming`) acting on it.

### Likelihood Explanation
No malicious actor privilege is required beyond the pre-existing, expected relayer/consensus-proof submission flow (permissionless): a relayer submits a legitimate BEEFY/consensus proof that stores a new state-machine commitment (normal operation), and separately, at any later point, governance performs a routine `challengePeriod` parameter update through the standard `HostManager`/`updateHostParams` path. There is no code path that prevents this overlap, and — as in the referenced report — the contract offers no warning that in-flight (not-yet-elapsed) commitments are affected. The only thing required for exploitation is that a bad/borderline commitment exists inside the (now-shrunk) window when the parameter changes and a relayer submits a delivery message immediately afterward, which is a single-transaction action available to any relayer.

### Recommendation
Snapshot the challenge period alongside the state-machine commitment at the time it is stored (e.g., store `(commitment, updateTime, challengePeriodAtStoreTime)` instead of only `updateTime`), and have `HandlerV2`/`verify_delay_passed` enforce the snapshotted value rather than re-reading the live `hostParams.challengePeriod()`. Alternatively, restrict `challengePeriod` reductions to apply only to commitments stored after the update (e.g., via an effective-height/timestamp cutoff), and emit a prominent warning/require a minimum grace period before a lowered challenge period can take effect for pending commitments.

### Proof of Concept
1. Governance sets `challengePeriod = 7 days` via `updateHostParams`.
2. A relayer submits a BEEFY/consensus proof that calls `storeStateMachineCommitment`, recording `_stateCommitmentsUpdateTime[stateMachineId][height] = block.timestamp` (per `evm/src/core/EvmHost.sol` lines 544-562). This commitment is, unbeknownst to fishermen, contentious/incorrect and would normally be vetoed within the 7-day window.
3. Before the 7 days elapse and before any fisherman vetoes it, governance issues a legitimate parameter tune reducing `challengePeriod` to `0` (or a very small value) via `updateHostParams` (`evm/src/core/EvmHost.sol` lines 573-575, 617-636).
4. A relayer immediately calls `HandlerV2.handlePostRequests` with proofs referencing the height from step 2. The check `challengePeriod != 0 && challengePeriod > delay` (`evm/src/core/HandlerV2.sol` lines 182-185) now passes instantly because `host.challengePeriod()` returns the new, reduced value — even though fishermen never got their originally-promised 7-day window for that specific commitment.
5. Requests/responses tied to the unsound commitment are dispatched to destination modules via `host.dispatchIncoming`, before any veto could occur.

### Citations

**File:** evm/src/core/EvmHost.sol (L544-562)
```text
    /**
     * @param height - state machine height
     * @return the state machine update time at `height`
     */
    function stateMachineCommitmentUpdateTime(StateMachineHeight memory height) external view returns (uint256) {
        return _stateCommitmentsUpdateTime[height.stateMachineId][height.height];
    }

    /**
     * @param height - state machine height
     * @return the state commitment at `height`
     */
    function stateMachineCommitment(StateMachineHeight memory height)
        external
        payable
        returns (StateCommitment memory)
    {
        return _stateCommitments[height.stateMachineId][height.height];
    }
```

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
