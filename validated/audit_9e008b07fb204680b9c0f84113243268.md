## Title
Permissionless `fund_message` allows adding funds to already-delivered or already-timed-out requests/responses, permanently losing the caller's funds — ([File: modules/pallets/ismp/src/lib.rs])

### Summary
`pallet-ismp`'s `fund_message` extrinsic — the on-chain analog of Paladin's `increaseQuestDuration()` — increases the fee attached to a request/response commitment without verifying that the underlying message is still "alive" (i.e., not yet delivered and not yet timed out). Just as `increaseQuestDuration()` extends a quest that may already be in the past, `fund_message` lets anyone top up the fee on a message whose lifecycle has effectively ended, and the added funds become unrecoverable.

### Finding Description
`fund_message` is a signed, permissionless extrinsic that looks up the stored commitment metadata and blindly increments `metadata.fee.fee` after transferring the caller's funds to `RELAYER_FEE_ACCOUNT`: [1](#0-0) 

The doc-comment itself acknowledges the exact failure mode the external report describes for `increaseQuestDuration()`: "Should not be called on a message that has been completed (delivered or timed-out) as those funds will be lost forever" — but no code enforces this invariant; the only guard is `RequestCommitments`/`ResponseCommitments` still containing an entry.

Critically, on successful delivery the request handler (`modules/ismp/core/src/handlers/request.rs::handle`) never deletes the request commitment — it only stores a request *receipt* via `store_request_receipt`, leaving `RequestCommitments` (and thus `metadata.fee`) intact indefinitely for delivered requests: [2](#0-1) 

The commitment is deleted only in the timeout path via `delete_request_commitment`: [3](#0-2) 

This means for any request that was already delivered to its destination (the common, successful case), `fund_message` will happily accept new funds forever, since `RequestCommitments::<T>::get(commitment)` still returns `Some`. There is also a narrower window on the timeout path between a message timing out on the destination and the timeout being processed on the source, during which `fund_message` can also be called on a message that is effectively dead.

### Impact Explanation
This is directly analogous to the reported bug class: a duration/fee-extension function that fails to check whether the underlying object (quest / message) is already past its useful lifecycle. Funds sent via `fund_message` to a delivered request are permanently locked — no relayer or module has any reason or mechanism to claim a fee bump on a message that was already delivered and already paid for, so the transferred tokens are effectively burned. This is a fund-loss bug reachable by any unprivileged, signed extrinsic caller.

### Likelihood Explanation
Likelihood is driven purely by user/relayer error or a UI bug (e.g., a frontend/relayer script calling `fund_message` on a stale commitment cache), not by malicious exploitation for profit — this mirrors the "Acknowledged" / Medium disposition Paladin gave to the original `increaseQuestDuration()` finding. It requires no special privileges and can happen any time between message delivery and eventual pruning of `RequestCommitments`/`ResponseCommitments`.

### Recommendation
Add an explicit liveness check in `fund_message` before transferring funds and mutating `metadata.fee.fee`: reject the call if a request receipt already exists for the request (i.e., it has been delivered) or if the response/request `timeout_timestamp` has already elapsed relative to the current host timestamp, mirroring the check Paladin implemented for `increaseQuestDuration()` (reverting once the period is already in the past / the quest is over).

### Proof of Concept
1. Source chain dispatches a `PostRequest` `R` with `nonce = N`, storing `RequestCommitments[hash(R)] = metadata { fee: F, ... }`.
2. A relayer delivers `R` to the destination chain and its module successfully processes `on_accept` — no deletion of `RequestCommitments[hash(R)]` occurs on the source chain (only a receipt entry is stored on the destination, and on the source, `RequestCommitments` is unaffected by delivery at all).
3. Any account later calls `fund_message(FundMessageParams { commitment: MessageCommitment::Request(hash(R)), amount: X })`.
4. The call succeeds: `X` tokens are transferred from the caller to `RELAYER_FEE_ACCOUNT`, and `metadata.fee.fee` is incremented by `X`, even though `R` was already fully delivered/processed and no relayer will ever be paid this incremental amount.
5. The caller's `X` tokens are permanently stuck, matching the "funds lost forever" risk explicitly called out in the function's own doc-comment.

Note: I was unable to fully verify (within available tool budget) whether `pallet-ismp-relayer`'s fee-accumulation proof logic could later read this bumped `fee.fee` value and pay it out to a relayer who re-submits a state proof after the bump (which would change this from "funds frozen" to a possible double-payment/fee-theft vector). This would require reviewing `modules/pallets/relayer/src/lib.rs`, which was not inspected in this pass — flagging as an open question for further investigation.

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

**File:** modules/ismp/core/src/handlers/request.rs (L95-127)
```rust
	let mut total_weights = Weight::zero();
	let result = msg
		.requests
		.into_iter()
		.map(|request| {
			let wrapped_req = Request::Post(request.clone());
			let mut lambda = || {
				let cb = router.module_for_id(request.to.clone())?;
				// Re-check the receipt right before dispatch. The up-front pass above
				// runs before any callback executes; a prior request's on_accept in
				// this same batch could have stored a receipt for this request
				// (directly or by re-entering the handler), and we must not invoke
				// on_accept a second time.
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
				});
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
				Ok(res)
			};
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L106-112)
```rust
					// Delete commitment to prevent rentrancy attack
					let meta = host.delete_request_commitment(&request)?;
					let mut signer = None;
					// If it was a routed request delete the receipt
					if host.host_state_machine() != post.source {
						signer = host.delete_request_receipt(&request).ok();
					}
```
