[1](#0-0) [2](#0-1)

### Citations

**File:** substrate/frame/honzon/oracle/src/lib.rs (L395-403)
```rust
	/// Returns the aggregated and timestamped value for a given key.
	pub fn get(key: &T::OracleKey) -> Option<TimestampedValueOf<T, I>> {
		Self::values(key)
	}

	fn combined(key: &T::OracleKey) -> Option<TimestampedValueOf<T, I>> {
		let values = Self::read_raw_values(key);
		T::CombineData::combine_data(key, values, Self::values(key))
	}
```

**File:** substrate/frame/psm/src/lib.rs (L1208-1225)
```rust
		#[pallet::call_index(7)]
		#[pallet::weight(T::WeightInfo::set_asset_status())]
		pub fn set_asset_status(
			origin: OriginFor<T>,
			internal_asset: T::AssetId,
			external_asset: T::AssetId,
			status: CircuitBreakerLevel,
		) -> DispatchResult {
			Self::ensure_psm_admin(origin, &internal_asset, |l| l.can_set_circuit_breaker())?;
			ExternalAssets::<T>::try_mutate(
				&internal_asset,
				&external_asset,
				|maybe| -> DispatchResult {
					let info = maybe.as_mut().ok_or(Error::<T>::AssetNotApproved)?;
					info.status = status;
					Ok(())
				},
			)?;
```
