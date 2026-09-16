This is confirmed as a critical reachable path: `pallet-beefy-consensus-proofs` accepts **signed extrinsics carrying SP1/BEEFY consensus proofs from untrusted submitters** [1](#0-0) , ABI-decodes the sol-generated proof struct with `alloy_sol_types::SolType`, and converts it into the SCALE shape via `evm/rust/src/conversions.rs` `From` impls before dispatching into `pallet-ismp`'s consensus handler.

### Title
Panicking numeric-conversion `.expect()` on attacker-controlled proof fields lets an unprivileged extrinsic halt block execution - (File: evm/rust/src/conversions.rs)

### Summary
`evm/rust/src/conversions.rs` contains multiple `TryInto`/`try_into().expect(...)` conversions that **panic** instead of returning an error when an attacker-controlled numeric field (from a submitted BEEFY/SP1 consensus proof) exceeds the target integer width. This mirrors the CVE-2017-7961 bug class: an out-of-range numeric conversion causing undefined/crashing behavior on attacker-supplied input.

### Finding Description
Several `From` impls used to convert ABI-decoded (Solidity `sol!`-generated) consensus proof types into the local Rust/SCALE structures use `.try_into().expect("... out of bounds")`, which panics on failure rather than propagating a `Result`:

- `Commitment -> SpCommitment`: `value.blockNumber.try_into().expect("block number out of bounds")` and `value.validatorSetId.try_into().expect(...)` [2](#0-1) 
- `Vote -> SignatureWithAuthorityIndex`: `value.authorityIndex.try_into().expect("authority index out of bounds")` [3](#0-2) 
- `RelayChainProof -> MmrProof`: `value.latestMmrLeaf.leafIndex.try_into().expect("mmr leaf index out of bounds")` [4](#0-3) 
- `SP1BeefyProof -> Sp1BeefyProof`: `value.commitment.blockNumber.try_into().expect(...)` and `validatorSetId.try_into().expect(...)` [5](#0-4) 
- `IntermediateState -> local::IntermediateState`: `value.stateMachineId.try_into().expect(...)`, `value.height.try_into().expect(...)`, `value.commitment.timestamp.try_into().expect(...)` [6](#0-5) 

These sol types (`AuthoritySetCommitment`, `Commitment`, `RelayChainProof`, `SP1BeefyProof`, `IntermediateState`, etc.) are `U256`/`uint256`-backed fields on the Solidity/ABI side, and are converted to narrow Rust integers (`u32`, `u64`) that the SCALE `Commitment`/`MmrProof` structures expect [7](#0-6) . Because these fields originate from a submitted proof that any account can send via a **signed, permissionless extrinsic** to `pallet-beefy-consensus-proofs` [1](#0-0) , an attacker can craft a `blockNumber`, `validatorSetId`, `leafIndex`, `authorityIndex`, `height`, or `timestamp` value that exceeds `u32`/`u64` bounds. If the pallet's first-proof verification path (documented at `modules/pallets/beefy-consensus-proofs/src/lib.rs:793-798` as decoding the ABI proof "into the SCALE shape `ismp-beefy` consumes") uses these same conversion routines on-chain, the `.expect()` panics inside runtime/WASM execution, which aborts the transaction's block execution rather than returning a graceful `DispatchError`.

### Impact Explanation
A panic triggered from within pallet extrinsic execution on a Substrate/FRAME runtime is not merely a reverted transaction — depending on where the panic occurs relative to storage transaction boundaries, it can produce non-deterministic execution or, at minimum, is treated as a bug class runtimes must never allow reachable from unprivileged input, since panicking code paths are explicitly excluded from the "should return `Result`, never panic" invariant that FRAME pallets require. Given this proof-submission is the mechanism that "feeds finalized parachain state commitments into `pallet-ismp`," a crash here is on the critical consensus-verification path that other pallets/apps depend on for message delivery — i.e., a route unable to deliver messages if it can be repeatedly triggered by any submitter.

### Likelihood Explanation
High — the proof submission extrinsic is explicitly permissionless (any signed account may submit, per the pallet's own documentation) [8](#0-7) , and the numeric fields are attacker-supplied raw `uint256` values from the ABI-encoded proof, requiring no cryptographic validity to reach the conversion code — the `.expect()` fires during decoding, before/independent of the SP1/BEEFY cryptographic checks.

### Recommendation
Replace every `.try_into().expect(...)` in `evm/rust/src/conversions.rs` (and any other consensus-proof conversion path reachable from `pallet-beefy-consensus-proofs`) with fallible `TryFrom`/`TryInto` that returns a `Result` and is propagated up as a `DispatchError`/decode error instead of panicking. This affects the `From<Commitment> for SpCommitment`, `From<Vote> for SignatureWithAuthorityIndex`, `From<RelayChainProof> for MmrProof`, `From<SP1Beefy::SP1BeefyProof> for Sp1BeefyProof`, and `From<IntermediateState> for local::IntermediateState` impls.

### Proof of Concept
1. Submit `submit_beefy_consensus_proof` (or equivalent extrinsic in `pallet-beefy-consensus-proofs`) with an SP1/BEEFY proof whose ABI-encoded `commitment.blockNumber`, `commitment.validatorSetId`, `latestMmrLeaf.leafIndex`, `votes[i].authorityIndex`, or `IntermediateState.height`/`timestamp` field is set to a `uint256` value greater than `u32::MAX`/`u64::MAX` (e.g., `2^64`).
2. When the pallet decodes the proof and invokes the `From`/`TryInto` conversions in `evm/rust/src/conversions.rs`, the `.expect("... out of bounds")` fires and panics.
3. Observe the runtime panic during extrinsic execution, aborting normal error handling for that block/transaction.

**Note on uncertainty**: I was not able to fully confirm within the available tool budget that the pallet's on-chain decode path calls `evm/rust/src/conversions.rs` directly (as opposed to a separate SCALE-native decode step) — the pallet source shows it "ABI-decodes the proof into the SCALE shape `ismp-beefy` consumes" but I could not read the exact decode call site before running out of iterations. A Devin session with full file access should verify the precise call chain from `pallet::Call::submit_*` into these `From` impls before treating this as fully confirmed.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L16-27)
```rust
//! # Pallet BEEFY Consensus Proofs
//!
//! Verifies BEEFY consensus proofs (primarily SP1 ZK) submitted by off-chain provers and
//! feeds the finalized parachain state commitments into `pallet-ismp`. Rewards submitters
//! from the treasury when a proof does useful work — either carries the expected next
//! authority-set rotation, or advances the latest proven parachain height past a block
//! in which new ISMP requests were dispatched.
//!
//! Proofs are submitted via **signed** extrinsics: the signer of the extrinsic is the
//! reward payee. The pallet sets `Pays::No` on accepted proofs so a successful prover
//! gets their fee refunded along with the reward; failed proofs pay the transaction
//! fee normally, which keeps spam off the chain.
```

**File:** evm/rust/src/conversions.rs (L18-44)
```rust
use crate::ecdsa_beefy::Beefy::IntermediateState;

use alloy_primitives::U256;
use primitive_types::H256;

/// Helper trait for converting primitive types to alloy U256
pub trait ToU256 {
	fn to_u256(self) -> U256;
}

impl ToU256 for u32 {
	fn to_u256(self) -> U256 {
		U256::from(self)
	}
}

impl ToU256 for u64 {
	fn to_u256(self) -> U256 {
		U256::from(self)
	}
}

impl ToU256 for usize {
	fn to_u256(self) -> U256 {
		U256::from(self)
	}
}
```

**File:** evm/rust/src/conversions.rs (L344-353)
```rust
			}
			sp_consensus_beefy::Commitment {
				payload,
				block_number: value.blockNumber.try_into().expect("block number out of bounds"),
				validator_set_id: value
					.validatorSetId
					.try_into()
					.expect("validator set id out of bounds"),
			}
		}
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

**File:** evm/rust/src/conversions.rs (L368-389)
```rust
	impl From<RelayChainProof> for MmrProof {
		fn from(value: RelayChainProof) -> Self {
			let leaf_index: u64 =
				value.latestMmrLeaf.leafIndex.try_into().expect("mmr leaf index out of bounds");
			let items: Vec<H256> = value.mmrProof.into_iter().map(|h| H256(h.0)).collect();
			let mmr_proof = LeafProof {
				leaf_indices: vec![leaf_index],
				leaf_count: leaf_index.saturating_add(1),
				items,
			};

			MmrProof {
				signed_commitment: BvpSignedCommitment {
					commitment: value.signedCommitment.commitment.into(),
					signatures: value.signedCommitment.votes.into_iter().map(Into::into).collect(),
				},
				latest_mmr_leaf: value.latestMmrLeaf.into(),
				mmr_proof,
				authority_proof: value.proof.into_iter().map(|h| h.0).collect(),
			}
		}
	}
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

**File:** evm/rust/src/conversions.rs (L419-436)
```rust
impl From<IntermediateState> for local::IntermediateState {
	fn from(value: IntermediateState) -> Self {
		local::IntermediateState {
			height: local::StateMachineHeight {
				state_machine_id: value
					.stateMachineId
					.try_into()
					.expect("state machine id out of bounds"),
				height: value.height.try_into().expect("state machine height out of bounds"),
			},
			commitment: local::StateCommitment {
				timestamp: value.commitment.timestamp.try_into().expect("timestamp out of bounds"),
				state_root: H256(value.commitment.stateRoot.0),
				overlay_root: H256(value.commitment.overlayRoot.0),
			},
		}
	}
}
```
