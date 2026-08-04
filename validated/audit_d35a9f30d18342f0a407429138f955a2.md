### Title
Single global `ExpiresIn` staleness threshold applied to all oracle keys causes stale-data acceptance / valid-data rejection DoS - (File: `substrate/frame/honzon/oracle/src/default_combine_data.rs`)

### Summary
The `pallet-oracle` aggregation logic (`DefaultCombineData`) uses one hard-coded, pallet/instance-wide `ExpiresIn` expiry period for every `OracleKey`, even though different keys (e.g. different currency/asset feeds) can have very different natural update frequencies. This mirrors the reported CAP Protocol PriceOracle bug where a single staleness period was applied to assets with heartbeats ranging from 3600s to 86400s.

### Finding Description
`DefaultCombineData::combine_data` filters raw values by a single, generic `ExpiresIn: Get<MomentOf<T, I>>` bound before computing the median: [1](#0-0) 

`ExpiresIn` is a compile-time constant configured once per pallet instantiation via `type CombineData = DefaultCombineData<Runtime, MinimumCount, ExpiresIn>` and is applied uniformly to every `OracleKey` fed through `feed_values`/`feed_value`, regardless of what asset/data type that key represents: [2](#0-1) 

There is no per-key configuration mechanism anywhere in the pallet (`Config`, storage, or `CombineData` trait) that allows different `OracleKey`s to have distinct expiry/staleness windows: [3](#0-2) 

This is structurally identical to the reported bug: a system that aggregates/serves multiple independent price/data feeds but enforces one staleness window for all of them, when in reality feeds are expected to update at different frequencies.

### Impact Explanation
If a runtime integrator configures `ExpiresIn` short enough to suit frequently-updated keys (e.g., stablecoins expected to be fed hourly), then keys that are legitimately fed less often (e.g., once per day, matching a slower off-chain source's heartbeat) will have their raw values discarded by the `values.retain(...)` filter before the minimum-count threshold is reached, causing `combine_data` to fall back to `prev_value` — or `None` if no prior aggregate exists — resulting in denial of service for consumers of `DataProvider::get`/`get_value` for that key. Conversely, if `ExpiresIn` is set generously for slow feeds, fast-moving asset prices could be considered "fresh" long after they should be treated as stale, allowing downstream pallets (e.g., a CDP/lending module built on this oracle) to use outdated prices. This is a configuration-class DoS/staleness issue with real protocol impact wherever `pallet-oracle` backs price-sensitive logic with multiple heterogeneous keys.

### Likelihood Explanation
The trigger requires no attacker action beyond normal permissionless consumption of oracle data (`DataProvider::get`) — the flaw is purely in how the runtime integrator configures a single `ExpiresIn`/`MinimumCount` pair for a multi-asset oracle instance. Any downstream pallet or runtime that instantiates `pallet-oracle` with multiple `OracleKey`s having heterogeneous natural update cadences is affected as soon as feeders follow their legitimate (differing) update schedules — this is a configuration risk inherent to the pallet's design rather than a rare edge case, matching the "Configuration" classification and Medium-likelihood nature of the original report.

### Recommendation
- Short term: Document that `pallet-oracle` requires all `OracleKey`s aggregated under one `Config`/`Instance` to share a common, worst-case-safe update cadence; runtimes needing heterogeneous heartbeats should instantiate `pallet-oracle` multiple times (one instance per staleness class) via the pallet's existing instance (`I`) generic, or wrap `CombineData` in a custom implementation keyed by `OracleKey` to look up a per-key `ExpiresIn`.
- Long term: Extend `CombineData`/`DefaultCombineData` (or provide an alternative implementation) to accept a `Get<BTreeMap<OracleKey, Moment>>`-like per-key expiry map, and add runtime tests asserting configured `ExpiresIn` matches the real feeder cadence for each key type used in production.

### Proof of Concept
Not applicable as an on-chain exploit — this is a configuration-pattern vulnerability, not a directly attacker-triggerable bug. It is demonstrated by inspection: `DefaultCombineData<T, MinimumCount, ExpiresIn, I>` takes `ExpiresIn` as a single type parameter shared across all `T::OracleKey` values [4](#0-3) , and `Pallet::do_feed_values`/`combined` invoke `T::CombineData::combine_data(key, values, ...)` identically for every key with no per-key parameterization [5](#0-4) . A runtime that feeds e.g. `key=USDC` daily and `key=ETH` hourly under one `pallet-oracle` instance configured with `ExpiresIn` tuned to the ETH cadence would see `USDC`'s raw values expire and be filtered out before three operators can feed within the window, causing `Values::<T,I>::get(USDC)` to remain `None`/stale indefinitely.

### Citations

**File:** substrate/frame/honzon/oracle/src/default_combine_data.rs (L25-52)
```rust
pub struct DefaultCombineData<T, MinimumCount, ExpiresIn, I = ()>(
	marker::PhantomData<(T, I, MinimumCount, ExpiresIn)>,
);

impl<T, I, MinimumCount, ExpiresIn>
	CombineData<<T as Config<I>>::OracleKey, TimestampedValueOf<T, I>>
	for DefaultCombineData<T, MinimumCount, ExpiresIn, I>
where
	T: Config<I>,
	I: 'static,
	MinimumCount: Get<u32>,
	ExpiresIn: Get<MomentOf<T, I>>,
{
	fn combine_data(
		_key: &<T as Config<I>>::OracleKey,
		mut values: Vec<TimestampedValueOf<T, I>>,
		prev_value: Option<TimestampedValueOf<T, I>>,
	) -> Option<TimestampedValueOf<T, I>> {
		let expires_in = ExpiresIn::get();
		let now = T::Time::now();

		values.retain(|x| x.timestamp.saturating_add(expires_in) > now);

		let count = values.len() as u32;
		let minimum_count = MinimumCount::get();
		if count < minimum_count || count == 0 {
			return prev_value;
		}
```

**File:** substrate/frame/honzon/oracle/src/lib.rs (L161-230)
```rust
	#[pallet::config]
	pub trait Config<I: 'static = ()>: frame_system::Config {
		/// A hook to be called when new data is received.
		///
		/// This hook is triggered whenever an oracle operator successfully submits new data.
		/// It allows other pallets to react to oracle updates, enabling real-time responses to
		/// external data changes.
		type OnNewData: OnNewData<Self::AccountId, Self::OracleKey, Self::OracleValue>;

		/// The implementation to combine raw values into a single aggregated value.
		///
		/// This type defines how multiple oracle operator submissions are combined into a single
		/// trusted value. Common implementations include taking the median (to resist outliers)
		/// or weighted averages based on operator reputation.
		type CombineData: CombineData<Self::OracleKey, TimestampedValueOf<Self, I>>;

		/// The time provider for timestamping oracle data.
		///
		/// This type provides the current timestamp used to mark when oracle data was submitted.
		/// Timestamps are crucial for determining data freshness and preventing stale data usage.
		type Time: Time;

		/// The key type for identifying oracle data feeds.
		///
		/// This type is used to uniquely identify different types of oracle data (e.g., currency
		/// pairs, asset prices, weather data).
		type OracleKey: Parameter + Member + MaxEncodedLen;

		/// The value type for oracle data.
		///
		/// This type represents the actual data submitted by oracle operators (e.g., prices,
		/// temperatures, scores).
		type OracleValue: Parameter + Member + Ord + MaxEncodedLen;

		/// The pallet ID.
		///
		/// Will be used to derive the pallet's account, which is used as the oracle account
		/// when values are fed by root.
		#[pallet::constant]
		type PalletId: Get<PalletId>;

		/// The source of oracle members.
		///
		/// This type provides the set of accounts authorized to submit oracle data.
		/// Typically implemented by membership pallets to allow governance-controlled
		/// management of oracle operators.
		type Members: SortedMembers<Self::AccountId>;

		/// Weight information for extrinsics in this pallet.
		type WeightInfo: WeightInfo;

		/// The maximum number of oracle operators that can feed data in a single block.
		#[pallet::constant]
		type MaxHasDispatchedSize: Get<u32>;

		/// The maximum number of key-value pairs that can be submitted in a single extrinsic.
		#[pallet::constant]
		type MaxFeedValues: Get<u32>;

		/// A helper trait for benchmarking oracle operations.
		///
		/// Provides sample data for benchmarking the oracle pallet, allowing accurate
		/// weight calculations and performance testing.
		#[cfg(feature = "runtime-benchmarks")]
		type BenchmarkHelper: BenchmarkHelper<
			Self::OracleKey,
			Self::OracleValue,
			Self::MaxFeedValues,
		>;
	}
```

**File:** substrate/frame/honzon/oracle/src/lib.rs (L400-403)
```rust
	fn combined(key: &T::OracleKey) -> Option<TimestampedValueOf<T, I>> {
		let values = Self::read_raw_values(key);
		T::CombineData::combine_data(key, values, Self::values(key))
	}
```

**File:** substrate/frame/honzon/oracle/src/lib.rs (L415-429)
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

			T::OnNewData::on_new_data(&who, key, value);
		}
		Self::deposit_event(Event::NewFeedData { sender: who, values });
	}
```
