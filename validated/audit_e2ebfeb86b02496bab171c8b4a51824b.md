### Title
Front-runnable dispute-game/claim blacklist lets a fraudulent OP-stack or Arbitrum consensus proof be finalized before the fisherman's veto lands - ([File: modules/pallets/fishermen/src/lib.rs])

### Summary
`pallet-fishermen::blacklist_dispute_game` / `blacklist_arbitrum_claim` are permissioned (`IsCollator`) but *publicly observable* extrinsics submitted to Hyperbridge's public mempool once a fisherman watcher decides an L1 OP-stack dispute game or Arbitrum claim is fraudulent. The consensus verifiers only refuse a proof if the blacklist entry already exists in storage *at the moment `verify_consensus` runs* [1](#0-0) [2](#0-1) . Because the corresponding consensus update is delivered via the permissionless, unsigned `handle_unsigned` extrinsic [3](#0-2) , anyone can race to get the fraudulent proof included in an earlier block than the fisherman's blacklist transaction — exactly the same "observe the restricting tx in the mempool, beat it to inclusion" pattern as the reported `TransferRestrictor.restrict` issue.

### Finding Description
The fisherman/blacklist design intentionally trusts a single collator's call to permanently block future proofs referencing a given dispute-game proxy or Arbitrum claim hash [4](#0-3) . The comment explicitly documents the race: the off-chain watcher only submits the blacklist *after* detecting fraud by polling L1 and comparing against an L2 RPC quorum [5](#0-4) [6](#0-5) . Between the moment the fraudulent dispute game/assertion becomes visible on L1 and the moment the resulting `blacklist_dispute_game`/`blacklist_arbitrum_claim` extrinsic is actually included on Hyperbridge, the blacklist storage entry does not exist. `verify_consensus` checks the blacklist map *before* the heavy proof verification and, if the entry is absent, proceeds to accept the proof [7](#0-6) .

Any relayer (or the attacker who caused the fraudulent dispute-game outcome, e.g. by censoring/griefing the honest L2 challenger on L1) can submit the `OpFaultProofGames`/`ArbitrumOrbit`/`ArbitrumBold` consensus update through `handle_unsigned` as soon as the proof is constructible, without waiting for or being gated by the fisherman's pending blacklist transaction. `handle_unsigned` is unsigned/free (`Pays::No`-style unpermissioned dispatch, validated only for well-formedness/priority by `ValidateUnsigned`) [8](#0-7) [9](#0-8) , so there is no cost or authorization barrier to racing ahead of the fisherman's transaction and getting the fraudulent update mined first, mirroring the fee-bump front-running described in the report.

### Impact Explanation
If the fraudulent proof lands before the blacklist, `verify_consensus` accepts it and stores a state commitment for the forged L2 output/assertion, entering the normal challenge period [10](#0-9) . Note that the generic `veto_state_commitment` path [11](#0-10)  still exists as a secondary safety net during that challenge window, so the permanent dispute-game/claim blacklist is not the *sole* defense — but it is the specific, purpose-built control the fisherman watcher relies on for this consensus type, and it is only effective if it lands before the malicious proof. A successful race narrows or eliminates the intended margin of the OP-stack/Arbitrum fault-proof defense-in-depth and can let a forged state commitment briefly exist that a colluding/careless relayer could try to exploit for message delivery during the challenge window before a fisherman notices and separately vetoes it via `veto_state_commitment`.

### Likelihood Explanation
Medium-to-low. Exploitation requires: (1) the attacker to already control or benefit from a fraudulent OP-stack dispute-game outcome or Arbitrum claim on L1 (a non-trivial precondition involving griefing/censoring honest challengers), and (2) winning a race against the fisherman watcher's blacklist submission, which the watcher issues promptly upon detecting quorum mismatch. Because `veto_state_commitment` still provides a second, independent safety net during the challenge period, the practical impact is bounded unless the attacker can also deliver a message off the forged commitment within that window.

### Recommendation
- Gate `verify_consensus` acceptance of `OpFaultProofGames`/`ArbitrumOrbit`/`ArbitrumBold` proofs on an explicit minimum delay after game/assertion creation (a mini "challenge period" specific to these proof types) so fishermen have a guaranteed window to submit `blacklist_dispute_game`/`blacklist_arbitrum_claim` before any proof referencing that claim can be accepted.
- Alternatively/additionally, treat entries pending the fisherman's off-chain quorum check as provisionally blocked (e.g., require a short cool-down since `DisputeGameCreated`/assertion creation before `verify_consensus` will accept a proof for it), removing the race window entirely rather than relying on inclusion-order luck.
- Ensure `veto_state_commitment` remains as a mandatory backstop and is being exercised in monitoring/alerting whenever a forged commitment slips past the blacklist race, so operators can measure actual exposure.

### Proof of Concept
1. Attacker (or a censoring adversary) causes a `FaultDisputeGame` on L1 whose `rootClaim` is fraudulent relative to the real L2 output, and the game passes the "not challenged" storage check (`claimData.length == 1`) because the honest challenger's `move()` was censored/delayed.
2. The off-chain opstack fisherman watcher (`tesseract/messaging/fisherman/src/opstack.rs`, `evaluate`/`scan_target`) detects the mismatch against its L2 RPC quorum and calls `FishermanClaim::blacklist_dispute_game`, submitting `pallet_fishermen::blacklist_dispute_game(state_machine_id, proxy)` to Hyperbridge's mempool [6](#0-5) .
3. Before that extrinsic is included, the attacker (or a colluding relayer) submits `pallet_ismp::handle_unsigned` carrying an `OpFaultProofGames` consensus message referencing the same fraudulent `proxy`.
4. `ArbitrumConsensusClient`/`OptimismConsensusClient::verify_consensus` reads `BlacklistedDisputeGames` — which is still empty because the fisherman's tx has not landed — and proceeds to fully verify and accept the fraudulent state commitment [12](#0-11) .
5. The fisherman's blacklist transaction lands afterward and is effectively useless for this specific proof, since the commitment for that height/claim is already stored; recovery now depends entirely on a separate `veto_state_commitment` call during the challenge period.

### Citations

**File:** modules/ismp/clients/ismp-optimism/src/lib.rs (L213-255)
```rust
			OptimismConsensusProof::OpFaultProofGames(dispute_proof) => {
				if let Some((dispute_game_factory, game_type_configs)) =
					Pallet::<T>::state_machines_dispute_game_factories_types(state_machine_id)
				{
					// Refuse proofs that reference a blacklisted dispute-game proxy. The check
					// happens before the heavy proof verification so a blacklisted entry costs
					// only one storage read.
					if <T as pallet::Config>::FishermanBlacklist::is_dispute_game_blacklisted(
						state_machine_id,
						dispute_proof.proxy,
					) {
						return Err(
							OptimismError::DisputeGameBlacklisted(dispute_proof.proxy).into()
						);
					}

					let state = verify_optimism_dispute_game_proof::<H>(
						dispute_proof,
						state_root,
						dispute_game_factory,
						game_type_configs,
						consensus_state_id.clone(),
					)?;

					let state_commitment_height = StateCommitmentHeight {
						commitment: state.commitment,
						height: state.height.height,
					};

					let mut state_commitment_vec: Vec<StateCommitmentHeight> = Vec::new();
					state_commitment_vec.push(state_commitment_height);
					state_machine_map.insert(
						StateMachineId {
							state_id: consensus_state.state_machine_id.state_id,
							consensus_state_id: consensus_state
								.l1_state_machine_id
								.consensus_state_id,
						},
						state_commitment_vec,
					);

					consensus_state.finalized_height = state.height.height;
				}
```

**File:** modules/ismp/clients/ismp-arbitrum/src/lib.rs (L130-148)
```rust
		if let Some(rollup_core_address) =
			Pallet::<T>::state_machines_rollup_core_addresses(state_machine_id)
		{
			match proof {
				ArbitrumConsensusProof::ArbitrumOrbit(proof) => {
					// Derive the unified claim hash and refuse blacklisted entries before the
					// heavy proof verification.
					let state_hash = get_state_hash::<H>(
						proof.global_state,
						proof.machine_status,
						proof.inbox_max_count,
					);
					let claim = orbit_claim_hash::<H>(state_hash, proof.node_number);
					if <T as pallet::Config>::FishermanBlacklist::is_arbitrum_claim_blacklisted(
						state_machine_id,
						claim,
					) {
						return Err(ArbitrumError::ClaimBlacklisted(claim).into());
					}
```

**File:** modules/pallets/ismp/src/lib.rs (L360-382)
```rust
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
		///
		/// Emits different message events based on the Message received if successful.
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/pallets/ismp/src/lib.rs (L614-645)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;

			if let Some((state_machine_id, latest_height)) = events.iter().find_map(|event| {
				if let ismp::events::Event::StateMachineUpdated(state_machine_updated_event) = event
				{
					Some((
						state_machine_updated_event.state_machine_id.clone(),
						state_machine_updated_event.latest_height,
					))
				} else {
					None
				}
			}) {
				return Ok(ValidTransaction {
					priority: latest_height,
					requires: vec![],
					provides: vec![sp_io::hashing::keccak_256(&state_machine_id.encode()).to_vec()],
					longevity: 25,
					propagate: true,
				});
			}
```

**File:** modules/pallets/fishermen/src/lib.rs (L158-193)
```rust
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

**File:** modules/pallets/fishermen/src/lib.rs (L195-229)
```rust
		/// A collator has determined that the opstack dispute game at `proxy` (registered
		/// against the configured `DisputeGameFactory` for `state_machine_id`) is fraudulent
		/// — typically because the off-chain fisherman watcher verified the claimed L2 output
		/// root against a supermajority (2/3·N + 1) of L2 RPC endpoints and observed a
		/// mismatch (or a quorum of the L2 height being absent).
		///
		/// Any single collator finalizes the blacklist. The entry is permanent (there is no
		/// `unblacklist` extrinsic) — the consensus verifier will refuse any future
		/// `OpFaultProofGames` consensus proof that references this proxy.
		///
		/// Dispatches with `Pays::No`. The on-chain `IsCollator` check is the DOS guard.
		#[pallet::call_index(1)]
		#[pallet::weight((<T as frame_system::Config>::DbWeight::get().reads_writes(1, 1), Pays::No))]
		pub fn blacklist_dispute_game(
			origin: OriginFor<T>,
			state_machine_id: StateMachineId,
			proxy: H160,
		) -> DispatchResult {
			let account = ensure_signed(origin)?;
			ensure!(T::IsCollator::contains(&account), Error::<T>::UnauthorizedAction);

			// Idempotent: a second call for the same (chain, proxy) is silently Ok and does
			// not overwrite the original fisherman.
			if BlacklistedDisputeGames::<T>::contains_key(state_machine_id, proxy) {
				return Ok(());
			}

			BlacklistedDisputeGames::<T>::insert(state_machine_id, proxy, account.clone());
			Self::deposit_event(Event::DisputeGameBlacklisted {
				state_machine_id,
				proxy,
				fisherman: account,
			});
			Ok(())
		}
```

**File:** tesseract/messaging/fisherman/src/opstack.rs (L1-8)
```rust
// Copyright (C) Polytope Labs Ltd.
// SPDX-License-Identifier: Apache-2.0

//! Opstack fisherman watcher. Polls Ethereum L1 for `DisputeGameCreated` events emitted by
//! configured `DisputeGameFactory` contracts and, for each new game, verifies the game's
//! claimed L2 `root_claim` against a 2/3·N+1 quorum of L2 RPC endpoints. On mismatch (or
//! quorum-of-missing-blocks) the game's proxy is permanently blacklisted via
//! `pallet-fishermen::blacklist_dispute_game` on hyperbridge.
```

**File:** tesseract/messaging/fisherman/src/opstack.rs (L126-151)
```rust
		match evaluate(cfg, target, event.rootClaim, proxy_h160, to).await {
			Ok(true) => {
				log::trace!(
					target: crate::LOG_TARGET,
					"fish_opstack: proxy {proxy_h160:?} on {} agrees with L2 quorum",
					target.state_machine,
				);
			},
			Ok(false) => {
				log::warn!(
					target: crate::LOG_TARGET,
					"fish_opstack: blacklisting opstack dispute-game proxy {:?} on {} \
					(rootClaim {:?}, gameType {})",
					proxy_h160, target.state_machine, event.rootClaim, event.gameType,
				);
				if let Err(e) = cfg
					.hyperbridge
					.blacklist_dispute_game(target.state_machine_id, proxy_h160)
					.await
				{
					log::error!(
						target: crate::LOG_TARGET,
						"fish_opstack: submit blacklist_dispute_game for {proxy_h160:?} failed: {e:?}",
					);
				}
			},
```
