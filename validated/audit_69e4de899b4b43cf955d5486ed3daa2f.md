### Title
Consensus state commitments can be permanently bricked by an unresolvable duplicate-height reorg — (File: `modules/ismp/core/src/handlers/consensus.rs`)

### Summary
The reported Babylon staking-indexer bug is a case where a lower-trust ("probabilistic finality") consensus mechanism reorgs beyond the configured confirmation depth, and the indexer permanently reuses/never overwrites stale per-transaction status recorded before the reorg, breaking cross-node consensus. Hyperbridge's ISMP `update_client` handler has the same structural flaw for probabilistic/PoA-style consensus clients (BSC, Pharos): once a `StateCommitment` is recorded at a given `StateMachineHeight`, the handler can never replace it, even if a later, honest consensus proof shows the source chain actually finalized a *different* block at that same height.

### Finding Description
The generic consensus-message handler that every consensus client (BSC, Pharos, sync-committee, GRANDPA, Optimism, etc.) funnels through explicitly treats an already-stored height as terminal: [1](#0-0) 

```
// Only allow heights greater than latest height
if previous_latest_height > commitment_height.height { continue; }
// Skip duplicate states
if host.state_machine_commitment(state_height).is_ok() { continue; }
```

The corresponding EVM path (`HandlerV2.sol`) enforces the same "never overwrite" invariant: [2](#0-1) 

The comment in the pallet storage layer states this is by design: *"ISMP does not allow duplicate state updates so we don't have an overwrite path."* [3](#0-2) 

This is safe for clients backed by deterministic BFT finality (GRANDPA/BEEFY with slashing), where a finalized header cannot later be replaced by a conflicting one without a provable equivocation (handled via `freeze_client`/fraud proofs). It is **not** safe for the PoA/probabilistic-finality clients present in this repo, e.g. the Pharos consensus client and the BSC PoS/PoA client, whose verifiers only check that the new height strictly exceeds the last committed height and never re-derive/replace a commitment at an already-committed height: [4](#0-3) [5](#0-4) 

For such chains, if the validator set signs/attests to two different blocks at the same height in short succession (e.g. brief network partition, validator misbehavior, or any liveness/safety hiccup before slashing/finality catches up — exactly analogous to a Bitcoin-style reorg deeper than `confirmationDepth`), the first relayer to submit a consensus proof for that height locks in that block's `StateCommitment` (state root, timestamp, overlay root) forever. Any subsequent, more-canonical proof for the *same height* is silently dropped by the `continue` in `update_client`, regardless of correctness. This is a single unsigned/unpermissioned relayer transaction (`Message::Consensus`) — exactly the kind of unprivileged, dispatcher-reachable action targeted by this scan.

The only escape hatch is `delete_state_commitment`/`deleteStateMachineCommitmentInternal`, triggered by the fisherman veto/fraud-proof flow — but that requires an off-chain fisherman to detect the divergence and submit a fraud proof, an entirely separate trust assumption that is not guaranteed to fire within the challenge period, particularly since `verify_fraud_proof` is explicitly unimplemented for the sync-committee client and PoA-style clients don't have a slashing-backed safety guarantee to begin with.

### Impact Explanation
Once a stale/incorrect `StateCommitment` is locked in at a height, every downstream consumer of that height (post/get request and response Merkle proofs verified against `overlayRoot`/`stateRoot` at that height, in `HandlerV2.sol` and `pallet-ismp`) permanently verifies against the wrong root. This can:
- Freeze legitimate cross-chain messages that were actually included in the true finalized block but are absent from the locked-in (reorged-away) root — a route becomes permanently unable to deliver messages at/around that height.
- If the stale block happened to be an attacker-influenced fork, allow a forged state root to remain the trusted source of truth for state/non-membership proofs used by downstream apps (mint/burn, intents, etc.), i.e. unsound state commitment.

This is High impact because it breaks the core safety invariant of the bridge (a single canonical, correct commitment per height) with no recovery path other than an unreliable fisherman/fraud-proof mechanism.

### Likelihood Explanation
This requires a specific precondition: a PoA/probabilistic-finality-backed consensus client (BSC, Pharos) experiencing a short-range reorg or validator-set inconsistency at a specific height before the first relayer's proof for that height is accepted. Such events are rare on healthy networks but are exactly the class of event the referenced Babylon report calls out as "rare but not impossible," and unlike GRANDPA/BEEFY, these clients have no deterministic finality/slashing backstop — matching the report's Medium/High likelihood classification for a design that "can currently be set as low as 1" confirmation-equivalent trust window.

### Recommendation
For consensus clients without deterministic BFT finality (BSC, Pharos, and any future PoA-style client), add an explicit overwrite/re-verification path in `update_client`/`HandlerV2.handleConsensus` analogous to the veto flow: if a new, validly-verified consensus proof at an already-committed height presents a *different* block/state root than what is stored, and it arrives within the client's challenge period, replace the stored `StateCommitment` (and its dependent `latest_commitment_height`) rather than silently skipping it via `continue`. This mirrors the Babylon team's own recommendation to allow indexers to "overwrite or remove" transactions/commitments on reorg detection rather than treating first-seen data as immutable.

### Proof of Concept
1. A relayer submits a `ConsensusMessage` for the Pharos (or BSC) client proving block `B` at height `H`, which passes `verify_pharos_block`/`verify_bsc_header` and is stored via `store_state_machine_commitment`/`storeStateMachineCommitment`.
2. Due to a validator-set inconsistency or short-lived fork on the source PoA chain, the *actual* canonical chain instead finalizes a different block `B'` at height `H` (different `state_root`/timestamp).
3. A second relayer submits a `ConsensusMessage` proving `B'` at height `H`. `verify_pharos_block`/`verify_bsc_header` may still succeed (the update's own internal check `update_block_number <= current_block_number` only guards against replays below the *client's* finalized height, not divergent commitments at the *same* previously-committed height in the `update_client` handler).
4. `update_client`'s loop hits `if host.state_machine_commitment(state_height).is_ok() { continue; }` and silently discards `B'`'s commitment — `B` (potentially the wrong fork) remains permanently the trusted state at height `H`, with no non-fisherman path to correct it.

### Citations

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

**File:** modules/pallets/ismp/src/lib.rs (L740-742)
```rust
		/// Insert a state commitment into the bounded map. ISMP does not allow
		/// duplicate state updates so we don't have an overwrite path.
		///
```

**File:** modules/consensus/pharos/verifier/src/lib.rs (L49-57)
```rust
	let update_block_number = update.block_number();
	let current_block_number = trusted_state.finalized_block_number;

	if update_block_number <= current_block_number {
		return Err(Error::StaleUpdate {
			current: current_block_number,
			update: update_block_number,
		});
	}
```

**File:** modules/ismp/clients/bsc/src/lib.rs (L88-93)
```rust
		if consensus_state.finalized_height >= bsc_client_update.source_header.number.low_u64() {
			Err(Error::ExpiredUpdate {
				current: consensus_state.finalized_height,
				update: bsc_client_update.source_header.number.low_u64(),
			})?
		}
```
