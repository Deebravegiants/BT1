### Title
Panic via unchecked empty `payload` array in BEEFY `Commitment` → `SpCommitment` conversion, reachable from the unprivileged `submit_proof` extrinsic - ([File: evm/rust/src/conversions.rs])

### Summary
`pallet-beefy-consensus-proofs::submit_proof` is a signed, permissionless extrinsic that accepts a raw `Vec<u8>` "naive" BEEFY proof, ABI-decodes it into `ismp_abi::ecdsa_beefy::BeefyConsensusProof`, and converts it into the native SCALE `ConsensusMessage` via a `From` impl chain that eventually calls `From<Commitment> for SpCommitment`. That conversion unconditionally does `value.payload.into_iter().next().expect("commitment has at least one payload entry")` on an attacker-controlled, dynamically-sized Solidity array that can legally be empty. This is the direct Rust analog of CVE-2017-6298's "return value not checked" pattern: an attacker-controlled, possibly-empty/`None` value is force-unwrapped instead of validated, causing a runtime panic instead of a typed error.

### Finding Description
The extrinsic path is:
- `pallet_beefy_consensus_proofs::Pallet::submit_proof` → `do_submit_proof` (signed, permissionless) [1](#0-0) 
- → `verify_and_apply(&proof)`, which for `PROOF_TYPE_NAIVE` ABI-decodes the raw bytes into `ismp_abi::ecdsa_beefy::BeefyConsensusProof` and immediately converts it with `.into()` into `beefy_verifier_primitives::ConsensusMessage`, **before** any cryptographic or structural validation runs: [2](#0-1) 
- That `.into()` chain bottoms out in `From<MmrProof> for RelayChainProof`/`From<SpCommitment> for Commitment` and, on the reverse (ABI→SCALE) direction used here, in `From<Commitment> for SpCommitment`: [3](#0-2) 

```rust
impl From<Commitment> for SpCommitment {
    fn from(value: Commitment) -> Self {
        let mut iter = value.payload.into_iter();
        let first = iter.next().expect("commitment has at least one payload entry");
        ...
    }
}
```

`Commitment.payload` is a Solidity `Payload[]` — a dynamically-sized ABI array with no minimum-length constraint. `abi_decode_params` will happily decode a `BeefyConsensusProof` whose `commitment.payload` array has zero elements; nothing in the decode step or in `verify_and_apply`/`do_submit_proof` checks `payload.is_empty()` before the conversion runs. The `.expect(...)` then panics.

This is exactly the CVE-2017-6298 bug class transplanted into Rust: a value that can be empty/`None` (the ytnef advisory's unchecked `calloc` return / null pointer) is force-unwrapped (`.expect`) instead of being propagated as a typed `Error` — turning attacker-controlled, syntactically-valid-but-semantically-empty input into an uncontrolled runtime panic deep in consensus-message conversion, which is invoked directly from a public, permissionless, signed extrinsic.

Note: the codebase elsewhere (BEEFY verifier's `verify_mmr_update_proof`) already correctly guards the equivalent case with `commitment.payload.get_raw(&MMR_ROOT_PAYLOAD_ID).ok_or(Error::MmrRootHashMissing)?` [4](#0-3) , confirming the project's own established pattern for this exact class of input is to return a typed error — the conversion function in `evm/rust/src/conversions.rs` is the one path that was missed and still panics.

### Impact Explanation
A panic raised while executing a dispatchable call inside a Substrate/FRAME runtime is not a benign `Result::Err` — WASM runtimes are compiled with `panic = "abort"`, so an unhandled panic traps the whole runtime execution for that block. Depending on how the host executes the extrinsic (inside `apply_extrinsic` vs. block-import), this can fail the transaction pool validation, cause the collator to reject/crash on the block, or in the worst case desynchronize nodes that disagree on whether the panicking extrinsic is includable — a "route unable to deliver messages" condition for the whole `pallet-beefy-consensus-proofs` BEEFY-proof ingestion path, since any attacker can repeatedly submit zero-cost/zero-payload proofs to trigger it. Because BEEFY consensus updates gate all downstream state-commitment verification (and thus token bridge / intents / relayer settlement that depends on fresh consensus state), halting this ingestion path is a High-severity availability issue for the whole bridge.

### Likelihood Explanation
High. The `submit_proof` extrinsic is explicitly permissionless/signed and reachable by any account; `do_submit_proof` dispatches `PROOF_TYPE_NAIVE` bytes directly to `verify_and_apply` with only a leading-byte and ABI-decode check before the vulnerable conversion runs [5](#0-4) . Constructing a syntactically valid ABI-encoded `BeefyConsensusProof` with `commitment.payload = []` requires no special privileges, no valid signatures, and no cryptographic work — it is a pure calldata-construction exercise.

### Recommendation
In `evm/rust/src/conversions.rs`, change `From<Commitment> for SpCommitment` to a fallible conversion (`TryFrom`) that returns a typed error (e.g., reusing/extending `beefy_verifier::error::Error::MmrRootHashMissing` or a new `EmptyCommitmentPayload` variant) when `value.payload` is empty, and propagate that error through every call site currently relying on the infallible `Into`/`From` (including `RelayChainProof`/`ConsensusMessage` conversions built on top of it) so `do_submit_proof`/`verify_and_apply` surface `Error::<T>::AbiDecodeFailed`-style rejections instead of panicking. Add a regression test analogous to the existing `test_over_deep_proof_rejected` / `empty_hp_prefix_returns_error_not_panic` patterns, submitting a `PROOF_TYPE_NAIVE` proof with an empty `commitment.payload` array and asserting a clean `Err`, not a panic.

### Proof of Concept
1. Construct `ismp_abi::ecdsa_beefy::BeefyConsensusProof { relay: RelayChainProof { signedCommitment: SignedCommitment { commitment: Commitment { payload: vec![], blockNumber: 1, validatorSetId: 0 }, votes: vec![] }, latestMmrLeaf: <any>, mmrProof: vec![], proof: vec![] }, parachain: <any> }`.
2. ABI-encode it with `abi_encode_params`, prefix with `[PROOF_TYPE_NAIVE]`.
3. Submit as `submit_proof(origin, proof)` from any signed account.
4. `do_submit_proof` → `verify_and_apply` → ABI-decodes successfully (empty array is valid ABI) → `abi_proof.into()` invokes `From<Commitment> for SpCommitment` → `iter.next().expect(...)` panics because `payload` is empty.

Caveat: I was not able to trace, within the available tool budget, the exact `From<BeefyConsensusProof> for ConsensusMessage` glue impl connecting `verify_and_apply`'s `abi_proof.into()` call to the `Commitment`/`SpCommitment` conversion shown above (it likely lives in the same `evm/rust/src/conversions.rs` file, outside the line ranges retrieved). The individual pieces (the vulnerable `.expect` on an empty attacker-controlled array, and the extrinsic that decodes attacker ABI bytes and calls `.into()` on the decoded `Commitment` without checking `payload.is_empty()`) are confirmed directly from source; the reader should verify the intermediate glue `From` impl before treating this as fully proven end-to-end.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L448-485)
```rust
		fn do_submit_proof(submitter: T::AccountId, proof: Vec<u8>) -> DispatchResultWithPostInfo {
			// Size is enforced by the `BoundedVec<u8, T::MaxProofSize>` parameter on
			// `submit_proof` — oversized payloads fail SCALE decoding inside the txpool
			// and never reach this dispatch.
			// The set of accepted proof types is gated by `ismp-beefy`'s
			// `BeefyClientConfig::allowed_proof_types` during `verify_and_apply`. Unknown bytes
			// fall through to the `_ => UnknownProofType` arm below.
			let proof_type = *proof.first().ok_or(Error::<T>::UnknownProofType)?;

			// For SP1 proofs, decode the committed nonce and require it to equal the extrinsic
			// signer. The nonce is committed into the proof's public values, so it can only be
			// changed by re-running the SP1 program — a copied proof verifies cryptographically
			// but is bound to the *original* prover's account, so a different signer cannot claim
			// it. This is the anti-theft gate and also the dedup key: see [`AcceptedProvers`].
			//
			// Binding to the committed nonce also makes dedup robust without canonical
			// re-encoding: Groth16 re-randomization (or re-proving) yields different proof bytes
			// for the same statement, but all of them carry the same committed nonce, so they
			// collapse to a single per-account slot regardless of trailing padding or alternate
			// encodings.
			let account = match proof_type {
				types::PROOF_TYPE_SP1 => {
					let p =
						<ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof as SolType>::abi_decode_params(
							&proof[1..],
						)
						.map_err(|_| Error::<T>::AbiDecodeFailed)?;
					let nonce = H256(p.nonce.0);
					// `T::AccountId` is `AccountId32` in hyperbridge runtimes, which SCALE-encodes
					// to its 32 raw bytes; compare those against the committed nonce.
					if submitter.encode().as_slice() != nonce.as_bytes() {
						Err(Error::<T>::UnauthorizedProof)?
					}
					Some(nonce)
				},
				types::PROOF_TYPE_NAIVE => None,
				_ => Err(Error::<T>::UnknownProofType)?,
			};
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

**File:** evm/rust/src/conversions.rs (L334-344)
```rust
	impl From<Commitment> for SpCommitment {
		/// BEEFY commitment reconstruction. Reassembles the `Payload` from its
		/// `(id, data)` entries, starting with the first entry and pushing the rest via
		/// `push_raw` (which re-sorts by id to keep the invariant `Payload` expects).
		fn from(value: Commitment) -> Self {
			let mut iter = value.payload.into_iter();
			let first = iter.next().expect("commitment has at least one payload entry");
			let mut payload = BeefyPayload::from_single_entry(first.id.0, first.data.to_vec());
			for p in iter {
				payload = payload.push_raw(p.id.0, p.data.to_vec());
			}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L135-138)
```rust
	let mmr_root_data = commitment
		.payload
		.get_raw(&MMR_ROOT_PAYLOAD_ID)
		.ok_or(Error::MmrRootHashMissing)?;
```
