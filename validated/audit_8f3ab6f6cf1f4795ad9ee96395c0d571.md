### Title
`ExchangeAsset` capacity check only validates `want.len()`, not the actual number of assets returned by `AssetExchange::exchange_asset`, allowing holding to silently exceed `MaxAssetsIntoHolding` - ([File: polkadot/xcm/xcm-executor/src/lib.rs])

### Summary
In the `ExchangeAsset` instruction handler, `ensure_can_subsume_assets(want.len())` is checked *before* invoking `Config::AssetExchanger::exchange_asset`, but the `AssetExchange` trait contract does not bound the returned `AssetsInHolding` to `want.len()` items — it only guarantees "at least `want`" are returned. `subsume_assets` then unconditionally merges whatever is returned into holding with no size check at all. A custom, multi-asset `AssetExchanger` (composed via tuple, since the single-asset restriction lives only in `SingleAssetExchangeAdapter`, not in the trait or executor) can therefore push `AssetsInHolding` past its configured bound undetected.

### Finding Description
The relevant code is: [1](#0-0) 

- `self_ref.holding.saturating_take(give)` removes `give` from holding leniently — if `give` references assets not actually held, it is simply capped to what's available (`saturating_take` never errors), matching the described attacker-controlled input.
- `self_ref.ensure_can_subsume_assets(want.len())?` only reserves capacity for `want.len()` distinct assets, based on the *declared minimum* the exchanger is supposed to return.
- `Config::AssetExchanger::exchange_asset(...)` is called; the `AssetExchange` trait documents "At least `want` must be in the set" but does not cap the upper bound of returned assets: [2](#0-1) 
- The tuple impl for `AssetExchange` simply forwards to whichever adapter in the tuple succeeds, with no additional bounding of the result: [3](#0-2) 
- `self_ref.holding.subsume_assets(received)` is called unconditionally on success. Critically, `subsume_assets` performs **no bound/limit check whatsoever** — it just inserts into the `BTreeMap`/`BTreeSet` with saturating amount merges: [4](#0-3) 

So the only place that ever validates against `MaxAssetsIntoHolding` is the pre-check on `want.len()`, which is a lower bound the exchanger promises to satisfy, not an upper bound it is required to respect. `SingleAssetExchangeAdapter` happens to only ever produce/accept a single asset, but that restriction is enforced by that specific adapter's implementation, not by the executor or the `AssetExchange` trait contract. Any other adapter (or a tuple of adapters) implementing `AssetExchange` directly can legally return an arbitrarily large `AssetsInHolding` from `exchange_asset`, and the executor will merge it into holding without any bound enforcement.

### Impact Explanation
If a custom/tuple `AssetExchanger` returns more distinct assets than the pre-checked `want.len()` capacity allowed for, `AssetsInHolding` can grow past the runtime's configured `MaxAssetsIntoHolding` with no error surfaced at the `ExchangeAsset` instruction itself. Since `MaxAssetsIntoHolding` is meant to be a hard ceiling enforced consistently through `ensure_can_subsume_assets` checks elsewhere in the executor (e.g., on subsequent `WithdrawAsset`/`ReceiveTeleportedAsset`/deposit instructions in the same message), any following instruction that performs its own `ensure_can_subsume_assets(n)` check will now unexpectedly fail because `holding.len()` is already inflated beyond the configured bound — even though the instructions themselves are legitimate and would otherwise succeed. This causes cascading instruction failures for the remainder of the XCM program, consistent with the scoped impact of accounting desync leading to stuck/failed message processing, without any explicit, well-defined error being raised at the actual point where the bound is violated (the violation is silent at `ExchangeAsset` time).

### Likelihood Explanation
Exploitability requires a runtime to configure `AssetExchanger` with a custom or tuple-composed `AssetExchange` implementation that does not itself restrict the count of assets it can return relative to `want` (the shipped `SingleAssetExchangeAdapter` does enforce single-asset semantics, so runtimes using only that adapter are not affected). Given that requirement, the attack path is straightforward and fully reachable by an unprivileged party: submit or relay an XCM message with `WithdrawAsset` (to fill holding near the configured max) followed by `ExchangeAsset { give, want: [1 asset], maximal: true }`, targeting a chain whose exchanger config can be induced (via the swap pool's actual state) to return many distinct output assets. No signature/origin/barrier check intercepts this because `ExchangeAsset` is a normal, permitted instruction and the flaw is purely in `xcm-executor`'s internal accounting.

### Recommendation
Enforce the `MaxAssetsIntoHolding` bound at the point `received` is subsumed back into holding, not only via the pre-check against `want.len()`. E.g., after calling `exchange_asset`, verify `self_ref.holding.len() + received.len() <= Config::MaxAssetsIntoHolding::get()` and return a defined `XcmError` (rather than silently succeeding) if violated, or make `subsume_assets`/`ensure_can_subsume_assets` part of the same atomic check-and-insert operation so the bound cannot be exceeded by any caller of `subsume_assets`, including `ExchangeAsset`.

### Proof of Concept
Rust unit test in `xcm-executor`'s instruction test suite (`polkadot/xcm/xcm-executor/src/tests/`):
1. Configure `MaxAssetsIntoHolding = 4` (or similar small bound) in the mock `Config`.
2. Implement a mock `AssetExchange` (not `SingleAssetExchangeAdapter`) whose `exchange_asset` always returns `MaxAssetsIntoHolding::get() + 5` distinct fungible assets regardless of `want`.
3. Build holding via `WithdrawAsset` with `MaxAssetsIntoHolding - 1` distinct assets.
4. Execute `ExchangeAsset { give: <one existing asset>, want: vec![<1 asset>], maximal: true }`.
5. Assert either:
   - the instruction returns a defined error (expected fixed behavior), or
   - (demonstrating the bug) the instruction succeeds and `holding.len() > MaxAssetsIntoHolding::get()`, proving the bound was silently violated.
6. Follow with a legitimate subsequent instruction (e.g., another `WithdrawAsset` of one more asset) and assert it now fails with a capacity error purely due to the prior silent overflow, demonstrating cascading failure of an otherwise-valid instruction.

### Citations

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1760-1776)
```rust
			ExchangeAsset { give, want, maximal } => {
				self.transactional_process(|self_ref| {
					let give = self_ref.holding.saturating_take(give);
					self_ref.ensure_can_subsume_assets(want.len())?;
					let received = Config::AssetExchanger::exchange_asset(
						self_ref.origin_ref(),
						give,
						&want,
						maximal,
					).map_err(|unspent| {
						self_ref.holding.subsume_assets(unspent);
						XcmError::NoDeal
					})?;
					self_ref.holding.subsume_assets(received);
					Ok(())
				})
			},
```

**File:** polkadot/xcm/xcm-executor/src/traits/asset_exchange.rs (L26-39)
```rust
	/// - `want`: The minimum amount of assets which should be given to the caller in case any
	///   exchange happens. If more assets are provided, then they should generally be of the same
	///   asset class if at all possible.
	/// - `maximal`: If `true`, then as much as possible should be exchanged.
	///
	/// `Ok` is returned along with the new set of assets which have been exchanged for `give`. At
	/// least want must be in the set. Some assets originally in `give` may also be in this set. In
	/// the case of returning an `Err`, then `give` is returned.
	fn exchange_asset(
		origin: Option<&Location>,
		give: AssetsInHolding,
		want: &Assets,
		maximal: bool,
	) -> Result<AssetsInHolding, AssetsInHolding>;
```

**File:** polkadot/xcm/xcm-executor/src/traits/asset_exchange.rs (L63-78)
```rust
#[impl_trait_for_tuples::impl_for_tuples(30)]
impl AssetExchange for Tuple {
	fn exchange_asset(
		origin: Option<&Location>,
		give: AssetsInHolding,
		want: &Assets,
		maximal: bool,
	) -> Result<AssetsInHolding, AssetsInHolding> {
		for_tuples!( #(
			let give = match Tuple::exchange_asset(origin, give, want, maximal) {
				Ok(r) => return Ok(r),
				Err(a) => a,
			};
		)* );
		Err(give)
	}
```

**File:** polkadot/xcm/xcm-executor/src/assets.rs (L212-233)
```rust
	/// Mutate `self` to contain all given `assets`, saturating if necessary.
	///
	/// NOTE: [`AssetsInHolding`] are always sorted
	pub fn subsume_assets(&mut self, assets: AssetsInHolding) {
		// for fungibles, find matching fungibles and sum their amounts so we end-up having just
		// single such fungible but with increased amount inside
		for (asset_id, accounting) in assets.fungible.into_iter() {
			match self.fungible.entry(asset_id) {
				btree_map::Entry::Occupied(mut e) => {
					e.get_mut().saturating_subsume(accounting);
				},
				btree_map::Entry::Vacant(e) => {
					e.insert(accounting);
				},
			}
		}
		// for non-fungibles, every entry is unique so there is no notion of amount to sum-up
		// together if there is the same non-fungible in both holdings (same instance_id) these
		// will be collapsed into just single one
		let mut non_fungible = assets.non_fungible;
		self.non_fungible.append(&mut non_fungible);
	}
```
