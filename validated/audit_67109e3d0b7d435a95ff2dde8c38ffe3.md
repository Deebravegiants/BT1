Based on my investigation, I found a valid analog to the C4 M-06 finding in this repository.

### Title
Missing upper-bound validation on `HostParams.challengePeriod` / `unStakingPeriod` in `EvmHost.updateHostParamsInternal` can permanently freeze message delivery - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.updateHostParamsInternal` validates that `hostManager`, `handler`, and `consensusClient` are proper contracts, that `hyperbridge` id and `stateMachines` are non-empty, and that `unStakingPeriod >= 1 day`. It performs **no upper bound** check on `challengePeriod` or `unStakingPeriod`. `challengePeriod` is later consulted in every message-delivery entry point in `HandlerV2.sol` as a strict gate (`challengePeriod > delay → revert ChallengePeriodNotElapsed()`), with no cap on how large it can be set.

### Finding Description
`updateHostParamsInternal` in [1](#0-0)  checks address validity, hyperbridge id, state-machine list length, and enforces only a lower bound on `unStakingPeriod` (`if (1 days > params.unStakingPeriod) revert InvalidUnstakingPeriod();`). There is no check that `challengePeriod` (or `unStakingPeriod`) is below any sane maximum (e.g., `type(uint256).max` is accepted).

`challengePeriod` is read and enforced as a hard gate in every message-processing function of `HandlerV2.sol`: [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

If `challengePeriod` is ever set to a value large enough that it can never be satisfied by `block.timestamp - stateMachineCommitmentUpdateTime` (e.g. a value comparable to `type(uint256).max`, or simply hundreds of years), every one of `handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` will unconditionally revert with `ChallengePeriodNotElapsed()` for that host, forever. This is the same class of bug as the referenced C4 finding: a single unbounded config write to a settings struct (delivered here through `updateHostParams`, restricted to the configured `hostManager` per [6](#0-5) ) can brick the host's message pipeline with no bounds enforced at write time, and — crucially — the very mechanism that is supposed to allow fixing the parameter (another `updateHostParams` call carried as an ordinary POST request through the same message-delivery path) is itself gated by the same broken `challengePeriod` check, since any correcting governance message must also clear `challengePeriod` before it can be delivered by `HandlerV2.handlePostRequests`. This mirrors exactly the original report's "without being able to execute a proposal, the setting itself could never be fixed" scenario.

### Impact Explanation
Once `challengePeriod` is bricked this way, the host stops accepting any inbound POST/GET requests, responses, or timeouts, permanently freezing the delivery route for that state machine's `IHost`, including the correcting governance message that would need to travel through that same permanently-gated path. Funds locked in escrow (e.g., `IntentGatewayV2`/`ExtrinsicIntents` cross-chain fills/refunds) or route-dependent flows on that host become permanently undeliverable, which fits the "route unable to deliver messages" and "freezing of funds" criteria.

### Likelihood Explanation
Low likelihood — it requires a governance-issued `SetHostParam`/`updateHostParams` update with a pathologically large `challengePeriod`, matching the original report's framing (unlikely but plausible misconfiguration, not malice). The `TestnetHost` admin-privileged override path in [7](#0-6)  similarly exercises `updateHostParamsInternal` with no additional bound checks, widening the surface where the mistake can be made.

### Recommendation
Add an explicit upper bound (e.g., a few days/weeks, well below the values that would make `challengePeriod > delay` impossible in practice) on `challengePeriod` (and reconsider an upper bound on `unStakingPeriod`) inside `updateHostParamsInternal`, reverting with a dedicated error if exceeded — mirroring the existing `InvalidUnstakingPeriod` pattern already used for the lower bound.

### Proof of Concept
1. Hyperbridge governance dispatches a `SetHostParam` request to the configured `HostManager` with `challengePeriod = type(uint256).max` (or any value the pallet-side operator mistakenly enters, e.g. mixing up units).
2. `HostManager.onAccept` delivers it and calls `EvmHost.updateHostParams` → `updateHostParamsInternal`, which stores the value with no upper-bound check, per [8](#0-7) .
3. Any subsequent call to `HandlerV2.handlePostRequests`/`handleGetResponses`/`handlePostRequestTimeouts`/`handleGetRequestTimeouts` computes `delay = block.timestamp - updateTime` and reverts with `ChallengePeriodNotElapsed()` because `challengePeriod > delay` can never become false.
4. Because the corrective `updateHostParams` message must itself be delivered as a POST request through `handlePostRequests`, which is gated by the same broken `challengePeriod`, the host is permanently unable to process any inbound message, including the one meant to fix it.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L581-621)
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
```

**File:** evm/src/core/EvmHost.sol (L627-637)
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

**File:** evm/src/core/HandlerV2.sol (L254-261)
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

**File:** evm/src/core/TestnetHost.sol (L35-59)
```text
contract TestnetHost is EvmHost {
    constructor(address _admin) EvmHost(_admin) {}

    /**
     * @dev Updates the HostParams. Callable by either `hostManager`
     * (cross-chain governance) or the configured `admin`. When invoked by
     * the admin, resets `_latestStateMachineHeight` for each state machine
     * in `params.stateMachines` before applying the new params, mirroring
     * the prior testnet behavior that lived inside `EvmHost`.
     */
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
