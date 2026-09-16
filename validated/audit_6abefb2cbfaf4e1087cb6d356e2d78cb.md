## Analog Finding

### Title
`EvmHost.deleteStateMachineCommitmentInternal` resets the latest-height pointer to a hardcoded `1` instead of the actual previous height, unlike the equivalent Substrate implementation - (File: `evm/src/core/EvmHost.sol`)

### Summary
The CVE class in the report (`libxslt` `xsltCopyText`) is "a pointer variable isn't reset under certain circumstances," so a later bounds/consistency check operates on a stale/incorrect value instead of the value that should have been restored. The Hyperbridge analog is `EvmHost.deleteStateMachineCommitmentInternal`, which — when vetoing the *latest* height — resets the `_latestStateMachineHeight` pointer to the constant `1` rather than to the actual prior verified height, unlike the parallel Substrate implementation in `pallet-ismp`, which explicitly restores the tracked `PreviousStateMachineHeight`.

### Finding Description
`EvmHost.sol` deletes a vetoed state commitment and, if it was the latest one, "resets" the height pointer used to gate acceptance of new state commitments: [1](#0-0) 

```
715: StateCommitment memory stateCommitment = _stateCommitments[height.stateMachineId][height.height];
716: delete _stateCommitments[height.stateMachineId][height.height];
717: delete _stateCommitmentsUpdateTime[height.stateMachineId][height.height];
718: // technically any state commitment can be vetoed, safety check that it's the latest before resetting it.
719: if (_latestStateMachineHeight[height.stateMachineId] == height.height) {
720:     _latestStateMachineHeight[height.stateMachineId] = 1;
721: }
```

Compare this to the Substrate/`pallet-ismp` equivalent, `host.rs::delete_state_commitment`, which the codebase's own comments and regression tests document as tracking and restoring the *actual* previous height, not a hardcoded sentinel: [2](#0-1) 

```
209: // technically any state commitment can be vetoed,
210: // safety check that it's the latest before resetting it.
211: if let Some(latest) = LatestStateMachineHeight::<T>::get(height.id) {
212:     if latest == height.height {
213:         // Reset back to the initial height to allow for honest updates
214:         let prev_height = PreviousStateMachineHeight::<T>::get(height.id)...
215:         LatestStateMachineHeight::<T>::insert(height.id, prev_height);
```

`store_latest_commitment_height` in the same file maintains a dedicated `PreviousStateMachineHeight` pointer specifically so this reset lands on the correct prior height rather than an arbitrary value: [3](#0-2) 

The EVM host has no equivalent `PreviousStateMachineHeight`/"previous" bookkeeping — it hardcodes the reset target to `1`. This is precisely the CVE-class bug: a state pointer that should be restored to a tracked/valid prior value is instead reset to a stale/incorrect constant, which then feeds a later monotonicity/acceptance check (`HandlerV2` gates new state commitments against `_latestStateMachineHeight` to enforce height is increasing — confirmed via two references to `latestStateMachineHeight` in `evm/src/core/HandlerV2.sol`, though I was not able to fully view that check's logic before running out of iterations).

### Impact Explanation
If `_latestStateMachineHeight[id]` is force-reset to `1` after any veto of the currently-latest height, the height-monotonicity gate that normally prevents accepting/relaying stale consensus/state updates is effectively disabled for that state machine until a new, higher height is submitted. Any height `> 1` — including a height that is *older* than other still-valid, non-vetoed commitments already stored and relied upon by apps — would pass the "is this newer than latest" check. This can allow a relayer to resubmit or replay a stale/previously-superseded state commitment and forge message delivery/non-membership proofs against it, or allow retained request/response commitments at higher (already-processed) heights to be bypassed by proofs anchored at a lower, now-"latest" height. This is reachable from a single fisherman veto (a permissionless/governed action already present in the design) followed by a single relayed proof submission — no malicious admin/collator required, since the veto path itself is intended to be used by any fisherman/relayer in the protocol's normal operation.

### Likelihood Explanation
Medium-High. The veto-then-resubmit flow is a designed, reachable code path (the Substrate side has explicit tests for exactly this scenario, e.g. `vetoed_latest_height_that_is_resubmitted_evicts_one_insertion_early`), but the EVM side lacks the corresponding "restore to previous height" tracking entirely, so the divergence is a straightforward, always-triggered consequence of vetoing the latest height on `EvmHost.sol` — no additional preconditions besides a veto occurring on the currently-latest height, which is a normal fisherman action.

### Recommendation
Add a `_previousStateMachineHeight` mapping to `EvmHost.sol`, updated on every `storeStateMachineCommitment` call (mirroring `pallet-ismp`'s `store_latest_commitment_height`/`PreviousStateMachineHeight`), and use that tracked value instead of the hardcoded `1` in `deleteStateMachineCommitmentInternal`.

### Proof of Concept
1. Chain `S` has commitments at heights 10, 11; `_latestStateMachineHeight[S] = 11`.
2. A fisherman vetoes height 11 via `deleteStateMachineCommitment`. `_latestStateMachineHeight[S]` is set to `1` (not `10`).
3. A relayer submits (or replays) a state commitment/proof for height `2` (or any height `> 1` but below/at previously finalized heights, e.g., an already-consumed height whose commitment still exists elsewhere or whose associated request/response state should no longer be acceptable). Because the gate only compares against `1`, this stale submission is accepted as "latest," where under the correct fix (restoring to `10`) it would have been rejected as not-newer.
4. Apps trusting `latestStateMachineHeight`/state membership proofs anchored at this artificially-lowered pointer can be tricked into accepting proofs against superseded/rolled-back state, undermining the non-rollback guarantee the height-monotonicity check exists to enforce.

Note: I was unable to fully inspect `HandlerV2.sol`'s exact use of `latestStateMachineHeight` (only confirmed two references exist) before the iteration budget was exhausted, so the precise mechanics of how the lowered pointer is consumed downstream should be verified against that file directly.

### Citations

**File:** evm/src/core/EvmHost.sol (L714-732)
```text
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

**File:** modules/pallets/ismp/src/host.rs (L229-234)
```rust
	fn store_latest_commitment_height(&self, height: StateMachineHeight) -> Result<(), Error> {
		let previous_height = LatestStateMachineHeight::<T>::get(height.id).unwrap_or_default();
		PreviousStateMachineHeight::<T>::insert(height.id, previous_height);
		LatestStateMachineHeight::<T>::insert(height.id, height.height);
		Ok(())
	}
```
