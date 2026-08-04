### Title
Stale EIP-2612 `permit` signatures remain valid after asset id/address reuse because `permit::Nonces` is never invalidated on asset destruction - (File: `substrate/frame/assets/precompiles/src/permit.rs`)

### Summary
The `permit::Nonces` storage is keyed only by `(verifying_contract: H160, owner: H160)` and is never cleared when the asset behind that `verifying_contract` address is destroyed. For local/pool assets, the precompile address embeds the raw numeric `AssetId` (`InlineAssetIdExtractor`), so if that numeric id is later reused for a new asset (`force_create` explicitly allows reusing any id that is not *currently* in use), the new asset resurrects the exact same `verifying_contract` address and inherits the old, unconsumed nonce state, allowing a stale signed permit for the destroyed asset to be replayed against the new one.

### Finding Description
`Nonces` is a `StorageDoubleMap<H160, H160, U256>` keyed purely by `verifying_contract` and `owner`, with no notion of an "asset generation" or creation nonce: [1](#0-0) 

`compute_domain_separator` binds the EIP-712 domain only to `verifying_contract` (the raw H160 address) and the token `name`/`chainId` — not to any asset-existence/generation identifier: [2](#0-1) 

`do_verify_permit`/`use_permit` read the current nonce for `(verifying_contract, owner)`, verify the ECDSA signature over that nonce, and increment on success — there is no check tying the permit to a specific asset "incarnation": [3](#0-2) 

For local (trust-backed/pool) assets, the precompile address is derived directly and deterministically from the numeric `AssetId` via `InlineAssetIdExtractor`, with only a static prefix distinguishing asset classes: [4](#0-3) 

Critically, the codebase already recognizes this exact hazard for foreign assets and defends against it explicitly: `pallet_assets_precompiles::foreign_assets` uses a **monotonically increasing** `NextAssetIndex` that is never decremented or reused even after `remove_asset_mapping` is called on asset destruction, guaranteeing a destroyed foreign asset's precompile address can never be reassigned to a new asset: [5](#0-4) 

No equivalent protection exists for local/pool assets using `InlineAssetIdExtractor` — their address is literally `asset_id`, and `pallet_assets` itself documents that asset id reuse is possible and dangerous: `do_force_create`'s `InUse` check only verifies the id is not *currently* in use, not that it was never used before, and `force_create` explicitly permits a privileged origin to pick "any id not currently in use": [6](#0-5) [7](#0-6) 

Combined with the fact that no `AssetsCallback::destroyed` hook purges `permit::Nonces` for the corresponding address (unlike the foreign-asset index mapping, which is purged and never reused), a destroyed-then-recreated asset at the same address inherits: (1) the same domain separator (if name/chainId unchanged) and (2) the same outstanding nonce value for any owner who had signed but not yet submitted a permit. The existing regression test only covers cross-*prefix* replay (trust-backed vs. foreign address spaces), not same-address reincarnation after destroy/recreate: [8](#0-7) 

### Impact Explanation
An attacker holding an unexpired, unconsumed EIP-2612 permit signature for a destroyed asset A can submit it against a newly created asset A' that reuses A's numeric id (and therefore A's exact precompile address), because `Nonces` and the domain separator are unaffected by the destroy/recreate cycle. This grants the attacker (as the named `spender`) an ERC20 allowance on asset A' without the current owner's consent for that specific new asset instance — a scoped, unauthorized-allowance-grant impact.

### Likelihood Explanation
This requires the precondition that a local/pool asset's numeric id is destroyed and then reused for a new asset at the same address — for local `TrustBackedAssets`/`PoolAssets`, this reuse can only realistically happen either (a) via a privileged `force_create` deliberately picking an old, freed id (documented as an accepted-but-dangerous capability), or (b) on any `pallet_assets` instance configured without an `AssetIdAllocator` (`()`), where plain unprivileged `create` can freely reuse a freed id (demonstrated by `asset_id_cannot_be_reused` test which shows id 0 being destroyed and recreated). Once that precondition holds, the actual replay (submitting the stale `permit()` call) is a fully unprivileged, attacker-controlled extrinsic/contract-call action, satisfying "privileged action creates a later user-triggered exploit path."

### Recommendation
Bind the EIP-712 domain separator (or the `Nonces` key) to an asset-generation identifier that changes across destroy/recreate cycles — e.g., include the asset's `Metadata`/creation block, or maintain a per-address "asset epoch" counter incremented on destruction (mirroring the monotonic `NextAssetIndex` scheme already used for foreign assets) and mix it into `compute_domain_separator`/`permit_digest`. Alternatively, add an `AssetsCallback::destroyed` hook for all `pallet_assets` instances (not just `ForeignAssetId`) that clears `permit::Nonces` entries for the corresponding `verifying_contract`, and/or forbid reuse of destroyed local asset ids at the `pallet_assets` level (require `AssetIdAllocator` semantics even for `force_create`, contradicting the currently documented "dangerous but allowed" behavior).

### Proof of Concept
Rust integration test in `substrate/frame/assets/precompiles/src/permit_precompile_tests.rs`:
1. `force_create` asset id `7` at address `addr = set_prefix_in_address(PRECOMPILE_ADDRESS_PREFIX)` with id embedded as `7`, set matching metadata name "Token A".
2. Owner signs (off-chain, via `sign_permit`) a permit for `addr` granting `spender` an allowance, but the call is never submitted.
3. `start_destroy` → `destroy_accounts` → `destroy_approvals` → `finish_destroy` asset id `7`.
4. `force_create` a *new* asset also with id `7` (same address `addr`), same metadata name "Token A" (or same domain-separator inputs).
5. Submit the previously-signed, never-consumed permit via `raw_permit` against `addr`.
6. Assert the call **succeeds** and `Assets::allowance(7, owner, spender)` becomes non-zero, and `permit::Pallet::<Test>::nonce(&addr, &owner)` increments from its stale pre-destroy value — demonstrating the signature and nonce state survived the destroy/recreate boundary and was never invalidated, violating the stated invariant that "asset id reuse must not resurrect stale nonces/signatures."

### Citations

**File:** substrate/frame/assets/precompiles/src/permit.rs (L101-110)
```rust
	#[pallet::storage]
	pub type Nonces<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		H160, // verifying contract address (precompile address)
		Blake2_128Concat,
		H160, // owner ethereum address
		U256, // nonce (EIP-2612 uses uint256)
		ValueQuery,
	>;
```

**File:** substrate/frame/assets/precompiles/src/permit.rs (L160-178)
```rust
		pub fn compute_domain_separator(verifying_contract: &H160, name: &[u8]) -> H256 {
			let name_hash = keccak_256(name);
			let version_hash = keccak_256(b"1");
			let chain_id = T::ChainId::get();

			// Encode: typehash || name_hash || version_hash || chainId || verifyingContract
			let mut data = Vec::with_capacity(DOMAIN_SEPARATOR_ENCODED_LEN);
			data.extend_from_slice(&DOMAIN_TYPEHASH);
			data.extend_from_slice(&name_hash);
			data.extend_from_slice(&version_hash);
			// Pad chain_id to 32 bytes (big-endian)
			data.extend_from_slice(&[0u8; 24]);
			data.extend_from_slice(&chain_id.to_be_bytes());
			// Pad address to 32 bytes
			data.extend_from_slice(&[0u8; 12]);
			data.extend_from_slice(verifying_contract.as_bytes());

			H256(keccak_256(&data))
		}
```

**File:** substrate/frame/assets/precompiles/src/permit.rs (L344-400)
```rust
			let nonce = Self::nonce(verifying_contract, owner);
			let digest = Self::permit_digest(
				verifying_contract,
				name,
				owner,
				spender,
				value,
				&nonce,
				deadline,
			);

			let recovered = Self::ecrecover(&digest, v, r, s)?;

			if &recovered != owner {
				return Err(Error::<T>::SignerMismatch);
			}

			Ok(())
		}

		/// Verify and consume a permit signature atomically.
		///
		/// This is the recommended function for production use. It:
		/// 1. Validates the deadline against the current timestamp
		/// 2. Verifies the signature matches the owner
		/// 3. Increments the nonce to prevent replay attacks
		///
		/// The `name` parameter should be the token name per EIP-2612 specification.
		///
		/// After this function returns `Ok(())`, the permit cannot be used again.
		pub fn use_permit(
			verifying_contract: &H160,
			name: &[u8],
			owner: &H160,
			spender: &H160,
			value: &[u8; 32],
			deadline: &[u8; 32],
			v: u8,
			r: &[u8; 32],
			s: &[u8; 32],
		) -> Result<(), Error<T>> {
			// Verify the permit first
			Self::do_verify_permit(
				verifying_contract,
				name,
				owner,
				spender,
				value,
				deadline,
				v,
				r,
				s,
			)?;

			// Consume the permit by incrementing the nonce
			// This prevents the same permit from being used again
			Self::increment_nonce(verifying_contract, owner)?;
```

**File:** substrate/frame/assets/precompiles/src/lib.rs (L86-103)
```rust
pub struct InlineAssetIdExtractor;

impl AssetIdExtractor for InlineAssetIdExtractor {
	type AssetId = u32;
	fn asset_id_from_address(addr: &[u8; 20]) -> Result<Self::AssetId, Error> {
		let bytes: [u8; 4] = addr[0..4].try_into().expect("slice is 4 bytes; qed");
		let index = u32::from_be_bytes(bytes);
		Ok(index)
	}
}

/// A precompile configuration that uses a prefix [`AddressMatcher`].
pub struct InlineIdConfig<const PREFIX: u16>;

impl<const P: u16> AssetPrecompileConfig for InlineIdConfig<P> {
	const MATCHER: AddressMatcher = AddressMatcher::Prefix(core::num::NonZero::new(P).unwrap());
	type AssetIdExtractor = InlineAssetIdExtractor;
}
```

**File:** substrate/frame/assets/precompiles/src/foreign_assets.rs (L95-121)
```rust
		/// Insert a new asset mapping, allocating a sequential index.
		/// Returns the allocated asset index on success.
		pub fn insert_asset_mapping(asset_id: &T::ForeignAssetId) -> Result<u32, ()> {
			if ForeignAssetIdToAssetIndex::<T>::contains_key(asset_id) {
				log::error!(target: LOG_TARGET, "Asset id {:?} already mapped", asset_id);
				return Err(());
			}

			let asset_index = NextAssetIndex::<T>::get();
			let next_index = asset_index.checked_add(1).ok_or_else(|| {
				log::error!(target: LOG_TARGET, "Asset index overflow");
			})?;

			AssetIndexToForeignAssetId::<T>::insert(asset_index, asset_id.clone());
			ForeignAssetIdToAssetIndex::<T>::insert(asset_id, asset_index);
			NextAssetIndex::<T>::put(next_index);

			log::debug!(target: LOG_TARGET, "Mapped asset {:?} to index {:?}", asset_id, asset_index);
			Ok(asset_index)
		}

		/// Remove an asset mapping if it exists, else this function has no effect.
		pub fn remove_asset_mapping(asset_id: &T::ForeignAssetId) {
			if let Some(asset_index) = ForeignAssetIdToAssetIndex::<T>::take(asset_id) {
				AssetIndexToForeignAssetId::<T>::remove(asset_index);
			}
		}
```

**File:** substrate/frame/assets/src/functions.rs (L758-773)
```rust
	/// * `enforce_allocator`: Whether `id` must be the one required by
	///   [`Config::AssetIdAllocator`]. Only pass `false` for a `ForceOrigin` caller.
	pub(super) fn do_force_create(
		id: T::AssetId,
		owner: T::AccountId,
		is_sufficient: bool,
		min_balance: T::Balance,
		enforce_allocator: bool,
	) -> DispatchResult {
		ensure!(!Asset::<T, I>::contains_key(&id), Error::<T, I>::InUse);
		ensure!(!min_balance.is_zero(), Error::<T, I>::MinBalanceZero);
		if enforce_allocator {
			if let Some(next_id) = T::AssetIdAllocator::next() {
				ensure!(id == next_id, Error::<T, I>::BadAssetId);
			}
		}
```

**File:** substrate/frame/assets/src/lib.rs (L903-910)
```rust
		/// # Warning
		///
		/// Forcing an arbitrary `id` is dangerous: the pallet only checks that `id` is not
		/// *currently* in use, not that it was never used before. Reusing an id can corrupt state,
		/// most severely for bridged assets, where a collision breaks the local/remote mapping.
		///
		/// - `id`: The identifier of the new asset. This must not be currently in use to identify
		/// an existing asset, and must never have been in use previously (see warning above).
```

**File:** substrate/frame/assets/precompiles/src/permit_precompile_tests.rs (L837-885)
```rust
/// A signature for asset A must NOT be replayable against asset B —
/// pins the `verifyingContract` field of the EIP-712 domain. We register
/// the same underlying asset under both prefixes, sign for one, submit
/// to the other; both directions are tested.
#[test_case(PRECOMPILE_ADDRESS_PREFIX, PRECOMPILE_ADDRESS_PREFIX_FOREIGN)]
#[test_case(PRECOMPILE_ADDRESS_PREFIX_FOREIGN, PRECOMPILE_ADDRESS_PREFIX)]
fn permit_signature_bound_to_verifying_contract(sign_prefix: u16, submit_prefix: u16) {
	new_test_ext().execute_with(|| {
		let setup = permit_setup(sign_prefix);
		if sign_prefix != PRECOMPILE_ADDRESS_PREFIX_FOREIGN &&
			submit_prefix == PRECOMPILE_ADDRESS_PREFIX_FOREIGN
		{
			crate::pallet::Pallet::<Test>::insert_asset_mapping(&setup.asset_id)
				.expect("foreign asset mapping must insert");
		}

		let asset_addr_signed = setup.asset_addr;
		let asset_addr_submitted = H160::from(set_prefix_in_address(submit_prefix));
		assert_ne!(asset_addr_signed, asset_addr_submitted);

		let (v, r, s) = sign_permit(
			asset_addr_signed,
			setup.spender_addr,
			AlloyU256::from(100),
			setup.deadline,
		);

		let result = raw_permit(
			setup.submitter,
			asset_addr_submitted,
			HARDHAT_ACCOUNT_0,
			setup.spender_addr,
			AlloyU256::from(100),
			setup.deadline,
			v,
			r,
			s,
		);
		assert_permit_reverted_with(result, "Signer does not match owner");
		assert_eq!(
			permit::Pallet::<Test>::nonce(&asset_addr_signed, &HARDHAT_ACCOUNT_0),
			U256::zero()
		);
		assert_eq!(
			permit::Pallet::<Test>::nonce(&asset_addr_submitted, &HARDHAT_ACCOUNT_0),
			U256::zero()
		);
	});
}
```
