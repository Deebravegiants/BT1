## Title
Fraud-proof mechanism cannot detect or freeze a "forward lunatic"-style consensus fork because `verify_fraud_proof` only recognizes equivocation at an identical block height - (File: `modules/ismp/clients/tendermint/src/lib.rs`)

### Summary
The Tendermint/CometBFT-based consensus clients in Hyperbridge (`ismp-tendermint`, `ismp-polygon`) implement Byzantine-fault detection ("fishermen"/fraud-proof model, per `docs/content/protocol/interoperability/consensus-proofs.mdx`) purely as a same-height equivocation check. This mirrors the root cause behind GHSA-f3w5-v9xx-rp8p/GHSA-jqfc-687g-59pw ("forward lunatic attack", FLA): a light client can accept and commit to a header for a block height that has not yet been produced by the honest chain, and there is no mechanism to later form evidence of the deception because evidence-formation here requires a second conflicting proof at the *same* height.

### Finding Description
`verify_header_update` in `modules/consensus/tendermint/verifier/src/verifier.rs` only checks that the submitted `SignedHeader` carries ≥ trust-threshold voting power from the trusted validator set and passes cometbft's `PredicateVerifier::verify_update_header`. There is no bound requiring the target height to be adjacent to, or bounded relative to, the chain's real progress rate — a validator set that meets the voting-power threshold can sign a header for an arbitrarily large future height with an attacker-chosen `app_hash`. [1](#0-0) 

Once accepted, `create_updated_trusted_state` unconditionally adopts this header's height, timestamp, and `app_hash`-derived state root as the new trusted state and promotes `next_validators` for the next round of verification: [2](#0-1) 

This flows directly into the ISMP consensus client `verify_consensus`, which persists the forged `app_hash` as the new `StateCommitment.state_root` for the tracked EVM state machine: [3](#0-2) 

The only remediation path available to fishermen is `freeze_client` → `verify_fraud_proof`, which explicitly requires **both submitted proofs to be for the same block height**: [4](#0-3) 

The identical restriction exists in the Polygon/Heimdall client: [5](#0-4) 

`freeze_client` in the ISMP core handler has no alternate path for a witness-based or time-based cross-check; it only ever calls `verify_fraud_proof` with the two proofs supplied by the caller: [6](#0-5) 

In a forward lunatic attack, the malicious header targets a height the honest chain has not reached yet (potentially arbitrarily far in the future, or a height number engineered so the honest chain will never coincide with it, e.g. right before a halt). Because `verify_fraud_proof` demands `height_1 == height_2`, fishermen cannot produce a valid fraud proof until (if ever) the honest chain organically produces a block at that exact height — which may never happen for an attacker-chosen arbitrary height, defeating the entire "optimistic bridging" safety story documented for this codebase: [7](#0-6) 

### Impact Explanation
Once the forged consensus update is committed, the new `StateCommitment.state_root` (attacker-chosen `app_hash`) becomes the basis for all subsequent ISMP state proofs on that state machine. An attacker can then construct forged Merkle state-membership proofs against this fabricated root and drive `handle_request`/`handle_response` in the ISMP handler to mint unbacked tokens, deliver forged cross-chain messages, or otherwise take unauthorized app actions. Because the only slashing/veto mechanism (`freeze_client`) cannot construct evidence across different heights, the forged commitment cannot be frozen or rolled back through the documented fisherman process, resulting in an unsound state commitment that is effectively permanent and enables unbacked mint / forged message delivery with no on-chain recourse.

### Likelihood Explanation
Exploitation requires the tracked Tendermint-based chain's active validator set to reach the trust threshold (≥ configured fraction, default 2/3) of malicious/colluding voting power — the same precondition acknowledged as "outside Tendermint's security model" in the original advisory. Given that precondition, the exploit path is a single crafted consensus proof submitted through the ordinary `update_client`/`verify_consensus` path (no additional privilege needed by the relayer submitting it), and the resulting damage is unrecoverable by the "fishermen" freeze mechanism as implemented, unlike genuine same-height double-signing which is explicitly detectable today.

### Recommendation
- Extend the misbehavior/fraud-proof evidence model beyond strict same-height equivocation: allow evidence based on a header whose height is *ahead of* the current chain's real progress combined with a timestamp/time-based check (mirroring the FetchBlock time addition in Tendermint Core v0.34.9), so a forward header can be challenged once the honest chain catches up to, or exceeds, the disputed height with a divergent header.
- Alternatively, bound the maximum height jump allowed in a single `verify_header_update` call relative to elapsed real time (host timestamp vs. header timestamp) so that headers claiming implausibly large height jumps are rejected outright rather than accepted and only contestable via an unreachable same-height fraud proof.
- Ensure `verify_misbehaviour_header` (already implemented but unused in the fraud-proof path) or an equivalent relaxed-height verification is actually wired into `verify_fraud_proof`/`freeze_client` so cross-height evidence can be evaluated.

### Proof of Concept
1. Assume the tracked chain's active validator set (≥ trust threshold voting power) is compromised/colluding.
2. Attacker crafts a `SignedHeader` for height `H_future` (far beyond the chain's current real height) with an arbitrary `app_hash`, signed by the compromised validator set, and wraps it as a `TendermintConsensusUpdate`/`ConsensusMessage`.
3. Relayer submits this via `update_client`, which calls `TendermintClient::verify_consensus` → `tendermint_verifier::verify_header_update`; voting-power/threshold checks pass, so the forged `app_hash` is committed as the new `StateCommitment.state_root` at height `H_future` (`modules/ismp/clients/tendermint/src/lib.rs:98-120`).
4. Attacker uses the forged root to build a fabricated Merkle membership proof, driving `handle_request`/`handle_response` to mint tokens or deliver a forged message.
5. A fisherman attempts to submit competing evidence via `freeze_client`, but cannot, because no honest header exists yet at height `H_future` (or never will, for an attacker-chosen height); `verify_fraud_proof` immediately rejects any proof pair whose heights differ (`modules/ismp/clients/tendermint/src/lib.rs:161-165`), leaving the forged state commitment un-freezable and permanent.

### Citations

**File:** modules/consensus/tendermint/verifier/src/verifier.rs (L20-35)
```rust
/// Main verification function for header updates
pub fn verify_header_update(
	trusted_state: TrustedState,
	consensus_proof: ConsensusProof,
	current_time: u64,
) -> Result<UpdatedTrustedState, VerificationError> {
	consensus_proof.validate().map_err(|e| VerificationError::Invalid(e))?;

	let chain_id = Id::try_from(trusted_state.chain_id.clone())
		.map_err(|e| VerificationError::Invalid(e.to_string()))?;
	let height = Height::try_from(trusted_state.height)
		.map_err(|e| VerificationError::Invalid(e.to_string()))?;
	let timestamp = Timestamp { seconds: trusted_state.timestamp as i64, nanos: 0 };
	let time = Time::try_from(timestamp).map_err(|e| VerificationError::Invalid(e.to_string()))?;
	let next_validators = ValidatorSet::new(trusted_state.next_validators.clone(), None);
	let next_validators_hash = Hash::Sha256(trusted_state.next_validators_hash);
```

**File:** modules/consensus/tendermint/verifier/src/verifier.rs (L274-294)
```rust
	let new_trusted_state =
		TrustedState {
			chain_id: consensus_proof.chain_id().to_string(),
			height: consensus_proof.height(),
			timestamp: consensus_proof.timestamp(),
			validators,
			next_validators,
			next_validators_hash,
			trusting_period: old_trusted_state.trusting_period,
			verification_options: old_trusted_state.verification_options.clone(),
			finalized_header_hash: header.hash().as_bytes().try_into().map_err(|_| {
				VerificationError::Invalid("Invalid finalized_header_hash".to_string())
			})?,
		};

	Ok(UpdatedTrustedState::new(
		new_trusted_state,
		consensus_proof.height(),
		consensus_proof.timestamp(),
	))
}
```

**File:** modules/ismp/clients/tendermint/src/lib.rs (L98-120)
```rust
		let updated_state = verify_header_update(trusted_state, consensus_proof.clone(), time)
			.map_err(|e| ismp::error::Error::Custom(e.to_string()))?;

		let mut state_machine_map: BTreeMap<StateMachineId, Vec<StateCommitmentHeight>> =
			BTreeMap::new();
		let mut updated_consensus_state = consensus_state.clone();

		let app_hash: [u8; 32] = consensus_proof
			.signed_header
			.header
			.app_hash
			.as_bytes()
			.try_into()
			.map_err(|_| Error::Custom("Invalid app hash length".to_string()))?;

		let state_commitment = StateCommitmentHeight {
			commitment: StateCommitment {
				timestamp: updated_state.verified_timestamp,
				overlay_root: None,
				state_root: primitive_types::H256(app_hash),
			},
			height: updated_state.trusted_state.height,
		};
```

**File:** modules/ismp/clients/tendermint/src/lib.rs (L161-179)
```rust
		let height_1 = consensus_proof_1.signed_header.header.height;
		let height_2 = consensus_proof_2.signed_header.header.height;
		if height_1 != height_2 {
			return Err(Error::Custom("Fraud proofs must be for the same block height".to_string()));
		}

		// A genuine fraud proof must demonstrate equivocation: two *distinct* blocks
		// signed by the validator set at the same height. Comparing the raw proof
		// bytes is insufficient — SCALE's `Decode` silently ignores trailing bytes
		// and other non-canonical encodings, so an attacker could submit the *same*
		// header twice with one copy malleated (e.g. an appended trailing byte or
		// reordered commit signatures), pass this byte-inequality check, and freeze
		// a live consensus client permissionlessly. Compare the canonical Tendermint
		// header hashes instead — they uniquely identify the block being committed.
		if consensus_proof_1.signed_header.header.hash() ==
			consensus_proof_2.signed_header.header.hash()
		{
			return Err(Error::Custom("Fraud proofs commit to the same block header".to_string()));
		}
```

**File:** modules/ismp/clients/polygon/src/lib.rs (L365-383)
```rust
		let height_1 = consensus_proof_1.signed_header.header.height;
		let height_2 = consensus_proof_2.signed_header.header.height;
		if height_1 != height_2 {
			return Err(PolygonError::FraudProofsDifferentHeight.into());
		}

		// A genuine fraud proof must demonstrate equivocation: two *distinct* blocks
		// signed by the validator set at the same height. Comparing the raw proof
		// bytes is insufficient — SCALE's `Decode` silently ignores trailing bytes
		// and other non-canonical encodings, so an attacker could submit the *same*
		// header twice with one copy malleated (e.g. an appended trailing byte or
		// reordered commit signatures), pass this byte-inequality check, and freeze
		// a live consensus client permissionlessly. Compare the canonical Tendermint
		// header hashes instead — they uniquely identify the block being committed.
		let header_hash_1 = consensus_proof_1.signed_header.header.hash();
		let header_hash_2 = consensus_proof_2.signed_header.header.hash();
		if header_hash_1 == header_hash_2 {
			return Err(PolygonError::FraudProofsIdentical.into());
		}
```

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

**File:** docs/content/protocol/interoperability/consensus-proofs.mdx (L140-146)
```text
To prevent the damage that can be done to our bridge in the event of a byzantine attack, **we must introduce a challenge window in the form of a time delay between when consensus proofs are verified by our consensus client and when state proofs associated with those headers can be used to process cross-chain messages.**

During this challenge window, consensus clients can detect byzantine attacks. Off-chain consensus clients can do this by participating in the P2P network. On-chain consensus clients, on the other hand, will need to rely on off-chain parties, which we'll call fishermen<sup>[3]</sup>, to provide the proofs of fraud to the client.

These fishermen will need some incentive to watch for byzantine attacks and report the fraud proofs which will safeguard the consensus client. As such, we will require relayers who submit consensus proofs to be staked, in the event of byzantine attacks, relayer’s stake can be used to incentivise fishermen to submit fraud proofs.

In the event of a byzantine attack, the fraud proofs will allow for the consensus client to go into a frozen state until the source chain recovers from this byzantine state, **The host chain can then unfreeze the consensus client through some kind of on-chain governance, allowing the bridge to resume operations safely and without any loss of funds ever having occurred.**
```
