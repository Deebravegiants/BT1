[1](#0-0) [2](#0-1)

### Citations

**File:** polkadot/xcm/xcm-builder/src/barriers.rs (L60-120)
```rust
/// Allows execution from `origin` if it is contained in `T` (i.e. `T::Contains(origin)`) taking
/// payments into account.
///
/// Only allows for `WithdrawAsset`, `ReceiveTeleportedAsset`, `ReserveAssetDeposited` and
/// `ClaimAsset` XCMs because they are the only ones that place assets in the Holding Register to
/// pay for execution.
pub struct AllowTopLevelPaidExecutionFrom<T>(PhantomData<T>);
impl<T: Contains<Location>> ShouldExecute for AllowTopLevelPaidExecutionFrom<T> {
	fn should_execute<RuntimeCall>(
		origin: &Location,
		instructions: &mut [Instruction<RuntimeCall>],
		max_weight: Weight,
		properties: &mut Properties,
	) -> Result<(), ProcessMessageError> {
		tracing::trace!(
			target: "xcm::barriers",
			?origin,
			?instructions,
			?max_weight,
			?properties,
			"AllowTopLevelPaidExecutionFrom",
		);

		ensure!(T::contains(origin), ProcessMessageError::Unsupported);
		// We will read up to 5 instructions. This allows up to 3 `ClearOrigin` instructions. We
		// allow for more than one since anything beyond the first is a no-op and it's conceivable
		// that composition of operations might result in more than one being appended.
		let end = instructions.len().min(5);
		instructions[..end]
			.matcher()
			.match_next_inst(|inst| match inst {
				WithdrawAsset(ref assets) |
				ReceiveTeleportedAsset(ref assets) |
				ReserveAssetDeposited(ref assets) |
				ClaimAsset { ref assets, .. } => {
					if assets.len() <= MAX_ASSETS_FOR_BUY_EXECUTION {
						Ok(())
					} else {
						Err(ProcessMessageError::BadFormat)
					}
				},
				_ => Err(ProcessMessageError::BadFormat),
			})?
			.skip_inst_while(|inst| {
				matches!(inst, ClearOrigin | AliasOrigin(..)) ||
					matches!(inst, DescendOrigin(child) if child != &Here) ||
					matches!(inst, SetHints { .. })
			})?
			.match_next_inst(|inst| match inst {
				BuyExecution { weight_limit: Limited(ref mut weight), .. }
					if weight.all_gte(max_weight) =>
				{
					*weight = max_weight;
					Ok(())
				},
				BuyExecution { ref mut weight_limit, .. } if weight_limit == &Unlimited => {
					*weight_limit = Limited(max_weight);
					Ok(())
				},
				PayFees { .. } => Ok(()),
				_ => Err(ProcessMessageError::Overweight(max_weight)),
```

**File:** polkadot/xcm/xcm-executor/src/traits/should_execute.rs (L37-51)
```rust
pub trait ShouldExecute {
	/// Returns `Ok(())` if the given `message` may be executed.
	///
	/// - `origin`: The origin (sender) of the message.
	/// - `instructions`: The message itself.
	/// - `max_weight`: The (possibly over-) estimation of the weight of execution of the message.
	/// - `properties`: Various pre-established properties of the message which may be mutated by
	///   this API.
	fn should_execute<RuntimeCall>(
		origin: &Location,
		instructions: &mut [Instruction<RuntimeCall>],
		max_weight: Weight,
		properties: &mut Properties,
	) -> Result<(), ProcessMessageError>;
}
```
