## Finding: Unchallenged OP dispute-game snapshot + one-way height ratchet lets a faulty proposer permanently freeze L2 state commitments

### Title
Malicious OP-stack proposer can seed a fraudulent, still-disputable L2 output into Hyperbridge's Optimism consensus client, and once vetoed the correct state for that exact height can never be resubmitted — permanently freezing cross-chain messages anchored to it - (File: `modules/ismp/clients/optimism/src/lib.rs`, `modules/ismp/core/src/handlers/consensus.rs`)

### Summary
Hyperbridge's Optimism consensus client accepts an L2 output as a trusted `StateCommitment` the moment its OP-stack `FaultDisputeGame`/`AggregateVerifier` is proven merely "not yet challenged" — a point-in-time snapshot with no requirement that the dispute game has actually resolved or that OP's challenge window has elapsed. Combined with `pallet-ismp`'s "one-way height ratchet" (a height can only ever be committed once, and never below/at the previously recorded latest height), a proposer who seeds a fraudulent, freshly-created (hence trivially "unchallenged") dispute game and immediately relays it to Hyperbridge can get that height's `StateCommitment` locked in. Once fishermen detect the fraud on the real OP chain and veto the commitment, the true state for that exact height can **never** be resubmitted, permanently blocking verification of any genuine request/response anchored to that height. This is a structural analog of the original report: a "proposer" plants an unresolved/faulty claim before finality, the bridge treats it as settled, and even after the fraud is caught and reverted, the honest data for that slot is permanently unrecoverable.

### Finding Description
`verify_optimism_dispute_game_proof` derives an `IntermediateState` for an L2 block by proving that a `FaultDisputeGame` (or `AggregateVerifier`) proxy registered in the `DisputeGameFactory` is currently "not challenged": [1](#0-0) 

The "not challenged" check (`verify_not_challenged`) only inspects the *current* value of `claimData.length` (must equal exactly `1`, i.e. only the root claim exists) or `counteredByIntermediateRootIndexPlusOne` (must be zero): [2](#0-1) 

Both are trivially true for a **brand-new, just-created** dispute game — nothing requires the game to have completed OP's actual challenge/resolution window (typically 7 days) before Hyperbridge accepts the corresponding `state_root` as a finalized `IntermediateState`. This is functionally identical to the original report's `proveWithdrawalTransaction`, which accepted any never-before-proven output without verifying that the underlying `L2toL1Messenger` state genuinely existed at that block height.

Once accepted, `update_client` persists the state commitment and advances `latest_commitment_height`, but crucially it will **never re-accept a corrected commitment for that same height**: [3](#0-2) 

- `if previous_latest_height > commitment_height.height { continue; }` — skips any height at or below what was already recorded as latest.
- `if host.state_machine_commitment(state_height).is_ok() { continue; }` — skips any height that already has *any* stored commitment, correct or not.

The EVM `HandlerV2.handleConsensus` has the identical one-way check (`intermediate.height > latestHeight`): [4](#0-3) 

If fishermen later veto the fraudulent commitment (via `veto_state_commitment` / `delete_state_commitment` / `deleteStateMachineCommitmentInternal`), the height is deleted but `latest_commitment_height`/`_latestStateMachineHeight` is only reset when the vetoed height *is* the current latest — otherwise it is left untouched, and this exact scenario is explicitly exercised and accepted as correct behavior in the pallet's own test suite: [5](#0-4)  — the test comment states outright: *"A height below the latest can never be resubmitted... so ... permanently unsubmittable."* [6](#0-5) 

Chaining these three facts together: (1) a snapshot-only "unchallenged" check with no finality/timing guarantee, (2) permanent inability to overwrite a previously-committed height even with a genuinely correct commitment, and (3) veto leaving the height permanently un-resubmittable unless it happened to be the current tip — reproduces the original bug's core failure mode inside Hyperbridge's own consensus layer for OP-stack chains.

### Impact Explanation
Any POST request or GET response whose membership/state proof is anchored to the specific L2 height that was seeded with a fraudulent dispute-game claim becomes permanently unverifiable once the bad commitment is vetoed, because the correct commitment for that exact height can never be re-stored. Depending on which cross-chain flow relies on that height, this can permanently freeze user funds/messages routed through Hyperbridge for that L2 (token bridge mints/burns, intents fills, or any application relying on state proofs at that height), and if the fraudulent commitment is *not* caught before Hyperbridge's own `challenge_period` elapses, it can also enable delivery of forged messages (an application's `onAccept`/`onGetResponse` executing against a state root that was never real, e.g. unbacked mint). This satisfies "concrete... permanent freezing of funds... unsound state commitment" per the validation bar.

### Likelihood Explanation
The attack is reachable by any permissionless relayer/proposer on the OP-stack side: creating a dispute game with a false root claim and immediately relaying the corresponding `ConsensusMessage` to Hyperbridge is a single, unprivileged transaction pair — no validator collusion or admin/governance access is required, since the "unchallenged" check is satisfied by construction for any newly created game. The permanent-freeze consequence (item 2/3 above) triggers deterministically any time a commitment for a given height needs correcting after being superseded/vetoed, which is an intended, tested code path rather than a hypothetical edge case.

### Recommendation
- Require the OP dispute game to be fully **resolved** (`status == CHALLENGER_WINS`/`DEFENDER_WINS` and `resolvedAt` set, past the game's own finalization delay) before `verify_optimism_dispute_game_proof` accepts its root claim as a trusted `IntermediateState`, rather than merely "not yet challenged."
- Modify `update_client`'s intermediate-state storage logic so that a fisherman veto (`delete_state_commitment`) actually permits re-submission of a corrected commitment for the vetoed height, e.g. by tracking vetoed heights separately from `latest_commitment_height` and allowing height ≤ latest to be re-accepted specifically when the prior entry was deleted via veto.
- Consider requiring `store_state_machine_commitment` to allow overwriting an existing (non-finalized/challengeable) commitment with a newer proof for the same height during Hyperbridge's own `challenge_period`, rather than a strict "first write wins" rule.

### Proof of Concept
1. Attacker (acting as OP-stack proposer/relayer) creates a `FaultDisputeGame` in the `DisputeGameFactory` with a fabricated root claim for L2 block `H` that does not match the real `state_root`/`withdrawal_storage_root`.
2. Immediately (same block, before any challenger can call `move()`), attacker submits a `ConsensusMessage` to Hyperbridge containing an `OptimismDisputeGameProof` referencing this game; `verify_not_challenged` passes because `claimData.length == 1`.
3. `update_client` (`modules/ismp/core/src/handlers/consensus.rs`) stores the fraudulent `StateCommitment` for height `H` and advances `latest_commitment_height` to `H`.
4. An OP-stack challenger later disputes the game on L1 and it resolves as fraudulent; a Hyperbridge fisherman calls `veto_state_commitment`/`delete_state_commitment` for height `H`.
5. The honest proposer/relayer attempts to submit the correct consensus proof for height `H` (or any dispute game resolved at that exact height) — `update_client` skips it (`previous_latest_height > commitment_height.height` or the state already exists/was vetoed and latest height was never rolled back below `H`), so the correct state for height `H` can never be stored again.
6. Any genuine request/response depending on state proofs at height `H` is permanently unverifiable through Hyperbridge.

### Citations

**File:** modules/ismp/clients/optimism/src/lib.rs (L279-386)
```rust
pub fn verify_optimism_dispute_game_proof<H: Keccak256 + Send + Sync>(
	payload: OptimismDisputeGameProof,
	root: H256,
	dispute_factory_address: H160,
	game_type_configs: Vec<GameTypeConfig>,
	consensus_state_id: ConsensusStateId,
) -> Result<IntermediateState, Error> {
	// Find the per-game-type configuration for this proof's game type.
	let game_config = game_type_configs
		.iter()
		.find(|c| c.game_type == payload.game_type)
		.ok_or(Error::UnsupportedGameType(payload.game_type))?
		.clone();

	let factory_storage_root =
		get_contract_account::<H>(payload.dispute_factory_proof, &dispute_factory_address.0, root)?
			.storage_root
			.0
			.into();
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

	// Bind the proxy's storage layout to the expected implementation by proving
	// `gameImpls[game_type]` in the factory matches the configured address. This is what makes
	// the per-kind "not challenged" check below meaningful: a factory upgrade that swaps
	// `gameImpls` to an implementation with a different layout would fail this check.
	let game_type_key = {
		let mut key = vec![0u8; 32];
		key[28..].copy_from_slice(&payload.game_type.to_be_bytes());
		derive_map_key::<H>(key, GAME_IMPLS_SLOT)
	};
	let impl_value = get_value_from_proof::<H>(
		game_type_key.0.to_vec(),
		factory_storage_root,
		payload.game_impl_proof,
	)?
	.ok_or(Error::GameImplsMissing)?;
	let impl_address = decode_address_from_storage_value(&impl_value)?;
	if impl_address != game_config.expected_impl {
		Err(Error::GameImplMismatch {
			game_type: payload.game_type,
			actual: impl_address,
			expected: game_config.expected_impl,
		})?
	}

	// Prove the proxy account, then verify "not challenged" against its storage root.
	verify_not_challenged::<H>(
		&game_config.kind,
		root,
		payload.proxy,
		payload.proxy_account_proof,
		payload.challenge_proof,
	)?;

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

**File:** modules/ismp/clients/optimism/src/lib.rs (L407-461)
```rust
/// Verifies that the dispute game at `proxy_address` has not been challenged. The check varies
/// by implementation kind. For `OPSuccinct`, no challenge mechanism exists so the proof fields
/// are not consulted.
fn verify_not_challenged<H: Keccak256 + Send + Sync>(
	kind: &DisputeGameImpl,
	root: H256,
	proxy_address: H160,
	proxy_account_proof: Vec<Vec<u8>>,
	challenge_proof: Vec<Vec<u8>>,
) -> Result<(), Error> {
	if matches!(kind, DisputeGameImpl::OPSuccinct) {
		// OPSuccinctDisputeGame has no challenge mechanism by construction, so any game we
		// accepted as registered in the factory is unchallenged.
		return Ok(());
	}

	let proxy_storage_root =
		get_contract_account::<H>(proxy_account_proof, &proxy_address.0, root)?
			.storage_root
			.0
			.into();

	match kind {
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

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L778-827)
```rust
// A height below the latest can never be resubmitted — the consensus handler skips
// anything at or below `previous_latest_height` — so its stale queue entry has no
// live twin and evicting it touches nothing.
#[test]
fn vetoed_height_that_cannot_be_resubmitted_evicts_as_a_noop() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let host = Ismp::default();
		let id = queue_test_state_machine();
		let store = |height: u64| {
			host.store_state_machine_commitment(
				StateMachineHeight { id, height },
				queue_test_commitment(),
			)
			.unwrap();
			host.store_latest_commitment_height(StateMachineHeight { id, height }).unwrap();
		};

		pallet_ismp::Pallet::<Test>::update_commitment_caps(
			RuntimeOrigin::root(),
			BTreeMap::from([(id, 2)]),
		)
		.unwrap();

		store(10);
		store(11);

		// Veto a height below the latest: the commitment goes away immediately while
		// its queue entry stays behind as a stale index. The latest height is
		// untouched, so 10 stays permanently unsubmittable.
		host.delete_state_commitment(StateMachineHeight { id, height: 10 }).unwrap();
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 10 }).is_err());
		assert_eq!(host.latest_commitment_height(id).unwrap(), 11);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 0, tail: 2 }
		);
		assert_eq!(StateCommitmentQueue::<Test>::get(id, 0), Some(10));

		// The stale index is evicted as a no-op on the next insertion.
		store(12);
		assert_eq!(
			CommitmentQueueStates::<Test>::get(id),
			CommitmentQueueState { head: 1, tail: 3 }
		);
		assert!(StateCommitmentQueue::<Test>::get(id, 0).is_none());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 11 }).is_ok());
		assert!(host.state_machine_commitment(StateMachineHeight { id, height: 12 }).is_ok());
	})
}
```

**File:** modules/pallets/fishermen/src/lib.rs (L157-193)
```rust
	{
		/// A collator has determined that some [`StateCommitment`] (which is ideally still in
		/// its challenge period) is in fact fraudulent and misrepresentative of the state
		/// changes at the provided height. They aren't required to provide any proofs for
		/// this — any single collator's call deletes the commitment.
		///
		/// Dispatches with `Pays::No`. The on-chain `IsCollator` check is the DOS guard, so
		/// the signer does not need to hold a balance.
		#[pallet::call_index(0)]
		#[pallet::weight((<T as frame_system::Config>::DbWeight::get().reads_writes(1, 2), Pays::No))]
		pub fn veto_state_commitment(
			origin: OriginFor<T>,
			height: StateMachineHeight,
		) -> DispatchResult {
			let account = ensure_signed(origin)?;
			ensure!(T::IsCollator::contains(&account), Error::<T>::UnauthorizedAction);

			let ismp_host = <T as Config>::IsmpHost::default();
			let commitment =
				ismp_host.state_machine_commitment(height).map_err(|_| Error::<T>::VetoFailed)?;
			ismp_host.delete_state_commitment(height).map_err(|_| Error::<T>::VetoFailed)?;

			Self::deposit_event(Event::StateCommitmentVetoed {
				height,
				commitment,
				fisherman: account.clone(),
			});
			pallet_ismp::Pallet::<T>::deposit_event(
				ismp::events::Event::StateCommitmentVetoed(StateCommitmentVetoed {
					height,
					fisherman: account.as_ref().to_vec(),
				})
				.into(),
			);

			Ok(())
		}
```
