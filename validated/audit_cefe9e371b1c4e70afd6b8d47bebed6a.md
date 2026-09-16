### Title
Unbounded ECDSA signature count in BEEFY naive consensus proofs allows CPU-cost/weight-charge mismatch DoS - ([File: modules/consensus/beefy/verifier/src/lib.rs])

### Summary
The BEEFY "naive" (ECDSA) consensus-proof verifier accepts a signature list of arbitrary length and only enforces a **lower bound** ("at least supermajority") on it, never an **upper bound**. Every entry in that list triggers a `secp256k1_recover` (an expensive cryptographic operation), analogous to the CVE-2017-14059 pattern where an attacker-controlled count field drives an unbounded loop of expensive work with no check relating the claimed/possible length to real cost. On the Substrate side this proof is submitted through a normal signed extrinsic whose weight is benchmarked only for the *SP1* (single zk-proof) worst case, not for the ECDSA/naive path with a variable number of `secp256k1_recover` calls.

### Finding Description
`verify_mmr_update_proof` in `modules/consensus/beefy/verifier/src/lib.rs` (lines 105-187) does:
```
let signatures_length = mmr.signed_commitment.signatures.len();
...
if !check_participation_threshold(signatures_length as u32, authority_set.len) {
    return Err(Error::SuperMajorityRequired);
}
...
for sig in mmr.signed_commitment.signatures.iter() {
    let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)...
    ...
}
``` [1](#0-0) 

`check_participation_threshold` only checks `len >= (2*total)/3 + 1`: [2](#0-1) 

There is no corresponding check that `signatures_length <= authority_set.len` (or any sane maximum), so a submitted proof can list far more "votes" than the authority set actually has members — each one still costs a full `secp256k1_recover` before the (later) merkle multi-proof membership check can reject it. The identical unbounded pattern exists on the EVM side in `EcdsaBeefy.sol::verifyMmrUpdateProof`, which loops `for (uint256 i = 0; i < sigLen; i++) { ECDSA.recover(...) }` after only a lower-bound `checkParticipationThreshold` check: [3](#0-2) 

On the parachain side, this proof is submitted via `pallet_beefy_consensus_proofs::submit_proof`, a *signed* extrinsic bounded only by total byte size (`BoundedVec<u8, T::MaxProofSize>`), not by signature count: [4](#0-3) 

Crucially, the pallet's own benchmarking documentation states the weight for `submit_proof` is derived **only from the single-SP1-verification worst case**, explicitly bypassing the cryptographic cost of the naive/ECDSA path: [5](#0-4) [6](#0-5) 

So a `PROOF_TYPE_NAIVE` submission with an inflated `signed_commitment.votes`/`signatures` array (as many entries as fit inside `MaxProofSize` bytes) causes the runtime to perform many `secp256k1_recover` calls while only being charged the flat weight benchmarked for the cheap SP1 short-circuit path — the same "claimed length not bound-checked against the real cost of processing it" defect as CVE-2017-14059's missing EOF check driving unbounded work from an attacker-supplied length field.

### Impact Explanation
An attacker who can submit a `submit_proof` extrinsic (or a naive `verify()` call to `EcdsaBeefy.sol` on the EVM side, or any relayer submitting a message through the BEEFY-consensus route) can craft a proof whose signature array is much larger than the actual authority set while still passing the ratio-only `checkParticipationThreshold`. This causes each processing node/relayer to burn CPU on a disproportionate number of `secp256k1_recover`/`ECDSA.recover` operations relative to what was paid for (weight-metered on Substrate, gas-metered but underestimated relative to attacker cost/benefit ratio on EVM if `MaxProofSize`/vote array is not properly capped), degrading block-production time for the parachain and potentially causing legitimate consensus/message-delivery proofs to be starved — a "route unable to deliver messages" condition under sustained abuse.

### Likelihood Explanation
Requires only a signed account able to call `submit_proof` (any funded account) with a crafted `PROOF_TYPE_NAIVE` payload, or any address invoking `EcdsaBeefy.verify` with an oversized `votes` array. No special privilege is needed. The severity of the resulting DoS is directly proportional to `T::MaxProofSize` and how many spurious 65-byte-signature entries can be packed into it — I was not able to confirm the exact configured value of `MaxProofSize` in the running parachain runtimes (`parachain/runtimes/gargantua/src/lib.rs`, `parachain/runtimes/nexus/src/lib.rs`) within this session, so the concrete magnitude of the attack (how many recoveries can be forced per submission) is unverified and should be checked before treating this as confirmed-exploitable at scale.

### Recommendation
Add an explicit upper bound on `signatures_length`/`sigLen` — e.g., reject any signature list longer than `authority_set.len` — in both `modules/consensus/beefy/verifier/src/lib.rs::verify_mmr_update_proof` and `evm/src/consensus/EcdsaBeefy.sol::verifyMmrUpdateProof`, mirroring the existing bit-set bound-checks already used elsewhere in the codebase (e.g. the BSC and sync-committee verifiers reject bits beyond validator count). Additionally, benchmark `pallet_beefy_consensus_proofs::submit_proof`'s naive/ECDSA path against its true worst case (maximum signatures permitted by `MaxProofSize`) so the extrinsic's weight scales with the actual number of `secp256k1_recover` calls performed, rather than assuming the cheap SP1 short-circuit cost for all proof types.

### Proof of Concept
1. Craft a `RelayChainProof`/`ConsensusMessage` whose `signed_commitment.signatures` (`votes` in the Solidity `BeefyConsensusProof`) contains as many 65-byte ECDSA signature entries as fit within `T::MaxProofSize` (or the equivalent EVM calldata budget), each with an arbitrary `authorityIndex`, while keeping the ratio `len >= 2/3*total_authorities + 1` satisfied (e.g., duplicate legitimate indices or pad with junk indices that will only be rejected later by the merkle multi-proof check).
2. Submit via `pallet_beefy_consensus_proofs::submit_proof` (`PROOF_TYPE_NAIVE`) as any signed account, or call `EcdsaBeefy.verify` directly on EVM.
3. Observe that `verify_mmr_update_proof`/`verifyMmrUpdateProof` performs one `secp256k1_recover`/`ECDSA.recover` per entry before eventually failing the merkle multi-proof membership check — i.e., full attacker-controlled-length CPU cost is paid regardless of the proof's ultimate validity, while the extrinsic is charged the flat weight benchmarked only for the cheap SP1 stale-height short-circuit.

### Citations

**File:** modules/consensus/beefy/verifier/src/lib.rs (L105-162)
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

	let commitment = mmr.signed_commitment.commitment.clone();

	// Pick the authority set the commitment claims to be signed under, then judge
	// participation against that set alone.
	let authority_set = if commitment.validator_set_id == trusted_state.current_authorities.id {
		&trusted_state.current_authorities
	} else if commitment.validator_set_id == trusted_state.next_authorities.id {
		&trusted_state.next_authorities
	} else {
		return Err(Error::UnknownAuthoritySet { id: commitment.validator_set_id });
	};

	if !check_participation_threshold(signatures_length as u32, authority_set.len) {
		return Err(Error::SuperMajorityRequired);
	}

	let mmr_root_data = commitment
		.payload
		.get_raw(&MMR_ROOT_PAYLOAD_ID)
		.ok_or(Error::MmrRootHashMissing)?;

	if mmr_root_data.len() != 32 {
		return Err(Error::InvalidMmrRootHashLength { len: mmr_root_data.len() });
	}
	let mmr_root = H256::from_slice(mmr_root_data);

	let commitment_hash = H::keccak256(&commitment.encode());
	let mut authority_leaves: Vec<[u8; 32]> = Vec::new();
	let mut authority_indices = Vec::new();

	for sig in mmr.signed_commitment.signatures.iter() {
		let uncompressed = H::secp256k1_recover(&commitment_hash.0, &sig.signature)
			.map_err(|_| Error::FailedToRecoverPublicKey)?;

		let hashed_uncompressed = H::keccak256(&uncompressed);

		let mut eth_address = [0u8; 20];
		eth_address.copy_from_slice(&hashed_uncompressed.as_ref()[12..]);

		let authority_address_hash = H::keccak256(&eth_address);

		authority_leaves.push(authority_address_hash.into());
		authority_indices.push(sig.index as usize);
	}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L258-261)
```rust
/// Checks for supermajority participation
fn check_participation_threshold(len: u32, total: u32) -> bool {
	len >= ((2 * total) / 3) + 1
}
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L122-163)
```text
    function verifyMmrUpdateProof(BeefyConsensusState memory trustedState, RelayChainProof memory relayProof)
        internal
        pure
        returns (BeefyConsensusState memory, bytes32)
    {
        uint256 sigLen = relayProof.signedCommitment.votes.length;
        uint256 latestHeight = relayProof.signedCommitment.commitment.blockNumber;
        Commitment memory commitment = relayProof.signedCommitment.commitment;
        if (
            commitment.validatorSetId != trustedState.currentAuthoritySet.id
                && commitment.validatorSetId != trustedState.nextAuthoritySet.id
        ) {
            revert UnknownAuthoritySet();
        }

        bool isCurrentAuthorities = commitment.validatorSetId == trustedState.currentAuthoritySet.id;
        AuthoritySetCommitment memory authoritySet =
            isCurrentAuthorities ? trustedState.currentAuthoritySet : trustedState.nextAuthoritySet;
        if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();

        uint256 payloadLength = commitment.payload.length;
        bytes32 mmrRoot;
        for (uint256 i = 0; i < payloadLength; i++) {
            if (commitment.payload[i].id == MMR_ROOT_PAYLOAD_ID && commitment.payload[i].data.length == 32) {
                mmrRoot = Bytes.toBytes32(commitment.payload[i].data);
            }
        }
        if (mmrRoot == bytes32(0)) revert MmrRootHashMissing();

        // verify the commitment
        bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
        MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
        for (uint256 i = 0; i < sigLen; i++) {
            Vote memory vote = relayProof.signedCommitment.votes[i];
            address authority = ECDSA.recover(commitmentHash, vote.signature);
            authorities[i] =
                MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
        }

        bool valid = MerkleMultiProof.VerifyProof(authoritySet.root, relayProof.proof, authorities, authoritySet.len);
        if (!valid) revert InvalidAuthoritiesProof();

```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L360-374)
```rust
		/// Submit a BEEFY consensus proof. Signed: the signer is the reward payee.
		///
		/// `proof` is a `BoundedVec` so SCALE decoding rejects oversized payloads inside
		/// the txpool, before the runtime ever pays for the call. Successful proofs
		/// (first or uncle) refund their transaction fee via `Pays::No`; failed proofs
		/// pay the fee, which is the spam deterrent.
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::submit_proof())]
		pub fn submit_proof(
			origin: OriginFor<T>,
			proof: BoundedVec<u8, T::MaxProofSize>,
		) -> DispatchResultWithPostInfo {
			let submitter = ensure_signed(origin)?;
			Self::do_submit_proof(submitter, proof.into_inner())
		}
```

**File:** modules/pallets/beefy-consensus-proofs/src/benchmarking.rs (L57-66)
```rust
	/// Benches the uncle path of `submit_proof` along the single-SP1 worst case. Setup
	/// seeds the live consensus state with `latest_beefy_height` equal to the fixture
	/// proof's `blockNumber`. When dispatch reaches `BeefyConsensusClient::verify_consensus`,
	/// the inner SP1 verifier's own stale check (`beefy_verifier::error::Error::StaleHeight`)
	/// returns immediately — before any cryptographic work — and the pallet maps that to
	/// `StaleProof`. Dispatch then routes to `settle_uncle_proof`, which runs
	/// `verify_sp1_consensus` exactly once against the pre-seeded snapshot in
	/// `ProofContext`. The resulting weight covers one SP1 verification plus uncle storage
	/// writes — also the right bound for the first-proof path, which runs SP1 once inside
	/// `verify_and_apply`.
```

**File:** parachain/runtimes/gargantua/src/weights/pallet_beefy_consensus_proofs.rs (L52-59)
```rust
/// Weight functions for `pallet_beefy_consensus_proofs`.
///
/// `submit_proof` is benchmarked along the single-SP1-verification worst case: the live
/// consensus state is seeded so that when `verify_and_apply` calls
/// `BeefyConsensusClient::verify_consensus`, the inner SP1 verifier returns
/// `StaleHeight` *before* doing any cryptographic work. The pallet maps that error to
/// `StaleProof`, dispatch routes to `settle_uncle_proof`, and SP1 runs once there
/// against the pre-seeded snapshot. This bounds both the uncle path (single SP1 +
```
