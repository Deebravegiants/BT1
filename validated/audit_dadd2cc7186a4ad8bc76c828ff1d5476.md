### Title
Panic-on-decode DoS via unbounded `blockNumber`/`validatorSetId` in SP1 BEEFY proof conversion - (File: `evm/rust/src/conversions.rs`)

### Summary
`pallet-beefy-consensus-proofs::submit_proof` is a **signed but permissionless** extrinsic — any account can submit an SP1 BEEFY consensus proof and have it processed by the runtime [1](#0-0) . For `PROOF_TYPE_SP1` proofs, `verify_and_apply` ABI-decodes the attacker-supplied bytes into `ismp_abi::sp1_beefy::SP1Beefy::SP1BeefyProof` and immediately converts it with `.into()` before any cryptographic check occurs [2](#0-1) .

### Finding Description
The `From<SP1Beefy::SP1BeefyProof> for Sp1BeefyProof` conversion narrows Solidity `uint256` fields (`commitment.blockNumber`, `commitment.validatorSetId`) into `u64` using `.try_into().expect(...)`: [3](#0-2) 

Because `abi_decode_params` only validates ABI shape, not value ranges, an attacker can submit `blockNumber` or `validatorSetId` as any `uint256` up to `2^256-1`. Any value `> u64::MAX` makes `try_into::<u64>()` return `Err`, and `.expect("block number out of bounds")` / `.expect("validator set id out of bounds")` **panics** — this happens during `verify_and_apply`, called synchronously from the dispatched extrinsic, before the SP1 Groth16 proof or any BEEFY signature is checked.

This is structurally identical to the CVE-2020-9490 bug class: a value from an attacker-controlled protocol field is accepted at intake with no bound check, and the crash occurs later during a subsequent processing step (here, type conversion prior to real verification), rather than being rejected immediately with a typed error like every other consensus-verifier code path in this codebase (BEEFY `verify_mmr_leaf`, GRANDPA `verify_parachain_headers_with_grandpa_finality_proof`, sync-committee `calculate_multi_merkle_root`, Pharos `nibble_at_depth`, BSC `parse_extra`) has been hardened to do, per the many "previously panicked the runtime … now surfaces a typed error" regression comments found throughout `modules/consensus/*`.

A panic inside a FRAME extrinsic's dispatch is not caught as a normal `DispatchError`; it aborts WASM execution for the block. Since `handle_unsigned`/`submit_proof` style calls are re-executed deterministically by every validator/full node importing the block, a transaction triggering this panic causes the same trap on every node processing it, which for many Substrate runtime configurations manifests as a node-level failure/abort rather than a graceful `Err` — a permissionless, single-transaction denial of service against the BEEFY consensus intake path, which is the trust root for state-commitment and message-delivery on all downstream chains served by this consensus client.

### Impact Explanation
The BEEFY/SP1 consensus client is a foundational trust anchor: it feeds verified parachain state commitments into `pallet-ismp`, which backs message delivery, state-proof verification, and (via HFT/IntentGateway/TokenGateway apps) fund transfers. A crash triggered on every full node processing the malicious extrinsic halts or degrades the block-import/consensus-relaying path for that route, meeting the "route unable to deliver messages" bar in scope. It requires no privileged role — any signed account (a relayer / prover) can submit the malformed `submit_proof` extrinsic.

### Likelihood Explanation
High: the extrinsic is explicitly documented as open to any signed account ("submitted via **signed** extrinsics … a successful prover gets their fee refunded … failed proofs pay the transaction fee normally"), requires no special setup beyond ABI-encoding a `SP1BeefyProof` tuple with an oversized `blockNumber`/`validatorSetId`, and the panic occurs on the very first `.into()` conversion before any expensive cryptographic verification, making it cheap to trigger repeatedly.

### Recommendation
Replace the `.try_into().expect(...)` calls in `evm/rust/src/conversions.rs`'s `From<SP1Beefy::SP1BeefyProof> for Sp1BeefyProof` (and the sibling `From` impls for `BeefyMmrLeaf`, `PartialBeefyMmrLeaf`, `Parachain`, `ParachainProof`, `Commitment`, `Vote`, `RelayChainProof` which have the identical pattern) with fallible conversions that propagate a typed error up through `verify_and_apply`, mirroring the fix pattern already applied to `verify_mmr_leaf`, `nibble_at_depth`, and `parse_extra` elsewhere in the codebase. At minimum, bound-check `blockNumber`/`validatorSetId`/leaf indices/authority-set id/len against `u64`/`u32` ranges before dispatch reaches these conversions, e.g. inside `verify_and_apply` right after `abi_decode_params`.

### Proof of Concept
1. Craft ABI-encoded bytes matching `abi_decode_params::<SP1Beefy::SP1BeefyProof>` where `commitment.blockNumber = U256::MAX` (or any value `> u64::MAX`), with otherwise well-formed (or arbitrary) `mmrLeaf`, `headers`, `proof`, `nonce` fields — the panic fires before those are used.
2. Prefix the payload with `PROOF_TYPE_SP1` and submit via `pallet_beefy_consensus_proofs::submit_proof(proof)` from any signed account.
3. `verify_and_apply` reaches `abi_proof.into()` at `modules/pallets/beefy-consensus-proofs/src/lib.rs:825`, which invokes `evm/rust/src/conversions.rs:397-416`; `commitment.blockNumber.try_into().expect("block number out of bounds")` panics, aborting execution of the extrinsic for every node that imports/re-executes the block containing it.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L24-27)
```rust
//! Proofs are submitted via **signed** extrinsics: the signer of the extrinsic is the
//! reward payee. The pallet sets `Pays::No` on accepted proofs so a successful prover
//! gets their fee refunded along with the reward; failed proofs pay the transaction
//! fee normally, which keeps spam off the chain.
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L818-827)
```rust
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
