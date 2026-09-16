Confirmed: `EvmHost.sol` has no `_previousStateMachineHeight` tracking at all, unlike the Substrate `pallet-ismp` implementation which explicitly stores `PreviousStateMachineHeight` and restores it correctly on veto.

### Title
Fisherman veto on EVM host rolls back `latestStateMachineHeight` to a hardcoded `1` instead of the true previous verified height, breaking monotonicity and re-opening stale heights to acceptance - (File: evm/src/core/EvmHost.sol)

### Summary
`EvmHost.deleteStateMachineCommitmentInternal` resets the `_latestStateMachineHeight` pointer to a hardcoded `1` whenever the vetoed height happens to be the current latest, instead of restoring the actual last-known-good height as the analogous Substrate implementation does. [1](#0-0)  This is directly comparable to the Aptos consensus race class in the report: a pause/veto operation ("sync manager decides to pause pre_commit") resets state using a value that does not reflect the actual verified progress, letting a subsequently-delivered, otherwise-stale proof "resume" and be accepted as if it were new, bypassing the intended monotonic height guard.

### Finding Description
`HandlerV2.handleConsensus` only accepts an intermediate state commitment when its height is strictly greater than `latestStateMachineHeight` for that state machine: [2](#0-1)  This check is the sole monotonicity/anti-replay guard protecting `_stateCommitments`.

The pallet-ismp Substrate host correctly maintains a `PreviousStateMachineHeight` alongside `LatestStateMachineHeight`, updating both on every successful commit: [3](#0-2)  and when a veto removes the current latest commitment, it restores `LatestStateMachineHeight` to that tracked `PreviousStateMachineHeight`, correctly returning the monotonicity guard to the actual last-good height: [4](#0-3) 

`EvmHost.sol` has no equivalent "previous height" bookkeeping at all (confirmed absent from the contract). Instead, `deleteStateMachineCommitmentInternal` special-cases the "vetoed height == latest" condition by simply setting `_latestStateMachineHeight[...] = 1`: [5](#0-4) 

Because `1` is far below any realistic prior legitimate height `M`, this collapses the monotonicity guard entirely for the affected state machine. Any subsequent `handleConsensus` call (permissionless — callable by any relayer with a valid consensus proof) that produces an intermediate commitment at any height strictly greater than `1` will pass the `intermediate.height > latestHeight` check and be stored/promoted to "latest," even if that height is far below the actual last confirmed-good height `M`. This silently rolls back the effective state-machine height, re-opening a window in which older, already-superseded (and possibly already-challenged/incorrect) heights can be re-accepted as authoritative, and lets any relayer determine what height becomes "latest" next, rather than requiring true forward progress from the last good height.

### Impact Explanation
`latestStateMachineHeight`/`stateMachineCommitment` values are the trust anchor for `handlePostRequests`/`handleGetResponses` membership/non-membership proof verification (`MerkleMountainRange.VerifyProof` against `host.stateMachineCommitment(...).overlayRoot`) [6](#0-5) . A collapsed monotonicity guard after a single fisherman veto allows an attacker-influenced or merely stale consensus update to become the new "latest" state root reference, undermining the challenge-period/veto security model that the fisherman mechanism is supposed to enforce. This can result in unsound state commitments backing message delivery (forged/incorrect membership proofs being trusted), i.e., unauthorized dispatch of requests/responses derived from a rolled-back or otherwise invalid state root — a Medium/High severity issue depending on which chains are affected and how easily an attacker can arrange for a stale-but-verifiable consensus update to land after a veto.

### Likelihood Explanation
Triggering `deleteStateMachineCommitmentInternal` requires the veto path (restricted to `_hostParams.handler`, typically driven by the fishermen/veto flow), so this is not attacker-callable directly. However, the vulnerable follow-on step — submitting a normal `handleConsensus` consensus proof afterward — is fully permissionless and routine relayer activity that happens continuously in production. Any veto of the current latest height (a legitimate, expected fisherman action in response to detected byzantine behavior) will trigger this broken reset, and the very next ordinary relayed consensus update (which will almost certainly commit a height greater than `1`) will silently re-establish an artificially low "latest" pointer, regressing the anti-replay/monotonicity protection until enough further updates accumulate to catch back up — an unintentional but realistic occurrence anytime the veto mechanism is exercised.

### Recommendation
Track a `_previousStateMachineHeight` mapping on `EvmHost` analogous to pallet-ismp's `PreviousStateMachineHeight`, updated on every successful `storeStateMachineCommitment`, and have `deleteStateMachineCommitmentInternal` restore `_latestStateMachineHeight` to that tracked previous height (rather than the hardcoded `1`) when the vetoed height equals the current latest.

### Proof of Concept
1. Relayer submits a valid consensus proof advancing `_latestStateMachineHeight[id]` to height `M` (e.g., 1000) via `handleConsensus`. [7](#0-6) 
2. Fisherman detects fraud in that commitment and calls `deleteStateMachineCommitment(height=1000, fisherman)`. Because `1000 == _latestStateMachineHeight[id]`, the contract resets `_latestStateMachineHeight[id] = 1`. [1](#0-0) 
3. Any relayer now calls `handleConsensus` again with a proof whose intermediate state includes height `500` (a height that is stale relative to the real last-good height, e.g., 900, which was verified before the vetoed 1000). Since `500 > 1`, the check in `HandlerV2.handleConsensus` passes and `_stateCommitments[id][500]` is (re)stored and `_latestStateMachineHeight[id]` becomes `500`. [2](#0-1) 
4. The state-machine height has been rolled back from what should have remained at least `900`, and the monotonicity guard is now anchored at an incorrect, attacker/relayer-influenced value, undermining the guarantees the veto/challenge-period mechanism is designed to provide.

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

**File:** evm/src/core/HandlerV2.sol (L144-164)
```text
    function handleConsensus(IHost host, bytes calldata proof) external notFrozen(host) {
        uint256 delay = block.timestamp - host.consensusUpdateTime();
        if (delay >= host.unStakingPeriod()) revert ConsensusClientExpired();

        bytes memory previousState = host.consensusState();
        (bytes memory verifiedState, IntermediateState[] memory intermediates, uint256 nextAuthoritySetId) =
            IConsensusV2(host.consensusClient()).verify(previousState, proof);

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

**File:** evm/src/core/HandlerV2.sol (L181-210)
```text
    function handlePostRequests(IHost host, PostRequestMessage calldata request) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(request.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
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

**File:** modules/pallets/ismp/src/host.rs (L229-234)
```rust
	fn store_latest_commitment_height(&self, height: StateMachineHeight) -> Result<(), Error> {
		let previous_height = LatestStateMachineHeight::<T>::get(height.id).unwrap_or_default();
		PreviousStateMachineHeight::<T>::insert(height.id, previous_height);
		LatestStateMachineHeight::<T>::insert(height.id, height.height);
		Ok(())
	}
```
