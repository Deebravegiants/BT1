## Analysis Result [1](#0-0) , [2](#0-1)  together establish a valid analog to CVE-2023-52353's bug class ("state is reset to a weaker floor instead of the correct prior value, silently lowering a security-relevant maximum/threshold").

### Title
Vetoing the latest `EvmHost` state-machine commitment resets the height floor to a hardcoded `1` instead of the true previous height, breaking the monotonicity gate in `HandlerV2.handleConsensus` - (File: `evm/src/core/EvmHost.sol`)

### Summary
`deleteStateMachineCommitmentInternal` in `EvmHost.sol` is the fisherman-veto path analogous to `mbedtls_ssl_session_reset` mishandling the negotiated maximum: instead of restoring the tracked "previous" state on reset, it clamps the security floor to a fixed low value, permanently weakening a check that gates all future consensus updates.

### Finding Description
When a fisherman successfully vetoes a state commitment that happens to be the current latest one for a state machine, `deleteStateMachineCommitmentInternal` resets `_latestStateMachineHeight[height.stateMachineId]` to the literal constant `1`: [3](#0-2) 

This differs from the equivalent Substrate pallet-ismp implementation, `delete_state_commitment`, which correctly restores the tracked `PreviousStateMachineHeight` rather than an arbitrary constant: [4](#0-3) 

The consequence is that `_latestStateMachineHeight` — the value used by `HandlerV2.handleConsensus` as the monotonicity floor for accepting new intermediate states from consensus proofs — is now `1` regardless of how far the chain had legitimately progressed before the veto: [2](#0-1) 

`if (latestHeight != 0 && intermediate.height > latestHeight)` becomes trivially satisfiable by nearly any height greater than `1`. This is the same bug class as the CVE: a stateful security-relevant value ("the maximum previously negotiated/verified level") is not properly restored on a reset event, permanently downgrading the effective security floor going forward instead of returning to the last known-good value.

### Impact Explanation
Once triggered, this permanently weakens the freshness/monotonicity check that protects `EvmHost` against acceptance of stale or superseded state-machine commitments. A relayer (or any party able to submit a subsequent consensus proof) could then have a stale, previously superseded intermediate state (any height `> 1` that is otherwise valid per the consensus client's own verification) accepted as the new "latest" state via `storeStateMachineCommitment`, even though it does not exceed the height that was legitimately established prior to the veto. This can unsoundly reset which `StateCommitment` is considered canonical/latest for a destination chain, which downstream determines which request/response/membership proofs (`stateMachineCommitment`, `handlePostRequests`, etc.) are accepted — undermining state-commitment soundness for message delivery and proof verification. This satisfies the "unsound state commitment" / "route unable to deliver messages correctly" bar.

### Likelihood Explanation
Likely only after a legitimate fisherman veto occurs against the *current latest* commitment for a state machine — an intentional, protocol-supported event (not attacker-controlled setup), so it requires the pre-condition of a veto happening at all, but once it occurs the downgrade is automatic and requires no further privilege or special conditions to exploit; any future legitimate-looking consensus update with `intermediate.height > 1` will pass the (now trivial) gate.

### Recommendation
Track and restore the actual previous verified height (mirroring `PreviousStateMachineHeight` in `modules/pallets/ismp/src/host.rs`) in `EvmHost.sol` instead of hardcoding `1` when the vetoed height equals the current latest, so the monotonicity floor in `HandlerV2.handleConsensus` cannot regress below the last honestly-verified height.

### Proof of Concept
1. Consensus proofs advance `_latestStateMachineHeight[id]` to height `H` (large) via `HandlerV2.handleConsensus`.
2. A fisherman submits a valid veto against the commitment at height `H`, calling the handler-restricted path that invokes `deleteStateMachineCommitmentInternal` [1](#0-0) .
3. `_latestStateMachineHeight[id]` is now set to `1`, not to the true prior legitimate height (e.g., `H-1` or whatever height preceded `H`).
4. A subsequent consensus proof containing an intermediate state at a low height `h` (`1 < h < H`) that is otherwise validly signed/finalized by the consensus client is now accepted by `handleConsensus`'s gate `intermediate.height > latestHeight` (`h > 1`), even though it does not represent forward progress relative to the pre-veto canonical height `H-1`.

**Note on completeness:** I was unable to locate, within the available iterations, the exact externally-callable veto/fraud-proof entrypoint that leads into `deleteStateMachineCommitmentInternal` (only its internal logic and the `restrict(_hostParams.handler)` modifier were confirmed) — a full review would need to trace that entrypoint to confirm the precise caller-permission model for the veto trigger.

### Citations

**File:** evm/src/core/EvmHost.sol (L704-721)
```text
    function deleteStateMachineCommitment(StateMachineHeight memory height, address fisherman)
        external
        restrict(_hostParams.handler)
    {
        deleteStateMachineCommitmentInternal(height, fisherman);
    }

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
```

**File:** evm/src/core/HandlerV2.sol (L155-163)
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
```

**File:** modules/pallets/ismp/src/host.rs (L194-222)
```rust
	fn delete_state_commitment(&self, height: StateMachineHeight) -> Result<(), Error> {
		// The height's entry in the state commitment queue is deliberately left
		// behind; locating it would mean scanning the queue, which is the per-insert
		// cost the queue exists to avoid. Usually its eviction is a no-op, but when
		// the vetoed height is the latest the reset below re-opens it for honest
		// resubmission, and the resubmitted height gets a *second* queue entry. The
		// stale entry then evicts the live commitment when it reaches the head —
		// one insertion before the live entry would have, since the resubmission
		// lands directly behind its stale twin. So a veto costs that height one
		// insertion of retention and permanently burns one queue slot. Both are
		// negligible against the configured caps; making it exact would need a
		// height -> index map on the insert path.
		BoundedStateCommitments::<T>::remove(height.id, height.height);
		BoundedStateMachineUpdateTime::<T>::remove(height.id, height.height);

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
		Ok(())
	}
```
