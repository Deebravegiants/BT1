Confirmed: `ismp_abi` (imported in `modules/pallets/beefy-consensus-proofs/src/lib.rs:89`) is the package name for `evm/rust`, so `evm/rust/src/conversions.rs` is compiled directly into this on-chain pallet, and its `From` impls run on attacker-controlled ABI bytes submitted via a signed extrinsic.

### Title
Panic-based DoS in `settle_uncle_proof` via oversized SP1 BEEFY commitment fields - (File: `evm/rust/src/conversions.rs`)

### Summary
The `beefy-consensus-proofs` pallet's uncle-proof path decodes a Solidity-ABI-encoded `SP1BeefyProof` from an unprivileged, signed submission and converts it into the native `Sp1BeefyProof` type via `From<crate::sp1_beefy::SP1Beefy::SP1BeefyProof> for Sp1BeefyProof`. That conversion calls `.try_into().expect(...)` on attacker-supplied `uint256` fields (`blockNumber`, `validatorSetId`) before any cryptographic verification occurs, allowing a crafted proof to panic the runtime.

### Finding Description
`settle_uncle_proof` in `modules/pallets/beefy-consensus-proofs/src/lib.rs:636-712` decodes the raw proof bytes with `abi_decode_params` and converts the result with `abi_proof.into()`: [1](#0-0) 

That `.into()` resolves to the `From` impl in `evm/rust/src/conversions.rs`, whose crate is imported as `ismp_abi` by this pallet: [2](#0-1) [3](#0-2) 

`blockNumber` and `validatorSetId` are Solidity `uint256` values fully controlled by the caller inside the ABI-encoded proof; `.try_into()` on a `U256` that exceeds the native `u32`/`u64` target type fails, and `.expect(...)` converts that failure into a Rust panic instead of a typed error. This executes *before* any signature or MMR verification, so no valid consensus data is required to reach it — any signed extrinsic with a malformed `blockNumber`/`validatorSetId` triggers it deterministically.

This mirrors the CVE-2020-14869 bug class: a value supplied over the network by a permitted-but-untrusted caller (an "easily exploitable" DoS requiring only ordinary access, no special privilege) crashes/hangs the server process — here, causes the parachain runtime to panic during block execution.

The same conversion module contains multiple other `.expect(...)` calls on data whose ultimate origin traces to submitted proof bytes (e.g. `RelayChainProof -> MmrProof` at line 371, `SpCommitment -> Commitment` at line 103), and the file itself notes elsewhere in the codebase (`sync-committee`, `pharos`, `beefy/verifier`, `grandpa`, ethereum trie) that this exact panic-on-untrusted-input class has already been systematically hardened with typed errors and regression tests — this conversion path was evidently missed.

### Impact Explanation
A panic inside on-chain dispatch (particularly one reached from a `#[frame_support::transactional]` extrinsic) causes the executor to abort transaction/block processing, which can halt block production or crash collator/validator nodes processing the block — a "hang or frequently repeatable crash" analogous to the CVE. Because `settle_uncle_proof` is reachable by any account willing to pay a transaction fee (uncle-proof submission is a normal, signed, permissionless path per the pallet's own documentation), this is a low-cost, repeatable route to disrupt Hyperbridge's BEEFY consensus-relay pipeline, which is required for message delivery — a route unable to deliver messages while under attack.

### Likelihood Explanation
High: the attacker only needs to construct an ABI-encoded `SP1BeefyProof` with `blockNumber` or `validatorSetId` set above `u64::MAX`/`u32::MAX` and submit it as a normal signed extrinsic to `settle_uncle_proof` (or the equivalent first-proof path if it shares this conversion). No cryptographic material, authority set knowledge, or elevated privilege is required, and the panic occurs before verification, so the transaction fee is the only cost.

### Recommendation
Replace `.try_into().expect(...)` in the `From<SP1Beefy::SP1BeefyProof> for Sp1BeefyProof` conversion (and any other panicking conversions in `evm/rust/src/conversions.rs` reachable from on-chain proof submission, e.g. line 371) with fallible conversions that return a typed `Error` the pallet can propagate as a normal `DispatchError`, consistent with the fix pattern already applied to `modules/consensus/beefy/verifier/src/lib.rs` (`InvalidMmrProof` for empty `leaf_indices`) and `modules/consensus/grandpa/verifier/src/error.rs`.

### Proof of Concept
1. Construct `SP1Beefy::SP1BeefyProof { commitment: MiniCommitment { blockNumber: U256::MAX, validatorSetId: 0 }, ... }` with otherwise arbitrary/garbage `mmrLeaf`, `headers`, `proof`, `nonce`.
2. ABI-encode it and prefix with `PROOF_TYPE_SP1`.
3. Submit as the `proof` argument to `beefy-consensus-proofs::submit_sp1_proof` (or whichever public extrinsic funnels into `settle_uncle_proof`) from any funded account, at a time when `ProofContext` for the current `latest_height` is populated (i.e., during normal uncle-proof contention, which is a documented, reachable protocol state).
4. `Sp1BeefyProof::from(abi_proof)` executes `value.commitment.blockNumber.try_into().expect("block number out of bounds")`, which panics because `U256::MAX` cannot fit the target integer type, aborting the extrinsic's execution.

Note: I could not fully trace whether the primary (non-uncle) SP1 proof submission path shares this exact conversion call or uses a different route into `verify_sp1_consensus`; confirming that would require reading the full `submit_sp1_proof`/dispatch entry point and the `beefy_verifier_primitives::Sp1BeefyProof` field type definitions, which were not fully retrievable within the available searches.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L89-89)
```rust
	use ismp_abi::ecdsa_beefy::BeefyConsensusState as SolBeefyConsensusState;
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
