## Analysis Result

Based on the investigation, the closest reachable analog to the "Batch Fee Multiplier Cap Bypassed With Multiple Calls" bug class is in `pallet-beefy-consensus-proofs`, where the treasury reward paid per accepted consensus proof is a **flat, admin-configured amount** rather than one scaled to the amount of "work" (blocks/height advanced) the proof actually represents — mirroring the original report's core flaw of a per-call reward that does not properly account for the magnitude of the batch being processed, letting a permissionless caller multiply their payout by splitting one large state advance into many minimal ones.

### Title
Flat Per-Proof Treasury Reward Lets a Prover Multiply Payouts by Splitting Consensus Advances into Minimal Increments - ([File: modules/pallets/beefy-consensus-proofs/src/lib.rs])

### Summary
`pallet-beefy-consensus-proofs::submit_proof` is a public, signed extrinsic that pays the submitter a reward from the treasury whenever a proof "advances state" (a new authority-set rotation or new dispatched messages since the last rewarded proof). The reward is `ProofReward` (a single, flat, governance-set `BalanceOf<T>` value) multiplied only by a decreasing position curve for uncle provers — it is never scaled by how many parachain heights, authority-set rotations, or bytes of new messaging work the proof actually proves.

### Finding Description
`ProofReward` is stored as a flat value with no dependency on the magnitude of progress a proof represents: [1](#0-0) 

The only gate on whether a proof qualifies for a reward is a boolean "did anything change" check (`NoNewWork`), not a magnitude check: [2](#0-1) 

The reward transfer itself just reads the flat `ProofReward` base and applies the position curve — there is no factor for `latest_height - previous_height` or count of new dispatched messages: [3](#0-2) 

`submit_proof` is callable by any signed account (no admin/privileged origin), and it is the reward payee: [4](#0-3) 

This is structurally the same defect as the Polygon report: a per-call incentive that is supposed to be proportional to the "batch" (there, number of L2 batches verified; here, number of parachain heights/messages proven) is instead capped/priced *per call*, so a rational actor can split one legitimate large advance into the minimum number of individually-qualifying small advances (e.g., one height + one new message each) to collect `ProofReward` many times over instead of once, extracting far more from the treasury than the pallet's economic model intends. Contrast this with the sibling `consensus-incentives` pallet, which correctly scales reward by `(latest_height - baseline) * cost_per_block` — `beefy-consensus-proofs` has no equivalent scaling.

### Impact Explanation
An account able to produce valid BEEFY/SP1 proofs (a normal, non-privileged network participant, not an admin/governance actor) can repeatedly submit minimally-advancing proofs instead of batching all pending progress into one proof, multiplying the treasury payout it receives for the same underlying finality/messaging progress. Over time this drains `TreasuryPalletId`'s funds faster than intended and distorts the incentive design (a large, useful piece of work earns the same `ProofReward` as many trivial ones), potentially exhausting the treasury and starving legitimate reward payouts (Medium impact, direct fund loss to the protocol treasury).

### Likelihood Explanation
Medium. Exploiting this requires only the ability to generate legitimate BEEFY/SP1 consensus proofs (already required to participate as a prover) and to submit them more frequently/in smaller increments rather than batching, which is entirely within a normal relayer's discretion and gas/verification-cost budget — analogous to the original report's conclusion that the attack is technically trivial but its profitability depends on whether the extra proof-submission and (for SP1) proving/verification cost outweighs the duplicated flat reward. Because SP1 proving is comparatively expensive, the attack is more likely to be economically attractive for cheap "naive" proofs (`PROOF_TYPE_NAIVE`) where the marginal cost of submitting many small proofs is low.

### Recommendation
Scale `ProofReward` payouts to the actual amount of proven progress, analogous to `pallet-consensus-incentives`'s `Reward = (LatestHeight - PreviousHeight) * CostPerBlock` model:
- Track a height/messages watermark per submitter's proof and pay `ProofReward` scaled by `latest_height - previous_rewarded_height` (and/or by whether new messages were proven), rather than a flat amount per accepted proof.
- Alternatively, rate-limit rewarded proofs per submitter per block/time-window so splitting into many small proofs cannot yield more total reward than one proof covering the same span.

### Proof of Concept
Conceptual sequence (not executed, given no direct code execution capability in this analysis):
1. Attacker controls a valid consensus state advancing hyperbridge's view of the coprocessor chain from height H to H+100, with new ISMP messages dispatched throughout that range.
2. Instead of submitting one `submit_proof` call proving the full H→H+100 advance (and collecting `ProofReward` once), the attacker submits 100 separate proofs, each advancing by 1 height and including at least one new message, so each call passes the `NoNewWork` check.
3. Each of the 100 calls independently qualifies as a "first proof" at its respective height (`pay_position_reward` pays `ProofReward` at position 0 each time), yielding `100 × ProofReward` from the treasury instead of `1 × ProofReward` for equivalent finality/messaging progress.

**Uncertainty note:** I could not fully trace `verify_and_apply`/`settle_first_proof` (the functions that decide whether a given SP1/naive proof is accepted as advancing exactly one height vs. a range) within the available context, so I cannot confirm the exact minimum granularity (e.g., whether a single proof can be constructed to advance by just 1 height, or whether SP1 proof generation cost makes fine-grained splitting uneconomical). This would need to be verified directly in the full `beefy-consensus-proofs` source before treating this as confirmed rather than a plausible analog.

### Citations

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L165-168)
```rust
	/// Base reward amount paid to position-0 (first) provers. Uncle rewards are derived from
	/// this value by applying [`RewardCurve`].
	#[pallet::storage]
	pub type ProofReward<T: Config> = StorageValue<_, BalanceOf<T>, ValueQuery>;
```

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L252-254)
```rust
		/// The proof does not advance state: no authority set rotation and no new
		/// messages since the last rewarded proof.
		NoNewWork,
```

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

**File:** modules/pallets/beefy-consensus-proofs/src/lib.rs (L731-746)
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
```
