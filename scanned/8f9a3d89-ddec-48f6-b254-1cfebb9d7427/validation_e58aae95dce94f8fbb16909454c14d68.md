### Title
Stale oracle price can be served indefinitely via `prev_value` fallback in `DefaultCombineData` - (File: substrate/frame/honzon/oracle/src/default_combine_data.rs)

### Summary
`pallet-oracle`'s default aggregation logic (`DefaultCombineData::combine_data`) filters out stale raw submissions using an `ExpiresIn` window, but when too few fresh values remain, it unconditionally falls back to `prev_value` — the previously aggregated value — without checking whether *that* value is itself still within the freshness window. This mirrors the GMX finding: a price can remain "valid" and be served to consumers indefinitely if operators stop submitting fresh data, because there is no timestamp/staleness check applied to the value actually returned to consumers.

### Finding Description
`combine_data` retains only raw values newer than `now - ExpiresIn`: [1](#0-0) 

If the number of surviving fresh values is below `MinimumCount` (including the case where oracle operators stop feeding entirely, `count == 0`), the function returns `prev_value` as-is — with no comparison of `prev_value.timestamp` against `now`. This means the value stored in `Values<T,I>` storage can become arbitrarily old and never expire on its own; it is only replaced when a *new* aggregation succeeds.

Consumers reading this data via the `DataProvider` trait get only the raw value with the timestamp stripped entirely, so even a diligent consumer pallet cannot detect staleness itself: [2](#0-1) [3](#0-2) 

Even for consumers using `DataProviderExtended::get_all_values()` or the `get_value` view function, which do return the `TimestampedValue` (value + timestamp), the design places the staleness-check burden entirely on downstream consumer pallets — the oracle pallet itself provides no enforced staleness guarantee on the aggregated `Values` storage: [4](#0-3) [5](#0-4) 

This is directly analogous to the GMX `Oracle._setPricesFromPriceFeeds()` bug: a price source exists, timestamps are tracked, but nothing enforces that the price actually consumed is recent — old/frozen data silently continues to be treated as valid.

### Impact Explanation
If oracle operators are unable to submit fresh data in time (network partition, censorship of a subset of operators, chain congestion, or a `MinimumCount` that can no longer be met due to reduced operator set via `ChangeMembers`), the aggregated `Values` entry for a key freezes at its last known value and is served to any downstream consumer (e.g. a stablecoin/lending/liquidation pallet built on `pallet-honzon`, which this oracle was introduced specifically to support per prdoc/stable2512/pr_9815.prdoc) indefinitely, with no built-in signal that the data is stale. Consumers relying purely on `DataProvider::get()` (value only, no timestamp) have absolutely no way to detect this. This can lead to incorrect collateral valuations, wrongful liquidations, or failure to liquidate undercollateralized positions — the same class of financial harm described in the GMX report.

### Likelihood Explanation
This is not a bug requiring an attacker; it is a systemic design gap triggered by any legitimate operational failure of the oracle operator set (e.g., temporary unavailability of a quorum of operators, which is a realistic and foreseeable condition for any permissioned oracle feed). No privileged or malicious actor is required — an unprivileged consumer of oracle data (or any protocol built on this pallet) is exposed purely through normal operation once operator submissions lag.

### Recommendation
Enforce a staleness check on the value actually being *returned*, not just on the values being aggregated: when falling back to `prev_value` in `combine_data`, also verify `prev_value.timestamp.saturating_add(expires_in) > now` and return `None` if it fails. Additionally, consider exposing timestamp-aware freshness checking as part of the base `DataProvider::get()` contract (or requiring consumers to use `DataProviderExtended`/`get_value` and mandate they validate `timestamp` against a staleness threshold before use), so no consumer pallet can silently trust an unbounded-age price.

### Proof of Concept
1. Configure `pallet-oracle` with `MinimumCount = 3`, `ExpiresIn = N` blocks/moments, and 3 members.
2. Feed 3 values from all 3 members at time `t0` → `Values[key]` gets set (median), with `timestamp = t0`.
3. Two of the three oracle members stop feeding data (e.g., go offline) permanently.
4. At time `t0 + ExpiresIn + 1`, the single remaining operator feeds a new value. In `combine_data`, `read_raw_values` returns at most 1 fresh value (the others are either absent or expired), so `count < MinimumCount` → the function returns `prev_value` unchanged: [6](#0-5) 
5. `Values[key]` still holds the value fed at `t0`, now arbitrarily stale, and any consumer calling `Pallet::get(key)` or `DataProvider::get(key)` receives this stale price as if it were valid, with no indication (via the stripped-timestamp `DataProvider` API) that it is outdated.

### Citations

**File:** substrate/frame/honzon/oracle/src/default_combine_data.rs (L43-52)
```rust
		let expires_in = ExpiresIn::get();
		let now = T::Time::now();

		values.retain(|x| x.timestamp.saturating_add(expires_in) > now);

		let count = values.len() as u32;
		let minimum_count = MinimumCount::get();
		if count < minimum_count || count == 0 {
			return prev_value;
		}
```

**File:** substrate/frame/honzon/oracle/src/traits.rs (L30-33)
```rust
pub trait DataProvider<Key, Value> {
	/// Returns the data for a given key.
	fn get(key: &Key) -> Option<Value>;
}
```

**File:** substrate/frame/honzon/oracle/src/lib.rs (L313-318)
```rust
	#[pallet::view_functions]
	impl<T: Config<I>, I: 'static> Pallet<T, I> {
		/// Retrieve the aggregated oracle value for a specific key, including its timestamp.
		pub fn get_value(key: T::OracleKey) -> Option<TimestampedValueOf<T, I>> {
			Self::get(&key)
		}
```

**File:** substrate/frame/honzon/oracle/src/lib.rs (L395-398)
```rust
	/// Returns the aggregated and timestamped value for a given key.
	pub fn get(key: &T::OracleKey) -> Option<TimestampedValueOf<T, I>> {
		Self::values(key)
	}
```

**File:** substrate/frame/honzon/oracle/src/lib.rs (L449-453)
```rust
impl<T: Config<I>, I: 'static> DataProvider<T::OracleKey, T::OracleValue> for Pallet<T, I> {
	fn get(key: &T::OracleKey) -> Option<T::OracleValue> {
		Self::get(key).map(|timestamped_value| timestamped_value.value)
	}
}
```
