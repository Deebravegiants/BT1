### Title
MEV frontrunning of unauthenticated NAIVE/ECDSA BEEFY proofs allows theft of prover rewards in `submit_proof` - (File: `modules/pallets/beefy-consensus-proofs/src/lib.rs`)

### Summary
`pallet-beefy-consensus-proofs::submit_proof` is a signed extrinsic where "the signer is the reward payee" [1](#0-0) . For `PROOF_TYPE_SP1` proofs, the reward payee is cryptographically bound to the proof content itself: the pallet doc explicitly states "Each SP1 proof commits a prover-chosen nonce into its public values, and the pallet requires that nonce to equal the extrinsic signer... This binds a proof to its submitter: a copied proof verifies cryptographically but cannot be claimed by a different account, so proofs cannot be stolen from the mempool" [2](#0-1) . No equivalent binding exists for `PROOF_TYPE_NAIVE` (ECDSA) proofs: `verify_and_apply` simply ABI-decodes the raw `BeefyConsensusProof` bytes with no nonce/account check before dispatching to the verifier [3](#0-2) .

### Finding Description
This is a direct analog of the Ajna `updateBucketExchangeRatesAndClaim` MEV finding: a publicly-visible, unauthenticated payload that anyone can resubmit under their own account to redirect a reward. Here, an honest prover assembles a valid NAIVE/ECDSA BEEFY proof and submits it via the signed `submit_proof(origin, proof)` extrinsic [4](#0-3) . Because `PROOF_TYPE_NAIVE` proof bytes carry no submitter-binding nonce (unlike SP1's committed nonce), the proof bytes are fully "stealable": once visible in the transaction pool, an MEV bot can copy the byte-for-byte proof and resubmit it as its own signed extrinsic with a higher tip/priority. The account recovered for the reward is purely `ensure_signed(origin)` — i.e., whoever's signature is on the wrapping extrinsic — with no requirement that the signer be tied to the proof content [4](#0-3) . Whichever copy lands first advances state and its submitter is paid the full `ProofReward` plus 1:1 reputation, per `pay_position_reward` [5](#0-4) . The docs corroborate that only SP1 proofs get uncle-curve protection/binding ("Uncle rewards apply to SP1 proofs only"), leaving NAIVE proofs on the plain first-submitter-wins path with no anti-theft binding.

### Impact Explanation
The stolen reward is paid from the Hyperbridge treasury (`TreasuryPalletId`) to the frontrunner instead of the honest prover who did the real off-chain work of generating the ECDSA/BEEFY proof [6](#0-5) . This also mints the reputation asset to the wrong account, which "is the primary factor in Collator selection" [7](#0-6) , meaning MEV theft additionally corrupts the permissionless collator-selection process by handing block-production eligibility to a bot rather than a genuine network operator. This is a direct, repeatable fund-theft and governance-corrupting vector against any prover using the ECDSA/NAIVE proof path, which the docs say is the recommended path for testnets and is explicitly supported in mainnet consensus (`AllowedBeefyProofTypes` accepts both `PROOF_TYPE_NAIVE` and `PROOF_TYPE_SP1`) [8](#0-7) .

### Likelihood Explanation
Likelihood is high wherever NAIVE proofs are accepted: proof generation is computationally cheap relative to SP1 (no GPU/Groth16 proving needed), so an attacker's copy-and-resubmit cost is negligible — just observing the mempool and resubmitting with a higher tip. Because rewards are transparent, deterministic per accepted proof (`ProofReward`, currently 100 `$BRIDGE`) and paid to whoever's signature wraps the extrinsic [9](#0-8) , this is economically identical to the Ajna scenario: predictable, first-come-first-served rewards over public transaction data create a durable MEV opportunity that disincentivizes honest, low-resource (non-SP1) provers exactly the way it disincentivized Alice in the Ajna report.

### Recommendation
Extend the SP1 nonce-binding mechanism to `PROOF_TYPE_NAIVE`/ECDSA proofs: require the proof (or a companion signed statement) to commit the submitting account, and verify that commitment against `ensure_signed(origin)` before paying any reward — mirroring the protection already documented for SP1. Alternatively, disallow `submit_proof` extrinsics whose reward payee is not cryptographically bound to the proof content, or require proofs to be submitted unsigned with attribution derived from an embedded, prover-signed payload (as done elsewhere, e.g. `pallet-consensus-incentives`, which recovers the relayer from a signature embedded in message content rather than from `ensure_signed`) [10](#0-9) .

### Proof of Concept
1. Honest prover Alice runs a naive/ECDSA BEEFY prover, assembles a valid `PROOF_TYPE_NAIVE` proof for a new finality target, and submits `submit_proof(origin=Alice, proof)` [1](#0-0) .
2. A bot watching the Hyperbridge transaction pool observes Alice's pending extrinsic, extracts the `proof` byte vector (unbound to any account since `PROOF_TYPE_NAIVE` has no nonce commitment, unlike SP1) [3](#0-2) .
3. The bot resubmits `submit_proof(origin=Bot, proof)` with the same bytes but signed by its own key, at higher priority/tip.
4. `verify_and_apply` succeeds identically for either submitter since it performs no submitter-binding check for `PROOF_TYPE_NAIVE` [11](#0-10) ; whichever lands first is recorded as `submitter` and paid via `pay_position_reward` [5](#0-4) .
5. Bot's transaction lands first (frontrunning), Bot receives the `ProofReward` and reputation mint intended for Alice; Alice's now-stale duplicate transaction fails on inclusion (`StaleProof`/already-advanced state).

**Note on uncertainty:** I could not fully verify the `validate_unsigned`/transaction-pool priority configuration for `submit_proof` (it is a signed, not unsigned, extrinsic per the code, so standard transaction-pool tip/priority mechanics apply rather than a custom `provides` tag) — this affects the precision of the "frontrunning" mechanics but not the core finding that NAIVE proofs lack submitter-binding. Full verification of transaction-pool ordering guarantees would require reviewing the runtime's `TransactionPayment`/priority configuration, which was not located in the indexed content.

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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L731-757)
```rust
		/// Apply the curve at `position` to [`ProofReward`], transfer from the treasury,
		/// and mint reputation 1:1.
		fn pay_position_reward(
			submitter: &T::AccountId,
			position: u32,
		) -> Result<BalanceOf<T>, Error<T>> {
			let zero = BalanceOf::<T>::default();
			let base = ProofReward::<T>::get();
			if base == zero {
				return Ok(zero);
			}

			let reward = Self::position_reward(base, position);
			if reward == zero {
				return Ok(zero);
			}

			let treasury: T::AccountId =
				<T as Config>::TreasuryPalletId::get().into_account_truncating();
			<T as Config>::Currency::transfer(&treasury, submitter, reward, Preservation::Preserve)
				.map_err(|e| {
					log::warn!(
						target: "ismp",
						"[beefy-consensus-proofs] treasury reward transfer failed: {e:?}",
					);
					Error::<T>::RewardTransferFailed
				})?;
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

**File:** docs/content/developers/explore/provers.mdx (L28-35)
```text
## Incentives

Provers are rewarded with `$BRIDGE` tokens from the Hyperbridge treasury for each accepted proof that does useful work:

- **Rotation proofs** — Proofs that carry a new BEEFY authority set transition.
- **Messaging proofs** — Proofs that advance the proven parachain height past blocks containing new cross-chain message dispatches.

The base reward amount is configurable via governance through `pallet-beefy-consensus-proofs::set_proof_reward` (currently **100 `$BRIDGE`** per proof).
```

**File:** docs/content/developers/explore/provers.mdx (L59-63)
```text
## Reputation and the Path to Becoming a Collator

In addition to `$BRIDGE` token rewards, provers automatically earn **Reputation Asset** tokens at a 1:1 ratio with their `$BRIDGE` earnings. This non-transferable reputation score is the primary factor in [Collator selection](/developers/network/collator) — the higher your reputation, the better your chances of being selected as a block-producing Collator for the Hyperbridge network.

This means that running a prover is a direct path to becoming a Collator and earning additional block production rewards. The same Controller account used as the prover's signer accrues reputation, which is evaluated at each session boundary when `pallet-collator-manager` selects the next collator set.
```

**File:** docs/outbound-request-incentivization.md (L377-377)
```markdown
On the BEEFY prover: the gargantua runtime's `AllowedBeefyProofTypes` accepts both `PROOF_TYPE_NAIVE` and `PROOF_TYPE_SP1`, so a naive proof is accepted on chain with no runtime change. For a local run the naive prover is preferable because the SP1 path needs the SP1 toolchain, proving keys, and multi-minute proving time per proof, none of which the feature under test cares about. Open item: the `BeefyHost` builder in `tesseract/consensus/beefy/src/lib.rs` is wired with `zk_beefy::LocalProver`, so the exact way to select naive output from the prover binary still needs to be confirmed.
```

**File:** modules/pallets/consensus-incentives/src/impls.rs (L112-122)
```rust
		let maybe_relayer_account = messages.get(0).and_then(|first_message| {
			if let Message::Consensus(consensus_msg) = &first_message.message {
				let data = sp_io::hashing::keccak_256(&consensus_msg.consensus_proof);
				Signature::decode(&mut &consensus_msg.signer[..])
					.ok()
					.and_then(|sig| sig.verify_and_get_sr25519_pubkey(&data, None).ok())
					.map(|pub_key| pub_key.into())
			} else {
				None::<[u8; 32]>
			}
		});
```
