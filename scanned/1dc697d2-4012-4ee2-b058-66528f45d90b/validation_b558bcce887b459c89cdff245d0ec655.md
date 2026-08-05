### Title
Stale/expired oracle prices are served as fresh, valid data via `DataProvider::get()` with no staleness signal - ([File: substrate/frame/honzon/oracle/src/lib.rs])

### Summary
`pallet-oracle`'s `DefaultCombineData::combine_data` silently falls back to the last-known aggregated price (`prev_value`) whenever fresh operator submissions become insufficient (e.g. all raw values have aged past `ExpiresIn`), and `Pallet::feed_values`/`do_feed_values` re-persists that same stale value into `Values` storage. The primary consumer interface, `DataProvider::get()`, strips the timestamp and returns only the raw value, so any pallet consuming oracle prices through this trait has no way to detect that the price it just received is stale/expired rather than fresh. This mirrors the Perennial H-2 root cause: an expired/invalid value is surfaced through the "normal" read path indistinguishably from a valid, fresh one.

### Finding Description
In `DefaultCombineData::combine_data` [1](#0-0) , raw values older than `ExpiresIn` are filtered out (`values.retain(...)`), and if the number of remaining fresh values is below `MinimumCount`, the function returns `prev_value` — the previously aggregated value — unchanged, including its original (now stale) timestamp.

`Pallet::do_feed_values` then persists whatever `combined()` returns straight into the `Values` storage map without any additional staleness check [2](#0-1) . If oracle operators stop feeding data entirely (network outage, keeper downtime, censorship, etc.), no `feed_values` call occurs at all, so the `Values` entry is never touched and keeps holding the old `TimestampedValue` indefinitely.

Critically, the pallet exposes two read interfaces:
- `Pallet::get(key)` / `DataProviderExtended::get_all_values()` return the full `TimestampedValue` (value + timestamp) [3](#0-2) , so a careful caller *could* check staleness itself.
- `DataProvider::get(key)` — the interface the pallet's own docs recommend other pallets use ("The pallet implements the `DataProvider` and `DataProviderExtended` traits, allowing other pallets to easily consume the oracle data") [4](#0-3)  — explicitly discards the timestamp and returns only the bare value: [5](#0-4) 

This is structurally identical to the Perennial bug: the underlying storage/aggregation layer has a concept of "this data is stale/expired" (age past `ExpiresIn`, no fresh submissions), but the value returned through the primary consumption API carries no validity/freshness flag — a consumer cannot distinguish "fresh median price" from "months-old price silently carried forward because operators stopped feeding."

### Impact Explanation
Any downstream pallet (e.g. a stablecoin/CDP/lending module built on top of `pallet-oracle`, as referenced by the PRDoc for "Polkadot Stablecoin on AssetHub", tracking issue #9765) that consumes prices via `DataProvider::get()` will use a stale price as if it were current. Depending on how that price is used (collateral valuation, liquidation thresholds, mint/redeem pricing), this can lead to using outdated market prices to value collateral, incorrectly allow/deny liquidations or mints, or otherwise apply an economically invalid price during oracle downtime — analogous to the Perennial impact where invalid/expired price data is treated as valid, keeping positions open that should have been invalidated.

### Likelihood Explanation
Likelihood depends on operational conditions rather than attacker action: any period where fewer than `MinimumCount` oracle operators submit a fresh value within the `ExpiresIn` window (feeder downtime, network partition, censorship of feeder extrinsics, or an oracle operator set that shrinks below `MinimumCount`) triggers this fallback. This is a realistic and not-uncommon operational condition for any oracle system, and it silently degrades data quality without alerting downstream consumers, since `DataProvider::get()` gives no timestamp to check. No privileged or attacker-controlled action is required — it is a passive/latent condition of the pallet's designed fallback behavior combined with an information-losing consumer interface.

### Recommendation
- Add an explicit staleness/validity concept to the `DataProvider` trait (or introduce a validity-aware variant) so consumers can distinguish "fresh" vs "carried-forward/stale" prices, mirroring the fix direction used for the Perennial issue (track validity alongside price rather than inferring it from the price value/last-known state alone).
- Alternatively, have `Values` storage expire (return `None`) once the last update timestamp exceeds `ExpiresIn`, rather than persisting/serving an indefinitely-stale `prev_value`, and document/enforce that all downstream consumers must use the timestamped interface (`Pallet::get`/`get_all_values`) and explicitly check `now - timestamp <= ExpiresIn` before trusting a price.
- Audit/require that any runtime integrating `pallet-oracle` for price-sensitive logic (e.g. the planned stablecoin pallets) uses the timestamped API and performs its own staleness check rather than the bare `DataProvider::get()`.

### Proof of Concept
1. Configure `pallet-oracle` with `DefaultCombineData<T, MinimumCount=3, ExpiresIn=100>` and feed 3 operator prices at `timestamp = t0`, producing `Values(key) = TimestampedValue { value: P, timestamp: t0 }` (per `do_feed_values` in [2](#0-1) ).
2. Advance chain time past `t0 + ExpiresIn` without any further `feed_values` calls (simulating operator downtime).
3. A consumer pallet calls `<OraclePallet as DataProvider<Key, Value>>::get(&key)`. Per [5](#0-4) , this still returns `Some(P)` — the same value from `t0` — with no indication that it is now stale/expired, because the timestamp is dropped before returning.
4. If the same consumer instead calls one more `feed_values` from an operator, `combine_data` re-filters the (now-expired) raw values, finds fewer than `MinimumCount` fresh ones, and returns `prev_value` unchanged via [6](#0-5) , re-persisting the stale `P`/`t0` pair indefinitely — confirming the value keeps being served as if it were a normal/valid, current price.

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

**File:** substrate/frame/honzon/oracle/src/lib.rs (L395-398)
```rust
	/// Returns the aggregated and timestamped value for a given key.
	pub fn get(key: &T::OracleKey) -> Option<TimestampedValueOf<T, I>> {
		Self::values(key)
	}
```

**File:** substrate/frame/honzon/oracle/src/lib.rs (L415-424)
```rust
	fn do_feed_values(who: T::AccountId, values: Vec<(T::OracleKey, T::OracleValue)>) {
		let now = T::Time::now();
		for (key, value) in &values {
			let timestamped = TimestampedValue { value: value.clone(), timestamp: now };
			RawValues::<T, I>::insert(&who, key, timestamped);

			// Update `Values` storage if `combined` yielded result.
			if let Some(combined) = Self::combined(key) {
				<Values<T, I>>::insert(key, combined);
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

**File:** substrate/frame/honzon/oracle/README.md (L37-40)
```markdown
### Data Providers

The pallet implements the `DataProvider` and `DataProviderExtended` traits, allowing other pallets to easily
consume the oracle data.
```
