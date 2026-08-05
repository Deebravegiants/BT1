Audit Report

## Title
Duplicate `NewRaise` entry via `poke` + `contribute` causes double `place_bid` execution per block - (File: polkadot/runtime/common/src/crowdloan/mod.rs)

## Summary
`Crowdloan::poke` (call_index 7) appends `para_id` to `NewRaise` after only checking `NewRaise::<T>::get().contains(&index)`, but never updates `fund.last_contribution`. Since `do_contribute`'s duplicate-suppression logic relies exclusively on `fund.last_contribution` (not on inspecting `NewRaise` itself), a subsequent `contribute`/`contribute_all` call on the same fund within the same block fails to detect that the fund was already queued by `poke`, and appends the same `para_id` to `NewRaise` a second time, causing `on_initialize` to invoke `T::Auctioneer::place_bid` twice for one fund in one block.

## Finding Description
The `poke` extrinsic at [1](#0-0)  is signed-origin, permissionless, and only guards against a duplicate append using `NewRaise::<T>::get().contains(&index)`; it does not touch `fund.last_contribution`.

`do_contribute`'s append logic, however, decides whether to skip the `NewRaise::append` purely based on `fund.last_contribution` state, as seen at [2](#0-1) . In the ending-period branch, the `_ =>` arm (which appends and sets `last_contribution = Ending(now)`) is taken unless `last_contribution` already equals `Ending(now)`. Since `poke` never sets this field, immediately after a `poke` call, `fund.last_contribution` still holds its pre-poke value (`Never`, `PreEnding(_)`, or `Ending(<earlier block>)`), so the very next `contribute` call in the same block falls into the `_ =>` arm and appends `index` to `NewRaise` again — producing a duplicate entry for the same `para_id`.

At the next `on_initialize`, `NewRaise::<T>::take()` returns this vector with the duplicate, and the loop at [3](#0-2)  iterates over every entry via `filter_map` without deduplication, calling `T::Auctioneer::place_bid` and emitting `HandleBidResult` once per entry — twice for the affected fund.

Existing guards are insufficient: `poke`'s `AlreadyInNewRaise` check only prevents `poke` from being called twice in a row on the same fund/block, but it does nothing to inform `do_contribute`, which never consults `NewRaise` membership directly and trusts `last_contribution` bookkeeping alone. This bookkeeping is bypassed by `poke`.

Note that once the `contribute` call in the sequence executes and sets `fund.last_contribution = Ending(now)` (or `PreEnding(endings_count)`), any further `contribute` calls in the same block will correctly be suppressed — so the duplication is bounded to exactly one extra append per fund per block (matching the claim's "twice" scope, not unbounded growth).

## Impact Explanation
The duplicate entry causes `on_initialize` to execute `place_bid` and emit `HandleBidResult` twice for the same fund/para within one block, doubling the actual weight/PoV cost of processing that fund relative to what unique-entry semantics assume. This hook runs in the `Mandatory` dispatch class during the auction ending period, so the extra cost cannot be skipped by normal block weight limits. Repeated across many funds and many blocks of the ending period, this allows wasted weight amplification in the auction-ending hot path, and breaks the intended invariant that each fund contributes at most one bid attempt per block during ending period. This matches an in-scope "wasted weight / auction-ending processing corruption" impact class, though it does not cause fund loss, freeze, or auction outcome corruption (the bid parameters are identical, and `place_bid` behavior is idempotent for identical calls).

## Likelihood Explanation
Both `poke` and `contribute`/`contribute_all` are permissionless, signed-origin extrinsics reachable by any account. The precondition (`fund.raised > 0` and an active auction in ending period) is trivially satisfiable, including by the attacker via a prior contribution. The exploit sequence (`poke` then `contribute` in the same block) is fully attacker-controlled, requires no privileged access, and is repeatable every block of the ending period for every active fund, subject only to normal transaction fees.

## Recommendation
Ensure `poke` and `do_contribute` share a single source of truth for "is this fund already in `NewRaise`". Either have `poke` also set `fund.last_contribution` to match exactly what `do_contribute` would set (`LastContribution::Ending(now)` during ending period or `LastContribution::PreEnding(endings_count)` otherwise) before appending, or change `do_contribute` to check `NewRaise::<T>::get().contains(&index)` directly instead of relying solely on `last_contribution`.

## Proof of Concept
1. Set up an active auction and place it into its ending period via the test mock (`TestAuctioneer`).
2. `create` a fund and `contribute` once pre-ending so `fund.raised > 0`; advance to a fresh block within the ending period.
3. In the same block, call `Crowdloan::poke(signed(attacker), index)` followed by `Crowdloan::contribute(signed(attacker), index, MinContribution)`.
4. Assert `NewRaise::<Test>::get().iter().filter(|&&p| p == index).count()` equals `2` (duplicate present) instead of the expected `1`.
5. Advance to the next block, trigger `on_initialize`, and observe the mock's bid-tracking vector contains two identical `BidPlaced`/`HandleBidResult` entries for `index` at that height instead of one, confirming `place_bid` was invoked twice for a single fund in a single block.

### Citations

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L335-352)
```rust
				let new_raise = NewRaise::<T>::take();
				let new_raise_len = new_raise.len() as u32;
				for (fund, para_id) in
					new_raise.into_iter().filter_map(|i| Funds::<T>::get(i).map(|f| (f, i)))
				{
					// Care needs to be taken by the crowdloan creator that this function will
					// succeed given the crowdloaning configuration. We do some checks ahead of time
					// in crowdloan `create`.
					let result = T::Auctioneer::place_bid(
						Self::fund_account_id(fund.fund_index),
						para_id,
						fund.first_period,
						fund.last_period,
						fund.raised,
					);

					Self::deposit_event(Event::<T>::HandleBidResult { para_id, result });
				}
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L645-653)
```rust
		pub fn poke(origin: OriginFor<T>, index: ParaId) -> DispatchResult {
			ensure_signed(origin)?;
			let fund = Funds::<T>::get(index).ok_or(Error::<T>::InvalidParaId)?;
			ensure!(!fund.raised.is_zero(), Error::<T>::NoContributions);
			ensure!(!NewRaise::<T>::get().contains(&index), Error::<T>::AlreadyInNewRaise);
			NewRaise::<T>::append(index);
			Self::deposit_event(Event::<T>::AddedToNewRaise { para_id: index });
			Ok(())
		}
```

**File:** polkadot/runtime/common/src/crowdloan/mod.rs (L799-825)
```rust
		if T::Auctioneer::auction_status(now).is_ending().is_some() {
			match fund.last_contribution {
				// In ending period; must ensure that we are in NewRaise.
				LastContribution::Ending(n) if n == now => {
					// do nothing - already in NewRaise
				},
				_ => {
					NewRaise::<T>::append(index);
					fund.last_contribution = LastContribution::Ending(now);
				},
			}
		} else {
			let endings_count = EndingsCount::<T>::get();
			match fund.last_contribution {
				LastContribution::PreEnding(a) if a == endings_count => {
					// Not in ending period and no auctions have ended ending since our
					// previous bid which was also not in an ending period.
					// `NewRaise` will contain our ID still: Do nothing.
				},
				_ => {
					// Not in ending period; but an auction has been ending since our previous
					// bid, or we never had one to begin with. Add bid.
					NewRaise::<T>::append(index);
					fund.last_contribution = LastContribution::PreEnding(endings_count);
				},
			}
		}
```
