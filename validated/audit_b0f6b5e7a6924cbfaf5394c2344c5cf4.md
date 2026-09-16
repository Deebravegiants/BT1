Based on the analysis, I found a real analog in the `ismp-arbitrum` consensus client: the `arbitrum_consensus_type` field in `ConsensusState` is declared but never enforced against the attacker-supplied `ArbitrumConsensusProof` variant when verifying a consensus update.

### Title
Attacker-selectable Arbitrum proof variant bypasses configured consensus-type binding, enabling verification-method confusion in `ArbitrumConsensusClient::verify_consensus` - (File: modules/ismp/clients/ismp-arbitrum/src/lib.rs)

### Summary
`ismp-arbitrum`'s `ConsensusState` stores an explicit `arbitrum_consensus_type: ArbitrumConsensusType` (`ArbitrumOrbit` or `ArbitrumBold`) field [1](#0-0) , mirroring the pattern the GRANDPA client uses (and explicitly documents as a fixed "type confusion" bug class) to bind an untrusted proof envelope to the trusted configuration [2](#0-1) . However, `ArbitrumConsensusClient::verify_consensus` never reads or checks `consensus_state.arbitrum_consensus_type` — it only `match`es on the relayer-controlled `ArbitrumConsensusProof` enum decoded straight from the untrusted `consensus_proof` bytes [3](#0-2) .

### Finding Description
This is the same bug class as CVE-2022-45343: a type/kind check that exists in the data model is never actually enforced at the point where untrusted, attacker-controlled data selects which decode/verification routine to run — a type-confusion condition. In GPAC, `Q_IsTypeOn` was misused to gate access to a freed/reinterpreted object; here, the equivalent guard (`arbitrum_consensus_type`) is defined on `ConsensusState` but is dead — it is set at genesis/config time and then never consulted in `verify_consensus`, so the relayer's `ArbitrumConsensusProof::ArbitrumOrbit(..)` vs `ArbitrumConsensusProof::ArbitrumBold(..)` choice alone decides which verifier (`verify_arbitrum_payload` vs `verify_arbitrum_bold`) runs, regardless of what the trusted consensus state says the chain's actual finality mechanism is [4](#0-3) .

Both verifier arms independently re-derive proofs against the real `RollupCore` storage via `Pallet::<T>::state_machines_rollup_core_addresses` and the L1 state root, so on the current, single-mechanism-per-chain deployment topology this is not directly exploitable — an attacker cannot forge a fake rollup state because both mechanisms verify against the same authentic on-chain contract storage. It is nonetheless a violation of the type/config-binding invariant the codebase treats as security-critical elsewhere (see the GRANDPA comment explicitly framing an identical unchecked pairing as "type confusion," and the OP Stack ismp client, which *does* correctly key selection off `consensus_state.optimism_consensus_type` [5](#0-4) ). Should Arbitrum ever undergo a migration window where a rollup-core address is reused across a pre-BoLD Orbit deployment and a post-BoLD deployment, or a fisherman blacklist keyed by claim hash under one scheme fails to cover the analogous claim under the other scheme, the missing binding removes a defense-in-depth check that the rest of the codebase relies on for this exact class of confusion.

### Impact Explanation
Given both Arbitrum verification arms perform full cryptographic/storage verification against the genuine `RollupCore` contract, the practical impact under the current single-mechanism-per-chain configuration is limited: no unbacked state commitment can be forged today purely from this gap. The severity is therefore best characterized as a missing invariant enforcement (a latent type-confusion primitive) rather than an immediately exploitable unbounded impact, in contrast to the GRANDPA case the codebase already patched for the same class of bug.

### Likelihood Explanation
Low today, because exploitation requires an additional condition (e.g., a rollup-core address reused across mismatched consensus mechanisms, or a fisherman blacklist gap between the Orbit claim-hash and Bold assertion-hash keying) that does not currently exist in the deployed configuration. It becomes directly relevant the moment Arbitrum chains are migrated between Orbit and BoLD without decommissioning the old rollup-core binding, which is an operationally realistic scenario given Arbitrum's own BoLD migration.

### Recommendation
Enforce `consensus_state.arbitrum_consensus_type` against the submitted `ArbitrumConsensusProof` variant in `verify_consensus`, rejecting proofs whose variant doesn't match the configured type — exactly mirroring `envelope_matches_state_machine` in the GRANDPA client [6](#0-5)  and the `optimism_consensus_type` gate already used in the OP Stack tesseract host [5](#0-4) .

### Proof of Concept
Not directly demonstrable as fund-affecting from the code alone: constructing an actual exploit would require an additional misconfiguration (shared rollup-core address across mismatched consensus types, or blacklist bypass across claim-hash schemes) that the index does not show existing in current deployments. The core, verifiable fact is the absence of the `arbitrum_consensus_type` check, confirmed by inspection of `verify_consensus` at [7](#0-6) , contrasted with the equivalent enforced check for GRANDPA and OP Stack.

### Citations

**File:** modules/ismp/clients/ismp-arbitrum/src/lib.rs (L45-63)
```rust
#[derive(Encode, Decode, Debug, PartialEq, Eq, Clone)]
pub struct ConsensusState {
	pub finalized_height: u64,
	pub state_machine_id: StateMachineId,
	pub l1_state_machine_id: StateMachineId,
	pub arbitrum_consensus_type: ArbitrumConsensusType,
}

#[derive(Encode, Decode)]
pub struct ArbitrumUpdate {
	pub l1_height: u64,
	pub proof: ArbitrumConsensusProof,
}

#[derive(Encode, Decode, Debug, Clone, PartialEq, Eq)]
pub enum ArbitrumConsensusType {
	ArbitrumOrbit,
	ArbitrumBold,
}
```

**File:** modules/ismp/clients/ismp-arbitrum/src/lib.rs (L102-217)
```rust
	fn verify_consensus(
		&self,
		host: &dyn IsmpHost,
		consensus_state_id: ConsensusStateId,
		trusted_consensus_state: Vec<u8>,
		consensus_proof: Vec<u8>,
	) -> Result<(Vec<u8>, VerifiedCommitments), Error> {
		let ArbitrumUpdate { l1_height, proof } =
			ArbitrumUpdate::decode(&mut &consensus_proof[..])
				.map_err(|_| ArbitrumError::DecodeArbitrumUpdate)?;

		let mut consensus_state = ConsensusState::decode(&mut &trusted_consensus_state[..])
			.map_err(|_| ArbitrumError::DecodeConsensusState)?;

		// The state machine being updated is fixed by the trusted consensus state, never
		// supplied by the (untrusted) update. This binds verifier-config selection to the
		// correct Arbitrum chain identity.
		let state_machine_id = consensus_state.state_machine_id;

		let l1_state_machine_height =
			StateMachineHeight { id: consensus_state.l1_state_machine_id, height: l1_height };

		let l1_state_commitment = host.state_machine_commitment(l1_state_machine_height)?;
		let state_root = l1_state_commitment.state_root;

		let mut state_machine_map: BTreeMap<StateMachineId, Vec<StateCommitmentHeight>> =
			BTreeMap::new();

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

					let state = verify_arbitrum_payload::<H>(
						proof,
						state_root,
						rollup_core_address,
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
				},
				ArbitrumConsensusProof::ArbitrumBold(proof) => {
					// BoLD assertions use the on-chain `assertionHash` directly as the claim key.
					let assertion_hash = compute_assertion_hash(
						proof.previous_assertion_hash,
						proof.after_state.hash(),
						proof.sequencer_batch_acc,
					);
					if <T as pallet::Config>::FishermanBlacklist::is_arbitrum_claim_blacklisted(
						state_machine_id,
						assertion_hash,
					) {
						return Err(ArbitrumError::ClaimBlacklisted(assertion_hash).into());
					}

					let state = verify_arbitrum_bold::<H>(
						proof,
						state_root,
						rollup_core_address,
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
				},
			}
		}
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L385-408)
```rust
/// Whether the proof envelope a submitter chose is valid for the class of state
/// machine the trusted consensus state tracks.
///
/// The envelope is attacker-selected; the state machine is trusted. Every arm of
/// `verify_consensus` labels the header it just verified with that trusted identity, so
/// an unchecked pairing is a type confusion rather than a mere decoding quirk: a
/// parachain tracker's authority set *is* the relay's GRANDPA set, so a genuine
/// relay-chain finality proof submitted under `StandaloneChain` passes signature
/// verification and its **global** state root is then recorded under the parachain's
/// identity, at a relay height.
///
/// The accepted pairings mirror the mapping the honest producer already uses in
/// `tesseract/consensus/grandpa/src/host.rs`.
pub(crate) fn envelope_matches_state_machine(
	state_machine: &StateMachine,
	message: &ConsensusMessage,
) -> bool {
	matches!(
		(state_machine, message),
		(StateMachine::Polkadot(_) | StateMachine::Kusama(_), ConsensusMessage::Polkadot(_)) |
			(StateMachine::Relay { .. }, ConsensusMessage::Relaychain(_)) |
			(StateMachine::Substrate(_), ConsensusMessage::StandaloneChain(_))
	)
}
```

**File:** tesseract/consensus/op-host/src/host.rs (L646-739)
```rust
			return match consensus_state.optimism_consensus_type {
				Some(OptimismConsensusType::OpL2Oracle)  => {
					match client.latest_event(previous_height + 1, current_height).await {
						Ok(Some(event)) => {
							trace!(target: crate::LOG_TARGET, "{state_machine:?}: fetching l2 oracle payload");
							match client.fetch_op_payload(current_height, event).await {
								Ok(payload) => {
									let update = OptimismUpdate {
										l1_height: current_height,
										proof: OptimismConsensusProof::OpL2Oracle(payload),
									};

									let consensus_message = ConsensusMessage {
										consensus_proof: update.encode(),
										consensus_state_id: client.consensus_state_id,
										signer: counterparty.address(),
									};

									trace!(target: crate::LOG_TARGET, "gotten update for {state_machine:?}");

									Some((Ok::<_, Error>(Some(consensus_message)), (interval, current_height)))
								}
								// Advance the pointer past this range on a payload-fetch error: the
								// event exists but its payload can't be built (e.g. pruned state),
								// so retrying the same range would stall. Skip ahead instead.
								Err(_) => Some((Err(anyhow!("Not a fatal error: Error fetching op stack l2 oracle payload with height {current_height:?}")), (interval, current_height),)),
							}
						}
						Ok(None) => {
							trace!(target: crate::LOG_TARGET, "{state_machine:?}: no events fetched for op l2 oracle");
							Some((Ok::<_, Error>(None), (interval, current_height)))
						}
						Err(_) => {
							Some((
								Err(anyhow!(
                                "Not a fatal error: Failed to fetch latest op l2 oracle event at height {current_height:?}",

                            )),
								(interval, latest_height),
							))
						}
					}
				}
				Some(OptimismConsensusType::OpFaultProofGames) => {
					let l2_state_machine_id = StateMachineId {
						state_id: client.state_machine,
						consensus_state_id: client.consensus_state_id,
					};
					let game_type_configs = match fetch_game_type_configs(&counterparty, l2_state_machine_id).await {
						Ok(Some(configs)) => configs,
						Ok(None) => {
							trace!(target: crate::LOG_TARGET, "{state_machine:?}: -> no dispute-game factory config installed for this state machine");
							return Some((Ok(None), (interval, previous_height)));
						},
						Err(e) => return Some((
							Err(anyhow!("Not a fatal error: failed to fetch dispute-game factory config: {e:?}")),
							(interval, latest_height),
						)),
					};
					match client.latest_dispute_games(previous_height + 1, current_height, game_type_configs.clone()).await {
						Ok(event) => {
							trace!(target: crate::LOG_TARGET, "{state_machine:?}: -> fetching op fault proof games payload");
							match client.fetch_dispute_game_payload(current_height, game_type_configs, event).await {
								Ok(maybe_payload) => {
									if let Some(payload) = maybe_payload {
										let update = OptimismUpdate {
											l1_height: current_height,
											proof: OptimismConsensusProof::OpFaultProofGames(payload),
										};

										let consensus_message = ConsensusMessage {
											consensus_proof: update.encode(),
											consensus_state_id: client.consensus_state_id,
											signer: counterparty.address(),
										};

										trace!(target: crate::LOG_TARGET, "{state_machine:?}: -> gotten update");

										Some((Ok::<_, Error>(Some(consensus_message)), (interval, current_height)))
									} else {
										trace!(target: crate::LOG_TARGET, "{state_machine:?}: -> No dispute game updates between {previous_height:?} -> {current_height:?}");
										Some((Ok::<_, Error>(None), (interval, current_height)))
									}
								}
								// Advance the pointer past this range on a payload-fetch error so a
								// range we can't build a payload for doesn't stall the task; the
								// next tick moves on to newer L1 heights.
								Err(e) => Some((Err(anyhow!("Not a fatal error: Error fetching op fault proof game payload at height {current_height:?}\n{e:?}")), (interval, current_height),)),
							}
						}
						Err(e) => Some((Err(anyhow!("Not a fatal error: Error fetching dispute game events at height {current_height:?}\n{e:?}")), (interval, latest_height),)),
					}
				}
				_ => return Some((Err(anyhow!("Fatal error: No op stack consensus type in consensus state")), (interval, latest_height),))
```
