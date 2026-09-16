## Title
`fund_message` allows users to permanently lose funds by topping up already-claimed/delivered ISMP requests - ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet-ismp::fund_message` lets *any* unprivileged signed account add fee to an existing request/response commitment by reading the stored `RequestMetadata`/leaf metadata, incrementing `fee.fee`, and writing it back. The function's own doc-comment warns "Should not be called on a message that has been completed (delivered or timed-out) as those funds will be lost forever" — but the code performs no check against `metadata.claimed` (or against delivery/timeout state) before accepting payment and mutating storage. This mirrors the reported bug class: a value relied upon for later payout (`fee.fee`) is mutated/topped-up by a normal user action without validating that the mutation will ever actually be consulted by the paying logic, so the user's added value silently becomes unusable.

### Finding Description
`fund_message` is a public, unsigned-origin-checked (`ensure_signed`) extrinsic reachable by any user: [1](#0-0) 

It fetches `RequestCommitments::<T>::get(commitment)` (or `ResponseCommitments`), which contains a `RequestMetadata { offchain, fee, claimed }` struct — the same struct consulted by `pallet-ismp-relayer::accumulate` when a relayer proves delivery: [2](#0-1) 

`accumulate()` explicitly filters out any commitment whose `leaf_meta.claimed == true` **before** ever reading `fee.fee` from source-chain state: [3](#0-2) 

So once a request has already been delivered and its fee accumulated (`claimed = true`), the fee-reading path can never again visit that commitment — the relayer accumulation logic treats it as fully settled and permanently ignores it. `fund_message`, however, has no equivalent guard: it does not check `metadata.claimed`, nor whether the request/response has already been delivered or timed out. A user can call `fund_message` on a commitment whose `claimed` flag is already `true` (or whose message has already timed out and been deleted-refunded through a different code path), transferring real currency to `RELAYER_FEE_ACCOUNT` and bumping `metadata.fee.fee`, while no relayer will ever read or claim that incremented value because the accumulation path has already excluded/settled that commitment. The transferred tokens sit in `RELAYER_FEE_ACCOUNT` with no code path that ever pays them out for that already-claimed commitment.

This is the same root-cause pattern as the report: a downstream reward/fee-accounting mechanism consults a stored value at a fixed point (staking snapshot / `claimed` flag) and a user-triggered top-up action (`increaseLiquidity` / `fund_message`) mutates related state without keeping that consultation point in sync, so the increment is economically wasted.

### Impact Explanation
Funds transferred via `fund_message` on an already-claimed or already-completed request are moved out of the payer's account into `RELAYER_FEE_ACCOUNT` but become permanently unclaimable by any relayer, since `accumulate()` skips any commitment already marked `claimed`. This is a genuine, on-chain, unprivileged-triggerable permanent loss of user funds (not merely a lost expectancy as in the liquidity-staking analog) — the docstring on the function itself acknowledges the danger ("those funds will be lost forever") but the code enforces no protection against it, meaning a confused or rushed user (e.g., attempting to bump gas/relayer incentive on a request they believe is still pending) permanently forfeits the additional fee. This satisfies "permanent freezing of funds" for a real user-submitted extrinsic.

### Likelihood Explanation
Likelihood is Medium: this requires user error (calling `fund_message` on a commitment that has already been delivered/claimed or timed out), which is plausible in real usage since request delivery/timeout status is not always visible synchronously to the caller, and there is a natural race between "relayer just delivered and accumulated fees" and "user submits `fund_message` to bump the fee, unaware delivery already completed." There is no malicious precondition required — a normal user transaction is sufficient to trigger the loss.

### Recommendation
Add validation in `fund_message` mirroring the guard already used in `accumulate()`:
- Reject the call (return an error) if `metadata.claimed == true`.
- Additionally reject if the request/response has already been deleted (i.e., it timed out and was already refunded — verify existence beyond simply matching `Some`/`None` if timeout deletion clears the entry, or add an explicit "delivered"/"timed-out" check consistent with how `_requestReceipts`/timeout logic marks completion elsewhere in the codebase).

### Proof of Concept
1. User dispatches a `PostRequest` with `fee = X`, creating `RequestCommitments[commitment] = RequestMetadata { fee: { fee: X }, claimed: false, .. }`.
2. A relayer delivers the request to the destination and calls `pallet-ismp-relayer::accumulate_fees`, which succeeds and sets `RequestCommitments[commitment].claimed = true` (per `modules/pallets/relayer/src/accumulate.rs:149-160`).
3. A user (unaware the request was already delivered/claimed, or attempting a fee top-up they believe is still needed) calls `Ismp::fund_message(origin, FundMessageParams { commitment: MessageCommitment::Request(commitment), amount: Y })`.
4. `fund_message` (`modules/pallets/ismp/src/lib.rs:445-480`) succeeds: `Y` tokens are transferred from the user to `RELAYER_FEE_ACCOUNT`, and `RequestCommitments[commitment].fee.fee += Y` is written — despite `claimed` already being `true`.
5. No future call to `accumulate()` will ever process this commitment again (it is filtered out at line 62-67 of `accumulate.rs` because `claimed == true`), so the additional `Y` tokens are permanently stuck in `RELAYER_FEE_ACCOUNT` and unclaimable by any relayer, a hard loss of the user's `Y` tokens.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L439-480)
```rust
		/// Add more funds to a message (request or response) to be used for delivery and execution.
		///
		/// Should not be called on a message that has been completed (delivered or timed-out) as
		/// those funds will be lost forever.
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().writes(5))]
		#[pallet::call_index(4)]
		pub fn fund_message(
			origin: OriginFor<T>,
			message: FundMessageParams<T::Balance>,
		) -> DispatchResult {
			let account = ensure_signed(origin)?;

			let metadata = match message.commitment {
				MessageCommitment::Request(commitment) => RequestCommitments::<T>::get(commitment),
				MessageCommitment::Response(commitment) =>
					ResponseCommitments::<T>::get(commitment),
			};

			let Some(mut metadata) = metadata else {
				return Err(Error::<T>::MessageNotFound.into());
			};

			T::Currency::transfer(
				&account,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				message.amount,
				Preservation::Expendable,
			)?;

			match message.commitment {
				MessageCommitment::Request(commiment) => {
					metadata.fee.fee += message.amount;
					RequestCommitments::<T>::insert(commiment, metadata);
				},
				MessageCommitment::Response(commiment) => {
					metadata.fee.fee += message.amount;
					ResponseCommitments::<T>::insert(commiment, metadata);
				},
			};

			Ok(())
		}
```

**File:** modules/pallets/ismp/src/dispatcher.rs (L64-78)
```rust
#[derive(codec::Encode, codec::Decode, scale_info::TypeInfo, Clone)]
#[cfg_attr(feature = "std", derive(serde::Deserialize, serde::Serialize))]
#[scale_info(skip_type_params(T))]
pub struct RequestMetadata<T: Config> {
	/// Information about where it's stored in the offchain db
	pub offchain: LeafIndexAndPos,
	/// Other metadata about the request
	pub fee: FeeMetadata<T>,
	/// Has fee been claimed?
	pub claimed: bool,
}

/// This is used for tracking user fee payments for requests
pub type FeeMetadata<T> =
	dispatcher::FeeMetadata<<T as frame_system::Config>::AccountId, <T as Config>::Balance>;
```

**File:** modules/pallets/relayer/src/accumulate.rs (L58-69)
```rust
		// Filter out already-claimed / missing commitments
		withdrawal_proof.commitments = withdrawal_proof
			.commitments
			.into_iter()
			.filter(|req| match RequestCommitments::<T>::get(*req) {
				Some(leaf_meta) => !leaf_meta.claimed,
				// If request commitment does not exist in storage which should not be
				// possible, we skip it
				None => false,
			})
			.collect();
		ensure!(!withdrawal_proof.commitments.is_empty(), Error::<T>::MissingCommitments);
```
