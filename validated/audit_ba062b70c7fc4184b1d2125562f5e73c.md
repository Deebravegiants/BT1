Audit Report

## Title
`handle_bid` under-tracks reserved deposit for multiple simultaneously-winning `SlotRange`s of the same para — `ReservedAmounts` keyed by `(bidder, para)` does not reflect the sum/true requirement across all currently-winning ranges - (File: `polkadot/runtime/common/src/auctions/mod.rs`)

## Summary
`Pallet::handle_bid` persists a bidder's on-chain reservation in `ReservedAmounts::<T>` keyed only by `(bidder, para)`, and adjusts it (reserve/unreserve) using solely the amount of the single bid just accepted for the one `SlotRange` slot being processed. Because the `Winning` array indexes bids per `SlotRange` slot and only invalidates *intersecting* prior entries for the same `(bidder, para)`, two disjoint (non-overlapping) ranges for the same bidder/para can remain simultaneously "winning," while the stored deposit reflects only the most-recently-processed bid amount rather than the true aggregate requirement across all currently-winning slots.

## Finding Description
`SlotRange` encodes sub-ranges over the lease-period space (e.g., a single-period range and a disjoint multi-period range), and the `Winning` array stores one optional `(AccountId, ParaId, Balance)` entry per `SlotRange::SLOT_RANGE_COUNT` slot, as reflected in the `WinningData<T>` type definition. [1](#0-0) 

When `handle_bid` processes a new bid, it updates the specific slot in the `Winning` array corresponding to the bid's `range`, comparing only against the previous occupant of that same slot (`amount > last.2`). Any existing entry for the same `(bidder, para)` pair occupying a *different* slot is left untouched unless it intersects the newly-bid range. This means a bidder can legitimately hold the top bid in two disjoint `SlotRange` slots for the same para at once (e.g., period `0` alone at amount 100, and periods `1-3` at amount 10).

The deposit bookkeeping, however, is keyed only by `(bidder, para)` and recomputed from the amount of the single bid just placed (`deposit_required = amount`), compared against the previously stored `deposit_held` from `ReservedAmounts::<T>::get((&bidder, para))`. Because this key does not include the range, submitting the second, lower-amount bid on the disjoint range overwrites the stored deposit and triggers an `unreserve` down to the new lower amount, even though the earlier higher-amount bid for the other, still-winning slot has not been superseded or removed from `Winning::<T>`. The per-slot intersection check that clears stale winners only fires for overlapping ranges, so it does not protect against this disjoint-range scenario — the storage design has no mechanism to track or sum deposits across multiple simultaneously-winning non-overlapping slots for the same bidder/para.

## Impact Explanation
This breaks the intended invariant that a bidder's reserved balance backs every bid currently recorded as "winning" in `Winning::<T>`. Since `calculate_winners`'s partition algorithm only requires selected ranges to be disjoint in lease periods (not distinct in bidder/para), both the higher and lower bids for the same para could be selected as final winners at auction settlement, while only the smaller amount is actually reserved against the bidder's balance. This is an accounting/integrity defect in the auction's payment-backing guarantee — it does not fabricate funds (all `reserve`/`unreserve` calls act on real balances), but it allows a "winning" bid amount to be unbacked by an actual reservation, undermining the auction's deposit-security assumption.

## Likelihood Explanation
The precondition is trivial and fully attacker-controlled: any signed account can call the public `bid` extrinsic twice during an active auction, targeting two disjoint `SlotRange`s for the same `para`, with the second bid amount lower than the first. No privileged origin or special setup is required beyond having sufficient balance to place the first bid, and the scenario is repeatable across any auction round with multiple bidding rounds.

## Recommendation
Track reserved deposits per `(bidder, para, range)`, or before adjusting `ReservedAmounts` on a new winning bid, recompute the required deposit as the maximum (or sum, per intended multi-range-win semantics) across all `Winning::<T>` slots currently held by that `(bidder, para)` pair, rather than comparing only against the amount of the bid just placed.

## Proof of Concept
1. Start an auction with 4 lease periods.
2. As bidder `1`, call `bid(para=X, first_slot=0, last_slot=0, amount=100)`; assert `Balances::reserved_balance(1) == 100` and `ReservedAmounts::<T>::get((1, X)) == Some(100)`.
3. As bidder `1`, call `bid(para=X, first_slot=1, last_slot=3, amount=10)` on a disjoint range with no prior bidder; observe `ReservedAmounts::<T>::get((1, X))` overwritten to `10` and `Balances::reserved_balance(1)` dropping to `10`, while the period-`0` entry for bidder `1`/para `X` at amount `100` remains in `Winning::<T>`.
4. Assert `Balances::reserved_balance(1) >= 100` — this fails, proving the reserved balance no longer covers the still-winning bid recorded in `Winning::<T>`.
5. Optionally run `calculate_winners` on the resulting `Winning` state to confirm both disjoint ranges (100 and 10) can be selected as final winners while only 10 is actually reserved.

### Citations

**File:** polkadot/runtime/common/src/auctions/mod.rs (L72-74)
```rust
// Winning data type. This encodes the top bidders of each range together with their bid.
type WinningData<T> = [Option<(<T as frame_system::Config>::AccountId, ParaId, BalanceOf<T>)>;
	SlotRange::SLOT_RANGE_COUNT];
```
