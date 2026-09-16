This confirms the analog: `on_accept` in `modules/pallets/hyper-fungible-token/src/module.rs` (line 55) resolves the *entire* asset identity for an inbound cross-chain transfer purely from `ContractToAsset::<T>::get(source, &from)` — a `(StateMachine, contract_address) → AssetId` reverse lookup — with no secondary check against anything in the message body itself (the `Message` struct only carries `from/to/amount/data`, no asset id). That mapping is written by `register_token`/`update_token` in `modules/pallets/hyper-fungible-token/src/lib.rs` (lines 356-367, 413-420), and neither function checks whether the `token_contract` address being inserted is already mapped to a *different* `AssetId` for that chain — `ContractToAsset::<T>::insert` silently overwrites.

### Title
Unchecked `ContractToAsset` overwrite in `register_token`/`update_token` lets a misregistered EVM contract address redirect inbound transfers to mint/unlock the wrong asset - ([File: modules/pallets/hyper-fungible-token/src/lib.rs])

### Summary
`register_token` and `update_token` write `TokenContracts[chain, asset_id] = contract` and the reverse index `ContractToAsset[chain, contract] = asset_id` without checking that `contract` isn't already the registered peer of a different `asset_id`. `on_accept` in `module.rs` trusts `ContractToAsset` alone to decide which local asset to credit for an inbound ISMP message. If governance (`CreateOrigin`) ever registers/updates a peer contract address that collides with an existing entry for another asset — a plain configuration mistake, structurally the same class of error as Rubic's "wrongly added USDC to the router whitelist" — every subsequent legitimate `send()` from that EVM contract gets misattributed to whichever asset last claimed that address, and the pallet mints/unlocks the wrong asset for the beneficiary.

### Finding Description
- `register_token`/`update_token` (`modules/pallets/hyper-fungible-token/src/lib.rs:356-367`, `413-420`) insert into `ContractToAsset<T>` keyed by `(chain, token_contract_bytes)` with no `ensure!` that this key is unclaimed or already points to the same `asset_id`.
- `on_accept` (`modules/pallets/hyper-fungible-token/src/module.rs:55-56`) does `ContractToAsset::<T>::get(source, &from).ok_or(...)` as the *sole* authentication of which asset an incoming `PostRequest` represents, then decodes `Message` (which contains no asset identifier) and mints/unlocks `local_asset_id` accordingly (lines 93-117).
- Consequently, the asset that gets credited on an inbound message is determined entirely by whichever `register_token`/`update_token` call most recently wrote that `(chain, contract)` key. There is no cross-check that the `from` contract still belongs to the asset it was originally registered for.

### Impact Explanation
If two assets are ever registered (even by an honest mistake, e.g. copy-pasted address, or re-registering the wrong ERC20/ERC6160 deployment for a chain during an `update_token`) such that they collide on the same `(chain, contract)` key, the pallet will mint or release the wrong asset for every subsequent inbound transfer from that contract. Concretely:
- A user genuinely sends the low-value asset A from its real, unmodified EVM contract; because the pallet's `ContractToAsset` entry for that address was overwritten to point to asset B (e.g. the chain's `NativeAssetId`, held in escrow via `pallet_account()`), `on_accept` unlocks/mints asset B to the beneficiary instead of A.
- This is an unbacked mint / drain of the native-asset escrow reachable by any unprivileged user simply calling `send()` on the (unmodified, legitimate) source-chain contract — exactly the "unbacked mint" / "forged message delivery" class called out in scope, and structurally identical to Rubic's root cause: an address that shouldn't have been trusted for a given purpose was, so ordinary user transactions against it are misinterpreted as authorizing movement of a different, more valuable pool of funds.

### Likelihood Explanation
Exploitation requires a pre-existing misconfiguration by `CreateOrigin` (governance) — the same precondition that caused the real Rubic incident. Given there is no code-level guard against this class of mistake (no uniqueness check, no reconciliation between `TokenContracts` and `ContractToAsset` beyond the one first-write path `update_token` cleans up), the likelihood is driven purely by operational discipline around registration payloads rather than any on-chain safeguard. Nothing in `register_token`/`update_token` would catch or reject a colliding registration, so if it happens, the destination pallet has no ability to detect or refuse it before minting.

### Recommendation
Add a collision guard in both `register_token` and `update_token`: before inserting into `ContractToAsset::<T>`, `ensure!` that any existing entry for `(chain, token_contract)` is either absent or already equal to the `asset_id` being registered, otherwise return a new `Error::<T>::ContractAlreadyMapped`. This turns an accidental cross-asset address collision into a hard extrinsic failure at registration time instead of a silent, exploitable state at delivery time.

### Proof of Concept
1. Governance registers asset `A` (e.g. a low-value wrapped token) with `register_token`, mapping `TokenContracts[Evm(1), A] = 0xCONTRACT` and `ContractToAsset[Evm(1), 0xCONTRACT] = A`.
2. Later, governance runs `update_token` for asset `B = NativeAssetId` (custodied/escrowed asset) and — by mistake — supplies the same `0xCONTRACT` address as `B`'s peer for `Evm(1)`. `update_token` only removes the *old* reverse mapping for `B` (if any); it does not check that `0xCONTRACT` was already claimed by `A`. `ContractToAsset[Evm(1), 0xCONTRACT]` is now overwritten to `B`, while `TokenContracts[Evm(1), A]` (used for outbound `send()`s of `A`) still equals `0xCONTRACT`.
3. Any user holding the real asset-`A` token calls the unmodified `HyperFungibleToken`/`WrappedHyperFungibleToken` contract at `0xCONTRACT` to bridge tokens in (a completely ordinary, unprivileged transaction).
4. On arrival, `on_accept` resolves `local_asset_id = ContractToAsset[Evm(1), 0xCONTRACT] = B` and unlocks/mints `B` (the native, escrow-backed asset) to the beneficiary instead of minting/crediting `A` — an unbacked release of `B`'s custodial pool paid for with a comparatively worthless inbound `A` transfer.

Note: I was unable to execute this against a live/test runtime within the scope of this review; the finding is based on static analysis of the exact `register_token`/`update_token`/`on_accept` logic cited above, and I could not find any existing test in the pallet's test-suite that exercises a colliding registration to confirm behavior empirically — a Devin session with cargo/test access could add and run such a test to confirm. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L127-138)
```rust
	/// Reverse lookup: (StateMachine, contract address bytes) → local asset ID.
	/// Used in on_accept to find which local asset an incoming message corresponds to.
	#[pallet::storage]
	pub type ContractToAsset<T: Config> = StorageDoubleMap<
		_,
		Blake2_128Concat,
		StateMachine,
		Blake2_128Concat,
		Vec<u8>,
		AssetId<T>,
		OptionQuery,
	>;
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L356-367)
```rust
				let token_contract = config.token_contract.0.to_vec();
				TokenContracts::<T>::insert(
					chain,
					registration.local_id.clone(),
					token_contract.clone(),
				);
				ContractToAsset::<T>::insert(
					chain,
					token_contract,
					registration.local_id.clone(),
				);
				Precisions::<T>::insert(registration.local_id.clone(), chain, config.decimals);
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L407-420)
```rust
				// Remove old reverse mapping if it exists
				if let Some(old_contract) = TokenContracts::<T>::get(chain, update.asset_id.clone())
				{
					ContractToAsset::<T>::remove(chain, old_contract);
				}

				let token_contract = config.token_contract.0.to_vec();
				TokenContracts::<T>::insert(
					chain,
					update.asset_id.clone(),
					token_contract.clone(),
				);
				ContractToAsset::<T>::insert(chain, token_contract, update.asset_id.clone());
				Precisions::<T>::insert(update.asset_id.clone(), chain, config.decimals);
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L50-56)
```rust
	fn on_accept(
		&self,
		PostRequest { body, from, source, .. }: PostRequest,
	) -> Result<Weight, anyhow::Error> {
		// Authenticate: look up which local asset this contract address maps to
		let local_asset_id = ContractToAsset::<T>::get(source, &from)
			.ok_or(HftError::UnknownSourceContract(source))?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L93-117)
```rust
		// Mint or transfer to beneficiary
		if local_asset_id == T::NativeAssetId::get() {
			<T as Config>::NativeCurrency::transfer(
				&Pallet::<T>::pallet_account(),
				&beneficiary,
				amount,
				ExistenceRequirement::AllowDeath,
			)
			.map_err(|e| HftError::TransferFailed(e.into()))?;
		} else {
			let is_native = NativeAssets::<T>::get(local_asset_id.clone());
			if is_native {
				<T as Config>::Assets::transfer(
					local_asset_id,
					&Pallet::<T>::pallet_account(),
					&beneficiary,
					amount.into(),
					Preservation::Expendable,
				)
				.map_err(|e| HftError::TransferFailed(e.into()))?;
			} else {
				<T as Config>::Assets::mint_into(local_asset_id, &beneficiary, amount.into())
					.map_err(|e| HftError::MintFailed(e.into()))?;
			}
		}
```
