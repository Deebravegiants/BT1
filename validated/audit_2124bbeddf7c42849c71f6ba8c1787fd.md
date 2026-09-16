## Finding

### Title
Vetoing the latest EVM state-machine commitment resets `_latestStateMachineHeight` to a hardcoded `1` instead of the real prior height, reopening a monotonicity gap for stale/forged state commitments — (File: `evm/src/core/EvmHost.sol`)

### Summary
The CVE describes a Linux kernel bug where PV-feature teardown was only performed on secondary CPUs, leaving the boot CPU's stale hypervisor-shared memory locations untouched; on resume the hypervisor could write into those stale locations, corrupting the resumed kernel's state. The root cause pattern is: two code paths are supposed to perform equivalent "reset to a known-safe state" logic, but one path does an incomplete/inconsistent reset, leaving stale state reachable.

The same pattern exists between Hyperbridge's two `IsmpHost` implementations for the "veto a state commitment" operation. The Substrate implementation, `delete_state_commitment` in `modules/pallets/ismp/src/host.rs`, correctly resets `LatestStateMachineHeight` back to the tracked `PreviousStateMachineHeight` when the vetoed height was the latest one: [1](#0-0) 

The EVM implementation, `deleteStateMachineCommitmentInternal` in `evm/src/core/EvmHost.sol`, performs the analogous "teardown" incompletely/incorrectly: instead of restoring the real previous valid height, it hardcodes the reset value to `1`: [2](#0-1) 

### Finding Description
`HandlerV2.handleConsensus` uses `host.latestStateMachineHeight(...)` purely as a monotonicity gate to decide whether an intermediate state coming out of consensus verification should be (re)stored: [3](#0-2) 

Under normal operation this check ensures a state commitment for a given `stateMachineId` can only move forward, i.e. `_stateCommitments[stateMachineId][height]` is only overwritten by heights strictly greater than the last accepted one, preventing a relayer from re-proposing an older (potentially reorganized, forged, or already-fraudulent) height/state-root pair over one the protocol has already accepted and possibly acted on.

When a fisherman successfully vetoes the *latest* commitment via `deleteStateMachineCommitment` (called by the handler on a valid fraud/veto path), `EvmHost.sol` resets `_latestStateMachineHeight[stateMachineId]` to the literal constant `1` rather than to the actual last-known-good height (which the Substrate host correctly tracks via `PreviousStateMachineHeight`). Because genesis/trusted state-machine heights for real chains are always far greater than `1`, this reset effectively collapses the monotonicity floor to zero for all practical purposes: any intermediate height greater than `1` — including a height that lies *below* the previously accepted, still-valid latest height, or even a height matching the just-vetoed one — will satisfy `intermediate.height > latestHeight` on the very next consensus update and get written into `_stateCommitments`.

This "incomplete teardown" reopens a window in which an already-superseded or previously-fraudulent state commitment (for the same stateMachineId) can be resubmitted and re-accepted through `handleConsensus`, since the guard rail that is supposed to enforce forward-only progress has been reset to a value that is essentially always satisfied, rather than to the value the protocol actually still trusts.

### Impact Explanation
State-machine commitments (`stateMachineCommitment`) are the root of trust used by `handlePostRequests`/`handleGetResponses` in `HandlerV2.sol` to verify Merkle-Mountain-Range membership proofs for cross-chain requests. Allowing a stale/forged height's commitment to overwrite the trusted one — after it has already been vetoed once, or below the genuinely latest verified height — can lead to unsound state commitments being accepted, which downstream permits forged message delivery or replay of already-processed/timed-out cross-chain messages against the corrupted commitment. This satisfies "unsound state commitment" / "forged message delivery" impact criteria.

### Likelihood Explanation
Triggering this requires: (1) a `StateCommitmentVetoed` event on the *latest* height for some `stateMachineId` (a normal, expected fisherman action against a byzantine/erroneous update), followed by (2) any subsequent consensus proof submission (an ordinary relayer action) whose consensus-client-verified intermediate states include a height between `1` and the true previous trusted height. Both steps are reachable by unprivileged relayers/fishermen through the standard `HandlerV2` dispatch path, with no special privileges required, making this a realistic sequence rather than a purely theoretical one.

### Recommendation
Track the actual previous verified height per `stateMachineId` on `EvmHost` (mirroring `PreviousStateMachineHeight` in `pallet-ismp`) and restore `_latestStateMachineHeight` to that tracked value in `deleteStateMachineCommitmentInternal`, instead of hardcoding `1`.

### Proof of Concept
1. Consensus client verifies and stores commitments for state machine `S` at heights `100`, `200` (latest = `200`).
2. A fisherman calls `deleteStateMachineCommitment` on height `200` (the latest) — `_latestStateMachineHeight[S]` is reset to `1` per `evm/src/core/EvmHost.sol:719-721`.
3. A relayer submits a new consensus proof whose verified intermediate states include height `150` (below the true prior trusted height of `100`... or even a stale/previously-superseded fork height). Since `150 > 1`, `HandlerV2.handleConsensus` (`evm/src/core/HandlerV2.sol:158-163`) accepts and stores it as if it were new, even though it violates the intended forward-only progress guarantee that the Substrate implementation enforces via its `PreviousStateMachineHeight` bookkeeping.

### Citations

**File:** modules/pallets/ismp/src/host.rs (L209-220)
```rust
		// technically any state commitment can be vetoed,
		// safety check that it's the latest before resetting it.
		if let Some(latest) = LatestStateMachineHeight::<T>::get(height.id) {
			if latest == height.height {
				// Reset back to the initial height to allow for honest updates
				let prev_height =
					PreviousStateMachineHeight::<T>::get(height.id).ok_or_else(|| {
						Error::Custom("Previous state machine height should exist".to_string())
					})?;
				LatestStateMachineHeight::<T>::insert(height.id, prev_height);
			}
		}
```

**File:** evm/src/core/EvmHost.sol (L711-732)
```text
    /**
     * @dev Delete the state commitment at given state height.
     */
    function deleteStateMachineCommitmentInternal(StateMachineHeight memory height, address fisherman) internal {
        StateCommitment memory stateCommitment = _stateCommitments[height.stateMachineId][height.height];
        delete _stateCommitments[height.stateMachineId][height.height];
        delete _stateCommitmentsUpdateTime[height.stateMachineId][height.height];
        // technically any state commitment can be vetoed, safety check that it's the latest before resetting it.
        if (_latestStateMachineHeight[height.stateMachineId] == height.height) {
            _latestStateMachineHeight[height.stateMachineId] = 1;
        }

        // track the fisherman responsible for rewards on hyperbridge through state proofs
        _vetoes[height.stateMachineId][height.height] = fisherman;

        emit StateCommitmentVetoed({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId),
            stateCommitment: stateCommitment,
            height: height.height,
            fisherman: fisherman
        });
    }
```

**File:** evm/src/core/HandlerV2.sol (L151-164)
```text

        if (keccak256(previousState) == keccak256(verifiedState)) return;
        host.storeConsensusState(verifiedState);

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
