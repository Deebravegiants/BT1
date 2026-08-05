Confirmed key mechanism `AccountId32Aliases::convert_location` only matches `(0, [AccountId32 { id, network }])` — a location with **parents = 0** and **exactly one interior junction**. [1](#0-0) 

### Title
No exploit: pool-account origin spoofing via XCM `Transact` is not reachable - (File: `substrate/frame/asset-conversion/src/lib.rs`, `polkadot/xcm/xcm-executor/src/traits/should_execute.rs`)

### Summary
While `do_swap_exact_tokens_for_tokens`'s internal `swap()`/`credit_swap()` mechanics *would* in theory allow a self-targeted swap to leak reserves if `sender == pool_account` (asset1 is withdrawn from and re-deposited to the same account, netting to zero, while asset2 is genuinely paid out to `send_to`), the precondition — deriving `RuntimeOrigin::signed(pool_account)` from a remote XCM message via `OriginConverter` — is not achievable with the `LocationToAccountId`/`OriginConverter` stacks actually deployed (Asset Hub Rococo/Westend and other parachain templates).

### Finding Description
`do_swap_exact_tokens_for_tokens` calls `Self::swap(&sender, &path, &send_to, keep_alive)`, which withdraws `amount_in` from `sender` [2](#0-1) , and `credit_swap` withdraws `amount_out` from the pool account and then resolves (deposits) `credit_in` back into `pool_to`, which for a 2-asset path equals the same pool account [3](#0-2) . If `sender` were the pool account itself, the asset1 leg nets to zero (withdrawn then redeposited into the same account) while asset2 is genuinely paid to an attacker-chosen `send_to`, which would constitute a real drain with no accounting check preventing it (unlike `do_remove_liquidity`, `do_swap_exact_tokens_for_tokens` has no `sender != pool_account` guard).

However, reaching this state requires the XCM `Transact` origin, after `OriginConverter::convert_origin`, to resolve to `RuntimeOrigin::signed(pool_account)` where `pool_account` is `T::PoolLocator::address(&pool_id)`, itself a `blake2_256` hash of `(PalletId, PoolId)` decoded via `TrailingZeroInput` [4](#0-3) . The only converter capable of mapping an arbitrary 32-byte value directly (without a domain-specific hash) into a `Signed` origin is `AccountId32Aliases`, which strictly requires `location.unpack() == (0, [AccountId32 { id, network }])` — i.e., **zero parents and exactly one interior junction** [1](#0-0) .

A remote/sibling-originated `Transact` message that has passed `WithComputedOrigin`/`AllowTopLevelPaidExecutionFrom` necessarily carries a non-trivial base origin (e.g. `Parent`, `(1, [Parachain(id)])`, or a bridged/global-consensus location) before any `DescendOrigin` is applied. `DescendOrigin` only *appends* junctions to the existing interior location; it cannot replace or clear the base junctions [5](#0-4) . Consequently the composed origin location will always contain the base prefix junction(s) plus the appended one(s), which never collapses to the single-junction `(0, [AccountId32 { .. }])` shape `AccountId32Aliases` requires. The other converters in the deployed `LocationToAccountId` stacks (`ParentIsPreset`, `SiblingParachainConvertsVia`, `HashedDescription`, `ExternalConsensusLocationsConverterFor`) all derive the account via a hash of the full location description [6](#0-5) , which is not invertible to a chosen target hash like `pool_account` (finding a location whose hash collides with a specific known 32-byte value requires a preimage attack, computationally infeasible).

### Impact Explanation
No concrete impact: the attacker cannot cause `OriginConverter::convert_origin` to produce `RuntimeOrigin::signed(pool_account)` through any legitimate remote XCM path (Transact + DescendOrigin) in the deployed configurations. The pool-draining mechanics inside `do_swap_exact_tokens_for_tokens`/`credit_swap` are real code paths but are unreachable with an attacker-controlled/forgeable origin.

### Likelihood Explanation
Not exploitable: requires either (a) a preimage collision against a `blake2_256` hash used by `HashedDescription`/`AccountId32Aliases`-style converters, or (b) a location with zero parents and a single junction exactly equal to the pool account bytes as the *base* channel-derived origin (not attacker-appendable via `DescendOrigin`), neither of which an unprivileged remote sender can produce.

### Recommendation
No fix required for this specific vector. As a defense-in-depth measure, `pallet-asset-conversion`'s swap functions could add an explicit `ensure!(sender != pool_account, Error::...)` check (mirroring the reserve-preservation checks already present in `do_remove_liquidity`) to eliminate the theoretical self-swap accounting anomaly even if some future/custom `OriginConverter` configuration made pool-account origin spoofing possible.

### Proof of Concept
Not applicable — no valid exploit path exists to construct. A negative test (documenting the invariant) could assert that no `LocationToAccountId`/`OriginConverter` composition in the shipped runtimes can convert a `Transact`+`DescendOrigin` composed location into `RuntimeOrigin::signed(pool_account)` for a known `pool_account`, e.g., by attempting `AccountId32Aliases::convert_location` on a multi-junction location and asserting it returns `None`.

### Citations

**File:** polkadot/xcm/xcm-builder/src/location_conversion.rs (L278-290)
```rust
pub struct AccountId32Aliases<Network, AccountId>(PhantomData<(Network, AccountId)>);
impl<Network: Get<Option<NetworkId>>, AccountId: From<[u8; 32]> + Into<[u8; 32]> + Clone>
	ConvertLocation<AccountId> for AccountId32Aliases<Network, AccountId>
{
	fn convert_location(location: &Location) -> Option<AccountId> {
		let id = match location.unpack() {
			(0, [AccountId32 { id, network: None }]) => id,
			(0, [AccountId32 { id, network }]) if *network == Network::get() => id,
			_ => return None,
		};
		Some((*id).into())
	}
}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1168-1181)
```rust
		fn swap(
			sender: &T::AccountId,
			path: &BalancePath<T>,
			send_to: &T::AccountId,
			keep_alive: bool,
		) -> Result<(), DispatchError> {
			let (asset_in, amount_in) = path.first().ok_or(Error::<T>::InvalidPath)?;
			let credit_in = Self::withdraw(asset_in.clone(), sender, *amount_in, keep_alive)?;

			let credit_out = Self::credit_swap(credit_in, path).map_err(|(_, e)| e)?;
			T::Assets::resolve(send_to, credit_out).map_err(|_| Error::<T>::BelowMinimum)?;

			Ok(())
		}
```

**File:** substrate/frame/asset-conversion/src/lib.rs (L1194-1243)
```rust
		fn credit_swap(
			credit_in: CreditOf<T>,
			path: &BalancePath<T>,
		) -> Result<CreditOf<T>, (CreditOf<T>, DispatchError)> {
			let resolve_path = || -> Result<CreditOf<T>, DispatchError> {
				for pos in 0..=path.len() {
					if let Some([(asset1, _), (asset2, amount_out)]) = path.get(pos..=pos + 1) {
						let pool_from = T::PoolLocator::pool_address(asset1, asset2)
							.map_err(|_| Error::<T>::InvalidAssetPair)?;

						if let Some((asset3, _)) = path.get(pos + 2) {
							let pool_to = T::PoolLocator::pool_address(asset2, asset3)
								.map_err(|_| Error::<T>::InvalidAssetPair)?;

							T::Assets::transfer(
								asset2.clone(),
								&pool_from,
								&pool_to,
								*amount_out,
								Preserve,
							)?;
						} else {
							let credit_out =
								Self::withdraw(asset2.clone(), &pool_from, *amount_out, true)?;
							return Ok(credit_out);
						}
					}
				}
				Err(Error::<T>::InvalidPath.into())
			};

			let credit_out = match resolve_path() {
				Ok(c) => c,
				Err(e) => return Err((credit_in, e)),
			};

			let pool_to = if let Some([(asset1, _), (asset2, _)]) = path.get(0..2) {
				match T::PoolLocator::pool_address(asset1, asset2) {
					Ok(address) => address,
					Err(_) => return Err((credit_in, Error::<T>::InvalidAssetPair.into())),
				}
			} else {
				return Err((credit_in, Error::<T>::InvalidPath.into()));
			};

			T::Assets::resolve(&pool_to, credit_in)
				.map_err(|c| (c, Error::<T>::BelowMinimum.into()))?;

			Ok(credit_out)
		}
```

**File:** substrate/frame/asset-conversion/src/types.rs (L146-158)
```rust
/// `PoolId` to `AccountId` conversion.
pub struct AccountIdConverter<Seed, PoolId>(PhantomData<(Seed, PoolId)>);
impl<Seed, PoolId, AccountId> TryConvert<&PoolId, AccountId> for AccountIdConverter<Seed, PoolId>
where
	PoolId: Encode,
	AccountId: Decode,
	Seed: Get<PalletId>,
{
	fn try_convert(id: &PoolId) -> Result<AccountId, &PoolId> {
		sp_io::hashing::blake2_256(&Encode::encode(&(Seed::get(), id))[..])
			.using_encoded(|e| Decode::decode(&mut TrailingZeroInput::new(e)).map_err(|_| id))
	}
}
```

**File:** polkadot/xcm/xcm-executor/src/lib.rs (L1110-1122)
```rust
				let dispatch_origin =
					Config::OriginConverter::convert_origin(origin.clone(), origin_kind).map_err(
						|_| {
							tracing::trace!(
								target: "xcm::process_instruction::transact",
								?origin,
								?origin_kind,
								"Failed to convert origin to a local origin."
							);

							XcmError::BadOrigin
						},
					)?;
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-rococo/src/xcm_config.rs (L103-114)
```rust
pub type LocationToAccountId = (
	// The parent (Relay-chain) origin converts to the parent `AccountId`.
	ParentIsPreset<AccountId>,
	// Sibling parachain origins convert to AccountId via the `ParaId::into`.
	SiblingParachainConvertsVia<Sibling, AccountId>,
	// Straight up local `AccountId32` origins just alias directly to `AccountId`.
	AccountId32Aliases<RelayNetwork, AccountId>,
	// Foreign locations alias into accounts according to a hash of their standard description.
	HashedDescription<AccountId, DescribeFamily<DescribeAllTerminal>>,
	// Different global consensus locations sovereign accounts.
	ExternalConsensusLocationsConverterFor<UniversalLocation, AccountId>,
);
```
