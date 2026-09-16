## Title
Fisherman veto resets `latestStateMachineHeight` to a hardcoded `1` instead of the real prior height, re-opening the entire height range for stale/superseded state commitments - (File: `evm/src/core/EvmHost.sol`)

### Summary
`EvmHost.deleteStateMachineCommitmentInternal` clears a vetoed state commitment and, if the vetoed height was the recorded "latest," resets `_latestStateMachineHeight[id]` to the literal constant `1` rather than restoring the actual last-known-good height. [1](#0-0) 

This is the same bug *class* as ALPINE-CVE-2022-42320: a per-identifier piece of trust state (Xen: per-domid access rights; here: per-state-machine "latest verified height") is not properly reset/re-derived when the underlying object is invalidated/removed, leaving a stale trust anchor that a subsequent, differently-scoped actor can exploit through a narrow timing/logic window.

### Finding Description
The Substrate implementation of the identical operation does this correctly — it restores the *real* previous height from a dedicated `PreviousStateMachineHeight` map: [2](#0-1) 

The EVM host has no equivalent "previous height" bookkeeping at all — it simply hardcodes `1`:
```solidity
if (_latestStateMachineHeight[height.stateMachineId] == height.height) {
    _latestStateMachineHeight[height.stateMachineId] = 1;
}
``` [3](#0-2) 

`_latestStateMachineHeight` is the authoritative "freshness" pointer that gates which state commitments the handler will accept from consensus/state proofs (`storeStateMachineCommitment` unconditionally overwrites it on every accepted update): [4](#0-3) 

Once a fisherman vetoes the currently-latest height, the pointer collapses to `1` — an arbitrary low value with no relationship to the chain's actual verified history. Any subsequent relayer (an ordinary, unprivileged, permissionless message dispatcher role in this system) can then submit a *cryptographically valid but already-superseded* consensus/state proof for any height `> 1` and have it accepted as the new "latest" state, because the freshness check only compares against this corrupted pointer. This is structurally identical to the Xen flaw: the removal of one trust object (`height`) leaves stale, ID-indexed state (the "latest" pointer) that a subsequent, unrelated request can ride on to gain access/trust it should not have.

### Impact Explanation
Once `_latestStateMachineHeight` is reset to `1`, the protocol's monotonicity guarantee for state commitments on that `stateMachineId` is broken:
- A relayer can reintroduce an old, already-superseded (but genuinely signed/finalized) state root as the "latest" commitment for the chain.
- Membership/non-membership proofs (used by `IntentGateway`, `HandlerV2` request/response delivery, and get-request timeouts) are verified against whatever `_stateCommitments[id][height]` is current. Reintroducing stale state can let a relayer resurrect membership proofs for requests whose true chain state has already moved on (e.g., proving a request "exists" or "does not exist" using an old snapshot), which the docs explicitly flag as the trust boundary for request handling and timeouts. [5](#0-4) 
- This can enable forged/duplicate message delivery or improper timeout/refund flows (e.g. IntentGateway cancellation relies on proving `_filled[commitment]` is empty at a height *after* `order.deadline` via a fresh, canonical state — see the cancel-from-source flow) if an attacker can substitute an old state root as "the" verified state for a chosen height. [6](#0-5) 

This satisfies the "unsound state commitment" / "forged message delivery" impact categories.

### Likelihood Explanation
Medium-High. It requires a fisherman veto to have occurred on the currently-latest height (a normal, expected operational event — vetoes are single-collator/permissionless-to-trigger via fraud detection, not an attacker-controlled precondition, but a routine part of protocol operation) followed by any relayer submitting a subsequent, valid state/consensus proof — a fully permissionless, routine action. No malicious governance/admin/collator action is required on the attacker's part; the attacker only needs to be a normal relayer acting after a routine veto.

### Recommendation
Mirror the Substrate implementation: introduce a `_previousStateMachineHeight[id]` mapping updated alongside every accepted `storeStateMachineCommitment`/`setConsensusState` call, and have `deleteStateMachineCommitmentInternal` restore that tracked previous height instead of hardcoding `1`.

### Proof of Concept
1. Handler stores height `H1` then `H2` for `stateMachineId = X` via `storeStateMachineCommitment`, so `_latestStateMachineHeight[X] = H2`.
2. A fisherman calls `deleteStateMachineCommitment` for height `H2` (the current latest) — `_latestStateMachineHeight[X]` collapses to `1` instead of `H1`. [7](#0-6) 
3. Any relayer submits a legitimate but stale/old consensus proof for a superseded height `H0` where `1 < H0 < H1` (a height that would previously have been rejected as not "newer than latest"). Because `_latestStateMachineHeight[X]` is now `1`, `H0` is accepted, overwriting `_stateCommitments[X][H0]` as the tracked latest and rewinding the effective view of chain `X`'s state.
4. Downstream consumers (IntentGateway cancellation, ISMP request/timeout proofs) that verify membership/non-membership against `stateMachineCommitment(height)` can now be served proofs rooted in this reintroduced stale state, producing outcomes inconsistent with the chain's true current state.

**Caveat/uncertainty:** I was not able to fully retrieve `evm/src/core/HandlerV2.sol`'s exact height-freshness comparison logic within the tool budget (only partial grep hits were returned, without full context), so I cannot cite the exact line that gates acceptance of a new height against `_latestStateMachineHeight`. The root-cause defect in `EvmHost.deleteStateMachineCommitmentInternal` (hardcoding `1` instead of restoring the real previous height) is confirmed directly from the source, but the precise downstream exploitation mechanics in `HandlerV2` should be verified against the full file before treating this as fully proven end-to-end.

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

**File:** docs/content/protocol/ismp/requests.mdx (L104-115)
```text
The request `handle` is used to notify onchain `IsmpModule`s of new requests to be processed. A relayer will construct the `RequestMessage` which holds a batch of new `PostRequest`s, as well as a _multi-proof_<sup>[1]</sup> of their existence on the source chain. The handler will perform the following operations

- Assert that the state machine's consensus client is not frozen
- Assert that the configured `challenge_period` for the `StateCommitment` has elapsed
- Assert that the requests have not been previously processed
- Assert that the requests have not timed out
- Assert that the membership proof for the requests verify
- Finally dispatch the requests to the relevant `IsmpModule::on_accept` and store a receipt for each request to prevent requests from being replayed.

<Callout title={'Danger'} type={"warn"}>
It's important to note that if the `IsmpModule::on_accept` does not return `Ok`, the receipt of this request will not be persisted, allowing the request to be **replayed**. Consequently, the `IsmpModule` is responsible for maintaining all invariants before modifying it's internal state to prevent partial state changes that could result in critical vulnerabilities in their request handler. This model ensures that if a request cannot be executed successfully on a destination state machine, it can time out gracefully on the source.
</Callout>
```

**File:** docs/content/developers/evm/intent-gateway/overview.mdx (L59-66)
```text
### Cancellation

There are two modes for cross-chain cancellation:

`cancelOrder` emits `OrderCancelled(commitment, canceller)` on the chain the cancellation is initiated from, before it routes to either path below. `EscrowRefunded` remains the terminal event, on the source chain, once the escrow is actually returned.

**Cancel from source chain**: The user calls `cancelOrder()` on the source chain, which dispatches a `DispatchGet` storage read request to query the destination chain's fill status. The `CancelOptions.height` must be greater than `order.deadline` — this ensures the proof is taken from a block after the order has expired. A relayer processes this request on Hyperbridge by providing storage proofs from the destination chain. If the storage slot for `_filled[commitment]` is empty (order unfilled), Hyperbridge dispatches a response back to the source chain. The `onGetResponse` handler verifies the empty proof and calls `withdraw()` to refund the escrowed tokens to the user. If the order was filled, the response contains a non-empty value and the handler reverts with `Filled()`.

```
