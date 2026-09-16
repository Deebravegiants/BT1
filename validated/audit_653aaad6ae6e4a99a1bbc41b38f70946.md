### Title
Single global `challengePeriod` applied to all state machines in `EvmHost` enables premature finality assumption and forged message delivery - (File: evm/src/core/EvmHost.sol, evm/src/core/HandlerV2.sol)

### Summary
`EvmHost` stores exactly one `challengePeriod` value in `HostParams` [1](#0-0)  that is applied uniformly to *every* state machine whose commitments the host accepts (`stateMachines` array, an arbitrary set of Polkadot parachains and other EVM chains) [2](#0-1) . `HandlerV2` reads this single value with no state-machine parameter and uses it to gate delivery of requests, responses, and timeouts: `uint256 challengePeriod = host.challengePeriod();` [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) . This mirrors exactly the reported bug class: a fixed time window chosen without regard to the differing risk/volatility (here: finality/reorg-risk) profile of each underlying data source (here: each counterparty state machine), which is unsafe for sources whose profile requires a longer window.

By contrast, the Substrate/pallet-ismp side of the same protocol correctly parameterizes the challenge period per state machine id: `host.challenge_period(proof_height.id)` in `verify_delay_passed` [7](#0-6) , confirming that per-chain differentiation is the intended and necessary design, which the EVM host implementation does not provide.

### Finding Description
`EvmHost` accepts state commitments from multiple, heterogeneous counterparty state machines (different parachains, different EVM chains, potentially with different finality guarantees, reorg depths, or consensus fault models) into `_stateCommitments`/`_stateCommitmentsUpdateTime` [8](#0-7) . Regardless of which state machine a proof originates from, `HandlerV2` computes `delay = block.timestamp - host.stateMachineCommitmentUpdateTime(...)` and compares it against the single global `challengePeriod` before treating the commitment as safe to act on, for POST requests, GET responses, POST timeouts, and GET timeouts alike:
- `handlePostRequests` [9](#0-8) 
- `handleGetResponses` [4](#0-3) 
- `handlePostRequestTimeouts` [5](#0-4) 
- `handleGetRequestTimeouts` [6](#0-5) 

Because `challengePeriod` is a single scalar in `HostParams` set by governance for the whole host [10](#0-9) , it can only be tuned to one value across the entire `stateMachines` allow-list. If it is calibrated for the fastest-finalizing/most-secure counterparty (to keep UX/latency acceptable for common routes), any other state machine in the allow-list with weaker finality/higher fork-choice risk is under-protected: a state commitment for that chain can be treated as "finalized" for message delivery/timeout purposes before it is actually irreversible, i.e. before an equivalent-length reorg risk window has genuinely elapsed for that chain. Conversely, if it is calibrated for the slowest/most-reorg-prone chain, all other routes suffer needless latency — this is the "yield/user loss" side of the same root cause (fixed one-size-fits-all freshness window applied to sources with different risk profiles), directly analogous to the Tellor 30-minute window applied uniformly to assets of different volatility.

### Impact Explanation
If the global `challengePeriod` is insufficient for a particular onboarded state machine's actual finality/reorg risk, a relayer can submit a state commitment for that chain, wait only the (globally-configured, too-short) challenge period, then deliver POST requests/GET responses or push a request/response through the non-membership timeout path against a state commitment that is not yet irreversibly final on the source. If the source chain subsequently reorgs, the "delivered" request/response never truly existed (or existed differently) on the source, resulting in forged message delivery / an unsound state commitment being acted upon by destination applications (`IApp.onAccept`, `IApp.onGetResponse`) [11](#0-10) , or a timeout refund being paid out based on a state commitment that gets invalidated — both are concrete fund-affecting outcomes (unauthorized app action / forged delivery / incorrect timeout refund), matching the accepted impact classes.

### Likelihood Explanation
Exploitability depends on governance's choice of `challengePeriod` and the actual heterogeneity of onboarded state machines' finality characteristics, which is a realistic operational scenario for a multi-chain message-passing protocol like Hyperbridge that intentionally supports many consensus clients with different finality assumptions (BEEFY/Polkadot, sync-committee/Ethereum, GRANDPA, BSC, Tendermint, Pharos, etc., as referenced in scope). Any unprivileged relayer can submit the proof and drive the handler calls once the (possibly-too-short) global delay has passed, requiring no privileged role.

### Recommendation
Store and enforce `challengePeriod` per state-machine (e.g., `mapping(uint256 stateMachineId => uint256 challengePeriod)` in `HostParams`/`EvmHost`), mirroring the pallet-ismp design that already parameterizes `challenge_period(id)` by state machine id [7](#0-6) . Update `HandlerV2.handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` to look up the challenge period keyed by the specific `proof.height.id`/`message.height.id` rather than calling the parameterless `host.challengePeriod()`.

### Proof of Concept
1. Governance/host-manager configures a single `HostParams.challengePeriod` (e.g. 30 minutes) tuned for a fast-finality EVM counterparty, then also adds a slower/weaker-finality state machine to `stateMachines` (e.g. via `IHostManager.updateHostParams`).
2. A relayer submits a consensus/state-machine update for the slow-finality chain, storing a commitment and `_stateCommitmentsUpdateTime` [12](#0-11) .
3. After only the global `challengePeriod` elapses (insufficient for the slow chain's real finality), the relayer calls `HandlerV2.handlePostRequests` with a valid MMR proof against that not-yet-irreversible commitment; `delay >= challengePeriod` passes the check [13](#0-12)  and the request is dispatched to the destination `IApp`.
4. The slow chain subsequently reorgs past the referenced block, invalidating the request that was already delivered/acted upon on the destination — demonstrating forged/unsound message delivery caused by the fixed, non-per-chain challenge window.

### Citations

**File:** evm/src/core/EvmHost.sol (L41-66)
```text
struct HostParams {
    // The fee token contract address. This will typically be DAI.
    // but we allow it to be configurable to prevent future regrets.
    address feeToken;
    // The admin account, this only has the rights to freeze, or unfreeze the bridge
    address admin;
    // Ismp message handler contract. This performs all verification logic
    // needed to validate cross-chain messages before they are dispatched to local modules
    address handler;
    // The authorized host manager contract, is itself an `IApp`
    // which receives governance requests from the Hyperbridge chain to either
    // withdraw revenue from the host or update its protocol parameters
    address hostManager;
    // The local UniswapV2Router02 contract, used for swapping the native token to the feeToken.
    address uniswapV2;
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

**File:** evm/src/core/EvmHost.sol (L127-133)
```text
    // mapping of state machine identifier to latest known height to state commitment
    // (stateMachineId => (blockHeight => StateCommitment))
    mapping(uint256 => mapping(uint256 => StateCommitment)) private _stateCommitments;

    // mapping of state machine identifier to latest known height to update time
    // (stateMachineId => (blockHeight => timestamp))
    mapping(uint256 => mapping(uint256 => uint256)) private _stateCommitmentsUpdateTime;
```

**File:** evm/src/core/EvmHost.sol (L781-787)
```text

        _consensusState = state;
        _consensusUpdateTimestamp = block.timestamp;

        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;
```

**File:** evm/src/core/EvmHost.sol (L809-817)
```text
        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
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

**File:** modules/ismp/core/src/handlers.rs (L108-113)
```rust
	let update_time = host.state_machine_update_time(*proof_height)?;
	let delay_period = host
		.challenge_period(proof_height.id)
		.ok_or(Error::ChallengePeriodNotConfigured { state_machine: proof_height.id })?;
	let current_timestamp = host.timestamp();
	Ok(delay_period.as_secs() == 0 || current_timestamp.saturating_sub(update_time) > delay_period)
```
