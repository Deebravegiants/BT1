### Title
Skipped intermediate consensus updates permanently orphan earlier state commitments, freezing messages contained in them - (File: `modules/ismp/core/src/handlers/consensus.rs`, `evm/src/core/HandlerV2.sol`)

### Summary
`update_client` in `modules/ismp/core/src/handlers/consensus.rs` and the equivalent intermediate-state-storage loop in `evm/src/core/HandlerV2.sol` only persist a `StateCommitment` for a given `StateMachineId` if its height is greater than (or equal to, in the pallet case) the *currently stored* `latest_commitment_height`/`latestStateMachineHeight`. A relayer submitting a legitimate BEEFY/SP1 consensus proof can freely choose which finalized parachain headers to include as intermediates (`verifyParachainHeaderProof` in `evm/src/consensus/EcdsaBeefy.sol` / `verifyConsensus` in `evm/src/consensus/SP1Beefy.sol` place no requirement that *all* intervening parachain blocks be included). If a relayer submits only a later parachain header while skipping an earlier one, the earlier height's `StateCommitment` is never stored. Because subsequent updates are gated on the "latest" height rather than on whether a specific height was ever recorded, that earlier `StateCommitment` can never be submitted afterward — permanently orphaning any `PostRequest`/`GetResponse`/`GetRequest` commitment produced at that block. This mirrors the Y2K bug: relying on the "latest" reading instead of verifying the full historical window means an event that truly happened (a dispatched message at that height) can be permanently missed if the party responsible for reporting it (the relayer, analogous to whoever calls `triggerDepeg()`) does not report it before a later update supersedes it.

### Finding Description
- In `modules/ismp/core/src/handlers/consensus.rs::update_client` (lines ~50-71):
```rust
let previous_latest_height = host.latest_commitment_height(id)?;
...
for commitment_height in commitment_heights.iter() {
    let state_height = StateMachineHeight { id, height: commitment_height.height };
    // Only allow heights greater than latest height
    if previous_latest_height > commitment_height.height {
        continue;
    }
    ...
    host.store_state_machine_commitment(state_height, commitment_height.commitment)?;
}
...
host.store_latest_commitment_height(latest_height)?;
``` [1](#0-0) 

- The same monotonic-gating pattern exists on the EVM side in `HandlerV2.sol`:
```solidity
uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
if (latestHeight != 0 && intermediate.height > latestHeight) {
    ...
    host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
}
``` [2](#0-1) 

- Consensus clients (`EcdsaBeefy.sol`, `SP1Beefy.sol`) allow a submitter to freely pick which parachain headers to include as `IntermediateState`s in a single BEEFY/SP1 proof — there is no protocol-level requirement that every finalized parachain block between the previous and new relay-chain heights be represented:
```solidity
function verifyParachainHeaderProof(bytes32 headsRoot, ParachainProof memory proof) ... {
    uint256 len = proof.parachains.length; // caller-supplied subset
    ...
}
``` [3](#0-2) 

- Once `latest_commitment_height`/`latestStateMachineHeight` advances past a given height (via a subsequent, honest-looking consensus update that only reports a later parachain block), any attempt to submit the *earlier* height's `StateCommitment` is filtered out by the `previous_latest_height > commitment_height.height` (Rust) / `intermediate.height > latestHeight` (Solidity) monotonicity checks. There is no mechanism to "backfill" a skipped height once a later one has been recorded as latest.
- Because request/response processing (`handlePostRequests`, `handleGetResponses`, timeout handlers in `HandlerV2.sol`) requires `host.stateMachineCommitment(proof.height)` to exist for the exact height a message was included at, any message dispatched in the skipped block can never be proven or delivered — its request/response commitment (already stored on the source chain via `store_request_commitment`) becomes permanently unroutable on the destination, and the fee/refund logic that depends on delivery or timeout is left stuck: the message is neither delivered nor timed out (since a timeout also relies on non-membership proofs against a specific, potentially unreachable `StateCommitment`, or in practice would eventually be timed out by timestamp — but before any legitimate delivery attempt can occur, the payload is unprovable).

This differs from the intentional, cryptographically-sound "stale proof is a no-op" behavior for the *consensus client's own* `latestHeight` (relay-chain block number) — that is a legitimate optimization to make replay idempotent. The bug is that the **application-level state-machine height tracking treats "latest processed" as equivalent to "canonical and complete history"**, exactly as the Y2K controller treated `latestRoundData()` as equivalent to "no depeg occurred," when in fact an intermediate round/height was simply never recorded.

### Impact Explanation
Any relayer (a fully unprivileged, permissionless party — the exact "single relayed proof" actor called out in the validation criteria) can, whether through negligence, a race with another relayer, or deliberate censorship, submit a consensus update that skips an earlier finalized parachain height containing pending requests/responses. Once a later height is recorded as "latest," the state commitment for the skipped height can never be stored again, which:
- Permanently prevents membership-proof-based delivery of any `PostRequest`/`GetResponse` dispatched in that block (`StateCommitmentNotFound` will forever be returned for that height).
- Results in indefinite freezing of any escrowed funds/fees tied to that message (e.g., relayer fees held in `FeeMetadata`, or funds locked in an application contract awaiting the cross-chain response), since the message can neither be delivered nor be non-membership-proven for a timeout against that specific height (timeouts use `host.stateMachineCommitmentUpdateTime`/state at a *different*, later height, and non-membership proofs are checked against whichever height is supplied — but the request's inclusion, if ever available, would only be provable through the orphaned height).
This satisfies the "permanent freezing of funds" / "route unable to deliver messages" bar for High severity.

### Likelihood Explanation
This requires only a single relayer to submit one consensus/message-relay transaction that happens to skip an intermediate parachain header — no admin, governance, collator, or multi-party collusion is needed, and it can happen accidentally when relayer implementations optimize for "catch up to the latest known height" (as seen in `tesseract/consensus/*` off-chain relayer logic, e.g. `submit_consensus_update` in `tesseract/consensus/op-host/src/host.rs`, which advances by fetching only the newest event/height). Given multiple relayers race to submit consensus updates and are economically incentivized to submit the freshest state as fast as possible (to claim fee/priority), skipping older, still-unprocessed parachain heights is a realistic scenario, not a contrived edge case.

### Recommendation
- Do not gate acceptance of a `StateCommitment` solely on whether its height exceeds the previously recorded "latest" height. Instead, allow any height to be stored as long as it has not already been recorded (track a set/range of processed heights, or require intermediate states in a single message to be contiguous/validated against the previous latest + 1), or explicitly reject consensus updates that would skip heights, forcing relayers to submit intermediate parachain headers for every block since the last processed height.
- Alternatively, require the consensus client's `verify()` to enforce completeness — i.e., that all finalized parachain heights between the previously trusted and new relay-chain height are included as intermediates before advancing `latestHeight`/`latest_commitment_height`, similar to how the recommended Y2K fix required querying `getRoundData` across the full elapsed window instead of trusting only `latestRoundData()`.

### Proof of Concept
1. Parachain P finalizes blocks N and N+1 within the same relay-chain epoch/interval; a `PostRequest` is dispatched at block N (its request commitment is stored on the source chain).
2. Relayer A submits a BEEFY/SP1 consensus proof to `HandlerV2`/pallet-ismp's `update_client` that only includes the parachain header for block N+1 (a legal choice, since `verifyParachainHeaderProof`/`verifyConsensus` place no completeness requirement on which headers are included) — see `evm/src/consensus/EcdsaBeefy.sol#L198-229` and `modules/ismp/core/src/handlers/consensus.rs#L41-46`.
3. `update_client` stores the `StateCommitment` for height N+1 and calls `store_latest_commitment_height`/`storeStateMachineCommitment`, setting the state machine's latest height to N+1 — see `modules/ismp/core/src/handlers/consensus.rs#L73-80` and `evm/src/core/HandlerV2.sol#L155-164`.
4. Any later attempt (by relayer A or any other party) to submit a consensus proof/intermediate state for height N is now rejected by the `previous_latest_height > commitment_height.height` check (Rust) or `intermediate.height > latestHeight` check (Solidity) — the commitment for height N is never stored.
5. `handlePostRequests`/`handleGetResponses` in `HandlerV2.sol` require `host.stateMachineCommitment(request.proof.height)` for height N, which returns `bytes32(0)` (`StateCommitmentNotFound`) forever — see `evm/src/core/HandlerV2.sol#L199-200`. The `PostRequest` dispatched at block N can never be delivered, and any escrowed relayer fee/funds tied to it are permanently stuck.

### Citations

**File:** modules/ismp/core/src/handlers/consensus.rs (L50-80)
```rust
	let mut state_updates = vec![];
	for (id, mut commitment_heights) in intermediate_states {
		commitment_heights.sort_unstable_by(|a, b| a.height.cmp(&b.height));
		let previous_latest_height = host.latest_commitment_height(id)?;
		let mut last_commitment_height = None;
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
		}

		if let Some(latest_height) = last_commitment_height {
			let latest_height = StateMachineHeight { id, height: latest_height.height };
			state_updates.push(Event::StateMachineUpdated(StateMachineUpdated {
				state_machine_id: id,
				latest_height: latest_height.height,
			}));
			host.store_latest_commitment_height(latest_height)?;
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L198-229)
```text
    // @dev Verifies that some parachain header has been finalized, given the current trusted consensus state.
    function verifyParachainHeaderProof(bytes32 headsRoot, ParachainProof memory proof)
        internal
        pure
        returns (IntermediateState[] memory)
    {
        uint256 len = proof.parachains.length;
        MerkleMultiProof.Leaf[] memory leaves = new MerkleMultiProof.Leaf[](len);
        IntermediateState[] memory intermediates = new IntermediateState[](len);

        for (uint256 i = 0; i < len; i++) {
            Parachain memory para = proof.parachains[i];
            Header memory header = Codec.DecodeHeader(para.header);
            if (header.number == 0) revert IllegalGenesisBlock();

            leaves[i] = MerkleMultiProof.Leaf(
                para.index,
                keccak256(bytes.concat(ScaleCodec.encode32(uint32(para.id)), ScaleCodec.encodeBytes(para.header)))
            );

            StateCommitment memory commitment = header.stateCommitment();
            intermediates[i] =
                IntermediateState({stateMachineId: para.id, height: header.number, commitment: commitment});
        }

        if (len > 0) {
            bool valid = MerkleMultiProof.VerifyProof(headsRoot, proof.proof, leaves, proof.leafCount);
            if (!valid) revert InvalidMmrProof();
        }

        return intermediates;
    }
```
