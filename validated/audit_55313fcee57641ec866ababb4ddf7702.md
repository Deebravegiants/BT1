### Title
OP-Stack fault-dispute-game consensus client permanently DOSes a state machine's height progression via an unbound `header.number` field - (File: `modules/ismp/clients/optimism/src/lib.rs`)

### Summary
Hyperbridge's OP-Stack consensus client derives the `StateMachineHeight` it commits from the raw, prover-supplied `payload.header.number` field of an `OptimismDisputeGameProof`, with no check that this number corresponds to any real, reachable L2 block. Because OP Stack `FaultDisputeGame`s can be permissionlessly created on L1 with an arbitrary `rootClaim`/`extraData` pair (the audit's underlying assumption that dispute-game resolution can be manipulated/incorrect), an attacker can get a fabricated header with an extreme block number accepted as a verified consensus update, which is then written into `LatestStateMachineHeight`. All subsequent legitimate (lower) updates for that state machine are then rejected forever by the strict `previous_latest_height > commitment_height.height` guard in the shared consensus handler.

### Finding Description
`verify_optimism_dispute_game_proof` computes the accepted height purely from the header the prover supplies, not from any value that is cross-checked against real L2 chain progression: [1](#0-0) 

The only "correctness" check on this fabricated header is that its RLP hash, together with attacker-chosen `state_root`/`withdrawal_storage_root`, reproduces the `root_claim` that must exist as a real dispute game in the L1 factory (via the `game_uuid` derivation) and that the game is currently "unchallenged": [2](#0-1) [3](#0-2) 

This is the exact decoupling described in the Optimism report: the dispute game's `rootClaim`/`extraData` pair is chosen entirely by the (permissionless) game creator at creation time and is never validated against a real trace during creation — only during an actual fault-proof dispute, which the contest/report explicitly allows to resolve incorrectly. An attacker can therefore create (and leave unchallenged) a `FaultDisputeGame` whose `rootClaim` decodes, under `calculate_output_root`, to a self-consistent but entirely fictitious `Header` with `number = u64::MAX` (or any value far beyond the real chain head).

Once such a proof is submitted as a `ConsensusMessage`, the generic ISMP consensus handler accepts any height greater than the previously stored one and unconditionally advances the "latest height" pointer: [4](#0-3) 

Because the comparison `previous_latest_height > commitment_height.height` is the *only* gate, and it is a simple numeric comparison, a single malicious/incorrectly-resolved fault-dispute-game height poisons `LatestStateMachineHeight` for that OP-Stack state machine ID. From that point, every subsequent legitimate `OptimismUpdate` (with a real, low, monotonically-increasing L2 block number) is silently skipped by the `continue` in the loop above, exactly mirroring the original OP `ANCHOR_STATE_REGISTRY`/`FaultDisputeGame` bug.

### Impact Explanation
If exploited, the affected OP-Stack-based state machine's height can never advance again through this consensus client, which blocks:
- All new `state_machine_commitment` entries for that chain (no further state proofs can be delivered/verified),
- All requests/responses (and therefore withdrawals/messages) that need a state proof against a height greater than the poisoned one, since `validate_state_machine`/`verify_delay_passed` and downstream proof verification all key off `latest_commitment_height`/stored commitments for that `StateMachineId`. [5](#0-4) 

There is a partial mitigation: pallet-ismp exposes a fisherman veto path (`delete_state_commitment`) that resets `LatestStateMachineHeight` back to `PreviousStateMachineHeight` if the vetoed height was the current latest: [6](#0-5) 

This is analogous to Optimism's own "switch game type/admin recovery" mitigation that the Sherlock judges ultimately treated as insufficient to fully invalidate the issue (it was judged Medium, not dismissed) — recovery is only a single level deep (`PreviousStateMachineHeight`), is not automatic, and depends on a fisherman detecting and reacting to the malicious/incorrectly-resolved dispute game before/while it is submitted as a consensus update. Until vetoed, the state machine is fully stalled.

### Likelihood Explanation
Creating an OP Stack `FaultDisputeGame` with an arbitrary `rootClaim`/`extraData` is permissionless and requires only posting the game's bond on L1 — no privileged role, collator, or governance action is needed. The remaining precondition — that the game resolves (or is treated as "unchallenged" long enough to be submitted) with an incorrect/fabricated claim — mirrors the exact precondition the original report and Sherlock discussion treated as in-scope ("assume FaultDisputeGame resolution logic can be wrong/manipulated"). Given that, any permissionless relayer/attacker able to submit a `ConsensusMessage` referencing such a game can trigger this.

### Recommendation
- Bound the height derived from `OptimismDisputeGameProof`/`OptimismUpdate` to a sane, monotonic delta from the currently trusted height (or otherwise sanity-check `payload.header.number` against an L1-observable bound, e.g., a maximum plausible L2 blocks-per-L1-block ratio since the last trusted update), rather than trusting it unconditionally once the game/UUID exists in the factory.
- In `modules/ismp/core/src/handlers/consensus.rs::update_client`, do not treat "greater than previous height" alone as sufficient; consider tracking multiple historical trusted heights (not just one `PreviousStateMachineHeight`) so a bad update can be rolled back even after further (also-invalid, since they build on the poisoned height) updates land.
- Require dispute-game height claims to be corroborated against a bound tied to the L1 block/time at which the game was created (i.e., the claimed L2 height must be plausible given normal L2 block production rate since the previous verified height), independent of whether the game itself was later successfully or maliciously resolved.

### Proof of Concept
1. On L1, permissionlessly call `DisputeGameFactory.create(gameType, rootClaim, extraData)` where `rootClaim = keccak256(version || fake_state_root || fake_withdrawal_root || keccak256(fake_header_rlp))` and `fake_header_rlp` encodes a header with `number = u64::MAX` (analogous to the original `testZach_DOSWithMaxBlockNumber` PoC, but for Hyperbridge's OP verifier rather than OP's own `AnchorStateRegistry`).
2. Leave the game unchallenged (per the contest's assumption that fault-dispute resolution can be manipulated / assumed incorrect).
3. Construct an `OptimismDisputeGameProof` referencing this game (factory membership proof, game-impl proof, "unchallenged" `claimData.length==1` proof) with `header` set to the fabricated header, and submit it via `ConsensusMessage` to `update_client`.
4. `verify_optimism_dispute_game_proof` succeeds (see `modules/ismp/clients/optimism/src/lib.rs:371-386`) and returns `IntermediateState{ height: u64::MAX, ... }`.
5. `update_client` (`modules/ismp/core/src/handlers/consensus.rs:51-80`) stores this as the new `latest_commitment_height` for the state machine.
6. Any subsequent, legitimate `OptimismUpdate` with a real (much lower) L2 block number is skipped by the `previous_latest_height > commitment_height.height` check, permanently stalling consensus updates for that chain until a fisherman vetoes the poisoned height via `delete_state_commitment`.

Note: I was not able to execute this end-to-end in a live testnet/fork within this session (no code-execution tooling in ask-only mode); the analysis is based on static tracing of `verify_optimism_dispute_game_proof`, `update_client`, and the fisherman veto path shown above. I recommend a Devin session with repo access to build and run a concrete Rust unit test (analogous to `tesseract/consensus/op-host/src/tests.rs`) to confirm end-to-end behavior before treating this as fully proven.

### Citations

**File:** modules/ismp/clients/optimism/src/lib.rs (L298-336)
```rust
	let l2_block_hash = Header::from(&payload.header).hash::<H>();

	let root_claim = calculate_output_root::<H>(
		payload.version,
		payload.header.state_root,
		payload.withdrawal_storage_root,
		l2_block_hash,
	);

	let game_uuid = get_game_uuid::<H>(payload.game_type, root_claim, payload.extra_data);

	let dispute_game_key = derive_map_key::<H>(game_uuid.0.to_vec(), DISPUTE_GAMES_SLOT);

	// Does the dispute game's unique identifier exist in the _disputeGames map?
	let proof_value = match get_value_from_proof::<H>(
		dispute_game_key.0.to_vec(),
		factory_storage_root,
		payload.dispute_game_proof,
	)? {
		Some(value) => value.clone(),
		_ => Err(Error::DisputeGameIdMissing)?,
	};

	let mut encoded_game_id = <alloy_primitives::Bytes as Decodable>::decode(&mut &*proof_value)
		.map_err(|_| Error::DecodeDisputeGameId(format!("{:?}", &proof_value)))?
		.0
		.to_vec();

	let game_id = get_game_id(payload.game_type, payload.timestamp, payload.proxy);
	let game_id_bytes = game_id.to_big_endian();

	// Pad the encoded game id gotten from proof with zeros so it becomes 32 bytes long
	(0..game_id_bytes.len().saturating_sub(encoded_game_id.len()))
		.for_each(|_| encoded_game_id.insert(0, 0));

	// Derived game id must be equal to encoded game id
	if encoded_game_id != game_id_bytes {
		Err(Error::DisputeGameIdMismatch)?
	}
```

**File:** modules/ismp/clients/optimism/src/lib.rs (L371-386)
```rust
	Ok(IntermediateState {
		height: StateMachineHeight {
			id: StateMachineId {
				// note: This will state machine id should not be used to store the state commitment
				state_id: StateMachine::Evm(Default::default()),
				consensus_state_id,
			},
			height: payload.header.number.low_u64(),
		},
		commitment: StateCommitment {
			timestamp: payload.header.timestamp,
			overlay_root: None,
			state_root: payload.header.state_root,
		},
	})
}
```

**File:** modules/ismp/clients/optimism/src/lib.rs (L430-461)
```rust
		DisputeGameImpl::FaultDisputeGame => {
			// `claimData` is a dynamic `ClaimData[]` at `FAULT_DISPUTE_CLAIM_DATA_SLOT`. Solidity
			// stores a dynamic array's element count in the slot itself (the elements live at
			// `keccak256(slot)`). A freshly created, unchallenged game holds exactly one entry —
			// the root claim appended in `initialize()` — and every `move()` (attack or defense)
			// appends another. So `claimData.length == 1` iff the game has not been challenged.
			// Any other length (including absence, i.e. length 0 for a game that never registered
			// its root claim) is rejected.
			//
			// The MPT trie path for a direct storage slot is `keccak256(slot)`.
			let storage_key = U256::from(FAULT_DISPUTE_CLAIM_DATA_SLOT).to_big_endian();
			let trie_path = H::keccak256(&storage_key);
			let value = get_value_from_proof::<H>(
				trie_path.0.to_vec(),
				proxy_storage_root,
				challenge_proof,
			)?
			.ok_or(Error::ClaimDataSlotMissing)?;
			let raw = <alloy_primitives::Bytes as Decodable>::decode(&mut &*value)
				.map_err(|_| Error::DecodeClaimData(format!("{:?}", value)))?
				.0
				.to_vec();
			if raw.len() > 32 {
				Err(Error::ClaimDataTooLong)?
			}
			// RLP strips leading zeros from the stored length; reconstruct the uint256 and require
			// it to be exactly one.
			if U256::from_big_endian(&raw) != U256::one() {
				Err(Error::FaultDisputeGameChallenged)?
			}
			Ok(())
		},
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L51-80)
```rust
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

**File:** modules/ismp/core/src/handlers.rs (L121-148)
```rust
pub fn validate_state_machine<H>(
	host: &H,
	proof_height: StateMachineHeight,
) -> Result<Box<dyn StateMachineClient>, Error>
where
	H: IsmpHost,
{
	// Ensure consensus client is not frozen
	let consensus_client_id = host.consensus_client_id(proof_height.id.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized {
			consensus_state_id: proof_height.id.consensus_state_id,
		},
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	// Ensure client is not frozen
	host.is_consensus_client_frozen(proof_height.id.consensus_state_id)?;

	// Ensure delay period has elapsed
	if !verify_delay_passed(host, &proof_height)? {
		return Err(Error::ChallengePeriodNotElapsed {
			state_machine_id: proof_height.id,
			current_time: host.timestamp(),
			update_time: host.state_machine_update_time(proof_height)?,
		});
	}

	consensus_client.state_machine(proof_height.id.state_id)
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
