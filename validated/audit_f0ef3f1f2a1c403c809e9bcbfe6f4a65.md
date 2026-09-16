## Title
EvmHost resets `_latestStateMachineHeight` to a hardcoded `1` (not the true prior height) on veto, and `HandlerV2` lacks a duplicate/monotonicity guard — allowing a vetoed or superseded state commitment to be resurrected/overwritten by a later consensus proof - (File: `evm/src/core/EvmHost.sol`, `evm/src/core/HandlerV2.sol`)

### Summary
The EosDice incident is a class of "roll-back" attack: an attacker forces the chain's accepted history backward, then resubmits a transaction so a previously-settled (unfavorable) outcome can be redone/replaced. The Hyperbridge analog is the fisherman veto path for EVM destination hosts: when a `StateCommitment` is vetoed, `EvmHost.deleteStateMachineCommitmentInternal` rolls `_latestStateMachineHeight` back to the fixed value `1` instead of the actual prior height, and `HandlerV2.handleConsensus` only checks `intermediate.height > latestHeight` with no "commitment already exists" guard before calling `storeStateMachineCommitment`. This combination re-opens *every* height above 1 — not just the immediately-preceding one — to be silently overwritten by a subsequent consensus proof.

### Finding Description
In the Substrate pallet, `delete_state_commitment` restores the *exact* previous height via `PreviousStateMachineHeight`, and `update_client` explicitly skips storing when `host.state_machine_commitment(state_height).is_ok()` (i.e., a commitment already exists at that height): [1](#0-0) [2](#0-1) 

The EVM host does not mirror either safeguard. `deleteStateMachineCommitmentInternal` resets the latest-height watermark to the constant `1` whenever the vetoed height happens to be the latest one: [3](#0-2) 

`HandlerV2.handleConsensus` then accepts *any* intermediate state whose height merely exceeds `latestHeight`, with no check that a commitment for that height already exists: [4](#0-3) 

Because BEEFY/SP1-BEEFY MMRs are append-only, a relayer can always construct a valid proof containing *historical* parachain headers/heights (the verifiers only reject proofs that don't advance `latestBeefyHeight`/`latestHeight` in the *consensus state*, not proofs that include old intermediate heights): [5](#0-4) 

After a veto resets `_latestStateMachineHeight` to `1`, the very next consensus proof (honest or otherwise) that advances the underlying consensus client can carry an intermediate array re-including any height from `2` up through the just-vetoed height (or beyond). `HandlerV2` will accept and overwrite `_stateCommitments[stateMachineId][height]` for every one of those heights unconditionally, since the code path has no "already committed" skip, unlike the Rust host. This defeats the purpose of the veto: the fraudulent (or stale/reorged) commitment that a fisherman removed within its challenge period can be resurrected at the same height by simply resubmitting the original consensus proof, and other already-finalized heights below the vetoed one are also re-writable, breaking the monotonic, once-finalized invariant that request/response and timeout processing rely on.

### Impact Explanation
This breaks the safety guarantee documented for `StateCommitmentVetoed` — that a vetoed commitment (and, by the intended design, only that specific height) is discarded and relayers/apps must not rely on it: [6](#0-5) 
Silent re-acceptance of a previously-vetoed (fraudulent or reorged) state commitment can lead to forged message delivery: `handlePostRequests`/response handlers on `EvmHost` trust `stateMachineCommitment(height)` as canonical once the challenge period elapses, so a resurrected fraudulent root can be used to admit forged `PostRequest`s or `GetResponse`s, enabling unbacked mint/unauthorized app actions or theft of funds routed through Hyperbridge's EVM host. This is reachable by any relayer submitting a normal consensus-update transaction (no admin/governance privilege required) following a fisherman veto.

### Likelihood Explanation
Requires: (1) a fisherman veto having occurred on an EVM-hosted state machine's latest height (a normal, expected operational event covered by existing fishermen tests), and (2) a subsequent consensus proof — which relayers submit routinely and can construct from already-available, append-only MMR data — that includes the vetoed (or any older) height in its intermediate set. No cryptographic break or validator collusion is required beyond what already produced the original bad commitment; an ordinary relayer resubmission suffices.

### Recommendation
- In `EvmHost.deleteStateMachineCommitmentInternal`, restore `_latestStateMachineHeight` to the true previous height (mirroring `PreviousStateMachineHeight` in the Substrate host) instead of hardcoding `1`.
- In `HandlerV2.handleConsensus`, add a "skip if a commitment already exists at this height" guard before calling `storeStateMachineCommitment`, matching `modules/ismp/core/src/handlers/consensus.rs`'s duplicate-state check.
- Consider tracking vetoed `(stateMachineId, height)` pairs to explicitly reject resubmission of the same height until a new, distinct commitment is proposed and re-passes the challenge period.

### Proof of Concept
1. A relayer submits a consensus proof that finalizes EVM state machine `X` at height `100` with a state root `R_bad` (e.g., produced by a BEEFY validator misbehavior or reorg not caught by `freeze_client`).
2. A fisherman detects the discrepancy and calls `veto_state_commitment`/`EvmHost.deleteStateMachineCommitment` for height `100`. `_latestStateMachineHeight[X]` is reset to `1` (`evm/src/core/EvmHost.sol:719-721`).
3. Because the underlying MMR is append-only, the relayer resubmits (or a new relayer submits) a fresh consensus proof whose `ParachainProof` again includes the leaf for height `100` (still provable against the MMR root) alongside a newer advancing height.
4. `HandlerV2.handleConsensus` checks only `intermediate.height > latestHeight` (`1`), so height `100`'s commitment `R_bad` is written back into `_stateCommitments[X][100]` with no re-verification against the earlier veto and no "duplicate" rejection.
5. Any `PostRequest`/`GetResponse` proven against `StateMachineHeight{X, 100}` is now accepted again by `HandlerV2.handlePostRequests`/response handlers, effectively reversing the fisherman's veto.

### Citations

**File:** modules/pallets/ismp/src/host.rs (L194-221)
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

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-117)
```rust
pub fn verify_mmr_update_proof<H: Keccak256 + EcdsaRecover + Send + Sync>(
	mut trusted_state: ConsensusState,
	mmr: MmrProof,
) -> Result<(ConsensusState, H256), Error> {
	let signatures_length = mmr.signed_commitment.signatures.len();
	let latest_height = mmr.signed_commitment.commitment.block_number;

	if trusted_state.latest_beefy_height >= latest_height {
		return Err(Error::StaleHeight {
			trusted_height: trusted_state.latest_beefy_height,
			current_height: latest_height,
		});
	}
```

**File:** docs/content/protocol/ismp/consensus.mdx (L220-232)
```text
### `StateCommitmentVetoed`

```rust showLineNumbers
/// Emitted when a `StateCommitment` has been successfully vetoed by a fisherman
pub struct StateCommitmentVetoed {
    /// The state commitment identifier
    pub height: StateMachineHeight,
    /// The account responsible
    pub fisherman: Vec<u8>,
}
```

A `StateCommitmentVetoed` event is emitted after a fisherman successfully vetoes a `StateCommitment` that is still within its challenge period. This instructs relayers to discard any pending requests/responses whose proofs rely on the vetoed commitment.
```
