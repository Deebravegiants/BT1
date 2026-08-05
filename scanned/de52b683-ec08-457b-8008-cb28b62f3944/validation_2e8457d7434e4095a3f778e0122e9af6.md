### Title
Single global `ExpiresIn` staleness threshold applied uniformly to all `OracleKey`s in `pallet-oracle`'s `DefaultCombineData` - (File: `substrate/frame/honzon/oracle/src/default_combine_data.rs`)

### Summary
`pallet-oracle`'s default data-combination logic filters out stale price submissions using a single constant `ExpiresIn` value that is applied identically to every `OracleKey` (i.e., every asset/currency pair) configured on the pallet. This is the same anti-pattern described in the referenced Sherlock report: a constant staleness threshold used for all tokens, regardless of the fact that different assets have very different expected price-update cadences and volatility profiles.

### Finding Description
`DefaultCombineData::combine_data` retains raw values only if `x.timestamp.saturating_add(expires_in) > now`, where `expires_in` comes from a single `ExpiresIn: Get<MomentOf<T, I>>` type parameter shared across the whole pallet instance: [1](#0-0) 

The `CombineData` trait's `combine_data` function receives the `key: &OracleKey` but the reference implementation (`DefaultCombineData`) never uses the key to look up a per-asset threshold — `expires_in` is fixed for the whole pallet: [2](#0-1) 

In the kitchensink runtime, this constant is configured as a single value (`3600` — one hour, in the pallet's `Moment` unit) for `pallet_oracle::Config`, and `OracleKey = u32` is used to represent arbitrary asset/currency identifiers, meaning every asset priced through this oracle instance shares the same staleness window: [3](#0-2) 

This mirrors the reported RedstoneCoreOracle bug precisely: a `STALE_PRICE_THRESHOLD`-style constant (`3600`) is shared across all assets fed through one oracle instance, even though assets can have widely differing expected freshness requirements (e.g., a stablecoin peg vs. a volatile token). Any consumer pallet that relies on `pallet_oracle::Pallet::<T,I>::get(&key)` returning a value only when "fresh enough" is subject to the oracle accepting a genuinely stale price for a volatile/fast-moving asset within the 1-hour window, or, conversely, DoS'ing legitimate submissions for an asset whose natural update interval exceeds an hour.

### Impact Explanation
Any FRAME pallet built on top of `pallet-oracle` (e.g., collateral pricing, liquidation, or a stablecoin peg-stability module) that treats `Values::<T,I>::get(key)` as "fresh" simply because it exists inherits this weakness: a price up to `ExpiresIn` (3600 units) old is accepted as valid for every asset, regardless of whether that asset's natural volatility/update frequency justifies a much shorter window. This can lead to mispriced collateral, unfair liquidations, or incorrect solvency/backing calculations in any downstream pallet — the same impact class as the referenced report.

### Likelihood Explanation
This is a low-likelihood, permissioned-context issue rather than an unprivileged-attacker exploit: `pallet-oracle`'s `ExpiresIn`/`MinimumCount` values are set once at genesis/runtime-compile time by the runtime developer via `parameter_types!`, not by an attacker, and the pallet itself does not price collateral or drive liquidations — that logic lives in downstream consumer pallets that were not found to be wired to this oracle instance in this repository (no consumer such as a PSM/collateral pallet was found reading `pallet_oracle::Pallet::get` for liquidation or peg decisions in the code I could inspect). Without a concrete, in-scope consumer pallet that performs financial actions (liquidation, minting, redemption) keyed on this stale-tolerant price, there is no demonstrated attacker-controlled path to protocol-level loss — it is a design smell in `pallet-oracle` itself rather than a directly exploitable vulnerability against an unprivileged user in this codebase.

### Recommendation
If `pallet-oracle` is intended to back economically-sensitive decisions for multiple assets with differing volatility, `ExpiresIn` (and `MinimumCount`) should be parameterizable per-`OracleKey` rather than a single pallet-wide constant, or downstream consumers should be required to supply their own per-asset staleness check on top of `pallet_oracle::Pallet::get`'s timestamp rather than trusting pallet-level freshness alone.

### Proof of Concept
Not applicable as a standalone exploit — this is a configuration/design issue in `DefaultCombineData` (`substrate/frame/honzon/oracle/src/default_combine_data.rs:25-46`) and its instantiation in `substrate/bin/node/runtime/src/lib.rs:3154`. No in-scope consumer pallet using this oracle instance for liquidation/collateral decisions was located to construct a concrete attacker-triggered PoC, so this should be treated as an informational/design-hardening finding rather than a directly exploitable Medium/High vulnerability in this repository's current state.

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

**File:** substrate/bin/node/runtime/src/lib.rs (L3152-3165)
```rust
impl pallet_oracle::Config for Runtime {
	type OnNewData = ();
	type CombineData = pallet_oracle::DefaultCombineData<Self, ConstU32<5>, ConstU64<3600>>;
	type Time = Timestamp;
	type OracleKey = u32;
	type OracleValue = u128;
	type PalletId = OraclePalletId;
	type Members = TechnicalMembership;
	type WeightInfo = ();
	type MaxHasDispatchedSize = OracleMaxHasDispatchedSize;
	type MaxFeedValues = OracleMaxFeedValues;
	#[cfg(feature = "runtime-benchmarks")]
	type BenchmarkHelper = OracleBenchmarkingHelper;
}
```
