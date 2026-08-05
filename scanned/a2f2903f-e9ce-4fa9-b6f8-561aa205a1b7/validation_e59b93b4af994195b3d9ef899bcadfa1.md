## Analog Found: Front-running of user-chosen `CollectionId` in `pallet-uniques::create`, breaking batched `create + mint` extrinsics

### Title
Front-running attack on user-specified `CollectionId` in `pallet-uniques::create` causes DoS of legitimate batched collection creation - (File: `substrate/frame/uniques/src/lib.rs`)

### Summary
The Cauldron/Yield bug is a class of vulnerability where a protocol lets an unprivileged caller choose an arbitrary, unique identifier for a new resource, and later state-transitions revert if that identifier is already taken. An attacker who observes the pending transaction in the mempool can front-run it with the same identifier, causing the honest transaction (and any subsequent operations bundled with it) to fail. The same pattern exists in `pallet-uniques`, where the caller of `create()` supplies the `CollectionId` directly rather than the pallet auto-assigning it.

### Finding Description
`pallet-uniques::create` takes the `CollectionId` as a caller-supplied parameter and only checks that it is not already used: [1](#0-0) 

The uniqueness check is enforced in `do_create_collection`, which returns `Error::InUse` if the collection id already exists: [2](#0-1) 

Because there is no allocator (unlike the newer `pallet-assets`, which now supports an `AssetIdAllocator`/`NextAssetId` sequence enforcing that only the pallet-dictated next id can be used, see `substrate/frame/assets/src/lib.rs` lines 843-858 and `prdoc/pr_12378.prdoc`), any signed account can claim any unused `CollectionId` first. A common real-world usage pattern is to bundle `create(collection_id, admin)` together with subsequent `mint(collection_id, item_id, owner)` calls in a single `utility.batch_all` extrinsic, since `mint` requires the caller to hold the `Issuer`/admin role on that specific `collection_id`: [3](#0-2) 

An attacker who observes such a pending transaction in the mempool can submit their own `create(collection_id, attacker)` with a higher tip to be included first. When the victim's `create` executes afterward it fails with `Error::<T,I>::InUse`, and because it is wrapped in `batch_all` (which reverts entirely on any inner call failure), the whole batch — including the intended `mint` calls — fails atomically. This is structurally identical to the Cauldron/Ladle `vaultID` front-running issue: a user-chosen, protocol-wide unique ID that is referenced by later operations in the same batch, checked with an "already in use" guard that has no protection against front-running.

### Impact Explanation
The attacker gains only an empty, otherwise useless collection at the cost of a small deposit/gas outlay (`T::CollectionDeposit`), exactly as in the original report where the attacker gains only an "empty vault". The victim's entire batched extrinsic (collection creation + minting) fails and must be resubmitted with a new `CollectionId`, which is an availability/griefing issue rather than a loss of funds. This matches the "Medium" classification methodology used in the referenced report: low likelihood, but potentially high disruption to legitimate marketplace/dApp flows that pre-select a `CollectionId` client-side and batch it with dependent operations.

### Likelihood Explanation
Exploitation requires: (1) the victim's `CollectionId` selection being visible pre-inclusion (true for any public mempool/tx-pool), and (2) the attacker being willing to pay a comparable or higher tip to be included first. Both conditions are realistic on any parachain with an open transaction pool. However, likelihood is reduced in practice because `pallet-uniques` is largely superseded by `pallet-nfts`, which auto-increments `NextCollectionId` internally rather than accepting an arbitrary caller-chosen id for the standard `create` extrinsic: [4](#0-3) 
This significantly narrows real-world exposure to runtimes/integrations that still actively expose `pallet-uniques::create` to permissionless signed origins for new collections (I was not able to fully confirm, within the remaining investigation budget, whether Asset Hub's current `pallet_uniques::Config` still wires `CreateOrigin` to an open/signed origin versus a restricted one — this should be verified directly in `cumulus/parachains/runtimes/assets/asset-hub-westend/src/lib.rs` and `asset-hub-rococo/src/lib.rs`).

### Recommendation
- Prefer `pallet-nfts`-style auto-incrementing collection ids (`NextCollectionId`) for new deployments instead of caller-chosen ids, mirroring the fix already applied to `pallet-assets` via `AssetIdAllocator`/`NextAssetId` (see `substrate/frame/assets/src/functions.rs` `do_force_create`/`create`).
- For `pallet-uniques`, consider adding an equivalent allocator option, or documenting/deprecating the permissionless caller-chosen-id `create` path in favor of `force_create`/`pallet-nfts`.
- Alternatively, guard against batch griefing by making id-dependent batches commit-then-reveal, or by allowing the creator to specify a fallback/retry id list.

### Proof of Concept
1. Alice wants to launch a new NFT collection and mint items. Her wallet/dApp constructs `utility.batch_all([Uniques::create(collection_id=X, admin=Alice), Uniques::mint(X, item, Alice), Uniques::set_collection_metadata(X, ...)])` and broadcasts it.
2. Eve observes this transaction in the mempool and extracts `X`.
3. Eve submits `Uniques::create(collection_id=X, admin=Eve)` with a higher tip/priority.
4. Eve's transaction is included first; `Collection::<T,I>::contains_key(X)` becomes true, per `do_create_collection` at `substrate/frame/uniques/src/functions.rs` lines 84-94.
5. Alice's batch executes afterward: her `create(X, ...)` call hits `ensure!(!Collection::<T,I>::contains_key(collection.clone()), Error::<T, I>::InUse)` and fails; `batch_all` reverts the entire batch, so her `mint`/`set_collection_metadata` calls never take effect, forcing her to resubmit with a new id.

### Citations

**File:** substrate/frame/uniques/src/lib.rs (L467-485)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::create())]
		pub fn create(
			origin: OriginFor<T>,
			collection: T::CollectionId,
			admin: AccountIdLookupOf<T>,
		) -> DispatchResult {
			let owner = T::CreateOrigin::ensure_origin(origin, &collection)?;
			let admin = T::Lookup::lookup(admin)?;

			Self::do_create_collection(
				collection.clone(),
				owner.clone(),
				admin.clone(),
				T::CollectionDeposit::get(),
				false,
				Event::Created { collection, creator: owner, owner: admin },
			)
		}
```

**File:** substrate/frame/uniques/src/functions.rs (L84-94)
```rust
	pub fn do_create_collection(
		collection: T::CollectionId,
		owner: T::AccountId,
		admin: T::AccountId,
		deposit: DepositBalanceOf<T, I>,
		free_holding: bool,
		event: Event<T, I>,
	) -> DispatchResult {
		ensure!(!Collection::<T, I>::contains_key(collection.clone()), Error::<T, I>::InUse);

		T::Currency::reserve(&owner, deposit)?;
```

**File:** substrate/frame/uniques/src/tests.rs (L1625-1633)
```rust
			assert_ok!(Uniques::mint(
				RuntimeOrigin::signed(collection_admin),
				collection_id,
				item_id,
				item_owner,
			));

			assert_eq!(items(), vec![(item_owner, collection_id, item_id)]);
		});
```

**File:** substrate/frame/nfts/src/lib.rs (L710-722)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::create())]
		pub fn create(
			origin: OriginFor<T>,
			admin: AccountIdLookupOf<T>,
			config: CollectionConfigFor<T, I>,
		) -> DispatchResult {
			let collection = NextCollectionId::<T, I>::get()
				.or(T::CollectionId::initial_value())
				.ok_or(Error::<T, I>::UnknownCollection)?;

			let owner = T::CreateOrigin::ensure_origin(origin, &collection)?;
			let admin = T::Lookup::lookup(admin)?;
```
