### Title
L1-referencing rollup consensus clients (Arbitrum/Optimism) trust unchallenged L1 state commitments to derive child-chain state roots - ([File: modules/ismp/clients/ismp-arbitrum/src/lib.rs])

### Summary
The `ArbitrumConsensusClient::verify_consensus` and `OptimismConsensusClient::verify_consensus` implementations read an L1 `StateCommitment` at an attacker/relayer-supplied `l1_height` and use its `state_root` as the trust anchor for verifying Arbitrum/Optimism L2 proofs, without checking that the referenced L1 commitment has survived its challenge period (i.e. is no longer vetoable by a fisherman). This is directly analogous to the reported bug class: an externally supplied, not-yet-validated reference value (there: an oracle price; here: an L1 state root) is accepted and permanently baked into downstream, fund-affecting state (the child rollup's finalized consensus state and state commitments), with no mechanism to prevent an incorrect/soon-to-be-reverted value from being used.

### Finding Description
Any permissionless relayer can submit a `ConsensusMessage` for the Arbitrum or Optimism consensus client. The message decodes to an `ArbitrumUpdate`/`OptimismUpdate` containing an attacker-chosen `l1_height`: [1](#0-0) [2](#0-1) 

In both clients, `l1_state_machine_height` is built directly from the untrusted `l1_height` and immediately fed into `host.state_machine_commitment(l1_state_machine_height)` to fetch `state_root`, which is then trusted as the root against which the Merkle/storage proofs for the rollup's `RollupCore`/`L2Oracle`/`DisputeGameFactory` contracts are verified (`verify_arbitrum_payload`, `verify_arbitrum_bold`, `verify_optimism_payload`, `verify_optimism_dispute_game_proof`).

Crucially, this lookup bypasses the challenge-period gate (`verify_delay_passed` / `validate_state_machine`) that the core ISMP request/response handlers apply before trusting a state commitment for message delivery: [3](#0-2) 

That gate exists precisely so a state commitment can be vetoed by a fisherman (via `deleteStateMachineCommitment`/`delete_state_commitment`) before anything relies on it. The consensus-client code path for Arbitrum/Optimism, however, calls `host.state_machine_commitment()` unconditionally and uses whatever L1 height the relayer chooses — including a height that was just stored moments ago and is still within its L1 challenge window. If that L1 commitment turns out to be fraudulent (e.g., a malicious/erroneous BEEFY/GRANDPA/BSC update that a fisherman has not yet had time to veto), the Arbitrum/Optimism client will use its `state_root` to "verify" arbitrary rollup-side proofs, permanently updating `consensus_state.finalized_height` and inserting a `StateCommitment` for the L2 chain into storage via `update_client`'s `host.store_state_machine_commitment(...)` call: [4](#0-3) 

Once stored, this L2 state commitment becomes the trust anchor for `HandlerV2.sol`/`handlePostRequests`-style membership proofs used to dispatch incoming POST/GET messages (token bridge mints, intent escrow releases, etc.) on that state machine. There is no re-validation step tying the L2 commitment's continued validity to the fate of the L1 commitment it was derived from — if the L1 commitment is later deleted/vetoed, the L2 state commitment derived from it remains in storage and continues to authorize message delivery, exactly like the reported issue where "the last aggregated price ... will be recorded as reference prices" and "negatively impact the settlement phase," irreversibly.

### Impact Explanation
If an incorrect L1 state root is accepted and used to source Arbitrum/Optimism L2 state (due to a consensus fault, a racing/​still-challengeable BEEFY/GRANDPA/BSC update, or a malicious relayer choosing a favorable stale height before the true fraud is caught and vetoed), a forged or manipulated L2 `state_root`/`overlay_root` can be committed for that state machine. Downstream, this state commitment is exactly what `HandlerV2.handlePostRequests`/membership proofs rely on to dispatch incoming POST/GET requests to token bridge and intent-settlement modules. A forged commitment can therefore enable forged message delivery, unbacked minting on the token bridge, or unauthorized draining of intents escrow on the affected L2 — and because ISMP consensus clients do not support unwinding an already-stored `StateMachineCommitment` once relied upon by application-level effects (mints/transfers already executed are irreversible), this is a permanent freezing/theft-of-funds class impact.

### Likelihood Explanation
Exploitation requires the attacker (or a colluding/careless relayer) to be able to get an L1 state commitment accepted that is incorrect and still within its unexpired challenge window — i.e., it depends on a prior fault in the upstream L1 consensus client (BEEFY/GRANDPA/BSC/sync-committee) that hasn't yet been vetoed. This raises the bar above a simple single-transaction exploit, but the missing challenge-period check in the Arbitrum/Optimism consensus clients removes a defense-in-depth layer that is present elsewhere in the codebase (`validate_state_machine`), meaning any transient L1 fault — even one that is later corrected by a fisherman — has a window in which it can be irreversibly propagated into a rollup client's finalized state. Given the multiple, permissionless surfaces (any relayer can pick `l1_height`) and the irreversibility of the resulting commitment once used to dispatch messages, this is a credible Medium/High-likelihood latent issue rather than a purely theoretical one.

### Recommendation
Require that the L1 `StateMachineHeight` referenced by `l1_height` in `ArbitrumConsensusClient::verify_consensus` / `OptimismConsensusClient::verify_consensus` has passed its configured challenge period (mirroring `verify_delay_passed`/`validate_state_machine`) before its `state_root` is used to verify child-chain proofs. Additionally, consider binding the child-chain's stored state commitment lifecycle to the source L1 commitment so that if the L1 commitment is later deleted/vetoed by a fisherman, any L2 commitments derived from it during their still-challengeable window are also invalidated or flagged, rather than remaining a valid, unconditionally-trusted anchor for future message dispatch.

### Proof of Concept
1. An upstream L1 consensus client (e.g. BEEFY on Polkadot, or the BSC/GRANDPA client) accepts a state commitment at height `H` that is subtly incorrect (a known risk class this codebase already defends against via fisherman veto/challenge periods).
2. Before the challenge period for height `H` elapses (i.e., before a fisherman can call `deleteStateMachineCommitment`), a relayer submits a `ConsensusMessage` to the Arbitrum or Optimism consensus client with `l1_height = H` and a rollup proof (`ArbitrumPayloadProof`/`OptimismPayloadProof`) crafted against the (incorrect) `state_root` stored at `H`.
3. `verify_consensus` in `modules/ismp/clients/ismp-arbitrum/src/lib.rs` (or `ismp-optimism`) fetches `host.state_machine_commitment(l1_state_machine_height)` unconditionally — no challenge-period check is performed — and uses its `state_root` to validate the rollup storage proof.
4. If the proof is internally consistent with the (incorrect) L1 root, the L2 `StateCommitment` is accepted and persisted via `update_client`, permanently updating `finalized_height` for the Arbitrum/Optimism state machine.
5. Even if the fisherman subsequently vetoes the original L1 commitment at `H`, the already-derived and stored L2 commitment remains valid and continues to be used by `HandlerV2`/request-handling code to authorize message dispatch (mints, escrow releases) on that L2, with no corrective mechanism.

### Citations

**File:** modules/ismp/clients/ismp-arbitrum/src/lib.rs (L109-125)
```rust
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
```

**File:** modules/ismp/clients/ismp-optimism/src/lib.rs (L160-176)
```rust
		let OptimismUpdate { l1_height, proof } =
			OptimismUpdate::decode(&mut &consensus_proof[..])
				.map_err(|_| OptimismError::DecodeOptimismUpdate)?;

		let mut consensus_state = ConsensusState::decode_tolerant(&trusted_consensus_state)
			.map_err(|_| OptimismError::DecodeConsensusState)?;

		// The state machine being updated is fixed by the trusted consensus state, never
		// supplied by the (untrusted) update. This binds verifier-config selection to the
		// correct OP Stack chain identity.
		let state_machine_id = consensus_state.state_machine_id;

		let l1_state_machine_height =
			StateMachineHeight { id: consensus_state.l1_state_machine_id, height: l1_height };

		let l1_state_commitment = host.state_machine_commitment(l1_state_machine_height)?;
		let state_root = l1_state_commitment.state_root;
```

**File:** modules/ismp/core/src/handlers.rs (L116-147)
```rust
/// This function does the preliminary checks for a request or response message
/// - It ensures the consensus client is not frozen
/// - Checks for frozen state machine is deprecated and malicious state machine commitment will be
///   deleted instead
/// - Checks that the delay period configured for the state machine has elapsed.
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
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L41-80)
```rust
	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
	let timestamp = host.timestamp();
	host.store_consensus_update_time(msg.consensus_state_id, timestamp)?;
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
