I have sufficient evidence now to write the finding.

### Title
`challengePeriod` is deployed as `0`, disabling the fisherman veto window on `HandlerV2` message delivery - ([File: evm/script/DeployIsmp.s.sol])

### Summary
Hyperbridge's threat model relies on a configurable `challengePeriod` during which fishermen can veto a fraudulent state commitment before any request/response/timeout relying on it is delivered. The production EVM deployment script sets `challengePeriod: 0` for the `EvmHost`, and every `HandlerV2` delivery path treats `0` as "disabled" rather than "instant," so the veto window that the protocol design depends on is never enforced on mainnet deployments produced by this script.

### Finding Description
`HandlerV2` gates every incoming message class (post requests, get responses, post-request timeouts, get-request timeouts) on the host's `challengePeriod`, but explicitly short-circuits the check when it is `0`: [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

The same pass-through pattern exists in the Substrate-side handler used by `pallet-ismp`: [5](#0-4) 

This design is intentional for local testing/bootstrap (mirrors the analog report's Figure 2 `if (timeLockPeriod == 0) return;`), but the production deployment script for the EVM host, `DeployIsmp.s.sol`, hardcodes `challengePeriod: 0` in the `HostParams` used for `host.initialize(params)` on both mainnet and non-mainnet paths: [6](#0-5) 

`challengePeriod` can only be corrected later via `updateHostParams`, which is `restrict(_hostParams.hostManager)`-gated and driven exclusively by cross-chain governance requests relayed from Hyperbridge, mirroring the original bug's dependency on an explicit follow-up `setTimeLock` call that the deploy migration never makes: [7](#0-6) 

### Impact Explanation
With `challengePeriod == 0`, `HandlerV2.handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` will accept and dispatch messages the instant a state/consensus commitment is stored, with no window for fishermen to submit a fraud proof and veto it via `freeze_client`/`StateCommitmentVetoed`. This defeats the "vetoable window" safety property described for consensus updates: [8](#0-7) 

An attacker (or relayer colluding with a byzantine authority set) who can get any state commitment stored — including one obtained through consensus fault/eclipse conditions the challenge period is meant to catch — can have arbitrary forged requests/responses delivered to destination modules before any fisherman has a chance to react, enabling forged message delivery / unsound state commitment consumption, matching the "Accept" criteria for this scan (forged message delivery, unsound state commitment).

### Likelihood Explanation
This is not a hypothetical misconfiguration: the checked-in deployment script `evm/script/DeployIsmp.s.sol` sets `challengePeriod: 0` unconditionally for both the mainnet (`EvmHost`) and non-mainnet (`TestnetHost`) branches, and the SDK's own `waitForChallengePeriod` helper short-circuits identically when it reads `0` from-chain: [9](#0-8) 

Any host deployed with this script — unless a subsequent governance-only `updateHostParams` call is made to raise `challengePeriod` — runs permanently with the veto window disabled, exactly analogous to the original `TimeLockUpgrade` finding.

### Recommendation
- **Short term:** Set a non-zero `challengePeriod` (matching the documented/whitepaper-equivalent window) directly in `DeployIsmp.s.sol`'s `HostParams` before calling `host.initialize(params)`, for both mainnet and testnet paths.
- **Long term:** Make `EvmHost`/`pallet-ismp` reject a `0` challenge period as a valid production configuration (e.g., require an explicit minimum, or require `updateHostParams`/governance to affirmatively set it before request/response delivery is permitted), rather than silently treating `0` as "no delay."

### Proof of Concept
1. Run `DeployIsmp.s.sol` as-is; observe `HostParams.challengePeriod == 0` is passed to `host.initialize(params)`.
2. Have the consensus client/handler store a new state machine commitment via `handleConsensus`.
3. Immediately (same block) call `HandlerV2.handlePostRequests` with a valid MMR proof against that commitment: `delay = 0`, `challengePeriod == 0` so the `if (challengePeriod != 0 && challengePeriod > delay)` guard at `evm/src/core/HandlerV2.sol:184-185` never reverts, and the request is dispatched with zero elapsed veto time — regardless of whether fishermen have had any opportunity to challenge the underlying state commitment.

### Citations

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

**File:** evm/script/DeployIsmp.s.sol (L126-140)
```text
        // EvmHost
        HostParams memory params = HostParams({
            uniswapV2: uniswapV2,
            admin: admin,
            hostManager: address(manager),
            handler: address(handler),
            unStakingPeriod: 21 * (60 * 60 * 24),
            challengePeriod: 0,
            consensusClient: address(consensusClient),
            hyperbridge: hyperbridge,
            feeToken: feeToken,
            stateMachines: stateMachines
        });

        host.initialize(params);
```

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

**File:** docs/content/protocol/ismp/consensus.mdx (L171-174)
```text
The `update_client` method is responsible for advancing the state of the consensus client. This performs the consensus verification of new `StateCommitment`s that have been finalized by a `StateMachine`'s consensus system. The `IsmpHost` must return the concrete implementation of the associated `ConsensusClient` and a previously stored `ConsensusState`. The procedure for updating the consensus client is as follows.

- First the handler must assert that the consensus client is not frozen or expired. Consensus clients can expire if the last time the consensus client was updated has exceeded the chain's unbonding period. This effectively mitigates any potential long fork attacks that may arise due to a loss of liveness of consensus clients.
- Finally the handler may perform consensus proof verification using the concrete implementation for the consensus client using `ConsensusClient::verify_consensus`. If verifications pass, the udpated `ConsensusState` and `IntermediateState`s are persisted to storage and enter a new challenge period.
```

**File:** sdk/packages/sdk/src/utils.ts (L68-73)
```typescript
export async function waitForChallengePeriod(chain: IChain, stateMachineHeight: StateMachineHeight): Promise<void> {
	// Get the challenge period for this state machine
	const challengePeriod = await chain.challengePeriod(stateMachineHeight.id)

	if (challengePeriod === BigInt(0)) return

```
