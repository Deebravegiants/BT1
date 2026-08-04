## Analysis

The reported pattern — a non‑payable, token‑transfer‑style function that silently accepts and strands native currency because nobody checks `msg.value == 0` — has a concrete analog in `pallet-revive`'s ERC20 precompile.

### Root cause

In `pallet-revive`, every call/instantiate frame unconditionally transfers the attached native `value` from the caller to the callee's underlying account **before** the callee's logic (including a precompile's `call()`) ever runs: [1](#0-0) 

This happens regardless of whether the destination is a normal contract, a plain account, or a precompile. The ERC20 precompile (`substrate/frame/assets/precompiles/src/lib.rs`), which implements the standard, non‑payable `transfer`/`approve`/`transferFrom`/`permit` ABI, never inspects or validates the value that was attached to the call — it only checks read‑only state, never `env.value_transferred()`: [2](#0-1) [3](#0-2) 

The `Ext` trait exposes `value_transferred()` specifically so callees *can* check this, but the precompile ignores it: [4](#0-3) 

Since `HAS_CONTRACT_INFO = false` for this precompile, no real "contract" account is expected to exist at its address, but the native-value transfer path in `exec.rs` still creates/funds the account behind that address (via `transfer`, pulling in the ED if needed): [5](#0-4) 

The resulting `AccountId` is a synthetic "fallback" address derived deterministically from the precompile's `H160` (asset-id-encoded address), not from any real key: [6](#0-5) 

Because this address was never derived from an actual signing key, nobody can produce a signature to spend from it — the native value (and the ED that gets pulled in with it) becomes permanently unrecoverable.

### Reachability

This is directly reachable by an unprivileged user via the public `call` extrinsic, which lets a signed origin freely choose `dest` (the precompile address) and `value` (any non-zero native amount) together with ABI-encoded `data` (e.g. an ERC20 `transfer`/`approve` call): [7](#0-6) 

It is also reachable from Solidity/EVM bytecode via a raw low-level `call{value: x}(...)` (bypassing the compiler's "non-payable" enforcement, which only applies to normal high-level Solidity calls, not manually crafted low-level calls or malicious/buggy contracts), through the EVM `CALL` opcode handling: [8](#0-7) 

### Assessment

This is a legitimate analog of the reported class (missing `msg.value == 0` guard on a non-payable token-operation entry point causing user-inflicted, permanent loss of native currency), and it is reachable by any unprivileged signed account without any trusted-role assumption, matching the report's own impact framing (self-inflicted fund lock, not third-party fund theft).

### Title
Native value attached to ERC20 precompile calls is transferred and permanently locked because the precompile never validates `value_transferred() == 0` - (File: `substrate/frame/assets/precompiles/src/lib.rs`)

### Summary
`pallet-revive`'s built-in ERC20 precompile (`substrate/frame/assets/precompiles/src/lib.rs`) implements the standard non-payable `IERC20` interface (`transfer`, `approve`, `transferFrom`, `permit`) but never checks that no native value was attached to the call. Meanwhile, `pallet-revive`'s frame execution engine (`substrate/frame/revive/src/exec.rs`) unconditionally transfers any attached native `value` from the caller into the account underlying the callee address *before* the callee (including a precompile) executes. Because the precompile's address maps to a synthetic "fallback" `AccountId` with no corresponding private key (`substrate/frame/revive/src/address.rs`), any native value attached to a call targeting the precompile is irrecoverably stranded.

### Finding Description
- `Pallet::call` and `bare_call` accept an arbitrary `dest: H160` and `value: BalanceOf<T>` chosen entirely by the caller [7](#0-6) .
- Regardless of the destination type, the top execution frame transfers `frame.value_transferred` from the caller to the destination account before invoking either the contract executable or the precompile's `call()`/`call_with_info()` [9](#0-8) .
- The ERC20 precompile dispatch logic only guards against read-only state changes; it never inspects `env.value_transferred()` for any of its state-changing entry points (`transfer`, `approve`, `transferFrom`, `permit`) [10](#0-9) .
- The destination `AccountId` for the precompile's `H160` address is a stateless "fallback" account derived purely by byte-manipulation, with no corresponding private key, since the address was never registered via a real signing key [6](#0-5) .
- If the destination account doesn't yet exist, `exec.rs::transfer` will even pull it into existence by additionally transferring the Existential Deposit from the caller [5](#0-4) .

### Impact Explanation
Any native currency (plus ED, if the target account doesn't exist yet) mistakenly attached to a call targeting the ERC20 precompile is transferred out of the caller's balance and becomes permanently unspendable, since no private key exists for the fallback account. This mirrors the original report's impact class: user funds are locked forever due to a missing "no native value for this token operation" guard. There is no path within the precompile to refund or reclaim the value.

### Likelihood Explanation
Reachable by any unprivileged, signed account via the public `pallet_revive::call` extrinsic by simply specifying a non-zero `value` alongside a `dest` equal to a precompile's address and ABI-encoded ERC20 call data — no special role or condition is required. It can also occur via low-level EVM `CALL{value: x}` from a buggy or naively-generated contract, since Solidity's high-level non-payable enforcement doesn't apply to manually encoded low-level calls. Realistic triggers include tooling/wallet bugs or copy-pasted call-construction code that sets a non-zero value out of habit (e.g., mirroring a payable-pattern from elsewhere), analogous to how the original Nested Finance bug arose from users/integrators misusing a function signature.

### Recommendation
In the ERC20 precompile's `call()` dispatch (and any other non-payable precompile entry point in `pallet-revive`), reject calls carrying non-zero attached value before performing any state-changing logic, e.g.:
```rust
frame_support::ensure!(
    env.value_transferred().is_zero(),
    pallet_revive::Error::<Self::T>::...NonZeroValueForNonPayableCall...,
);
```
Ideally this check should happen prior to the unconditional balance transfer in `exec.rs`'s `run()` path for precompiles that don't declare themselves as accepting value, so that the value transfer itself is prevented rather than just rejecting the subsequent logic after the funds have already moved.

### Proof of Concept
1. Deploy/use an existing asset registered with the ERC20 precompile at address `P` (e.g. via `PRECOMPILE_ADDRESS_PREFIX`).
2. As any signed account `Alice` holding native balance, call `pallet_revive::Pallet::call(origin=Alice, dest=P, value=1_000_000_000, weight_limit=.., storage_deposit_limit=.., data=IERC20::transferCall{to: Bob, value: X}.abi_encode())`.
3. Observe: the ERC20 `transfer` semantics execute normally (asset units move from Alice to Bob via `pallet_assets`), but Alice's native balance is additionally reduced by `1_000_000_000` (plus ED, if the precompile's underlying account did not exist), which is credited to the fallback `AccountId` computed in `substrate/frame/revive/src/address.rs::AccountId32Mapper::to_fallback_account_id(P)`.
4. Confirm no dispatchable call, precompile function, or off-chain key exists that can move funds out of that fallback account back to Alice or anyone else — the value is permanently locked.

### Citations

**File:** substrate/frame/revive/src/exec.rs (L424-425)
```rust
	/// Returns the value transferred along with this call.
	fn value_transferred(&self) -> U256;
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

**File:** substrate/frame/revive/src/vm/evm/instructions/contract.rs (L105-128)
```rust
/// Implements the CALL instruction.
///
/// Message call with value transfer to another account.
pub fn call<E: Ext>(interpreter: &mut Interpreter<E>) -> ControlFlow<Halt> {
	let [gas_limit, to, value] = interpreter.stack.popn()?;
	let to = to.into_address();
	let has_transfer = !value.is_zero();
	if interpreter.ext.is_read_only() && has_transfer {
		return ControlFlow::Break(Error::<E::T>::StateChangeDenied.into());
	}
	let (input, return_memory_range) = get_memory_in_and_out_ranges(interpreter)?;
	let scheme = CallScheme::Call;
	charge_call_gas(interpreter, to, scheme, input.len(), value)?;

	run_call(
		interpreter,
		to,
		gas_limit,
		interpreter.memory.slice(input).to_vec(),
		scheme,
		value,
		return_memory_range,
	)
}
```
