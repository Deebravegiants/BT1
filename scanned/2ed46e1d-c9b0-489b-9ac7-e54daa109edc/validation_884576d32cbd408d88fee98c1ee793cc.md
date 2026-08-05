### Title
`handle_bid` under-tracks reserved deposit for multiple simultaneously-winning `SlotRange`s of the same para — `ReservedAmounts` keyed by `(bidder, para)` does not reflect the sum/true requirement across all currently-winning ranges - (File: `polkadot/runtime/common/src/auctions/mod.rs`)

### Summary
`Pallet::handle_bid` stores the bidder's deposit in `ReservedAmounts::<T>` keyed only by `(bidder, para)`, and updates it (reserving the delta or unreserving the surplus) based solely on the amount of the bid just placed. Because a single `(bidder, para)` pair can simultaneously hold the top bid in multiple, disjoint `SlotRange` slots of the `Winning` array (the pallet never de-duplicates winning ranges by `para`), a bidder can place a lower-amount bid on a second, non-overlapping range for the same para, causing the pallet to *unreserve* funds down to the new (lower) amount while the earlier, higher-amount winning bid for a different range is still recorded as "winning" in `Winning::<T>`.

### Finding Description
`handle_bid` computes the deposit to hold from `ReservedAmounts::<T>::get((&bidder, para))` and updates it to the amount of the bid just accepted for the specific `range` being bid on, without considering any other range slots in the `Winning` array where the same `(bidder, para)` pair is currently the leading bid. Since `SlotRange` variants can represent disjoint sub-ranges of the lease-period space (e.g. period `0` and periods `1-3`), the same bidder/para combination can be the "winning" entry for two different range slots at once — the code only guards per-slot, comparing the new bid against the previous winner of that one slot (`amount > last.2`), never against other slots held by the same bidder/para.

When the second (lower) bid for a different, non-overlapping range becomes winning, `deposit_held` (the amount from the *previous* bid, potentially for a different range) is compared against `deposit_required` (the new bid's amount only). If the new bid amount is lower than the previously reserved figure, the pallet unreserves the difference and overwrites `ReservedAmounts` with the new, smaller value — even though the earlier, larger winning bid for the other range slot in `Winning::<T>` is still on the books and could still be selected by `calculate_winners` at auction end. The bookkeeping invariant "reserved balance == max/sum of currently-winning amounts for that bidder/para" is violated because the storage key drops all range-specific information.

### Impact Explanation
This is a deposit-accounting/bid-integrity bug rather than a direct asset-theft bug: `Currency::reserve`/`unreserve` calls always operate on the bidder's real free balance, so funds are never fabricated or duplicated. The concrete impact is that a bid recorded as "winning" in `Winning::<T>` for one `SlotRange` is no longer guaranteed to be backed by an actual reservation once a second, lower bid for a different range by the same `(bidder, para)` reduces `ReservedAmounts`. If both ranges end up selected by `calculate_winners` at auction finalization (a legitimate outcome, since the DP partition only needs disjoint periods, not distinct bidders/paras), the recorded winning amount for the first range is no longer actually secured against the bidder's balance, undermining the purpose of requiring reservation to back auction bids. This could allow a bidder to "win" a slot at a nominal price without maintaining sufficient locked funds, an integrity defect in the auction's payment-backing guarantee.

### Likelihood Explanation
The precondition is simple and fully attacker-controlled: a signed account calling the public `bid` extrinsic (which forwards to `handle_bid`) with two bids on non-overlapping `SlotRange`s for the same `para`, where the second, later-winning bid has a smaller amount than the first. No privileged origin, proxy, or special setup beyond ordinary account balance is required, and it is repeatable in any active auction with `SampleLength`/`EndingPeriod` allowing several bid rounds. The main determining factor for whether this becomes de facto exploitable is the final `Leaser::lease_out`/settlement logic; regardless, the intra-auction invariant regarding reserved-vs-committed amounts is demonstrably violated by this sequence.

### Recommendation
Track deposits by `(bidder, para, range)` or recompute the required deposit as the maximum (or sum, depending on intended semantics of multi-range wins) over all `Winning::<T>` slots currently held by that `(bidder, para)` pair before deciding how much to unreserve, instead of comparing only against the amount of the bid just placed.

### Proof of Concept
Rust unit/invariant test in `polkadot/runtime/common/src/auctions/tests.rs`:
1. Start an auction with 4 lease periods (`SlotRange::SLOT_RANGE_COUNT` = 10 possible ranges).
2. As bidder `1`, call `bid(para=X, first_slot=0, last_slot=0, amount=100)` — becomes winning for the single-period range; assert `Balances::reserved_balance(1) == 100` and `ReservedAmounts::<T>::get((1, X)) == Some(100)`.
3. As bidder `1`, call `bid(para=X, first_slot=1, last_slot=3, amount=10)` on a disjoint range that has no prior bidder — this becomes winning for that range slot; observe `ReservedAmounts::<T>::get((1, X))` is overwritten to `10` and `Balances::reserved_balance(1)` drops to `10`.
4. Assert (expected to fail, proving the bug): `Balances::reserved_balance(1) >= 100` (the amount still recorded as winning for the first range in `Winning::<T>`), i.e., the invariant "reserved balance always covers every currently-winning bid amount for that bidder/para" is broken.
5. Optionally, run `calculate_winners` on the resulting `Winning` state and confirm both ranges (with amounts 100 and 10) can be selected as winners simultaneously while only 10 is actually reserved. [1](#0-0)

### Citations

**File:** polkadot/runtime/common/src/auctions/mod.rs (L72-78)
```rust
// Winning data type. This encodes the top bidders of each range together with their bid.
type WinningData<T> = [Option<(<T as frame_system::Config>::AccountId, ParaId, BalanceOf<T>)>;
	SlotRange::SLOT_RANGE_COUNT];
// Winners data type. This encodes each of the final winners of a parachain auction, the parachain
// index assigned to them, their winning bid and the range that they won.
type WinnersData<T> =
	Vec<(<T as frame_system::Config>::AccountId, ParaId, BalanceOf<T>, SlotRange)>;
```
