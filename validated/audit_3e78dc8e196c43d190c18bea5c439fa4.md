## Analysis: Mapping invalidation left in an inconsistent/stale state after a veto

The CVE's bug class is: a mapping/state change (unmap) is not fully propagated/flushed, so stale mappings remain live and reachable, letting privileges/permissions apply where they should not. The closest reachable analog in this codebase is in `EvmHost.sol`'s state-commitment veto path, where invalidating ("unmapping") a state commitment does not correctly restore the height-tracking invariant that guards against overwriting/re-accepting stale commitments — unlike the equivalent Substrate-side implementation, which does this correctly.### Title
Unsound state-commitment invalidation on veto — `_latestStateMachineHeight` is reset to sentinel `1` instead of the true prior height, reopening the monotonicity gate to stale/overwritten state commitments - (`evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.deleteStateMachineCommitmentInternal` (invoked via the fisherman-veto path, callable by any relayer/fisherman that submits a valid fraud/veto proof through the `handler`) deletes a state commitment and, if the vetoed height was the chain's latest, resets `_latestStateMachineHeight[stateMachineId]` to the hardcoded sentinel value `1` — the same sentinel used to mark an *uninitialized* state machine — rather than restoring the actual previous verified height. `HandlerV2.handleConsensus` only guards against overwriting an already-stored commitment implicitly, via the strict `intermediate.height > latestHeight` check; it has no explicit "commitment already exists, skip" check like the Substrate handler does. Resetting `latestHeight` to `1` therefore reopens the write-gate for the entire range of already-committed heights `(1, H]` for that state machine, breaking the monotonicity invariant the rest of the protocol relies on.

### Finding Description
On Substrate, `pallet_ismp`'s `delete_state_commitment` correctly restores the monotonic pointer from `PreviousStateMachineHeight` when vetoing the latest height: [1](#0-0) 

The EVM host's equivalent path does not track or restore a "previous height" at all — it unconditionally collapses the pointer to `1`: [2](#0-1) 

`1` is not an arbitrary low number — it is the exact sentinel the host uses to mark a state machine as "known but never committed," set the first time a state machine is whitelisted: [3](#0-2) 

The only gate protecting stored state commitments from being clobbered by a later consensus update is the strict inequality in `HandlerV2.handleConsensus`: [4](#0-3) 

This works correctly *only* as long as `latestHeight` faithfully reflects the maximum height ever committed for that chain — because once a height `h` is stored, `latestHeight` becomes `≥ h`, so a later message referencing the same `h` fails `intermediate.height > latestHeight` and is silently skipped (this is the *only* duplicate/overwrite protection on the EVM side; unlike the Rust core handler, there is no explicit "skip if `state_machine_commitment` already exists" check): [5](#0-4) 

The veto path breaks that invariant: after a veto of the latest height `H`, `latestHeight` becomes `1` even though heights `2..H-1` still hold live, previously-verified `StateCommitment` entries in `_stateCommitments`. Any subsequent consensus proof that verifies through `IConsensusV2.verify` and contains an `IntermediateState` for any height `h` with `1 < h ≤ H-1` will now pass `intermediate.height > latestHeight` and call `storeStateMachineCommitment`, unconditionally overwriting the existing, previously-verified commitment for that height: [6](#0-5) 

This is the same bug class as the Xen CVE: a state-invalidating operation (veto ≈ IOMMU unmap) fails to correctly synchronize the dependent tracking structure (the monotonic height pointer ≈ TLB), leaving a window where already-superseded/stale entries can be resurrected and treated as authoritative again.

### Impact Explanation
`_stateCommitments[stateMachineId][height]` backs every membership/non-membership proof verification for POST requests, GET responses, and timeouts in `HandlerV2` (`stateMachineCommitment(...).overlayRoot`/`.stateRoot`). If a stale or attacker-influenced commitment can silently overwrite a previously verified, higher-integrity commitment at a lower height, any request/response whose delivery, timeout, or fee-accounting proof is later checked against that height's root can be verified against a commitment that no longer represents what the source-chain consensus system actually finalized. Depending on what the replacement commitment encodes, this can enable forged message delivery, unsound non-membership timeout proofs, or unauthorized app actions — i.e., it undermines the core state-verification guarantee the protocol depends on for cross-chain message integrity.

### Likelihood Explanation
The trigger (a fisherman veto of the currently-latest height) is a normal, permissionless, reachable operation — any relayer/fisherman submitting a valid fraud/veto proof through the `handler` can invoke `deleteStateMachineCommitmentInternal`. The severity of the resulting write-gate breakage, however, depends on whether the underlying consensus client (BEEFY/GRANDPA/BSC/etc.) can be made to re-emit an `IntermediateState` for an already-superseded lower height with different commitment content, which is constrained by each consensus client's own proof-binding (e.g., MMR leaf immutability). This makes the *root-cause defect* (broken monotonicity invariant after veto) certain and concretely provable from the code, while the maximal blast radius depends on consensus-client-specific conditions that were not independently re-verified against every supported client in this scan.

### Recommendation
Track a `_previousStateMachineHeight` (or equivalent) on `EvmHost`, mirroring `pallet_ismp::PreviousStateMachineHeight`, and restore it on veto instead of hardcoding `1`. Additionally, add an explicit "commitment already exists at this height" guard in `HandlerV2.handleConsensus` (mirroring the Rust core handler's `if host.state_machine_commitment(state_height).is_ok() { continue; }`) so that the overwrite protection does not rely solely on the monotonic `latestHeight` pointer being perfectly maintained across all invalidation paths.

### Proof of Concept
1. State machine `S` has committed heights up to `H` (`_latestStateMachineHeight[S] == H`), with legitimate commitments stored for heights `2..H`.
2. A fisherman submits a valid veto/fraud proof for height `H`, calling `deleteStateMachineCommitment(height=H, fisherman)` → `_latestStateMachineHeight[S]` becomes `1` (per `evm/src/core/EvmHost.sol:718-721`), while commitments for heights `2..H-1` remain stored and untouched.
3. A relayer submits any subsequent consensus proof that verifies successfully and contains an `IntermediateState` for some height `h` where `2 ≤ h ≤ H-1`, with a commitment differing from what is already stored at `h`.
4. In `HandlerV2.handleConsensus` (`evm/src/core/HandlerV2.sol:155-164`), the check `intermediate.height > latestHeight` (`h > 1`) passes, and `host.storeStateMachineCommitment(...)` overwrites the previously verified commitment at height `h` with the new one — despite `h` being far below the chain's real prior progress, demonstrating the broken monotonicity guarantee introduced by the veto reset.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L638-644)
```text
        // add whitelisted state machines
        for (uint256 i = 0; i < stateMachinesLen; ++i) {
            // create if it doesn't already exist
            if (_latestStateMachineHeight[params.stateMachines[i]] == 0) {
                _latestStateMachineHeight[params.stateMachines[i]] = 1;
            }
        }
```

**File:** evm/src/core/EvmHost.sol (L687-699)
```text
    function storeStateMachineCommitment(StateMachineHeight memory height, StateCommitment memory commitment)
        external
        restrict(_hostParams.handler)
    {
        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;

        emit StateMachineUpdated({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId), 
            height: height.height
        });
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

**File:** modules/ismp/core/src/handlers/consensus.rs (L58-66)
```rust
			// Only allow heights greater than latest height
			if previous_latest_height > commitment_height.height {
				continue;
			}

			// Skip duplicate states
			if host.state_machine_commitment(state_height).is_ok() {
				continue;
			}
```
