## Title
Unbounded `challengePeriod` in `updateHostParamsInternal` can permanently freeze message delivery or eliminate the fisherman veto window - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.updateHostParamsInternal` validates several `HostParams` fields (`hostManager`, `handler`, `consensusClient`, `hyperbridge`, `stateMachines`, `unStakingPeriod ≥ 1 days`) but places **no bound at all on `challengePeriod`**. This value directly gates every incoming request/response/timeout handler in `HandlerV2`. An unconstrained value — either `0` or an arbitrarily large number — reproduces exactly the "unbounded/under‑constrained variable" bug class from the referenced report: it can silently disable the security window (unfair/unsound acceptance) or make the check permanently unsatisfiable (DoS on the whole message route).

### Finding Description
`updateHostParamsInternal` copies `params.challengePeriod` into `_hostParams.challengePeriod` with no validation, unlike every other consensus-relevant field in the same function: [1](#0-0) 

Compare this to `unStakingPeriod`, which is explicitly bound (`if (1 days > params.unStakingPeriod) revert InvalidUnstakingPeriod();`) — `challengePeriod` gets no equivalent floor or ceiling.

`challengePeriod` is the dispute/fisherman-veto window that every relayed message must wait out before `HandlerV2` will process it: [2](#0-1) 

The identical pattern (`if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();`) is repeated for GET responses, POST timeouts, and GET timeouts: [3](#0-2) [4](#0-3) [5](#0-4) 

Because `challengePeriod` is unbounded:
- Setting it to `0` disables the wait entirely (the `challengePeriod != 0` short-circuit), meaning any relayed request/response is dispatched to its destination `IApp` the instant a state commitment is stored — before fishermen have any chance to veto a bad/forged commitment. This is exactly the documented purpose of the challenge period, per the protocol docs and Rust host logic that mirror the same "delay must elapse" invariant: [6](#0-5) 
- Setting it to an arbitrarily large value (e.g. `type(uint256).max`) makes `challengePeriod > delay` true forever, since `delay = block.timestamp - stateMachineCommitmentUpdateTime(...)` can never overtake it. Every call to `handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` reverts with `ChallengePeriodNotElapsed()` permanently — freezing the entire inbound message route on that `EvmHost` instance with no recovery path other than another governance update.

### Impact Explanation
This directly matches two of the accepted High/Medium impact categories:
- **Unsound state commitment / forged message delivery**: `challengePeriod = 0` collapses the fraud-proof/veto window to zero, letting a malicious or buggy state commitment be acted upon by destination applications before fishermen can react.
- **Route unable to deliver messages (permanent freeze)**: an oversized `challengePeriod` makes the `ChallengePeriodNotElapsed` check unsatisfiable for the lifetime of the host, blocking every POST/GET request, response, and timeout dispatch — a protocol-wide DoS reachable by a single governance-relayed `SetHostParam` message with no additional exploit needed on the message-delivery path itself.

### Likelihood Explanation
`updateHostParamsInternal` is reachable both via the intended cross-chain governance path (`HostManager.onAccept` → `updateHostParams`) and, on `TestnetHost`, directly by the configured admin: [7](#0-6) 

Nothing besides value-copying constrains `challengePeriod`; a single malformed or fat-fingered `HostParams` payload — the same operational-mistake class the original report calls out (`daDropInterval`/`mintlistStartTime` typos) — is sufficient to trigger either failure mode. No other invariant in the codebase (tests, ABI, or dispatcher) enforces a sane range for this field.

### Recommendation
Bound `challengePeriod` in `updateHostParamsInternal`, mirroring the existing `unStakingPeriod` check, e.g.:
- Enforce a sane minimum (non-zero, unless intentionally disabling the veto window is an explicit, separately-gated action) and a sane maximum (e.g., substantially less than `unStakingPeriod`, and small enough that it cannot exceed realistic relayer/fisherman response windows).
- Consider requiring `challengePeriod < unStakingPeriod` so the dispute window cannot outlive the unbonding period it is meant to precede.

### Proof of Concept
1. Governance (via `HostManager.onAccept` → `SetHostParam`) submits a `HostParams` update with `challengePeriod = type(uint256).max` (all other fields valid, e.g. as in `HostManagerTest._setHostParamRequest`): [8](#0-7) 
2. `updateHostParamsInternal` accepts it unconditionally since no bound exists: [9](#0-8) 
3. Any relayer subsequently calling `HandlerV2.handlePostRequests` (or the GET/timeout variants) for any state machine height will always fail `delay > challengePeriod`, so `revert ChallengePeriodNotElapsed()` fires unconditionally: [10](#0-9) 
4. No request, response, or timeout can ever be dispatched again on this host — a permanent, protocol-wide freeze until another governance update repairs `challengePeriod`.
   (Symmetrically, setting `challengePeriod = 0` removes the wait entirely, letting `handlePostRequests` act on a state commitment the instant it is stored, before any fisherman veto window has elapsed.)

### Citations

**File:** evm/src/core/EvmHost.sol (L607-636)
```text
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

**File:** evm/src/core/HandlerV2.sol (L181-210)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
    }
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

**File:** evm/src/core/HandlerV2.sol (L293-297)
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

**File:** evm/src/core/TestnetHost.sol (L45-59)
```text
    function updateHostParams(HostParams memory params) external override {
        address caller = _msgSender();
        if (caller != _hostParams.hostManager && caller != _hostParams.admin) {
            revert UnauthorizedAction();
        }

        if (caller == _hostParams.admin) {
            uint256 whitelistLength = params.stateMachines.length;
            for (uint256 i = 0; i < whitelistLength; ++i) {
                delete _latestStateMachineHeight[params.stateMachines[i]];
            }
        }

        updateHostParamsInternal(params);
    }
```

**File:** evm/tests/foundry/HostManagerTest.sol (L47-57)
```text
    function _setHostParamRequest(HostParams memory params) internal view returns (PostRequest memory) {
        return PostRequest({
            source: host.hyperbridge(),
            dest: host.host(),
            nonce: 0,
            from: new bytes(0),
            to: abi.encodePacked(host.hostParams().hostManager),
            timeoutTimestamp: 0,
            body: bytes.concat(bytes1(uint8(HostManager.OnAcceptActions.SetHostParam)), abi.encode(params))
        });
    }
```
