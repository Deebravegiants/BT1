Confirmed reachable path: `pallet-beefy-consensus-proofs::submit_proof` (signed extrinsic, `PROOF_TYPE_NAIVE`) decodes an attacker-supplied ABI blob into `ismp_abi::ecdsa_beefy::BeefyConsensusProof` and converts it into `beefy_verifier_primitives::ConsensusMessage`, which walks each `Vote` in `signedCommitment.votes` through `From<Vote> for SignatureWithAuthorityIndex` [1](#0-0) . That conversion copies the ABI `bytes` signature field into a fixed `[u8; 65]` with no length check before `copy_from_slice`, matching the CVE's unchecked-length memmove/segfault class (there it's `MP4Box`'s `memmove_avx_unaligned_erms`; here it's `copy_from_slice` into a fixed-size buffer without validating source length).

### Title
Unchecked-length `copy_from_slice` panic in BEEFY Vote-to-signature conversion causes DoS on `submit_proof` - (File: evm/rust/src/conversions.rs)

### Summary
`From<Vote> for SignatureWithAuthorityIndex` copies an attacker-controlled, arbitrary-length ABI `bytes` field into a fixed `[u8; 65]` array via `copy_from_slice` without first checking that the source length equals 65, causing a Rust panic ("source slice length does not match destination") whenever the length differs.

### Finding Description
`SolBeefyConsensusProof`/`Vote.signature` is decoded from an untrusted `abi_payload` at `modules/pallets/beefy-consensus-proofs/src/lib.rs:820-838` inside `verify_and_apply`, which is reached by any signed account calling the `submit_proof` extrinsic with `PROOF_TYPE_NAIVE` (`modules/pallets/beefy-consensus-proofs/src/lib.rs:368-374`, `448-514`). The resulting `BeefyConsensusProof` (Solidity ABI type) is converted `.into()` a SCALE `ConsensusMessage`, which for every vote in `signedCommitment.votes` calls:

```
impl From<Vote> for SignatureWithAuthorityIndex {
    fn from(value: Vote) -> Self {
        let sig_bytes = value.signature.to_vec();
        let mut signature: TSignature = [0u8; 65];
        signature.copy_from_slice(&sig_bytes);   // panics unless sig_bytes.len() == 65
        ...
``` [2](#0-1) 

Because `signature` is Solidity `bytes` (ABI dynamic bytes, arbitrary length, fully controlled by the caller's ABI-encoded calldata), a malformed proof with a `Vote.signature` field whose length is not exactly 65 bytes will panic inside `copy_from_slice`, not return a typed error. Everywhere else in this same file, similarly risky conversions (`try_into().expect(...)`) at least document/accept the possibility of failure via `expect`, but this call site skips even that guard rail and uses a raw `copy_from_slice`, which is a hard panic regardless of `expect`/`Result` handling patterns used elsewhere in the module.

This is directly analogous to CVE-2021-46313: an unvalidated length is used to drive an unconditional memory copy (`memmove`/`copy_from_slice`) into a fixed-size buffer, and the length comes straight from untrusted input.

### Impact Explanation
A panic during dispatch of a signed, fee-paying extrinsic (`submit_proof`) inside a FRAME pallet extrinsic execution context typically aborts the transaction (handled by the runtime's panic-catching wasm executor) rather than crashing the whole node process in most cases, but if this code path is also exercised by tesseract relayer/prover client-side Rust binaries or off-chain workers that call these conversions without a panic-catching boundary (e.g., relayer processes building/validating BEEFY proofs, or SP1/relayer helper binaries linking `evm/rust`), it can crash that process entirely — a genuine remote Denial of Service against a component that must stay live for message delivery (consensus updates, hence hyperbridge message dispatch, halt if the prover/relayer crashes repeatedly). Even confined to on-chain dispatch, panics inside pallet logic are a correctness/liveness concern since Substrate's expectation is that dispatchables never panic; an uncaught panic during block execution can, depending on executor configuration, force a full node restart or halt block production for that node, degrading availability of the BEEFY consensus-update pipeline that gates message delivery for the entire bridge.

### Likelihood Explanation
High: the trigger requires only a validly ABI-shaped `BeefyConsensusProof` where one `Vote.signature` byte field's length is not exactly 65 bytes — trivial for any account to construct and submit via the public, signed `submit_proof` extrinsic. No special privileges, timing, or cryptographic material are required to reach the vulnerable conversion; the crash happens before any real BEEFY signature/authority verification takes place.

### Recommendation
Before calling `copy_from_slice`, explicitly validate `sig_bytes.len() == 65` and return a typed error (e.g., extend the existing error type or use `try_into().map_err(...)` the same way `bls_public_key.copy_from_slice(...)` should also be hardened in `modules/consensus/bsc/verifier/src/primitives.rs:172`, and the fixed-size conversions elsewhere in this file already use `.try_into().expect(...)`—replace the `expect` panics with proper `Result` propagation as well) instead of an unconditional `copy_from_slice`, so malformed vote signatures are rejected as `AbiDecodeFailed`/`VerificationFailed` rather than panicking.

### Proof of Concept
1. Construct a `BeefyConsensusProof` Solidity struct where `signedCommitment.votes[0].signature` is any `bytes` value whose length is not 65 (e.g., 64 or 66 bytes) — trivially done client-side with `alloy_sol_types`/`abi_encode_params`, no valid signature needed.
2. Prefix the ABI-encoded payload with `PROOF_TYPE_NAIVE` (`0x00`) as in `do_submit_proof`/`verify_and_apply` (`modules/pallets/beefy-consensus-proofs/src/lib.rs:818-838`).
3. Submit as `BeefyConsensusProofs::submit_proof(proof)` from any signed account.
4. Execution reaches `abi_proof.into()` → `ConsensusMessage`, which calls `From<Vote> for SignatureWithAuthorityIndex` and panics at `signature.copy_from_slice(&sig_bytes)` in `evm/rust/src/conversions.rs:360` because `sig_bytes.len() != 65`. [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L805-838)
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
				},
				types::PROOF_TYPE_NAIVE => {
					let abi_proof =
						<ismp_abi::ecdsa_beefy::BeefyConsensusProof as SolType>::abi_decode_params(
							abi_payload,
						)
						.map_err(|_| Error::<T>::AbiDecodeFailed)?;
					let scale_proof: beefy_verifier_primitives::ConsensusMessage = abi_proof.into();
					[&[types::PROOF_TYPE_NAIVE], scale_proof.encode().as_slice()].concat()
				},
				_ => Err(Error::<T>::UnknownProofType)?,
			};
```

**File:** evm/rust/src/conversions.rs (L356-366)
```rust
	impl From<Vote> for SignatureWithAuthorityIndex {
		fn from(value: Vote) -> Self {
			let sig_bytes = value.signature.to_vec();
			let mut signature: TSignature = [0u8; 65];
			signature.copy_from_slice(&sig_bytes);
			SignatureWithAuthorityIndex {
				signature,
				index: value.authorityIndex.try_into().expect("authority index out of bounds"),
			}
		}
	}
```
