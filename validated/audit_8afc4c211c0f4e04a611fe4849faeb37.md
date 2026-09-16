## Finding: Deposit reservation dropped before new reservation is confirmed in `place_bid`

### Title
Stale bid deposit accounting via premature `unreserve` before `reserve` success in `pallet-intents-coprocessor::place_bid` — ([File: modules/pallets/intents-coprocessor/src/lib.rs])

### Summary
`place_bid` unreserves a filler's existing bid deposit before attempting to reserve the new deposit amount, and only updates the `Bids` storage map after the new reservation succeeds. If the new `reserve` call fails, the function returns an error, but the previously-reserved funds have already been dropped while the old `Bids` entry remains untouched — leaving on-chain accounting that no longer matches the actual reserved balance.

### Finding Description
In `place_bid`, the pallet does: [1](#0-0) 

```
// If a bid already exists, unreserve the old deposit first
if let Some(old_deposit) = Bids::<T>::get(&commitment, &filler) {
    <T as Config>::Currency::unreserve(&filler, old_deposit);
}

let deposit = Self::storage_deposit_fee();

// Reserve the new deposit
<T as Config>::Currency::reserve(&filler, deposit)
    .map_err(|_| Error::<T>::InsufficientBalance)?;

...
Bids::<T>::insert(&commitment, &filler, deposit);
```

This unconditionally drops the "reference" to the old reserved deposit (`unreserve`) before the new one is confirmed acquired (`reserve`). If `reserve` fails with `InsufficientBalance`, the `?` early-returns before `Bids::<T>::insert` runs, so `Bids::<T>::get(&commitment, &filler)` still holds the *old* `old_deposit` value even though those funds are no longer actually reserved (they were unreserved moments earlier). `type Currency: ReservableCurrency<Self::AccountId>` [2](#0-1)  is the standard (non-named) reservable currency, where `reserved` balance is a single pooled counter per account, not tagged per purpose.

Consequences of this stale, phantom deposit entry:
1. `retract_bid` reads the stale `Bids` entry and calls `unreserve(&filler, deposit)` again [3](#0-2) . Since `ReservableCurrency::unreserve` is not purpose-scoped, this call reduces whatever amount is actually in the account's pooled `reserved` balance — even if that balance now backs some other legitimate reservation for the same account (e.g., a genuinely-placed bid on a different commitment, or another pallet's reserve). This lets a filler improperly release collateral that should remain locked.
2. The `Bids` map continues to advertise that the filler has posted `old_deposit` worth of collateral for a commitment, when in reality no funds are held — undermining any downstream logic (bidder selection, slashing on non-fulfillment) that treats a `Bids` entry as proof of posted, at-risk collateral.

### Impact Explanation
This corrupts the deposit-collateral accounting of the phantom-order/bid marketplace in `pallet-intents-coprocessor`, which is directly reachable by any unprivileged signed account via the `place_bid` extrinsic [4](#0-3) . A filler can end up with a bid recorded as deposit-backed while holding no actual reserved funds, and can trigger an `unreserve` call that frees funds reserved for unrelated purposes on the same account. This is a fund-accounting integrity issue in the intent-bidding/escrow subsystem.

### Likelihood Explanation
Triggering the bug only requires calling `place_bid` twice for the same `(commitment, filler)` pair where the second call's `reserve` fails (e.g., attacker transfers away free balance between the two calls, or simply has insufficient free balance for the new deposit while retaining an existing bid). No special privileges are needed — this is directly exploitable by any signed account holding a prior bid.

### Recommendation
Only unreserve the old deposit after the new deposit has been successfully reserved (or reserve the new deposit first and unreserve the old one afterward), so a failed `reserve` call cannot leave `Bids` storage referencing funds that are no longer held. Alternatively, unreserve and update `Bids` atomically only on the success path.

### Proof of Concept
1. Filler calls `place_bid(commitment, user_op)` with sufficient balance; `Bids[commitment, filler] = D1` and `D1` is reserved.
2. Filler transfers/spends free balance so it can't cover a new reservation.
3. Filler calls `place_bid(commitment, user_op2)` again for the same commitment: `unreserve(D1)` runs first, freeing `D1`; the subsequent `reserve(deposit)` fails with `InsufficientBalance` and the call reverts with `Bids[commitment, filler]` still `= D1`.
4. Filler calls `retract_bid(commitment)`: it reads `D1` from storage and calls `unreserve(&filler, D1)` again — this reduces the account's pooled `reserved` balance by up to `D1`, even though no funds are actually reserved for this bid, potentially releasing collateral reserved for another legitimate purpose on the same account. [5](#0-4) [6](#0-5)

### Citations

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L104-105)
```rust
		/// A currency implementation for handling storage deposits
		type Currency: ReservableCurrency<Self::AccountId>;
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L332-338)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::place_bid())]
		pub fn place_bid(
			origin: OriginFor<T>,
			commitment: H256,
			user_op: BoundedVec<u8, ConstU32<1_048_576>>,
		) -> DispatchResult {
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L360-383)
```rust

			// If a bid already exists, unreserve the old deposit first
			if let Some(old_deposit) = Bids::<T>::get(&commitment, &filler) {
				<T as Config>::Currency::unreserve(&filler, old_deposit);
			}

			let deposit = Self::storage_deposit_fee();

			// Reserve the new deposit
			<T as Config>::Currency::reserve(&filler, deposit)
				.map_err(|_| Error::<T>::InsufficientBalance)?;

			// Store the bid in offchain storage
			let bid = Bid { filler: filler.clone(), user_op: user_op.to_vec() };
			let offchain_key = Self::offchain_bid_key(&commitment, &filler);
			offchain_index::set(&offchain_key, &bid.encode());

			// Store deposit amount in onchain storage for discoverability and accurate refunds
			Bids::<T>::insert(&commitment, &filler, deposit);

			Self::deposit_event(Event::BidPlaced { filler, commitment, deposit });

			Ok(())
		}
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L392-414)
```rust
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::retract_bid())]
		pub fn retract_bid(origin: OriginFor<T>, commitment: H256) -> DispatchResult {
			let filler = ensure_signed(origin)?;

			// Get the bid deposit amount
			let deposit = Bids::<T>::get(&commitment, &filler).ok_or(Error::<T>::BidNotFound)?;

			// Unreserve the deposit
			<T as Config>::Currency::unreserve(&filler, deposit);

			// Remove the bid marker from onchain storage
			Bids::<T>::remove(&commitment, &filler);

			// Clear the bid from offchain storage
			let offchain_key = Self::offchain_bid_key(&commitment, &filler);
			offchain_index::clear(&offchain_key);

			Self::deposit_event(Event::BidRetracted { filler, commitment, refund: deposit });

			Ok(())
		}

```
