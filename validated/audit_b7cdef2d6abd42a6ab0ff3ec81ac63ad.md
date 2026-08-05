Audit Report

## Title
Native value attached to ERC20 precompile calls is transferred and permanently locked because the precompile never validates `value_transferred() == 0` - (File: `substrate/frame/assets/precompiles/src/lib.rs`)

## Summary
The ERC20 precompile in `pallet-revive` (`substrate/frame/assets/precompiles/src/lib.rs`) implements a standard, non-payable ERC20 interface (`transfer`, `approve`, `transferFrom`, `permit`) but never checks `env.value_transferred()`. `pallet-revive`'s frame execution engine unconditionally transfers any `value` attached to a `call`/`bare_call` from the caller to the destination account before invoking the callee, including precompiles.

## Finding Description
`Pallet::call` accepts caller-controlled `dest` and `value` [1](#0-0)  and the frame's `value_transferred` is transferred to the destination `account_id` before either the executable or precompile's `call()` runs [2](#0-1) . The ERC20 precompile's dispatch (`call`) only guards state-changing calls against `is_read_only()`, never against non-zero attached value [3](#0-2) , and its `transfer` implementation moves asset balances via `pallet_assets::do_transfer` without any value check [4](#0-3) . The destination account for an address with no registered origin key resolves to a synthetic fallback `AccountId32` derived purely from the `H160` bytes, with no corresponding private key [5](#0-4) . `transfer_from_origin`/`transfer` in `exec.rs` will also pull the ED into existence for the destination account if it doesn't yet exist [6](#0-5) .

## Impact Explanation
If an unprivileged, signed account submits `pallet_revive::Pallet::call` with `dest` set to the ERC20 precompile's address and a non-zero `value`, that native value (plus ED if needed) is moved out of the caller's balance into a fallback account nobody controls, and there is no dispatchable path to recover it. This is a genuine, code-confirmed self-inflicted loss-of-funds bug: the value transfer in `exec.rs` happens unconditionally before the precompile executes, and the precompile logic in `substrate/frame/assets/precompiles/src/lib.rs` never rejects non-zero value.

## Likelihood Explanation
Triggering requires the caller to deliberately or mistakenly set `value != 0` when calling a precompile address — this is an unusual but not implausible action (e.g., tooling bugs, wallet misuse, or copy-pasted payable-style call construction), and needs no special privilege. It is a "victim mistake" style pattern rather than an attacker extracting value from a third party; impact is confined to the calling account's own funds.

## Recommendation
Add a check in the ERC20 precompile's `call()` (and any other non-payable precompile) that rejects non-zero `env.value_transferred()` for state-changing entry points, ideally enforced generically in `exec.rs` before the unconditional balance transfer for precompiles that don't declare themselves payable, rather than only after funds have already moved.

## Proof of Concept
1. As signed account Alice with native balance, call `pallet_revive::Pallet::call(origin=Alice, dest=<ERC20 precompile address>, value=1_000_000_000, weight_limit=.., storage_deposit_limit=.., data=IERC20::transferCall{...}.abi_encode())`.
2. Observe the ERC20 transfer executes normally, but Alice's native balance is additionally debited by the attached value (plus ED if the fallback account didn't exist), credited to `AccountId32Mapper::to_fallback_account_id(precompile_address)`.
3. Confirm no extrinsic or precompile function exists that can move value out of that fallback account, since it has no corresponding private key.

### Citations

**File:** substrate/frame/revive/src/lib.rs (L1169-1190)
```rust
		#[pallet::call_index(1)]
		#[pallet::weight(<T as Config>::WeightInfo::call().saturating_add(*weight_limit))]
		pub fn call(
			origin: OriginFor<T>,
			dest: H160,
			#[pallet::compact] value: BalanceOf<T>,
			weight_limit: Weight,
			#[pallet::compact] storage_deposit_limit: BalanceOf<T>,
			data: Vec<u8>,
		) -> DispatchResultWithPostInfo {
			Self::ensure_non_contract_if_signed(&origin)?;
			let mut output = Self::bare_call(
				origin,
				dest,
				Pallet::<T>::convert_native_to_evm(value),
				TransactionLimits::WeightAndDeposit {
					weight_limit,
					deposit_limit: storage_deposit_limit,
				},
				data,
				&ExecConfig::new_substrate_tx(),
			);
```

**File:** substrate/frame/revive/src/exec.rs (L1375-1419)
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

**File:** substrate/frame/revive/src/exec.rs (L1711-1743)
```rust
	/// Transfer some funds from `from` to `to`.
	///
	/// This is a no-op for zero `value`, avoiding events to be emitted for zero balance transfers.
	///
	/// If the destination account does not exist, it is pulled into existence by transferring the
	/// ED from `origin` to the new account. The total amount transferred to `to` will be ED +
	/// `value`. This makes the ED fully transparent for contracts.
	/// The ED transfer is executed atomically with the actual transfer, avoiding the possibility of
	/// the ED transfer succeeding but the actual transfer failing. In other words, if the `to` does
	/// not exist, the transfer does fail and nothing will be sent to `to` if either `origin` can
	/// not provide the ED or transferring `value` from `from` to `to` fails.
	/// Note: This will also fail if `origin` is root.
	fn transfer<S: State>(
		origin: &Origin<T>,
		from: &T::AccountId,
		to: &T::AccountId,
		value: U256,
		preservation: Preservation,
		meter: &mut ResourceMeter<T, S>,
		exec_config: &ExecConfig<T>,
	) -> DispatchResult {
		let value = BalanceWithDust::<BalanceOf<T>>::from_value::<T>(value)
			.map_err(|_| Error::<T>::BalanceConversionFailed)?;
		if value.is_zero() {
			return Ok(());
		}

		if <System<T>>::account_exists(to) {
			return transfer_with_dust::<T>(from, to, value, preservation);
		}

		let origin = origin.account_id()?;
		let ed = <T as Config>::Currency::minimum_balance();
```

**File:** substrate/frame/assets/precompiles/src/lib.rs (L163-208)
```rust
	fn call(
		address: &[u8; 20],
		input: &Self::Interface,
		env: &mut impl Ext<T = Self::T>,
	) -> Result<Vec<u8>, Error> {
		frame_support::ensure!(
			!env.is_delegate_call(),
			pallet_revive::Error::<Self::T>::PrecompileDelegateDenied,
		);

		let asset_id = PrecompileConfig::AssetIdExtractor::asset_id_from_address(address)?.into();
		let contract_addr = H160::from(*address);

		match input {
			// State-changing calls - check read-only
			IERC20Calls::transfer(_) |
			IERC20Calls::approve(_) |
			IERC20Calls::transferFrom(_) |
			IERC20Calls::permit(_)
				if env.is_read_only() =>
			{
				Err(Error::Error(pallet_revive::Error::<Self::T>::StateChangeDenied.into()))
			},

			// ERC20 functions
			IERC20Calls::transfer(call) => Self::transfer(asset_id, call, env),
			IERC20Calls::totalSupply(_) => Self::total_supply(asset_id, env),
			IERC20Calls::balanceOf(call) => Self::balance_of(asset_id, call, env),
			IERC20Calls::allowance(call) => Self::allowance(asset_id, call, env),
			IERC20Calls::approve(call) => Self::approve(asset_id, call, env),
			IERC20Calls::transferFrom(call) => Self::transfer_from(asset_id, call, env),

			// ERC20Permit functions (EIP-2612)
			IERC20Calls::permit(call) => Self::permit(asset_id, contract_addr, call, env),
			IERC20Calls::nonces(call) => Self::nonces(contract_addr, call, env),
			IERC20Calls::DOMAIN_SEPARATOR(_) => {
				Self::domain_separator(asset_id, contract_addr, env)
			},

			// ERC20Metadata functions
			IERC20Calls::name(_) => Self::name(asset_id, env),
			IERC20Calls::symbol(_) => Self::symbol(asset_id, env),
			IERC20Calls::decimals(_) => Self::decimals(asset_id, env),
		}
	}
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

**File:** substrate/frame/revive/src/address.rs (L138-147)
```rust
	fn to_account_id(address: &H160) -> AccountId32 {
		<OriginalAccount<T>>::get(address).unwrap_or_else(|| Self::to_fallback_account_id(address))
	}

	fn to_fallback_account_id(address: &H160) -> AccountId32 {
		let mut account_id = AccountId32::new([0xEE; 32]);
		let account_bytes: &mut [u8; 32] = account_id.as_mut();
		account_bytes[..20].copy_from_slice(address.as_bytes());
		account_id
	}
```
