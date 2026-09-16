Based on my research, I found a direct analog to the Gearbox report in `EvmHost.sol`'s `updateHostParams`/`updateHostParamsInternal` mechanism, specifically regarding the mutable `challengePeriod` parameter.

### Title
Retroactive `challengePeriod` reduction via `updateHostParams` bypasses the fishermen veto window for already-stored state commitments - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.updateHostParams()` allows governance (via `hostManager`) to instantly change the global `challengePeriod` used to gate delivery of every pending request, response, and timeout. `HandlerV2` computes the elapsed delay against the *current* `challengePeriod` value rather than the value that was in effect when each `StateCommitment` was stored, so a parameter change retroactively applies to state commitments that are already in-flight, mirroring exactly the Gearbox `creditManager` bug class: mutable protocol parameters applied to pre-existing positions/commitments produce unintended, dangerous behavior.

### Finding Description
`updateHostParamsInternal` directly overwrites `_hostParams.challengePeriod` with no restriction preventing changes to already-pending state commitments: [1](#0-0) 

Every handler in `HandlerV2` (post requests, get responses, post/get timeouts) reads the challenge period live at call time and compares it against the delay since the commitment was stored: [2](#0-1) [3](#0-2) 

The same live-read pattern is used in `handlePostRequestTimeouts` and `handleGetRequestTimeouts`: [4](#0-3) [5](#0-4) 

The Rust `ismp-core` handler follows an identical pattern — `verify_delay_passed` reads `host.challenge_period(...)` live, not the value captured at commitment time: [6](#0-5) 

The challenge period exists precisely so that fishermen have a window to veto a fraudulent `StateCommitment` before it can be acted upon, as documented for the `vetoes` mapping and the fisherman mechanism: [7](#0-6) 

`updateHostParams` is dispatched cross-chain and applied without regard to any commitments already stored under the previous (longer) challenge period: [8](#0-7) 

### Impact Explanation
If `challengePeriod` is reduced (for entirely legitimate reasons — e.g. optimizing latency, matching an updated risk assessment of a consensus client), every `StateCommitment` stored before the update instantly becomes eligible for delivery under the new, shorter window, even though fishermen only budgeted their monitoring/veto cadence around the original, longer period. A relayer can then deliver `PostRequest`s, `GetResponse`s, or timeouts derived from a commitment that has not actually been vetted for the originally-intended duration, allowing state that should still be within its fraud-challenge window to be treated as final. This is functionally equivalent to processing an unsound/unverified state commitment — the exact bug class flagged in the original Gearbox report, where changing risk parameters retroactively affected already-open positions (there: credit accounts eligible for unintended liquidation; here: state commitments eligible for premature, unvetted delivery).

### Likelihood Explanation
No malicious actor is required — this triggers whenever `hostManager` legitimately updates `challengePeriod` downward (a normal governance action, e.g. tuning finality assumptions) while requests/responses/timeouts against older heights are still pending in the mempool or awaiting relayer submission. The parameter check performed in `updateHostParamsInternal` validates addresses/interfaces and non-zero lengths but places no constraint on how the new `challengePeriod` interacts with commitments already stored under the prior period, so this is trivially reachable on any governance-driven config update.

### Recommendation
Snapshot the `challengePeriod` value at the time each `StateCommitment` is stored (alongside `stateMachineCommitmentUpdateTime`) and use that stored value — not the live `_hostParams.challengePeriod` — when validating delay in `HandlerV2.handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` (and the analogous Rust `verify_delay_passed`). Alternatively, enforce that a `challengePeriod` decrease only applies to commitments stored after the update, never retroactively to already-stored heights.

### Proof of Concept
1. Governance (via `hostManager`) calls `updateHostParams` with `challengePeriod = 7 days` while a `StateCommitment` at height `H` is stored, giving fishermen a 7-day window to submit a veto.
2. Two days later, governance legitimately updates params again, reducing `challengePeriod` to `1 hour` (e.g., after gaining confidence in a faster consensus client).
3. A relayer immediately calls `handlePostRequests`/`handleGetResponses` referencing height `H`. `delay = block.timestamp - stateMachineCommitmentUpdateTime(H)` is now `> 1 hour`, so `challengePeriod > delay` is false and the check passes — even though fishermen were never given a fair chance to veto within the shortened window that now applies retroactively.
4. Any latent fraud in the commitment at height `H` (undetected because fishermen were still operating on the original 7-day cadence) is now actionable, enabling forged/unsound message delivery.

### Citations

**File:** evm/src/core/EvmHost.sol (L536-542)
```text
    /**
     * @dev Returns the fisherman responsible for vetoing the given state machine height.
     * @return the `fisherman` address
     */
    function vetoes(uint256 paraId, uint256 height) external view returns (address) {
        return _vetoes[paraId][height];
    }
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
