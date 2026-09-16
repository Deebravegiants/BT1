### Title
Production `challengePeriod` hardcoded to `0` instead of a safe fraud-proof window in `DeployIsmp.s.sol` / TRON deployment script - ([File: evm/script/DeployIsmp.s.sol])

### Summary
This is a direct analog to the reported bug class: a security-critical timing parameter is initialized to a value that only makes sense for testing (`0`), but the same initialization path is used for real (mainnet/production) deployments, silently disabling the protection the parameter is meant to provide unless an operator later corrects it via governance.

### Finding Description
`EvmHost`'s `challengePeriod` is meant to be the fraud-proof / dispute window that must elapse after a consensus/state-machine update before any request, response, or timeout referencing that height can be processed. This is enforced in `HandlerV2` via `ChallengePeriodNotElapsed` checks, e.g. in `handleGetRequestTimeouts`: [1](#0-0) 

However, the canonical EVM deployment script — used for both mainnet (`isMainnet == true`) and testnet paths — hardcodes `challengePeriod: 0` in the `HostParams` struct passed to `host.initialize(params)`, with no environment-configurable override (unlike `unStakingPeriod`, `feeToken`, `uniswapV2`, etc., which are read from config): [2](#0-1) 

The equivalent TRON migration script hardcodes the same `0, // challengePeriod` value directly into the constructor args used to deploy `TronHost` for production TRON deployments: [3](#0-2) 

Because `challengePeriod` gates every check throughout `HandlerV2` (`handleGetRequestTimeouts`, and by extension request/response/consensus-update handling that rely on the same `challengePeriod != 0 && challengePeriod > delay` guard pattern), setting it to `0` at deployment time means the guard is a no-op from genesis: any relayer can immediately submit proofs against a just-finalized consensus/state update with zero dispute window.

### Impact Explanation
The challenge period exists specifically to give watchers/fishermen time to detect and freeze a fraudulent consensus client update (e.g., forged BEEFY/SP1/ECDSA signatures or a compromised consensus source) before it can be acted upon. With `challengePeriod == 0` baked into the production deployment, a malicious or compromised consensus update can be immediately exploited to deliver forged messages, execute unauthorized cross-chain calls, or drain funds via `BandwidthManager`/`IntentGatewayV2`/token-bridge mint paths before any fraud-proof mechanism has a chance to intervene — a permanent loss of the core security guarantee of the state-proof pipeline, matching the "unsound state commitment / forged message delivery" impact class.

### Likelihood Explanation
This requires no attacker action beyond normal protocol operation once deployed as-is: any relayer submitting a proof through `HandlerV2` immediately after a state/consensus commitment lands satisfies the (disabled) check, since `challengePeriod != 0` short-circuits to false. The only mitigating factor is that governance (`HostManager`/`SetHostParam`) could raise `challengePeriod` post-deployment — but, mirroring the disputed report exactly, this depends on that follow-up governance action actually being taken, and the script gives no compile-time or config-driven safeguard preventing a production deployment with the unsafe `0` value.

### Recommendation
Make `challengePeriod` a required, explicitly-configured value in `DeployIsmp.s.sol` (and the TRON migration), sourced from `config.get("CHALLENGE_PERIOD")`/environment, with the script asserting a non-zero, sane minimum for `isMainnet` deployments (analogous to how `unStakingPeriod` is set to `21 days`), rather than defaulting silently to `0`.

### Proof of Concept
1. Run `DeployIsmp.s.sol` with `is_mainnet = true` (or any deployment) — `HostParams.challengePeriod` is set to `0` with no config override: [4](#0-3) 
2. `host.initialize(params)` commits this `0` value on-chain.
3. Once any consensus/state update is committed, an attacker/relayer can immediately call handler functions gated by `challengePeriod`, e.g. `handleGetRequestTimeouts`'s check: [5](#0-4) 
since `challengePeriod != 0` evaluates false, the `ChallengePeriodNotElapsed` revert never triggers, and the proof is processed with zero elapsed dispute time — identical in effect to the `Utils.getProtection()` bug where the safety-critical duration constant never takes effect in production.

### Citations

**File:** evm/src/core/HandlerV2.sol (L293-296)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();
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

**File:** evm/tron/migrations/2_deploy_ismp.js (L157-174)
```javascript
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
    ];

    await deployer.deploy(TronHost, hostParams);
```
