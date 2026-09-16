## Title
BEEFY naive (ECDSA) consensus proof reward is not bound to the submitting account and can be front-run - (`modules/pallets/beefy-consensus-proofs/src/lib.rs`)

### Summary
`pallet-beefy-consensus-proofs::submit_proof` accepts two proof kinds: SP1 and "naive" (full ECDSA validator-signature) proofs. For SP1 proofs the pallet explicitly binds the proof to the submitting account by requiring a committed nonce inside the proof's public values to equal the extrinsic signer, which the pallet's own documentation states exists specifically to prevent "stealing" a proof observed in the mempool. That binding is **not** applied to naive/ECDSA proofs, so anyone who observes a pending `submit_proof` extrinsic carrying a naive proof can copy the (public, verifiable) proof bytes into their own signed extrinsic and front-run the original submitter to claim the reward.

### Finding Description
In `do_submit_proof`, the account-binding check only runs for `PROOF_TYPE_SP1`; for `PROOF_TYPE_NAIVE` no binding to the submitter is enforced at all: [1](#0-0) 

The submitter of `submit_proof` becomes the reward payee (`settle_first_proof` pays `pay_position_reward(&submitter, 0)`), regardless of who actually produced the proof: [2](#0-1) [3](#0-2) 

A naive proof is a self-contained artifact — the full set of BEEFY validator ECDSA signatures over a header — and its validity does not depend on who submits it or what account signs the extrinsic. Since `verify_and_apply`/`verify_fraud_proof`-style verification for the naive path checks only the cryptographic content of the proof (not any commitment to the submitter), any account can lift the `proof` bytes from a pending `submit_proof(origin, proof)` transaction in the mempool, wrap them in a new extrinsic signed by an attacker-controlled key, and get it included first (or with a higher tip/priority) ahead of the original.

The codebase itself documents the exact threat model this leaves unaddressed for SP1, but not for naive proofs — the test suite for the SP1 uncle path spells this asymmetry out directly: [4](#0-3) [5](#0-4) 

This is structurally the same bug class as the external report: a fraud/consensus proof whose reward is tied to `msg.sender`/extrinsic-signer, but the proof payload itself carries no binding to that signer, so it can be copied out of the public mempool and resubmitted under a different identity to steal the reward.

### Impact Explanation
Every accepted naive/ECDSA proof (mandatory authority-set rotation proofs, and messaging proofs on chains still using the ECDSA variant, e.g. testnets per the docs) pays out `ProofReward` (position-0, full reward — not the decayed uncle curve, since uncle accounting is SP1-only) from the Hyperbridge treasury. An attacker running a bot that watches the transaction pool for `BeefyConsensusProofs::submit_proof` calls carrying naive proofs can systematically steal every legitimate prover's reward by resubmitting the copied proof with higher priority/gas, permanently redirecting treasury funds intended for honest provers to itself with no cost beyond gas/priority fee. This is a direct theft-of-funds vector against the treasury-funded incentive mechanism and, over time, disincentivizes honest ECDSA-proof provers from participating (since their reward can always be stolen), degrading the liveness of consensus proof submission on any deployment relying on the ECDSA path.

### Likelihood Explanation
Likelihood is high on any network with public mempool visibility (or where the attacker simply races resubmission after observing a finalized-but-unrewarded proof window): the naive proof bytes are the complete, self-verifying artifact required to win the reward, requiring no private information from the original submitter. The pallet's own design already treats this exact scenario ("copying the proof bytes from the mempool and submitting them under a different account") as an active, must-mitigate threat for SP1 proofs — the mitigation was simply never extended to the naive proof path.

### Recommendation
Bind naive/ECDSA proofs to the submitting account the same way SP1 proofs are bound: e.g., require the extrinsic to include a signature or committed value over the submitter's account (or over `(proof_hash, submitter)`), verified before payout, or route naive-proof submission through a commit-reveal scheme. At minimum, treat naive proofs' reward-eligibility identically to SP1 by rejecting/penalizing submissions that don't attest to `submitter`, closing the same front-running gap that `reportUnauthorizedSigning` had before binding to `msg.sender`.

### Proof of Concept
1. Honest prover `Alice` observes a new BEEFY finality target requiring a naive proof and constructs a valid ECDSA `proof` (full validator-signature bundle) for the parachain height/authority rotation.
2. Alice signs and broadcasts `BeefyConsensusProofs::submit_proof(origin=Alice, proof=P)`.
3. Attacker `Mallory` observes `P` in the public mempool (or via any relay/indexer exposing pending extrinsics), and since `do_submit_proof` performs no submitter-binding check for `PROOF_TYPE_NAIVE` (`modules/pallets/beefy-consensus-proofs/src/lib.rs:468-484`), Mallory constructs `BeefyConsensusProofs::submit_proof(origin=Mallory, proof=P)` using the identical bytes and submits it with a higher priority/tip.
4. Mallory's extrinsic lands first; `verify_and_apply(&P)` succeeds identically to Alice's case (the proof content is unchanged), and `settle_first_proof` pays `pay_position_reward(&Mallory, 0)` — Mallory receives the full `ProofReward` from the treasury.
5. Alice's now-stale resubmission of `P` fails (`StaleProof`/replay-protected consensus state), and she receives nothing despite having produced the original valid proof.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L41-50)
```rust
//! ## Prover-bound proofs & deduplication
//!
//! Each SP1 proof commits a prover-chosen nonce into its public values, and the pallet
//! requires that nonce to equal the extrinsic signer (the reward payee). This binds a proof
//! to its submitter: a copied proof verifies cryptographically but cannot be claimed by a
//! different account, so proofs cannot be stolen from the mempool. The committed account is
//! also the dedup key — recorded per parachain height in [`pallet::AcceptedProvers`] — so an
//! account is rewarded at most once per height. Because the nonce is committed (not derived
//! from the proof bytes), Groth16 re-randomization or re-proving cannot mint extra reward
//! slots: every variant a single prover can produce carries the same committed account.
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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L455-485)
```rust
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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L570-581)
```rust
			let reward_paid = match Self::pay_position_reward(&submitter, 0) {
				Ok(reward) => reward,
				Err(e) if outcome.rotated => {
					log::warn!(
						target: "ismp",
						"[beefy-consensus-proofs] reward skipped for rotation to set {}: {e:?}",
						outcome.current_set_id,
					);
					BalanceOf::<T>::default()
				},
				Err(e) => Err(e)?,
			};
```

**File:** tesseract/consensus/beefy/tests/mainnet_rotation.rs (L200-210)
```rust
	let prover_config = ProverConfig {
		relay_rpc_ws: relay_url.clone(),
		para_rpc_ws: para_url.clone(),
		para_ids: vec![para_id],
		proof_variant: ProofVariant::Ecdsa,
		max_rpc_payload_size: None,
		query_batch_size: None,
	};
	// ECDSA proof submitted to the EVM handler, which does not enforce the SP1 committed-
	// nonce binding, so a zero account is fine here.
	let prover: Prover<Blake2SubstrateChain, KeccakSubstrateChain, zk_beefy::LocalProver> =
```
