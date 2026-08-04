Confirmed: none of the built-in precompile crates (`substrate/frame/assets/precompiles/src/lib.rs`, `substrate/frame/vesting/precompiles/src/lib.rs`, `substrate/frame/asset-conversion/precompiles/src/lib.rs`) reference `value_transferred()` or perform any check to reject a non-zero native value sent alongside their calls.

### Title
Native value sent alongside calls to `pallet-revive` precompiles (ERC20/Vesting/AssetConversion) becomes permanently stuck - (File: `substrate/frame/revive/src/exec.rs`)

### Summary
This is the analog of the DeXe `DistributionProposal::execute()` bug: a function that can be simultaneously "funded" by native currency (`msg.value` / EVM `CALL` value) and an ERC20/asset-denominated operation, where the contract logic only accounts for the token side and never checks, refunds, or utilizes the native value, so it becomes permanently stranded.

### Finding Description
In `pallet-revive`'s execution engine, whenever a call frame is pushed (`substrate/frame/revive/src/exec.rs:1375-1387`), the value attached to the call is unconditionally transferred from the origin to the callee's account via `Self::transfer_from_origin(...)` *before* the callee's logic (including precompile logic) ever runs: [1](#0-0) 

This transfer happens regardless of whether the destination is a real contract or a built-in precompile, and regardless of `HAS_CONTRACT_INFO`: [2](#0-1) 

The shipped precompiles — the ERC20 asset precompile (`substrate/frame/assets/precompiles/src/lib.rs`), the Vesting precompile (`substrate/frame/vesting/precompiles/src/lib.rs`), and the AssetConversion precompile (`substrate/frame/asset-conversion/precompiles/src/lib.rs`) — implement `transfer`, `approve`, `transferFrom`, `vestedTransfer`, `swapExactTokensForTokens`, etc., but none of them read `env.value()` / check that the transferred native value is zero, nor do they forward/refund it: [3](#0-2) [4](#0-3) [5](#0-4) 

Because these precompile addresses are not "real" smart contracts (they have no bytecode, no owner-controlled withdrawal path, and — for `HAS_CONTRACT_INFO = false` precompiles like `ERC20` — no contract-info/account management at all), any native value sent to them alongside a call has no code path to be spent, refunded, or withdrawn. This exactly mirrors the DeXe root cause: a function is simultaneously invoked with both a token-denominated payload (ERC20 asset call data) and native currency (`msg.value`/EVM call value), but the receiving logic only handles the token side and silently drops the native value.

### Impact Explanation
Any unprivileged EOA or contract that calls an ERC20/Vesting/AssetConversion precompile function while attaching a non-zero native value (e.g. `IERC20(precompileAddr).transfer{value: 1 ether}(to, amount)` in Solidity, or the equivalent PVM `call` syscall with a non-zero `value_ptr`) will have that value irrecoverably locked. There is no withdraw/sweep function for these precompile addresses. This is a direct, permanent loss-of-funds bug for the caller, fully analogous to the "stuck ETH" impact in the original report.

### Likelihood Explanation
Likelihood for an unprivileged user is realistic but conditional on user/tooling error: EVM tooling (wallets, SDKs) commonly allow attaching `value` to any call; a user or an integrating contract that mistakenly (or due to a UI bug) sets a non-zero value while calling `transfer`/`approve`/`vestedTransfer`/`swapExactTokensForTokens` on these precompiles would lose those funds with no revert to warn them. Because none of the precompiles guard against this, the mistake is silent (the call succeeds), increasing the chance that affected users won't immediately notice the loss.

### Recommendation
Add an explicit guard at the top of each Precompile's `call`/`call_with_info` implementation (or centrally in the precompile dispatch path in `substrate/frame/revive/src/exec.rs`/`precompiles.rs`) that rejects any call carrying non-zero native value unless the specific precompile function is explicitly designed to accept native currency, e.g.:
```rust
ensure!(env.value_transferred().is_zero(), Error::Revert(...));
```
Apply this to all non-payable precompile entry points (`ERC20::transfer/approve/transferFrom/permit`, `Vesting::vestedTransfer`, `AssetConversion::swapExactTokensForTokens`, etc.), mirroring the DeXe fix pattern of reverting when `token != ETHEREUM_ADDRESS && msg.value > 0`.

### Proof of Concept
Not independently reproduced within this review (no test harness run); this is inferred from the code paths cited above:
1. Deploy/observe existing `ERC20` precompile at its fixed address on Asset Hub (`asset-hub-westend` runtime config wires it in, see `cumulus/parachains/runtimes/assets/asset-hub-westend/src/lib.rs:1383-1394`).
2. From an EOA, call `transfer(to, amount)` on the precompile address via an EVM `CALL` opcode / PVM `call` syscall with a non-zero `value` parameter.
3. Observe: the `transfer_from_origin` step (`exec.rs:1375-1387`) moves the native value to the precompile's account_id; the `ERC20::transfer` handler (`substrate/frame/assets/precompiles/src/lib.rs:261-294`) executes successfully and only moves the ERC20 asset balance; the native value remains at the precompile address with no code path to retrieve it. [6](#0-5)

### Citations

**File:** substrate/frame/revive/src/exec.rs (L1375-1387)
```rust
			// Every non delegate call or instantiate also optionally transfers the balance.
			// If it is a delegate call, then we've already transferred tokens in the
			// last non-delegate frame.
			if frame.delegate.is_none() {
				Self::transfer_from_origin(
					&self.origin,
					&caller,
					account_id,
					frame.value_transferred,
					&mut frame.frame_meter,
					self.exec_config,
				)?;
			}
```

**File:** substrate/frame/revive/src/exec.rs (L1389-1419)
```rust
			// We need to make sure that the pre-compiles contract exist before executing it.
			// A few more conditionals:
			// 	- Only contracts with extended API (has_contract_info) are guaranteed to have an
			//    account.
			//  - Only when not delegate calling we are executing in the context of the pre-compile.
			//    Pre-compiles itself cannot delegate call.
			if let Some(precompile) = executable.as_precompile() &&
				precompile.has_contract_info() &&
				frame.delegate.is_none() &&
				!<System<T>>::account_exists(account_id)
			{
				// prefix matching pre-compiles cannot have a contract info
				// hence we only mint once per pre-compile
				T::Currency::mint_into(account_id, T::Currency::minimum_balance())?;
				// make sure the pre-compile does not destroy its account by accident
				<System<T>>::inc_consumers(account_id)?;
			}

			let mut code_deposit = executable
				.as_executable()
				.map(|exec| exec.code_info().deposit())
				.unwrap_or_default();

			let mut output = match executable {
				ExecutableOrPrecompile::Executable(executable) => {
					executable.execute(self, entry_point, input_data)
				},
				ExecutableOrPrecompile::Precompile { instance, .. } => {
					instance.call(input_data, self)
				},
			}
```

**File:** substrate/frame/assets/precompiles/src/lib.rs (L261-294)
```rust
	/// Execute the transfer call.
	fn transfer(
		asset_id: <Runtime as Config<Instance>>::AssetId,
		call: &IERC20::transferCall,
		env: &mut impl Ext<T = Runtime>,
	) -> Result<Vec<u8>, Error> {
		env.charge(<Runtime as Config<Instance>>::WeightInfo::transfer())?;

		let from = Self::caller(env)?;
		let dest = <Runtime as pallet_revive::Config>::AddressMapper::to_account_id(
			&call.to.into_array().into(),
		);

		let f = TransferFlags { keep_alive: false, best_effort: false, burn_dust: false };
		pallet_assets::Pallet::<Runtime, Instance>::do_transfer(
			asset_id,
			&<Runtime as pallet_revive::Config>::AddressMapper::to_account_id(&from),
			&dest,
			Self::to_balance(call.value)?,
			None,
			f,
		)?;

		Self::deposit_event(
			env,
			IERC20Events::Transfer(IERC20::Transfer {
				from: from.0.into(),
				to: call.to,
				value: call.value,
			}),
		)?;

		Ok(IERC20::transferCall::abi_encode_returns(&true))
	}
```

**File:** substrate/frame/vesting/precompiles/src/lib.rs (L175-216)
```rust
				// is constant (depends only on MaxLocks and MAX_VESTING_SCHEDULES).
				let max_locks = MaxLocksOf::<T>::get();
				let dispatch_weight = <T as pallet_vesting::Config>::WeightInfo::vested_transfer(
					max_locks,
					T::MAX_VESTING_SCHEDULES,
				);
				env.frame_meter_mut()
					.charge_weight_token(RuntimeCosts::Precompile(dispatch_weight))?;

				ensure_mutable::<T>(env)?;

				let caller_account = caller_account_id(env, "vestedTransfer")?;
				let target_account = env.to_account_id(&H160::from_slice(target.as_slice()));
				let target_lookup = T::Lookup::unlookup(target_account);

				let locked: VestingBalance<T> = {
					let balance: <T as Config>::Balance =
						U256::from_big_endian(&locked.to_be_bytes::<32>())
							.try_into()
							.map_err(|_| Error::Revert("vestedTransfer: locked overflow".into()))?;
					<VestingBalance<T> as From<<T as Config>::Balance>>::from(balance)
				};
				let per_block: VestingBalance<T> = {
					let balance: <T as Config>::Balance =
						U256::from_big_endian(&perBlock.to_be_bytes::<32>()).try_into().map_err(
							|_| Error::Revert("vestedTransfer: perBlock overflow".into()),
						)?;
					<VestingBalance<T> as From<<T as Config>::Balance>>::from(balance)
				};
				let starting_block: BlockNumberFor<T> =
					U256::from_big_endian(&startingBlock.to_be_bytes::<32>()).try_into().map_err(
						|_| Error::Revert("vestedTransfer: startingBlock overflow".into()),
					)?;

				let schedule = VestingInfo::new(locked, per_block, starting_block);
				let origin = frame_system::RawOrigin::Signed(caller_account).into();
				pallet_vesting::Pallet::<T>::vested_transfer(origin, target_lookup, schedule)
					.map_err(|e| {
						Error::Revert(alloc::format!("vestedTransfer failed: {:?}", e).into())
					})?;
				Ok(Vec::new())
			},
```

**File:** substrate/frame/asset-conversion/precompiles/src/lib.rs (L289-319)
```rust
	fn swap_exact_tokens_for_tokens(
		call: &IAssetConversion::swapExactTokensForTokensCall,
		env: &mut impl Ext<T = Runtime>,
	) -> Result<Vec<u8>, Error> {
		let path_len = Self::validated_path_len(&call.path)?;
		env.charge(
			<Runtime as pallet_asset_conversion::Config>::WeightInfo::swap_exact_tokens_for_tokens(
				path_len,
			),
		)?;
		let path: Vec<_> =
			call.path.iter().map(|e| Self::decode_asset_kind(e)).collect::<Result<_, _>>()?;

		let sender = Self::caller_account_id(env)?;
		let send_to = env.to_account_id(&H160(call.sendTo.0 .0));

		let amount_out = <pallet_asset_conversion::Pallet<Runtime> as Swap<
			<Runtime as frame_system::Config>::AccountId,
		>>::swap_exact_tokens_for_tokens(
			sender,
			path,
			Self::to_balance(call.amountIn)?,
			Some(Self::to_balance(call.amountOutMin)?),
			send_to,
			call.keepAlive,
		)?;

		Ok(IAssetConversion::swapExactTokensForTokensCall::abi_encode_returns(&Self::to_u256(
			amount_out,
		)?))
	}
```

**File:** cumulus/parachains/runtimes/assets/asset-hub-westend/src/lib.rs (L1383-1394)
```rust
	type Precompiles = (
		ERC20<Self, InlineIdConfig<{ TRUST_BACKED_ASSETS_PRECOMPILE }>, TrustBackedAssetsInstance>,
		ERC20<Self, InlineIdConfig<{ POOL_ASSETS_PRECOMPILE }>, PoolAssetsInstance>,
		ERC20<
			Self,
			ForeignIdConfig<{ FOREIGN_ASSETS_PRECOMPILE }, Self, ForeignAssetsInstance>,
			ForeignAssetsInstance,
		>,
		XcmPrecompile<Self>,
		pallet_asset_conversion_precompiles::AssetConversion<{ ASSET_CONVERSION_PRECOMPILE }, Self>,
		VestingPrecompile<Self>,
	);
```
