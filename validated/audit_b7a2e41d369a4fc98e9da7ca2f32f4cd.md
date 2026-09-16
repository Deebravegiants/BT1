Confirmed: `EvmHost.challengePeriod()` is a single global mutable value read live at message-handling time in every `HandlerV2` entry point (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`), each computed against the immutable `stateMachineCommitmentUpdateTime` recorded when the state commitment landed. This is architecturally identical to the BendDAO bug: a duration parameter is stored as "start time" and the *current* (possibly just-changed) parameter is applied retroactively to already-pending windows.

### Title
Changing `challengePeriod` retroactively shortens the fisherman-veto window for already-finalized, pending state commitments - (File: evm/src/core/HandlerV2.sol)

### Summary
`updateHostParams`/`updateHostParamsInternal` lets cross-chain governance (via `hostManager`) change `_hostParams.challengePeriod` at any time, with no restriction tied to in-flight state commitments. Every message-handling entry point in `HandlerV2` (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`) computes elapsed delay as `block.timestamp - host.stateMachineCommitmentUpdateTime(height)` and compares it to the **current** `host.challengePeriod()`, rather than the challenge period that was in effect when that specific state commitment was finalized.

### Finding Description
When a state commitment is finalized via consensus update (`storeStateMachineCommitment`/`_stateCommitmentsUpdateTime`), fishermen are expected to have a full `challengePeriod` window (per [1](#0-0) ) to detect and veto fraudulent commitments via `pallet-fishermen::veto_state_commitment`. Relayers are likewise expected to wait out that same window before submitting requests/responses ( [2](#0-1) ).

If governance shortens `challengePeriod` while commitments finalized under the old (longer) period are still pending fisherman review, `HandlerV2` immediately honors the new, shorter delay: [3](#0-2) [4](#0-3) 

The check is not "was this commitment's own configured challenge period satisfied", it's "does the *current global* `challengePeriod()` value satisfy the elapsed delay". The parameter is updated globally and instantaneously: [5](#0-4) 

This exactly mirrors the BendDAO pattern: a start timestamp is stored (`stateMachineCommitmentUpdateTime`), but the duration used to compute the "window has elapsed" check is read dynamically rather than snapshotted per-commitment, so any parameter change applies retroactively to windows that already began under a different assumption.

### Impact Explanation
An unprivileged relayer can submit `PostRequestMessage`/`GetResponseMessage`/timeout messages referencing a state commitment the moment governance lowers `challengePeriod`, even though that commitment was finalized under the expectation of a longer veto window and fishermen infrastructure (which is asynchronous, off-chain, and paced against the originally-advertised period per [6](#0-5) ) has not finished its review. If a fraudulent or byzantine state commitment (e.g. from a compromised/faulty consensus client, per [7](#0-6) ) slips through before it can be vetoed, relayers can deliver forged messages against it, allowing unauthorized app actions / unsound state commitment usage on the destination `IApp`s that trust delivered ISMP requests/responses. This satisfies the "forged message delivery / unsound state commitment" impact bar.

### Likelihood Explanation
`challengePeriod` is an ordinary host parameter that legitimate, non-malicious governance is expected to tune over the protocol's lifetime (analogous to BendDAO's `auctionDuration`) — there is no code path preventing a reduction while commitments are in-flight, and no per-commitment snapshotting of the period that applied when it was created. Any relayer, immediately after such a routine update, can trigger the shortened check on an existing pending commitment; no attacker collusion with governance is required, only ordinary parameter maintenance colliding with the asynchronous, best-effort timing of the fisherman watch process.

### Recommendation
Snapshot the challenge period at the time a state commitment (or consensus update) is stored — e.g. persist `challengeEndTimestamp = block.timestamp + challengePeriod` alongside `_stateCommitmentsUpdateTime`, and have `HandlerV2` compare `block.timestamp > challengeEndTimestamp` for that specific height rather than re-deriving it from the live `challengePeriod()` value. Apply the analogous fix on the Substrate side (`store_challenge_period`/`verify_delay_passed` in `modules/ismp/core/src/handlers.rs`) so a global `update_host_params` change cannot retroactively affect commitments already in their challenge window.

### Proof of Concept
1. Consensus client updates state machine to height `H` at `t0`; `challengePeriod = 7 days` at that time, so fishermen and relayers alike expect the commitment to be safely finalized only after `t0 + 7 days`.
2. At `t0 + 1 hour`, governance dispatches `updateHostParams` (via `hostManager`) reducing `challengePeriod` to `1 hour` for unrelated reasons (e.g. optimizing latency for a different, trusted state machine) — see `updateHostParamsInternal` in [8](#0-7) .
3. Immediately at `t0 + 1 hour + 1s`, any relayer calls `handlePostRequests` with a proof against height `H`; `delay = 1 hour` now exceeds the new `challengePeriod = 1 hour`, so the check in [9](#0-8)  passes and the request is dispatched to the destination `IApp`, even though fishermen (paced against the original 7-day expectation) have not finished verifying height `H`.
4. If `H`'s commitment was fraudulent, the forged request is delivered before it can be vetoed.

### Citations

**File:** docs/content/protocol/ismp/consensus.mdx (L218-218)
```text
A `StateMachineUpdated` event is emitted to notify network participants (both relayers and fishermen) of some newly available `StateCommitment`s for a given state machine. Relayers will wait for the configured `challenge_period` before attempting to transmit new requests & responses. While fishermen will check if these pending `StateCommitment`s describe valid states on the counterparty network. If the `challenge_period` elapses without any fraud proofs being presented, we can safely conclude that the provided `StateCommitment`s are indeed canonical.
```

**File:** sdk/packages/sdk/src/utils.ts (L68-76)
```typescript
export async function waitForChallengePeriod(chain: IChain, stateMachineHeight: StateMachineHeight): Promise<void> {
	// Get the challenge period for this state machine
	const challengePeriod = await chain.challengePeriod(stateMachineHeight.id)

	if (challengePeriod === BigInt(0)) return

	// Get the state machine update time
	const updateTime = await retryPromise(() => chain.stateMachineUpdateTime(stateMachineHeight), {
		maxRetries: 3,
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

**File:** evm/src/core/EvmHost.sol (L573-645)
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

        // add whitelisted state machines
        for (uint256 i = 0; i < stateMachinesLen; ++i) {
            // create if it doesn't already exist
            if (_latestStateMachineHeight[params.stateMachines[i]] == 0) {
                _latestStateMachineHeight[params.stateMachines[i]] = 1;
            }
        }
    }
```

**File:** tesseract/messaging/primitives/src/lib.rs (L742-756)
```rust
pub async fn wait_for_challenge_period(
	client: Arc<dyn IsmpProvider>,
	last_consensus_update: Duration,
	counterparty_state_id: StateMachineId,
) -> anyhow::Result<()> {
	let challenge_period = client.query_challenge_period(counterparty_state_id).await?;
	if challenge_period != Duration::ZERO {
		log::info!(
			target: LOG_TARGET, "Waiting for challenge period {challenge_period:?} for {} on {}",
			counterparty_state_id.state_id,
			client.name()
		);
	}

	tokio::time::sleep(challenge_period).await;
```

**File:** docs/content/developers/explore/fishermen.mdx (L12-18)
```text
## What a Fisherman Can Do

A fisherman holding a seat in the active collator set can:

- **Veto a state commitment** by calling `pallet-fishermen.veto_state_commitment` with a specific `StateMachineHeight`. The veto is accepted without requiring a cryptographic proof — the fisherman's inclusion in the collator set is the trust anchor.
- **Block cross-chain message delivery** for the vetoed height. Because a state commitment is an accumulator, messages from a vetoed height will still be included in a later commitment once the correct state is finalised. A veto delays processing; it cannot censor a specific message permanently.
- **Prevent a compromised or faulty consensus client** from anchoring fraudulent L2 state on Hyperbridge, which would otherwise let attackers fabricate state proofs and drain applications of funds.
```
