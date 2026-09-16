## Title
Naive BEEFY proof rewards can be front-run/stolen by MEV via `submit_proof` — ([File: modules/pallets/beefy-consensus-proofs/src/lib.rs])

### Summary
`pallet-beefy-consensus-proofs::submit_proof` pays the `$BRIDGE` position-0 reward to whichever account's signed extrinsic is the *first* to land on-chain with a valid proof [1](#0-0) . For SP1 proofs, the reward is safe because each proof commits the payee's account as a nonce that must equal the extrinsic signer, so a copied proof cannot be claimed by anyone else [2](#0-1) . For `PROOF_TYPE_NAIVE` proofs, however, `account` is set to `None` — there is no binding at all between the proof bytes and any account [3](#0-2) . The reward is instead paid unconditionally to `submitter`, i.e. whoever's signature the runtime validated for that particular extrinsic (`ensure_signed(origin)`) [4](#0-3) [5](#0-4) .

This is structurally identical to the reported `tryNewEpoch` bug class: a permissionless, publicly-visible transaction that both advances protocol state and pays the caller a reward can be observed in the mempool and copied/resubmitted by an MEV actor before the honest submitter's transaction lands, stealing the reward while contributing zero original work.

### Finding Description
`submit_proof` is a normal **signed** extrinsic, visible in the transaction pool prior to block inclusion, per the pallet's own documentation ("Proofs are submitted via signed extrinsics: the signer of the extrinsic is the reward payee") [6](#0-5) .

`do_submit_proof` branches on `proof_type`:
- `PROOF_TYPE_SP1`: the proof's committed nonce must equal the submitter's account, or the call fails with `UnauthorizedProof` — this is the pallet's explicit "anti-theft gate" [7](#0-6) .
- `PROOF_TYPE_NAIVE`: `account = None`, with no equivalent binding check [8](#0-7) .

`settle_first_proof` then pays the position-0 reward straight to `submitter` regardless of proof type [9](#0-8) , and `pay_position_reward` transfers `$BRIDGE` from the treasury to that account and mints reputation to it [10](#0-9) .

Because the naive proof bytes carry no cryptographic binding to the honest submitter's account, an MEV searcher watching the mempool can:
1. Observe a pending `submit_proof(naive_proof_bytes)` extrinsic from an honest prover.
2. Extract `naive_proof_bytes` (public data — an ECDSA/BEEFY validator-signature bundle, unrelated to any specific claimant account).
3. Wrap the identical bytes in their own signed extrinsic and get it included first (e.g., via higher tip/priority, direct block-producer collusion, or simple latency racing).
4. `verify_and_apply` succeeds identically since the proof content is unchanged; `ensure_signed(origin)` now resolves to the attacker's account, which receives the full position-0 `$BRIDGE` reward and reputation mint, while the true submitter's later transaction hits `NoNewWork`/`StaleProof` and earns nothing.

The docs explicitly confirm naive proofs remain a first-class accepted type on-chain (`AllowedBeefyProofTypes` accepts both `PROOF_TYPE_NAIVE` and `PROOF_TYPE_SP1`), and are the default/only practical choice absent SP1 tooling (GPU, proving keys) [11](#0-10) . The anti-theft protection is documented and tested as SP1-only — the simnode test explicitly shows a copied SP1 proof rejected with `UnauthorizedProof` when resubmitted by a different account, but no equivalent test or protection exists for naive proofs [12](#0-11) .

### Impact Explanation
Reward theft: the treasury pays `$BRIDGE` and mints reputation to an MEV actor who did no proof-generation work, instead of the honest prover who assembled the BEEFY signature bundle. This is a direct, protocol-funded loss (treasury drain to an attacker) and undermines the reputation-based collator-selection mechanism (an MEV bot can farm reputation purely by front-running honest naive provers) [13](#0-12) . At scale, this also discourages legitimate naive-mode provers from operating, since their work can always be sniped, degrading liveness on any deployment relying on naive proofs (e.g., testnets, or any chain not yet running SP1 tooling).

### Likelihood Explanation
High for any deployment where naive proofs are accepted (which is the default/permitted state per `AllowedBeefyProofTypes`). `submit_proof` extrinsics are ordinary signed transactions sitting in the public mempool before inclusion, and naive proof bytes require no secret or account-specific data to replay — copying and resubmitting is trivial for any node with mempool visibility, including block-producing collators themselves.

### Recommendation
Extend the same anti-theft binding used for SP1 to naive proofs: require the submitter to commit to their claimed account inside the signed payload in a way that is cryptographically bound to the proof (e.g., include the submitter's account as part of the signed extrinsic's included payload and re-verify it, or require naive-proof submissions to also carry a signature over `(proof_hash, claimed_account)` recoverable independently of the extrinsic's own signature), or disable/deprecate `PROOF_TYPE_NAIVE` reward payment entirely and only accept it as a zero-reward fallback path, mirroring how `settle_first_proof` already treats naive proofs as "ineligible for uncle rewards" — the same ineligibility should extend to the position-0 reward.

### Proof of Concept
1. Alice runs a naive BEEFY prover and constructs a valid `PROOF_TYPE_NAIVE` proof for the next messaging/rotation target.
2. Alice signs and broadcasts `BeefyConsensusProofs::submit_proof(proof_bytes)` from her account; it enters the public transaction pool.
3. Bob (MEV) observes Alice's pending extrinsic, copies `proof_bytes` verbatim, and submits his own signed `submit_proof(proof_bytes)` with higher priority/tip so it is included first.
4. `do_submit_proof` runs with `submitter = Bob`; since `proof_type == PROOF_TYPE_NAIVE`, `account = None` and no ownership check is performed [8](#0-7) ; `verify_and_apply` succeeds on the unmodified bytes.
5. `settle_first_proof` pays the position-0 `$BRIDGE` reward and mints reputation to Bob [5](#0-4) .
6. Alice's identical follow-up transaction fails with `NoNewWork`/`StaleProof` since the state has already advanced, and she receives nothing despite doing the actual proof-generation work.

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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L457-485)
```rust
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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L563-581)
```rust
			// Same reasoning as the uncle bookkeeping above: the caller has already applied the
			// authority-set rotation, so a hard error here rolls it back, and since the mandatory
			// justification is the only one obtainable for that session every retry fails
			// identically until someone tops the treasury up — leaving the consensus state on the
			// old set in the meantime. A missed reward is the cheaper loss, so log and carry on.
			// Messaging proofs keep the hard error: reverting one is recoverable, because the work
			// is re-attempted by the next proof once the treasury can pay.
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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L731-767)
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

			if let Err(e) = T::ReputationAsset::mint_into(submitter, reward) {
				log::warn!(
					target: "ismp",
					"[beefy-consensus-proofs] reputation mint failed: {e:?}",
				);
			}

			Ok(reward)
		}
```

**File:** docs/content/developers/explore/provers.mdx (L25-26)
```text
- **ECDSA** — Includes the full 2/3+1 BEEFY ECDSA validator signatures which are verified on-chain. No special hardware required. Suitable for testnets.
- **SP1** — Delegates signature verification to an SP1 zero-knowledge program, producing a compact Groth16 proof. Requires a CUDA-capable GPU (e.g. RTX 4090 or newer). Used on mainnet for gas efficiency.
```

**File:** docs/content/developers/explore/provers.mdx (L59-63)
```text
## Reputation and the Path to Becoming a Collator

In addition to `$BRIDGE` token rewards, provers automatically earn **Reputation Asset** tokens at a 1:1 ratio with their `$BRIDGE` earnings. This non-transferable reputation score is the primary factor in [Collator selection](/developers/network/collator) — the higher your reputation, the better your chances of being selected as a block-producing Collator for the Hyperbridge network.

This means that running a prover is a direct path to becoming a Collator and earning additional block production rewards. The same Controller account used as the prover's signer accrues reputation, which is evaluated at each session boundary when `pallet-collator-manager` selects the next collator set.
```

**File:** parachain/simtests/src/pallet_beefy_consensus_proofs.rs (L845-863)
```rust
	// 6. Ferdie: Bob's exact bytes. The committed nonce is Bob's account, not Ferdie's, so the
	//    anti-theft `nonce == signer` check in `do_submit_proof` rejects it with
	//    `UnauthorizedProof` — a sniped proof cannot be claimed by another account.
	eprintln!("[stage] submit (Ferdie) — expect UnauthorizedProof (proof bound to Bob's account)");
	let ferdie_result = submit_signed(
		&client,
		&rpc_client,
		subxt::dynamic::tx(
			"BeefyConsensusProofs",
			"submit_proof",
			vec![Value::from_bytes(&ferdie_proof)],
		),
		Keyring::Ferdie,
	)
	.await;
	assert!(
		ferdie_result.is_err(),
		"a proof bound to Bob's account must be rejected when submitted by Ferdie",
	);
```
