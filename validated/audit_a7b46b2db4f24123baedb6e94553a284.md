## Analysis

`register_token` is governance-gated (`T::CreateOrigin::ensure_origin`), so `ContractToAsset` mappings only exist for legitimately registered bridge contracts [1](#0-0) . But any unprivileged holder of a registered token can permissionlessly call `send()` with attacker-chosen `call_data`, which is delivered verbatim as `message.data` cross-chain to `on_accept` [2](#0-1) . On the receiving side, `on_accept` decodes that untrusted payload into `SubstrateCalldata`, then decodes an embedded `T::RuntimeCall` with plain `Decode::decode` (not `decode_all_with_depth_limit`, unlike the sibling `call-decompressor` pallet which explicitly bounds recursion depth to guard against stack-overflow "decode bombs") [3](#0-2) [4](#0-3) [5](#0-4) .

### Title
Unbounded-recursion SCALE decode of attacker-controlled `RuntimeCall` in `pallet-hyper-fungible-token::on_accept` - (File: modules/pallets/hyper-fungible-token/src/module.rs)

### Summary
`on_accept` decodes `SubstrateCalldata` and the nested `RuntimeCall` from the ISMP message body using plain `codec::Decode::decode`, with no recursion-depth limit, even though the sibling `pallet-call-decompressor` explicitly documents and enforces `MAX_EXTRINSIC_DECODE_DEPTH_LIMIT` for the same class of attacker-supplied `RuntimeCall` bytes.

### Finding Description
`send()` is callable by any signed account holding a registered asset and forwards `params.call_data` unmodified into the cross-chain `Message.data` field [6](#0-5) . Once relayed and delivered, `on_accept` decodes this data path: `Message::abi_decode` → `SubstrateCalldata::decode` → `T::RuntimeCall::decode` [7](#0-6) [8](#0-7) [4](#0-3) . `RuntimeCall` is a deeply-nestable SCALE enum (containing calls that embed `Box<RuntimeCall>`, `Vec<RuntimeCall>`, etc., across the whole runtime's call surface). The comment in `pallet-call-decompressor` explicitly documents that the same `RuntimeCall::decode` operation is vulnerable to stack-exhaustion via deep nesting and must be bounded with `decode_all_with_depth_limit` [5](#0-4) [9](#0-8) . `pallet-hyper-fungible-token::on_accept` performs the analogous decode of fully untrusted, attacker-crafted bytes without that guard.

### Impact Explanation
A remote-chain sender can craft a `RuntimeCall` payload with maximal nesting to overflow the executor's call stack during `on_accept` processing, which executes inside message delivery (`handle_unsigned`/`handle` dispatch). A stack overflow inside runtime execution is undefined behavior in a WASM/native runtime context and can crash the node processing the block, halting or destabilizing the state machine and blocking delivery of subsequent ISMP messages on that route — a denial-of-service/permanent-message-non-delivery outcome analogous to the "deserialization of untrusted data" class in the reported CVE.

### Likelihood Explanation
Reachable from a single unprivileged transaction: any holder of a registered HFT asset can call `send()` with arbitrary `call_data`, and once the message reaches an EVM contract mapped in `ContractToAsset`, the recipient side decodes it without any depth bound. No governance or privileged action beyond ordinary token registration (a routine, expected setup step) is required to reach the vulnerable decode.

### Recommendation
Bound `SubstrateCalldata`/`RuntimeCall` decoding in `on_accept` with `T::RuntimeCall::decode_all_with_depth_limit(MAX_DEPTH, &mut &*substrate_data.runtime_call)`, mirroring the mitigation already implemented in `pallet-call-decompressor`.

### Proof of Concept
1. Register an HFT asset for an EVM chain via `register_token` (normal setup).
2. Call `send()` with `call_data` set to a `SubstrateCalldata { signature: None, runtime_call: <deeply nested RuntimeCall bytes, e.g. thousands of nested `System::remark` wrapped in `Utility::batch`/`Utility::as_derivative` calls> }`.
3. Relay the resulting request to the destination chain; `on_accept` calls `T::RuntimeCall::decode` on the nested bytes, exhausting the stack before the `BaseCallFilter` check is ever reached.

**Uncertainty**: I could not fully verify at what nesting depth the runtime's actual `RuntimeCall` enum triggers stack exhaustion (this depends on the concrete `RuntimeCall` composition in `parachain/runtimes/gargantua` and `nexus`, which I did not fully inspect), nor whether an upstream generic decode depth guard exists elsewhere in the SCALE codec version used. A background Devin session with full build/test access would be needed to confirm exploitability empirically.

### Citations

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L238-310)
```rust
		/// Sends tokens cross-chain to a HyperFungibleToken or WrappedHyperFungibleToken contract
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::send())]
		pub fn send(
			origin: OriginFor<T>,
			params: SendParams<
				AssetId<T>,
				<<T as Config>::NativeCurrency as Currency<T::AccountId>>::Balance,
			>,
		) -> DispatchResult {
			let who = ensure_signed(origin)?;
			let dispatcher = <T as Config>::Dispatcher::default();

			let token_contract =
				TokenContracts::<T>::get(params.destination, params.asset_id.clone())
					.ok_or(Error::<T>::TokenContractNotFound)?;
			let erc_decimals = Precisions::<T>::get(params.asset_id.clone(), params.destination)
				.ok_or(Error::<T>::DecimalsNotFound)?;

			// Lock or burn the local asset
			let decimals = if params.asset_id == T::NativeAssetId::get() {
				// escrow the native asset
				<T as Config>::NativeCurrency::transfer(
					&who,
					&Self::pallet_account(),
					params.amount,
					ExistenceRequirement::AllowDeath,
				)?;
				T::Decimals::get()
			} else {
				let is_native = NativeAssets::<T>::get(params.asset_id.clone());
				if is_native {
					<T as Config>::Assets::transfer(
						params.asset_id.clone(),
						&who,
						&Self::pallet_account(),
						params.amount.into(),
						Preservation::Expendable,
					)?;
				} else {
					<T as Config>::Assets::burn_from(
						params.asset_id.clone(),
						&who,
						params.amount.into(),
						Preservation::Expendable,
						Precision::Exact,
						Fortitude::Polite,
					)?;
				}
				<T::Assets as fungibles::metadata::Inspect<T::AccountId>>::decimals(
					params.asset_id.clone(),
				)
			};

			// Encode the Message body
			let sender: [u8; 32] = who.clone().into();
			let amount: u128 = params.amount.into();
			let erc20_amount = convert_to_erc20(amount, erc_decimals, decimals);

			let token_message = Message {
				from: sender.to_vec().into(),
				to: params.recipient.to_vec().into(),
				amount: alloy_primitives::U256::from_be_bytes(erc20_amount.to_big_endian()),
				data: params.call_data.unwrap_or_default().into(),
			};

			let dispatch_post = DispatchPost {
				dest: params.destination,
				from: PALLET_ID.to_bytes(),
				to: token_contract,
				timeout: params.timeout,
				body: Message::abi_encode(&token_message),
			};
```

**File:** modules/pallets/hyper-fungible-token/src/lib.rs (L328-334)
```rust
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::register_token(registration.chains.len() as u32))]
		pub fn register_token(
			origin: OriginFor<T>,
			registration: TokenRegistration<AssetId<T>>,
		) -> DispatchResult {
			T::CreateOrigin::ensure_origin(origin)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L59-59)
```rust
		let message = Message::abi_decode(&body).map_err(HftError::DecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L119-122)
```rust
		// Execute optional calldata
		if !message.data.is_empty() {
			let substrate_data = SubstrateCalldata::decode(&mut &message.data[..])
				.map_err(HftError::CalldataDecodeError)?;
```

**File:** modules/pallets/hyper-fungible-token/src/module.rs (L189-190)
```rust
			let runtime_call = T::RuntimeCall::decode(&mut &*substrate_data.runtime_call)
				.map_err(HftError::RuntimeCallDecodeError)?;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L46-51)
```rust
const ONE_MB: u32 = 1_000_000;
/// This is the maximum nesting level required to decode
/// the supported ismp messages and pallet_ismp_relayer calls
/// All suported call types require a recursion depth of 2 except calls containing Ismp Get requests
/// Ismp Get requests have a nested vector of keys requiring an extra recursion depth
const MAX_EXTRINSIC_DECODE_DEPTH_LIMIT: u32 = 4;
```

**File:** modules/pallets/call-decompressor/src/lib.rs (L263-268)
```rust
	pub fn decode_and_execute(call_bytes: Vec<u8>) -> DispatchResult {
		let runtime_call = <T as frame_system::Config>::RuntimeCall::decode_all_with_depth_limit(
			MAX_EXTRINSIC_DECODE_DEPTH_LIMIT,
			&mut &call_bytes[..],
		)
		.map_err(|_| Error::<T>::ErrorDecodingCall)?;
```
