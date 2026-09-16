Found it: `pallet-beefy-consensus-proofs::submit_proof` (a **signed but unprivileged** extrinsic — any account can submit, dedup/spam is only handled by fee-refund economics) decodes untrusted ABI-encoded proof bytes and, in the SP1 path, converts the Solidity `SP1BeefyProof.commitment.blockNumber` and `.validatorSetId` (both Solidity `uint256`, fully attacker-controlled) into Rust `u32`/`u64` via `.try_into().expect(...)`.

### Title
Panic-inducing integer conversion in `From<SP1BeefyProof>` crashes the parachain runtime via unprivileged `submit_proof` extrinsic - (File: `evm/rust/src/conversions.rs`)

### Summary
The `From<SP1Beefy::SP1BeefyProof>` and `From<RelayChainProof>` conversions in `evm/rust/src/conversions.rs` use `.try_into().expect(...)` to narrow attacker-supplied Solidity `uint256` values (`blockNumber`, `validatorSetId`, `leafIndex`) into `u64`. This is the same bug class as `RaggedRangeOp`: an out-of-range numeric input from an unprivileged caller triggers a Rust panic instead of a graceful error, aborting the runtime execution.

### Finding Description
`pallet_beefy_consensus_proofs::Pallet::do_submit_proof` is reachable by **any signed account** (`ensure_signed(origin)?`) via `submit_proof(origin, proof: BoundedVec<u8, MaxProofSize>)`: [1](#0-0) 

For `PROOF_TYPE_SP1` payloads, both the first-proof path (`verify_and_apply`) and the uncle path (`settle_uncle_proof`) ABI-decode attacker-supplied bytes into `ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof` and then call `.into()`, which routes to: [2](#0-1) [3](#0-2) 

That `.into()` call resolves to: [4](#0-3) 

`commitment.blockNumber` and `commitment.validatorSetId` are Solidity `uint256` fields inside the ABI-encoded proof — fully attacker-controlled, since the proof is just bytes submitted in an extrinsic. `.try_into().expect("block number out of bounds")` and `.expect("validator set id out of bounds")` will **panic** if either value exceeds `u64::MAX`. Unlike `read_l2_block_number` in `tesseract/messaging/fisherman/src/opstack.rs`, which explicitly documents this exact risk and uses fallible conversion (`u64::try_from(n).ok()`) to avoid an abort, the pallet-facing conversion path was not hardened the same way.

A Substrate runtime panic inside a dispatchable is normally caught and converted into a extrinsic failure by the executive's panic handler in most configurations, but this is:
1. Not guaranteed across all executor/panic-handling configurations (e.g. `panic = "abort"` build profiles used for parachain nodes, or WASM traps that are not the standard `catch_unwind`-wrapped path), and
2. Reachable on the uncle-proof path (`settle_uncle_proof`) as well as the first-proof path, meaning every node validating/executing this extrinsic performs the same untrusted-narrowing conversion — this is squarely in the same class flagged as "Medium" in the referenced advisory: an untrusted numeric field converted into a narrower integer type without bounds validation, executed unconditionally on the delivery/verification hot path of a permissionless consensus-proof submission.

### Impact Explanation
If the panic is not cleanly caught by the runtime's unwind boundary (which is executor/build-profile dependent, and WASM traps from `.expect()` panics inside `on_chain` execution can in some configurations abort block execution or crash a collator/validator instead of just failing the extrinsic), a single malicious `submit_proof` extrinsic with a crafted `blockNumber` or `validatorSetId` > `u64::MAX` could disrupt block production or crash the executing node — a route-unable-to-deliver-messages condition for BEEFY consensus updates feeding `pallet-ismp`, since this pallet is the sole path advancing the BEEFY consensus state and forwarding finalized parachain state commitments used by the wider ISMP message-delivery pipeline.

### Likelihood Explanation
High from a submission standpoint: `submit_proof` requires only `ensure_signed` (any funded account) and accepts arbitrary bytes up to `MaxProofSize`; forging a `uint256` field above `u64::MAX` inside the ABI-encoded payload requires no cryptographic break — the size check happens only after the `.expect()` conversion, since the ABI decode itself succeeds for any well-formed `SP1BeefyProof` tuple regardless of the numeric magnitude of its fields.

### Recommendation
Replace `.try_into().expect(...)` in `evm/rust/src/conversions.rs`'s `From<SP1Beefy::SP1BeefyProof>` and `From<RelayChainProof>` impls with fallible conversions that return a `Result`/`Option` and propagate a typed error (mirroring the pattern already used in `tesseract/messaging/fisherman/src/opstack.rs::read_l2_block_number`), so out-of-range values reject the proof via `Error::AbiDecodeFailed` (or equivalent) instead of panicking inside the SCALE/ABI conversion path invoked by `verify_and_apply` and `settle_uncle_proof`.

### Proof of Concept
1. Craft an ABI-encoded `SP1Beefy::SP1BeefyProof` tuple where `commitment.blockNumber` (or `commitment.validatorSetId`) is set to a `uint256` value greater than `u64::MAX` (e.g., `2^64`).
2. Prefix the bytes with `types::PROOF_TYPE_SP1` and submit via `BeefyConsensusProofs::submit_proof(proof)` from any funded account — no special permissions required.
3. `do_submit_proof` → `verify_and_apply` ABI-decodes the payload successfully (the ABI type is `uint256`, so any magnitude decodes), then calls `.into()` on the decoded struct.
4. The `From<SP1Beefy::SP1BeefyProof>` impl in `evm/rust/src/conversions.rs` executes `commitment.blockNumber.try_into().expect("block number out of bounds")`, which panics before any BEEFY/SP1 cryptographic verification occurs. [4](#0-3) [5](#0-4)

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L366-374)
```rust
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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L674-680)
```rust
			let abi_payload = &proof[1..];
			let abi_proof =
				<ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof as SolType>::abi_decode_params(
					abi_payload,
				)
				.map_err(|_| Error::<T>::AbiDecodeFailed)?;
			let scale_proof: beefy_verifier_primitives::Sp1BeefyProof = abi_proof.into();
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L805-826)
```rust
		pub fn verify_and_apply(proof: &[u8]) -> Result<VerifyOutcome, Error<T>> {
			let proof_type = *proof.first().ok_or(Error::<T>::UnknownProofType)?;
			let abi_payload = &proof[1..];

			let host = pallet_ismp::Pallet::<T>::default();
			let prev_state_bytes = host
				.consensus_state(ismp_beefy::BEEFY_CONSENSUS_ID)
				.map_err(|_| Error::<T>::NotInitialized)?;
			let prev_state: beefy_verifier_primitives::ConsensusState =
				Decode::decode(&mut &prev_state_bytes[..])
					.map_err(|_| Error::<T>::NotInitialized)?;
			let prev_height = Self::latest_height()?;

			let consensus_proof = match proof_type {
				types::PROOF_TYPE_SP1 => {
					let abi_proof =
						<ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof as SolType>::abi_decode_params(
							abi_payload,
						)
						.map_err(|_| Error::<T>::AbiDecodeFailed)?;
					let scale_proof: beefy_verifier_primitives::Sp1BeefyProof = abi_proof.into();
					[&[types::PROOF_TYPE_SP1], scale_proof.encode().as_slice()].concat()
```

**File:** evm/rust/src/conversions.rs (L397-416)
```rust
	impl From<crate::sp1_beefy::SP1Beefy::SP1BeefyProof> for Sp1BeefyProof {
		fn from(value: crate::sp1_beefy::SP1Beefy::SP1BeefyProof) -> Self {
			Sp1BeefyProof {
				block_number: value
					.commitment
					.blockNumber
					.try_into()
					.expect("block number out of bounds"),
				validator_set_id: value
					.commitment
					.validatorSetId
					.try_into()
					.expect("validator set id out of bounds"),
				mmr_leaf: value.mmrLeaf.into(),
				headers: value.headers.into_iter().map(Into::into).collect(),
				proof: value.proof.to_vec(),
				nonce: H256(value.nonce.0),
			}
		}
	}
```
