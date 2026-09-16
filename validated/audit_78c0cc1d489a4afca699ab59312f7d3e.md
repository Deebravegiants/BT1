### Title
Sync-committee (Ethereum) light client's fraud-proof / equivocation defense is unimplemented, leaving forged consensus updates unfreezable - (File: modules/ismp/clients/sync-committee/src/beacon_client.rs)

### Summary
The Hyperbridge protocol specification documents a mandatory "optimistic bridging" defense: fishermen submit conflicting consensus proofs via `freeze_client`/`FraudProofMessage`, and `ConsensusClient::verify_fraud_proof` must verify both proofs are valid-yet-conflicting so the client can be frozen before any byzantine state commitment is used to process cross-chain messages. This mirrors the zAuction pattern of a specified user flow that was never implemented in the on-chain contracts. For the `SyncCommitteeConsensusClient` (Ethereum), `verify_fraud_proof` is a stub that always returns an error, so `freeze_client` can never succeed for this client, regardless of the fraud evidence submitted.

### Finding Description
The spec defines the `ConsensusClient` trait with `verify_fraud_proof` as a required security mechanism, described in `docs/content/protocol/ismp/consensus.mdx` and `docs/content/protocol/interoperability/consensus-proofs.mdx`: fishermen submit `proof_1`/`proof_2` (two valid but conflicting consensus proofs) and, if verified, `freeze_client` (`modules/ismp/core/src/handlers/consensus.rs`, lines 124-145) freezes the consensus client, which is the only way to stop a byzantine chain's state commitments from being trusted. [1](#0-0) 

For the Ethereum sync-committee client, this defense is not implemented — `verify_fraud_proof` unconditionally returns `SyncCommitteeError::FraudProofUnimplemented`: [2](#0-1) 

This is a deliberate stub, matching the error definition: [3](#0-2) 

By contrast, the BEEFY and GRANDPA consensus clients — which are also validator-signature-based and subject to the same double-signing/eclipse-attack class — do implement `verify_fraud_proof` with full cryptographic verification of conflicting commitments: [4](#0-3) [5](#0-4) 

The sync-committee's 512-validator committee (per `docs/content/protocol/consensus/sync-committee.mdx` and `docs/content/protocol/consensus/casper-ffg.mdx`) has "much lower crypto-economic security" and no slashing, which the spec explicitly calls out as requiring the fraud-proof/freeze mechanism to be functional as a backstop. Since it is unimplemented, this backstop simply does not exist for this client.

### Impact Explanation
If a sufficient subset of the Ethereum sync committee (or an eclipse attacker) produces two conflicting, validly-signed attestations for different beacon-chain views, fishermen have no functioning path to freeze the `SyncCommitteeConsensusClient` via `freeze_client`, since `verify_fraud_proof` always errors before any freeze can occur. `update_client` (`modules/ismp/core/src/handlers/consensus.rs`, lines 29-84) will continue to accept and store new consensus states/state commitments from the byzantine view because `is_consensus_client_frozen` is never satisfied. This allows byzantine state commitments (and derived Ethereum state/storage proofs) to be treated as canonical indefinitely, enabling forged message delivery and unsound state commitments to be relayed cross-chain to Hyperbridge and permissionless token bridging/dispatch paths that trust this consensus client — directly matching the "forged message delivery" / "unsound state commitment" categories called out in the validation rules.

### Likelihood Explanation
Exploitation requires an actual equivocation/eclipse event on the Ethereum sync committee side (or an attacker capable of producing two valid conflicting attestations), which is a non-trivial but realistic threat the spec itself explicitly designs against ("Byzantine Attacks", "Eclipse Attacks" sections of `consensus-proofs.mdx`). The vulnerability is not in the attack's likelihood but in the total absence of the documented mitigating control for this specific client, unlike sibling clients (BEEFY, GRANDPA) where the same class of attack is defended against.

### Recommendation
Implement `verify_fraud_proof` for `SyncCommitteeConsensusClient` following the same pattern as `beefy`/`grandpa`: decode both `BeaconClientUpdate`/attestation proofs, confirm they attest to different/conflicting beacon-chain views at overlapping sync-committee periods, verify both BLS aggregate signatures against the trusted sync committee, and only then permit `freeze_client` to succeed. Until implemented, this should be explicitly flagged in the security model/documentation as an unmitigated risk for the Ethereum light client, and reliance on this client for high-value flows should require an alternate mitigating control (e.g., governance-based emergency freeze, or restricting the client's trust assumptions).

### Proof of Concept
1. An attacker (or a colluding sync-committee majority) produces two validly BLS-signed sync-committee attestations, `update_1` and `update_2`, referencing different, conflicting `finalized_header`s at the same/overlapping sync-committee period.
2. Attacker submits `update_1` as a `ConsensusMessage` to `update_client` (`modules/ismp/core/src/handlers/consensus.rs:29`), which passes `verify_sync_committee_attestation` and stores a new `ConsensusState` plus an Ethereum `StateCommitment` for the forged view.
3. A fisherman detects the equivocation and submits a `FraudProofMessage{proof_1: update_1, proof_2: update_2}` to `freeze_client` (`modules/ismp/core/src/handlers/consensus.rs:124`).
4. `consensus_client.verify_fraud_proof(...)` is dispatched to `SyncCommitteeConsensusClient::verify_fraud_proof` (`modules/ismp/clients/sync-committee/src/beacon_client.rs:140`), which unconditionally returns `Err(SyncCommitteeError::FraudProofUnimplemented)` — the call in `freeze_client` returns early via `?`, so `host.freeze_consensus_client` is never reached.
5. The consensus client remains active; requests/responses proven against the forged `StateCommitment` continue to be accepted by downstream handlers relying on this consensus client's state commitments, with no way for fishermen to stop it.

### Citations

**File:** modules/ismp/core/src/handlers/consensus.rs (L124-145)
```rust
/// Freeze a consensus client by providing a valid fraud proof.
pub fn freeze_client<H>(host: &H, msg: FraudProofMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	let consensus_client_id = host
		.consensus_client_id(msg.consensus_state_id)
		.ok_or_else(|| Error::Custom("Unknown Consensus State Id".to_string()))?;

	host.is_consensus_client_frozen(msg.consensus_state_id)?;

	let consensus_client = host.consensus_client(consensus_client_id)?;
	let trusted_state = host.consensus_state(msg.consensus_state_id)?;

	consensus_client.verify_fraud_proof(host, trusted_state, msg.proof_1, msg.proof_2)?;

	host.freeze_consensus_client(msg.consensus_state_id)?;

	host.store_consensus_update_time(msg.consensus_state_id, host.timestamp())?;

	Ok(MessageResult::FrozenClient(msg.consensus_state_id))
}
```

**File:** modules/ismp/clients/sync-committee/src/beacon_client.rs (L140-148)
```rust
	fn verify_fraud_proof(
		&self,
		_host: &dyn IsmpHost,
		_trusted_consensus_state: Vec<u8>,
		_proof_1: Vec<u8>,
		_proof_2: Vec<u8>,
	) -> Result<(), Error> {
		Err(SyncCommitteeError::FraudProofUnimplemented.into())
	}
```

**File:** modules/consensus/sync-committee/verifier/src/error.rs (L37-39)
```rust
	/// Fraud-proof verification is not implemented for this client.
	#[error("Fraud proof verification unimplemented")]
	FraudProofUnimplemented,
```

**File:** modules/ismp/clients/beefy/src/consensus.rs (L178-222)
```rust
	fn verify_fraud_proof(
		&self,
		_host: &dyn IsmpHost,
		trusted_consensus_state: Vec<u8>,
		proof_1: Vec<u8>,
		proof_2: Vec<u8>,
	) -> Result<(), Error> {
		let consensus_state: ConsensusState =
			codec::Decode::decode(&mut &trusted_consensus_state[..])
				.map_err(|e| BeefyError::DecodeConsensusState(format!("{e:?}")))?;

		let first_proof: MmrProof = codec::Decode::decode(&mut &proof_1[..])
			.map_err(|e| BeefyError::DecodeMmrProof(format!("{e:?}")))?;

		let second_proof: MmrProof = codec::Decode::decode(&mut &proof_2[..])
			.map_err(|e| BeefyError::DecodeMmrProof(format!("{e:?}")))?;

		let first_commitment = &first_proof.signed_commitment.commitment;
		let second_commitment = &second_proof.signed_commitment.commitment;

		if first_commitment.block_number != second_commitment.block_number {
			return Err(BeefyError::FraudProofsDifferentBlock.into());
		}

		if first_commitment.encode() == second_commitment.encode() {
			return Err(BeefyError::FraudProofsIdenticalCommitments.into());
		}

		let empty_parachain_proof =
			ParachainProof { parachains: vec![], proof: vec![], total_leaves: 0 };

		verify_consensus::<SubstrateCrypto>(
			consensus_state.clone(),
			ConsensusMessage { mmr: first_proof, parachain: empty_parachain_proof.clone() },
		)
		.map_err(|e| BeefyError::FraudProofVerificationFailed(format!("first: {e:?}")))?;

		verify_consensus::<SubstrateCrypto>(
			consensus_state,
			ConsensusMessage { mmr: second_proof, parachain: empty_parachain_proof },
		)
		.map_err(|e| BeefyError::FraudProofVerificationFailed(format!("second: {e:?}")))?;

		Ok(())
	}
```

**File:** modules/ismp/clients/grandpa/src/consensus.rs (L264-370)
```rust
	fn verify_fraud_proof(
		&self,
		_host: &dyn IsmpHost,
		trusted_consensus_state: Vec<u8>,
		proof_1: Vec<u8>,
		proof_2: Vec<u8>,
	) -> Result<(), Error> {
		// decode the consensus state
		let consensus_state: ConsensusState =
			codec::Decode::decode(&mut &trusted_consensus_state[..])
				.map_err(|e| GrandpaError::DecodeConsensusState(format!("{e:?}")))?;

		let first_proof: FinalityProof<SubstrateHeader> = codec::Decode::decode(&mut &proof_1[..])
			.map_err(|e| GrandpaError::DecodeFinalityProof(format!("{e:?}")))?;

		let second_proof: FinalityProof<SubstrateHeader> = codec::Decode::decode(&mut &proof_2[..])
			.map_err(|e| GrandpaError::DecodeFinalityProof(format!("{e:?}")))?;

		if first_proof.block == second_proof.block {
			return Err(GrandpaError::FraudProofsSameBlock.into());
		}

		let first_headers = AncestryChain::<SubstrateHeader>::new(&first_proof.unknown_headers);
		let first_target = first_proof
			.unknown_headers
			.iter()
			.max_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;

		let second_headers = AncestryChain::<SubstrateHeader>::new(&second_proof.unknown_headers);
		let second_target = second_proof
			.unknown_headers
			.iter()
			.max_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;

		if first_target.hash() != first_proof.block || second_target.hash() != second_proof.block {
			return Err(GrandpaError::FraudProofsDifferentChain.into());
		}

		let first_base = first_proof
			.unknown_headers
			.iter()
			.min_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;
		let first_chain = first_headers
			.ancestry(first_base.hash(), first_target.hash())
			.map_err(|_| GrandpaError::InvalidAncestry)?;

		let second_base = second_proof
			.unknown_headers
			.iter()
			.min_by_key(|h| *h.number())
			.ok_or(GrandpaError::UnknownHeadersEmpty)?;
		let second_chain = second_headers
			.ancestry(second_base.hash(), second_target.hash())
			.map_err(|_| GrandpaError::InvalidAncestry)?;

		let first_parent = first_base.parent_hash();
		let second_parent = second_base.parent_hash();

		if first_parent != second_parent {
			return Err(GrandpaError::FraudProofsDifferentAncestor.into());
		}

		// Equivocation means two finalized blocks on competing branches. If one
		// target appears in the other's ancestry then they share a canonical
		// chain and this is just ordinary finality moving forward.
		if first_chain.contains(&second_proof.block) ||
			second_chain.contains(&first_proof.block)
		{
			return Err(GrandpaError::FraudProofsSameBranch.into());
		}

		let first_justification =
			GrandpaJustification::<SubstrateHeader>::decode(&mut &first_proof.justification[..])
				.map_err(|e| GrandpaError::DecodeJustification(format!("{e:?}")))?;

		let second_justification =
			GrandpaJustification::<SubstrateHeader>::decode(&mut &second_proof.justification[..])
				.map_err(|e| GrandpaError::DecodeJustification(format!("{e:?}")))?;

		if first_proof.block != first_justification.commit.target_hash ||
			second_proof.block != second_justification.commit.target_hash
		{
			Err(GrandpaError::JustificationTargetMismatch)?
		}

		if first_justification.commit.target_hash != consensus_state.latest_hash &&
			second_justification.commit.target_hash != consensus_state.latest_hash
		{
			Err(GrandpaError::JustificationConsensusMismatch)?
		}

		let first_valid = first_justification
			.verify(consensus_state.current_set_id, &consensus_state.current_authorities)
			.is_ok();
		let second_valid = second_justification
			.verify(consensus_state.current_set_id, &consensus_state.current_authorities)
			.is_ok();

		if !first_valid || !second_valid {
			Err(GrandpaError::InvalidJustification)?
		}

		Ok(())
	}
```
