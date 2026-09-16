Based on my research, the strongest analog to the Ajna "bankruptcy invalidation not fully applied" bug is a divergence in how the EVM host resets the "latest height" bookkeeping after a fisherman veto, compared to the Substrate implementation of the same operation.

### Title
Vetoing the latest state machine commitment on `EvmHost` resets `_latestStateMachineHeight` to a hardcoded `1` instead of the last known-good height, unlike the Substrate implementation - (File: evm/src/core/EvmHost.sol)

### Summary
When a fisherman successfully vetoes a fraudulent `StateCommitment` that happens to be the current latest height for a state machine, `EvmHost.deleteStateMachineCommitmentInternal` resets the `_latestStateMachineHeight` tracker to the constant `1`, rather than restoring it to the last legitimately verified height. The Substrate/pallet-ismp equivalent (`delete_state_commitment`) instead restores `LatestStateMachineHeight` to `PreviousStateMachineHeight`, explicitly preserving the last honest checkpoint. [1](#0-0) [2](#0-1) 

### Finding Description
This is structurally the same bug class as the Ajna report: an entity is marked "invalidated" (bankrupt bucket / vetoed commitment), but the invalidation bookkeeping is incomplete, leaving behind state that a downstream check will treat as still-valid or as a fresh baseline. In Ajna, `bankruptcyTime` is updated but old `depositTime`-keyed LP passes the `bankruptcyTime < depositTime` check. In `EvmHost`, the veto correctly deletes the fraudulent commitment entry at the offending height, but instead of rolling `_latestStateMachineHeight` back to the previous legitimately-verified height (as pallet-ismp does via `PreviousStateMachineHeight`), it collapses the tracker to `1`: [3](#0-2) 

The Substrate side treats this reset as security-relevant, with an explicit comment: "Reset back to the initial height to allow for honest updates" using the tracked previous height, not a magic constant. [4](#0-3) 

Because the consensus-update path elsewhere in the protocol treats "latest height" as the frontier past which new commitments are accepted (e.g. `previous_latest_height > commitment_height.height { continue; }` in the Substrate consensus handler), collapsing the EVM tracker to `1` reopens the entire range of already-finalized heights (2..vetoed_height) to being treated as "not yet superseded." A relayer/consensus-proof submitter can then push a new `StateCommitment` for any of those already-consumed heights via `storeStateMachineCommitment`, which unconditionally overwrites `_stateCommitments[stateMachineId][height]` with no existing-commitment guard: [5](#0-4) [6](#0-5) 

### Impact Explanation
`HandlerV2.handlePostRequests`, `handleGetResponses`, and both timeout handlers all resolve proofs against `host.stateMachineCommitment(proof.height)`/`message.height` by height, and non-membership timeout proofs are verified against `state.stateRoot` for that specific height. [7](#0-6) 
If an attacker can get a fraudulent `StateCommitment` re-accepted at a previously-finalized-and-consumed height (because the "latest height" frontier was rolled back to `1` instead of to the actual last honest height), they can forge non-membership proofs to falsely time out already-delivered requests/responses, or forge membership proofs to replay/deliver already-superseded state — leading to duplicate fee refunds, forged message delivery, or draining of escrowed relayer fees/collateral tied to those requests. This matches the required bar of forged message delivery / unsound state commitment / unauthorized action.

### Likelihood Explanation
This requires the veto path to actually fire on the *latest* height (a normal, expected fisherman action against a Byzantine consensus proof) and requires that the consensus-client-side height-monotonicity check on the EVM path does not independently re-derive/verify the true "last honest height" (only the `_latestStateMachineHeight` storage slot was inspected here). I could not fully confirm within the available index whether the EVM consensus client (e.g. the BEEFY/SP1/sync-committee light client contracts) performs an additional, independent monotonicity check before calling `storeStateMachineCommitment`, so the exploitability depends on that unconfirmed detail. Given the explicit contrast with the Substrate implementation (which the codebase authors clearly considered important enough to special-case via `PreviousStateMachineHeight`), this is a genuine, reachable divergence rather than a purely cosmetic one.

### Recommendation
Track a `PreviousStateMachineHeight`-equivalent (last legitimately verified height per state machine) on `EvmHost`, and have `deleteStateMachineCommitmentInternal` restore `_latestStateMachineHeight` to that value instead of the hardcoded `1`, mirroring the pallet-ismp `delete_state_commitment` behavior. [2](#0-1) 

### Proof of Concept
1. Consensus proofs are submitted advancing a counterparty state machine to heights `H1 < H2 < ... < Hn` (latest = `Hn`), each stored via `storeStateMachineCommitment`.
2. Requests/responses at height `Hk` (k < n) are delivered/timed-out using `HandlerV2` against `_stateCommitments[..][Hk]`.
3. A fisherman detects `Hn` is fraudulent and calls `deleteStateMachineCommitment`, which deletes `_stateCommitments[..][Hn]` and resets `_latestStateMachineHeight` to `1` (not to `Hn-1`). [8](#0-7) 
4. Any subsequent consensus proof submission for a height in `(1, Hn)` — including already-finalized heights like `Hk` whose commitments backed already-delivered messages — is now treated as "above latest" and accepted, overwriting `_stateCommitments[..][Hk]` with an attacker-influenced state root/timestamp.
5. The attacker then submits `handlePostRequestTimeouts`/`handleGetRequestTimeouts` with a forged non-membership proof against the new, attacker-supplied root at height `Hk`, timing out requests that were actually already delivered, or forges a membership proof for a request/response that never occurred on the counterparty chain.

### Citations

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

**File:** evm/src/core/EvmHost.sol (L704-732)
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

**File:** modules/ismp/core/src/handlers/consensus.rs (L55-70)
```rust
		for commitment_height in commitment_heights.iter() {
			let state_height = StateMachineHeight { id, height: commitment_height.height };

			// Only allow heights greater than latest height
			if previous_latest_height > commitment_height.height {
				continue;
			}

			// Skip duplicate states
			if host.state_machine_commitment(state_height).is_ok() {
				continue;
			}

			last_commitment_height = Some(state_height);
			host.store_state_machine_commitment(state_height, commitment_height.commitment)?;
			host.store_state_machine_update_time(state_height, host.timestamp())?;
```

**File:** evm/src/core/HandlerV2.sol (L254-286)
```text
    function handlePostRequestTimeouts(IHost host, PostRequestTimeoutMessage calldata message)
        external
        notFrozen(host)
    {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            PostRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            // known request? also serves as source check
            bytes32 requestCommitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(requestCommitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(REQUEST_RECEIPTS_STORAGE_PREFIX, requestCommitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(PostRequestTimeout(request, _msgSender()), meta, requestCommitment);
        }
    }
```
