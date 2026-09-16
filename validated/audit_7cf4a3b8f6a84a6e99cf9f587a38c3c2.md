## Title
Cross-Function Signature Replay Between `withdraw_fees` and `accumulate_fees` Beneficiary Redirect Due to Identical Unscoped Signed Payloads - (File: `modules/pallets/relayer/src/withdrawal.rs`, `modules/pallets/relayer/src/accumulate.rs`)

### Summary
`pallet-relayer` signs two distinct privileged operations — a full-balance `withdraw_fees` disbursement and an `accumulate_fees` beneficiary redirect — using byte-for-byte identical message encodings and a single shared per-`(address, chain)` nonce counter, with no function selector or domain tag distinguishing them. A signature a relayer creates for one purpose validates and executes for the other, exactly mirroring the reported `RewardPool.burn()`/`move()` confusion where "the only substantial difference" between two operations is destination/effect while the signed payload is identical and separation relies solely on a nonce.

### Finding Description
`withdraw_fees` signs and verifies: [1](#0-0) 

`accumulate_fees`'s beneficiary redirect path signs and verifies: [2](#0-1) 

When `beneficiary` is `Some(...)`, `message(nonce, dest_chain, beneficiary)` and `beneficiary_message(nonce, state_machine, beneficiary)` encode the exact same tuple `(u64, StateMachine, Vec<u8>)` via SCALE and hash it with the same `keccak_256`, producing an identical digest for the same `(nonce, chain, beneficiary)` triple. Both call sites also read/increment the **same** `Nonce<T>` storage double-map keyed by `(address, StateMachine)`: [3](#0-2) [4](#0-3) 

Both dispatchables are unsigned (`ensure_none`) and reachable by any unprivileged caller/relayer node: [5](#0-4) 

Because the signed payload and the nonce space are indistinguishable between the two functions, a valid relayer signature produced for a small-scope `accumulate_fees` beneficiary redirect (intended only to redirect one batch's accrued fee) is also a valid signature to authorize `withdraw_fees`, which drains the *entire* currently accrued `Fees` balance for that `(address, chain)` to the same beneficiary: [6](#0-5) 

This is the same root cause the external report flags for `RewardPool`: two operations with materially different effects (partial/scoped redirect vs. full balance transfer) share one signature scheme with no function selector embedded, and the only "protection" is nonce alignment, which is fragile — an attacker who observes an in-flight, not-yet-included `accumulate_fees` extrinsic (submitted as an unsigned, publicly gossiped transaction) can extract `(nonce, state_machine, beneficiary, signature)` and front-run it as a `withdraw_fees` call before the nonce is consumed.

### Impact Explanation
Successful exploitation drains the entire `Fees<T>` balance accrued for a relayer on a given destination chain to a beneficiary address, using a signature the relayer only intended to authorize a scoped fee-redirect for one delivery batch. This is unauthorized fund movement/redirection stemming from a signature-scheme design flaw reachable by any party that can observe or relay the unsigned extrinsic — satisfying the "concrete theft" bar since the whole pending relayer balance can be disbursed earlier and to a possibly different recipient/timing than the relayer intended.

### Likelihood Explanation
Both `accumulate_fees` and `withdraw_fees` are `ensure_none` (unsigned) extrinsics, submittable by anyone once a valid signed payload exists; unsigned extrinsics with beneficiary-redirect signatures are gossiped in the transaction pool before inclusion, giving an attacker a window to extract and replay the signature into the sibling function. The relayer tooling routinely produces exactly this beneficiary-redirect signature during normal fee accumulation: [7](#0-6) 

### Recommendation
Include a function-specific domain tag/selector in both signed payloads (e.g., prefix `message()` and `beneficiary_message()` with distinct constants such as `b"WITHDRAW_FEES"` vs `b"ACCUMULATE_BENEFICIARY"`), and/or maintain separate nonce counters per function so a signature for one call can never satisfy the other, consistent with the external report's recommendation to bind signatures to a specific function selector.

### Proof of Concept
1. Relayer signs `beneficiary_message(nonce=N, chain=C, beneficiary=B)` intending to submit it inside a `WithdrawalProof.beneficiary_details` for `accumulate_fees`, per `tesseract/messaging/fees/src/lib.rs:392-397`.
2. The unsigned `accumulate_fees` extrinsic containing `(N, C, B, sig)` is broadcast to the network and sits in the mempool.
3. An observer extracts `(N, C, B, sig)` and immediately submits `withdraw_fees(WithdrawalInputData { signature: sig, dest_chain: C, beneficiary: Some(B) })`.
4. `Pallet::withdraw` computes `message(N, C, Some(B))`, which equals the same digest signed in step 1, verifies successfully, and disburses the relayer's entire `Fees::<T>::get(C, address)` balance to `B` — consuming nonce `N`.
5. The original `accumulate_fees` transaction, still referencing nonce `N`, now fails (nonce mismatch), but the relayer's full balance has already left via the replayed `withdraw_fees` call.

### Citations

**File:** modules/pallets/relayer/src/withdrawal.rs (L88-89)
```rust
		let nonce = Nonce::<T>::get(address.clone(), withdrawal_data.dest_chain);
		let msg = message(nonce, withdrawal_data.dest_chain, withdrawal_data.beneficiary.clone());
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L116-133)
```rust
		let available_amount = Fees::<T>::get(withdrawal_data.dest_chain, address.clone());

		if available_amount <
			Self::min_withdrawal_amount(withdrawal_data.dest_chain)
				.unwrap_or(MinWithdrawal::get())
		{
			Err(Error::<T>::NotEnoughBalance)?
		}

		let dispatcher = <T as Config>::IsmpHost::default();

		Nonce::<T>::try_mutate(address.clone(), withdrawal_data.dest_chain, |value| {
			*value += 1;
			Ok::<(), ()>(())
		})
		.map_err(|_| Error::<T>::ErrorCompletingCall)?;

		let beneficiary_address = withdrawal_data.beneficiary.clone().unwrap_or(address.clone());
```

**File:** modules/pallets/relayer/src/withdrawal.rs (L192-197)
```rust
pub fn message(nonce: u64, dest_chain: StateMachine, beneficiary: Option<Vec<u8>>) -> [u8; 32] {
	if let Some(beneficiary) = beneficiary {
		return sp_io::hashing::keccak_256(&(nonce, dest_chain, beneficiary).encode());
	}
	sp_io::hashing::keccak_256(&(nonce, dest_chain).encode())
}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L106-111)
```rust
		// Let's verify the beneficiary address
		let beneficiary_address = if let Some((beneficiary_address, signature)) =
			withdrawal_proof.beneficiary_details
		{
			let nonce = Nonce::<T>::get(&delivery_address, state_machine);
			let msg = beneficiary_message(nonce, state_machine, &beneficiary_address);
```

**File:** modules/pallets/relayer/src/accumulate.rs (L309-315)
```rust
pub fn beneficiary_message(
	nonce: u64,
	state_machine: StateMachine,
	beneficiary: &[u8],
) -> [u8; 32] {
	sp_io::hashing::keccak_256(&(nonce, state_machine, beneficiary).encode())
}
```

**File:** modules/pallets/relayer/src/lib.rs (L350-368)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight({1_000_000})]
		pub fn accumulate_fees(
			origin: OriginFor<T>,
			withdrawal_proof: WithdrawalProof,
		) -> DispatchResult {
			ensure_none(origin)?;
			Self::accumulate(withdrawal_proof)
		}

		#[pallet::call_index(1)]
		#[pallet::weight({1_000_000})]
		pub fn withdraw_fees(
			origin: OriginFor<T>,
			withdrawal_data: WithdrawalInputData,
		) -> DispatchResult {
			ensure_none(origin)?;
			Self::withdraw(withdrawal_data)
		}
```

**File:** tesseract/messaging/fees/src/lib.rs (L392-397)
```rust
			let beneficiary_details = if cross_chain_type {
				let beneficiary = source.address();
				let prehash = beneficiary_message(nonce, source_chain, &beneficiary);
				let details = Some((beneficiary, dest.sign(&prehash)));
				nonce += 1;
				details
```
