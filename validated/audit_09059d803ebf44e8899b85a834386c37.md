### Title
Late `fund_message` top-ups on an already-delivered/timed-out request or response are permanently locked - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`Pallet::fund_message` lets any signed account add more relayer fee to an existing request or response commitment by mutating the stored `RequestMetadata.fee.fee` field. The call only checks that the commitment metadata still exists in `RequestCommitments`/`ResponseCommitments`; it does not check whether the message has already been delivered (and its fee already accumulated/claimed by a relayer) or timed out (and its fee already refunded). Funds transferred via a late `fund_message` call are added to metadata that no relayer will ever read again, so they become permanently stuck in the `RELAYER_FEE_ACCOUNT`.

### Finding Description
`fund_message` is a public, unprivileged extrinsic (`ensure_signed(origin)?`) reachable by any user: [1](#0-0) 

The function pulls the metadata for the given commitment, transfers `message.amount` from the caller into `RELAYER_FEE_ACCOUNT`, and increments `metadata.fee.fee` before writing it back:

```rust
let metadata = match message.commitment {
    MessageCommitment::Request(commitment) => RequestCommitments::<T>::get(commitment),
    MessageCommitment::Response(commitment) => ResponseCommitments::<T>::get(commitment),
};
let Some(mut metadata) = metadata else {
    return Err(Error::<T>::MessageNotFound.into());
};
T::Currency::transfer(&account, &RELAYER_FEE_ACCOUNT.into_account_truncating(), message.amount, Preservation::Expendable)?;
match message.commitment {
    MessageCommitment::Request(commiment) => {
        metadata.fee.fee += message.amount;
        RequestCommitments::<T>::insert(commiment, metadata);
    },
    ...
}
```

The pallet's own doc comment acknowledges the risk but does not enforce it in code:

> "Should not be called on a message that has been completed (delivered or timed-out) as those funds will be lost forever." [2](#0-1) 

The relayer fee-claim path (`pallet_ismp_relayer::accumulate`) reads the fee straight out of `RequestCommitments`/the source-chain commitment via a state proof, and marks the commitment `claimed = true` after paying it out — a single, all-or-nothing settlement per commitment, mirroring the `rewardsClaimedForToken[tokenId][tdeId]` pattern in the reported `YsDistributor` bug: [3](#0-2) 

Because `RequestCommitments`/`ResponseCommitments` entries are not proven to be removed on delivery (they still return `Some(metadata)` after a request is delivered, as seen for GET responses where `claimed: true` is set but the entry is left in storage), `fund_message` will happily accept and record additional fee on a commitment whose one-shot relayer claim already fired. `state-coprocessor` even inserts response commitments with `claimed: true` directly: [4](#0-3) 

Once `claimed` is true (or once a timeout refund has already zeroed/consumed the fee accounting for that commitment), no code path re-reads the bumped `fee.fee` value to pay out a second time — a relayer's proof-based claim for a commitment is single-shot. Any amount added after that point sits in `RELAYER_FEE_ACCOUNT` with no future consumer, exactly like the sherlock `YsDistributor.depositMultipleToken` scenario where a second deposit made after `claimRewards` has already fired for a TDE becomes unclaimable.

### Impact Explanation
Any unprivileged account (a user, a relayer trying to "sponsor" delivery, or an automated resubmission script) that calls `fund_message` against a commitment that has already been delivered/claimed or timed-out/refunded permanently loses those funds. This is a straightforward, transaction-triggerable, permanent freezing/loss of user funds in the relayer fee account, satisfying the "permanent freezing of funds" bar. It requires only ordinary use of a public, documented extrinsic and a small race/misuse window (adding fee slightly after delivery, or funding a request whose deadline/timeout already passed), so this is not a purely theoretical edge case.

### Likelihood Explanation
Likelihood is moderate: it requires a user (or automated relayer helper) to call `fund_message` on a commitment concurrently with, or shortly after, that commitment's delivery/claim or timeout. Given `fund_message` exists specifically to let third parties bump fees on slow-to-deliver messages, and delivery/timeout timing is not synchronized with fee top-up calls, this race is realistically triggerable, especially under network congestion or by naive bots that always try to top up stalled-looking messages right before they get delivered.

### Recommendation
Before crediting the fee, `fund_message` should verify the message has not already reached a terminal state:
- For requests: check that the request has not been delivered (e.g., no `RequestReceipts` entry / `Responded` marker) and has not timed out (`timeout_timestamp` not yet passed) before accepting funds; otherwise revert.
- For responses: check that the response has not already been delivered/claimed.
Alternatively, remove `RequestCommitments`/`ResponseCommitments` entries eagerly on delivery/timeout so `fund_message`'s existing `MessageNotFound` check naturally rejects late top-ups, and refund the caller if a race is detected within the same block.

### Proof of Concept
1. User A dispatches a request via `IsmpDispatcher::dispatch_request`, creating a `RequestCommitments` entry with some fee.
2. A relayer delivers the request on the destination chain and later calls `pallet_ismp_relayer::accumulate` (via `pallet_ismp_relayer::Pallet::accumulate`, `modules/pallets/relayer/src/accumulate.rs:48-170`) to claim the fee, which is paid out based on the state-proof value of `fee.fee` at the time of the call, and the commitment is marked `claimed = true` (`RequestCommitments::<T>::insert(req, leaf_meta)` at line 156).
3. Before the `claimed` flag or fee state is externally visible / synchronized (or on a commitment already delivered but not yet pruned), user B calls `fund_message` with the same commitment, transferring more funds into `RELAYER_FEE_ACCOUNT` and bumping `metadata.fee.fee` (`modules/pallets/ismp/src/lib.rs:445-480`).
4. No relayer will ever claim this additional amount again for that commitment (accumulate only credits the fee once per commitment, gated by proof + `claimed` idempotency), so user B's added funds sit permanently in `RELAYER_FEE_ACCOUNT` with no path to reclaim them.

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

**File:** modules/pallets/relayer/src/accumulate.rs (L149-161)
```rust
		for req in withdrawal_proof.commitments {
			if !claimed_commitments.contains(&req) {
				continue;
			}
			match RequestCommitments::<T>::get(req) {
				Some(mut leaf_meta) => {
					leaf_meta.claimed = true;
					RequestCommitments::<T>::insert(req, leaf_meta)
				},
				// Unreachable
				None => {},
			}
		}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L213-226)
```rust
		let leaf_index_and_pos = <T as Config>::Mmr::push(Leaf::GetResponse(get_response));
		let meta = FeeMetadata::<T> { payer: [0u8; 32].into(), fee: Default::default() };

		pallet_ismp::child_trie::ResponseCommitments::<T>::insert(
			commitment,
			RequestMetadata {
				offchain: LeafIndexAndPos {
					leaf_index: leaf_index_and_pos.index,
					pos: leaf_index_and_pos.position,
				},
				fee: meta,
				claimed: true,
			},
		);
```
