### Title
Default deployment configuration sets `challengePeriod = 0`, disabling the fraud-proof challenge window - ([File: evm/script/DeployIsmp.s.sol])

### Summary
The `challengePeriod` protocol parameter — the analog of the reported "chain confirmations" — is hard-coded to `0` in the canonical EVM deployment script and mirrored across test fixtures and TRON migration scripts. A `challengePeriod` of `0` is treated as a sentinel that completely disables the delay check in both the Solidity handler and the Substrate pallet, meaning state commitments become immediately actionable the instant a consensus proof is accepted, with zero window for fishermen to submit fraud proofs against byzantine consensus behavior.

### Finding Description
`HostParams.challengePeriod` is meant to hold state commitments pending even after consensus verification, specifically to give fishermen time to detect and prove byzantine behavior before requests/responses/timeouts are actionable, as documented in [1](#0-0) .

In `HandlerV2.sol`, every message-processing entrypoint (`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, `handleGetRequestTimeouts`) gates on the same pattern: [2](#0-1) 

When `challengePeriod == 0`, the check `challengePeriod != 0 && challengePeriod > delay` short-circuits to `false`, meaning the delay requirement is entirely bypassed rather than reduced to "no wait" — this is not a benign zero, it is a disabled safety check. The same bypass-on-zero semantics exist in the Substrate/pallet-ismp side: [3](#0-2) 

Neither `EvmHost.updateHostParamsInternal` nor the deployment tooling enforces any minimum on `challengePeriod`, even though it validates several other invariants (`unStakingPeriod`, `hostManager`, `handler`, `consensusClient`, `hyperbridge` id): [4](#0-3) 

Crucially, the production/canonical deployment script that provisions a new `EvmHost` (used to deploy real Hyperbridge hosts, wiring an `SP1Beefy`/`EcdsaBeefy` consensus client) sets `challengePeriod: 0` directly in the initial `HostParams`: [5](#0-4) 

The same unsafe value is repeated in the TRON deployment migration and multiple test fixtures, showing it is the accepted "default" pattern rather than an isolated oversight: [6](#0-5) [7](#0-6) 

This is precisely the bug class described in the external report: a safety-critical delay/confirmation parameter with an unsafe (here, the most unsafe possible — zero, i.e. disabled) value used as the shipped/example default, with no protocol-enforced floor.

### Impact Explanation
With `challengePeriod = 0`, any state commitment accepted by the configured consensus client (`SP1Beefy`/`EcdsaBeefy`/BSC/etc.) is immediately usable to deliver post requests, get responses, and timeouts — there is no window for fishermen to submit a `freeze_client` fraud proof against a byzantine/faulty consensus update before it is acted upon. If a consensus client accepts an invalid finality proof (bug, misconfiguration, or compromised light-client input) even momentarily, an attacker can immediately push forged `PostRequest`/`GetResponse` messages through `HandlerV2` before any fraud-proof mechanism has a chance to intervene, since `EvmHost` deployed with these defaults has the delay check permanently disabled until governance (`updateHostParams`, restricted to `hostManager`) changes it. This directly undermines the protocol's documented safety model that "safety in on-chain consensus clients will require the use of a challenge window, even after consensus proof verification" and can lead to unauthorized app actions / forged message delivery on any host deployed with the script's defaults.

### Likelihood Explanation
Every freshly deployed `EvmHost` via the canonical `DeployIsmp.s.sol` script (and the TRON migration) starts with the challenge window disabled from block one, and stays that way until an explicit governance `updateHostParams` call raises it — there is no on-chain floor preventing an operator from leaving it at (or resetting it to) zero. Given this is the literal default baked into the deployment tooling used to stand up new hosts, the likelihood that a live host runs with no challenge window is high absent manual, unenforced operational discipline.

### Recommendation
Enforce a protocol-level minimum non-zero `challengePeriod` in `EvmHost.updateHostParamsInternal` (analogous to the existing `1 days > unStakingPeriod` check for `unStakingPeriod`), and change the semantics so `challengePeriod == 0` is not a magic "disable check" sentinel — require it to always apply the delay comparison. Update `DeployIsmp.s.sol` and the TRON migration script to set a safe non-zero default, and apply the equivalent floor in `pallet-ismp`'s `verify_delay_passed`/`create_client` path so no consensus state can be created or updated with a zero challenge period unless explicitly and safely justified.

### Proof of Concept
1. Deploy `EvmHost` using `evm/script/DeployIsmp.s.sol`, which sets `challengePeriod: 0` in `HostParams`.
2. A relayer submits a `ConsensusMessage` via `HandlerV2.handleConsensus`, which is accepted and stores a new `StateMachineHeight`/`StateCommitment` (`evm/src/core/HandlerV2.sol` lines 144-174).
3. Immediately in the same or a subsequent block, call `handlePostRequests` with a proof at that height: `challengePeriod` is `0`, so `challengePeriod != 0 && challengePeriod > delay` evaluates to `false` regardless of `delay`, and the request is dispatched with zero elapsed challenge time (`evm/src/core/HandlerV2.sol` lines 182-186).
4. No fisherman has any window to submit a fraud proof against the consensus update before its effects (message delivery) are already final.

### Citations

**File:** docs/content/protocol/ismp/consensus.mdx (L30-30)
```text
The quest for a mechanism by which a consensus client may observe and come to conclusions about the canonical state of another blockchain leads us to understand the concept of safety in distributed systems. We elaborate further on this in the section on [consensus proofs](/protocol/interoperability/consensus-proofs). In summary, we show that safety in on-chain consensus clients will require the use of a challenge window, even after consensus proof verification. This allows us to detect potential Byzantine behavior that may arise without the challenge window in place.
```

**File:** evm/src/core/HandlerV2.sol (L182-186)
```text
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
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

**File:** evm/src/core/EvmHost.sol (L573-616)
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

**File:** evm/tron/migrations/2_deploy_ismp.js (L156-171)
```javascript
    // HostParams struct — field order must match the Solidity struct definition
    const hostParams = [
        DEFAULT_TIMEOUT, // defaultTimeout
        defaultPerByteFee.toString(), // defaultPerByteFee
        stateCommitmentFee.toString(), // stateCommitmentFee
        feeToken, // feeToken
        admin, // admin
        handler.address, // handler
        hostManager.address, // hostManager
        uniswapV2, // uniswapV2
        UNSTAKING_PERIOD, // unStakingPeriod
        0, // challengePeriod
        consensusRouter.address, // consensusClient
        stateMachines, // stateMachines
        perByteFees, // perByteFees
        hyperbridge, // hyperbridge
```

**File:** evm/tests/foundry/HandlerV2Test.sol (L61-72)
```text
        HostParams memory params = HostParams({
            uniswapV2: address(0),
            admin: address(this),
            hostManager: address(manager),
            handler: address(handler),
            unStakingPeriod: 21 * (60 * 60 * 24),
            challengePeriod: 0,
            consensusClient: address(consensusClient),
            feeToken: address(feeToken),
            hyperbridge: StateMachine.kusama(paraId),
            stateMachines: stateMachines
        });
```
