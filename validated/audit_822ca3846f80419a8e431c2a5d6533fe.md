Based on my research, I found a directly analogous pattern in the Hyperbridge EVM handler contracts. Note: I was unable to fully retrieve the body of `storeStateMachineCommitment` in `evm/src/core/EvmHost.sol` within the available tool calls (a grep typo caused me to miss confirming whether `_stateCommitmentsUpdateTime` is unconditionally written alongside every commitment write), so the "always in sync" assumption below could not be fully verified from the index and would need confirmation in a full checkout.

### Title
Unchecked-zero `stateMachineCommitmentUpdateTime` allows challenge-period bypass in `HandlerV2` message delivery - (File: evm/src/core/HandlerV2.sol)

### Summary
`HandlerV2` computes the elapsed time since a state machine height's commitment was recorded by directly subtracting `host.stateMachineCommitmentUpdateTime(height)` from `block.timestamp`, with no check that the stored update time is non-zero. Since Solidity mappings default to `0`, any height for which `_stateCommitmentsUpdateTime[id][height]` was never (or not yet) written will yield `delay = block.timestamp - 0`, an artificially huge value that always satisfies `delay > challengePeriod`, silently bypassing the entire challenge-period protection — the same class of bug as the reported `_timestampLU == 0` issue, where a zero-initialized timestamp is used in a subtraction/elapsed-time calculation without a guard.

### Finding Description
`handlePostRequests`, `handleGetResponses`, `handlePostRequestTimeouts`, and `handleGetRequestTimeouts` in `HandlerV2.sol` all follow the same pattern: [1](#0-0) [2](#0-1) [3](#0-2) 

`stateMachineCommitmentUpdateTime` is a plain mapping read with no existence check: [4](#0-3) 

The Rust/pallet-ismp equivalent explicitly stores the state-commitment and its update-time together on every write path (`store_state_machine_commitment` and `store_state_machine_update_time` are always called as a pair): [5](#0-4) 

but in the EVM `HandlerV2` consensus-update path, only `host.storeStateMachineCommitment(...)` is invoked for intermediate states — no companion call analogous to `store_state_machine_update_time` is visible at the call site: [6](#0-5) 

If the underlying `storeStateMachineCommitment` implementation in `EvmHost.sol` does not also unconditionally set `_stateCommitmentsUpdateTime[id][height] = block.timestamp` for that same height, the mapping stays at its zero default, and the delay computed in `handlePostRequests`/`handleGetResponses`/timeout handlers becomes `block.timestamp - 0`, which trivially exceeds any configured `challengePeriod`.

### Impact Explanation
If reachable, this defeats the challenge-period mechanism that is supposed to give fishermen a window to veto fraudulent/malicious state commitments before requests/responses proved against them are dispatched to destination modules. An unprivileged relayer could submit `handlePostRequests`/`handleGetResponses` calls against a state machine height whose commitment/update-time pair is desynchronized, causing forged or premature message delivery to be accepted before the safety window elapses — a forged-message-delivery / unsound-state-commitment class impact (Medium/High depending on how easily the update-time can be left at zero for a live, non-zero-root commitment).

### Likelihood Explanation
Likelihood depends entirely on whether `storeStateMachineCommitment` in `EvmHost.sol` always pairs the commitment write with an update-time write for every code path (initial genesis seeding via `updateHostParamsInternal`/`initialize`, and the consensus-update loop in `HandlerV2.handleConsensus`). This could not be conclusively confirmed from the retrieved snippets in this session; the absence of a visible paired call at the consensus-update site is the main indicator of risk, but the actual setter body must be inspected in a full repository checkout to confirm whether it internally sets both fields atomically.

### Recommendation
In `stateMachineCommitmentUpdateTime` consumers within `HandlerV2.sol`, explicitly revert if the returned update time is `0` (i.e., commitment never recorded / update-time missing) instead of relying on the subsequent `overlayRoot == bytes32(0)` check as the sole guard, and audit `storeStateMachineCommitment` in `EvmHost.sol` to guarantee that every commitment write is always paired with a synchronized, non-zero update-time write across all call sites (genesis initialization and per-height consensus updates).

### Proof of Concept
Not constructible without confirming, in a full checkout, a concrete code path where `EvmHost.storeStateMachineCommitment` sets a commitment/root for a height without also setting `_stateCommitmentsUpdateTime` for that same height — this is the key fact left unverified in this session and would need to be checked directly in `evm/src/core/EvmHost.sol`'s `storeStateMachineCommitment` implementation.

### Citations

**File:** evm/src/core/HandlerV2.sol (L155-164)
```text
        uint256 intermediatesLen = intermediates.length;
        for (uint256 i = 0; i < intermediatesLen; i++) {
            IntermediateState memory intermediate = intermediates[i];
            uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
            if (latestHeight != 0 && intermediate.height > latestHeight) {
                StateMachineHeight memory stateMachineHeight =
                    StateMachineHeight({stateMachineId: intermediate.stateMachineId, height: intermediate.height});
                host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
            }
        }
```

**File:** evm/src/core/HandlerV2.sol (L181-185)
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

**File:** evm/src/core/EvmHost.sol (L544-550)
```text
    /**
     * @param height - state machine height
     * @return the state machine update time at `height`
     */
    function stateMachineCommitmentUpdateTime(StateMachineHeight memory height) external view returns (uint256) {
        return _stateCommitmentsUpdateTime[height.stateMachineId][height.height];
    }
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L68-70)
```rust
			last_commitment_height = Some(state_height);
			host.store_state_machine_commitment(state_height, commitment_height.commitment)?;
			host.store_state_machine_update_time(state_height, host.timestamp())?;
```
