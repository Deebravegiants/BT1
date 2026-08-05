### Title
Bypass of `UploadOrigin`/`InstantiateOrigin` permissioning via contract-to-contract instantiation - (File: `substrate/frame/contracts/src/exec.rs`, function `Stack::new_frame` / `Ext::instantiate`)

### Summary
The external report describes an access-control failure where a malicious CosmWasm contract, invoked through IBC, can bypass an intended authorization check because the check is only enforced at the top-level entry point and not re-checked for actions triggered indirectly by contract logic. `pallet-contracts` in this repo exhibits the same *class* of bug: the runtime-configurable `UploadOrigin`/`InstantiateOrigin` permissioning is enforced only on the top-level extrinsics (`instantiate`, `instantiate_with_code`, `upload_code`) via `Invokable::ensure_origin`, but is **not** re-checked when a contract instantiates another contract from within Wasm execution (`Ext::instantiate` → `Stack::new_frame`/`push_frame`).

### Finding Description
`pallet-contracts::lib.rs` documents this exact gap itself, via `prdoc/1.9.0/pr_3377.prdoc`:

> "This PR introduces two new config types that specify the origins allowed to upload and instantiate contract code. However, this check is not enforced when a contract instantiates another contract." [1](#0-0) 

The origin check lives in `Invokable::run_guarded`, which calls `self.ensure_origin(common.origin.clone())` before dispatching a call/instantiate — but this is only invoked from the pallet's public dispatchable entry points, not from the internal `Ext::instantiate` path used when a contract calls `seal_instantiate` to spawn a sub-contract: [2](#0-1) 

The actual instantiation of a nested contract goes through `Stack::push_frame` → `Stack::new_frame`, which builds the new `Frame` for `FrameArgs::Instantiate` directly from the `code_hash`/executable supplied by the calling contract, with no origin/permission gate of any kind: [3](#0-2) [4](#0-3) 

The `Ext` trait's `instantiate` method (the interface a contract uses to spawn a new contract) likewise has no `InstantiateOrigin`/`UploadOrigin` check baked in: [5](#0-4) 

This means that if a chain configures `Config::UploadOrigin`/`Config::InstantiateOrigin` to restrict *who* may deploy code on-chain (e.g., to a whitelist of governance-approved accounts, a common permissioning pattern for parachains that want to gate contract deployment), any already-deployed contract can still instantiate arbitrary new contracts from arbitrary code hashes already present in storage, completely sidestepping that restriction. This is structurally analogous to the CosmWasm/IBC report: a permission check that exists at the "outer" entry point is bypassable via nested/indirect execution paths that a malicious contract controls.

### Impact Explanation
On any parachain/runtime that relies on `UploadOrigin`/`InstantiateOrigin` to gate who can deploy contracts (a config knob explicitly added for permissioned deployments), a user who is not permitted to instantiate contracts directly can get the same effect by:
1. Deploying (or reusing) any contract that is permitted to call `seal_instantiate`.
2. Having that contract instantiate a target `code_hash` on the caller's behalf.

This defeats the intended access-control model, potentially allowing unauthorized parties to deploy/spawn contracts that mint tokens, drain funds, or read/write privileged storage that the permissioning was meant to prevent — directly matching the "unauthorized access... loss of money... unexpected minting of tokens" impact described in the source report.

### Likelihood Explanation
Moderate. It requires:
- A runtime configuration that actually restricts `InstantiateOrigin`/`UploadOrigin` (not all `pallet-contracts` deployments use permissioned deployment; Substrate's default config allows any signed origin).
- At least one contract with a permitted origin already deployed and callable by the attacker (a very low bar — the attacker doesn't need to bypass `UploadOrigin` for the *helper* contract if any permissive contract already exists, or if the attacker itself is permitted to deploy at least one benign-looking contract).

This is acknowledged in-repo as a known, documented gap (see the prdoc), which matches the report's "Acknowledged" status pattern — this is not a hypothetical or mocked-only path; it's reachable by an ordinary account that can call any existing contract's `call` extrinsic to trigger nested instantiation.

### Recommendation
Enforce `Config::InstantiateOrigin` (and, where relevant, `UploadOrigin` for `instantiate_with_code`-equivalent nested flows) inside `Ext::instantiate`/`Stack::new_frame` for `FrameArgs::Instantiate`, not only in the top-level `Invokable::ensure_origin` gate in `lib.rs`. The check should be origin-aware of the *original* extrinsic signer (or the pallet should explicitly document/restrict this as a known limitation and disallow contract-triggered instantiation entirely when permissioned deployment is configured).

### Proof of Concept
Given a runtime with `Config::InstantiateOrigin = EnsureSignedBy<Whitelist>` (only whitelisted accounts may instantiate):
1. Attacker (not in `Whitelist`) is nonetheless permitted to `call` some already-deployed, permissively-callable contract `Helper` (deployment of `Helper` needed only once, by any whitelisted party or via any pre-existing permissive contract).
2. Attacker calls `Contracts::call(Helper, ...)` with input instructing `Helper`'s Wasm to invoke `seal_instantiate` with a `code_hash` for a malicious contract `Evil`.
3. `Stack::push_frame`/`new_frame` (`substrate/frame/contracts/src/exec.rs:866-907`) creates the new instantiation frame for `Evil` purely from `Helper`'s call — no re-check of `Config::InstantiateOrigin` against the original extrinsic signer occurs.
4. `Evil` is instantiated successfully despite the attacker never holding `InstantiateOrigin` permission, confirming the bypass. [1](#0-0) [5](#0-4)

### Citations

**File:** prdoc/1.9.0/pr_3377.prdoc (L1-14)
```text
# Schema: Polkadot SDK PRDoc Schema (prdoc) v1.0.0
# See doc at https://raw.githubusercontent.com/paritytech/polkadot-sdk/master/prdoc/schema_user.json

title: Permissioned contract deployment

doc:
  - audience: Runtime Dev
    description: |
      This PR introduces two new config types that specify the origins allowed to
      upload and instantiate contract code. However, this check is not enforced when
      a contract instantiates another contract.

crates: 
- name: pallet-contracts
```

**File:** substrate/frame/contracts/src/lib.rs (L1502-1516)
```rust
	fn run_guarded(self, common: CommonInput<T>) -> InternalOutput<T, Self::Output> {
		let gas_limit = common.gas_limit;

		// Check whether the origin is allowed here. The logic of the access rules
		// is in the `ensure_origin`, this could vary for different implementations of this
		// trait. For example, some actions might not allow Root origin as they could require an
		// AccountId associated with the origin.
		if let Err(e) = self.ensure_origin(common.origin.clone()) {
			return InternalOutput {
				gas_meter: GasMeter::new(gas_limit),
				storage_deposit: Default::default(),
				result: Err(ExecError { error: e.into(), origin: ErrorOrigin::Caller }),
			};
		}

```

**File:** substrate/frame/contracts/src/exec.rs (L166-179)
```rust
	/// Instantiate a contract from the given code.
	///
	/// Returns the original code size of the called contract.
	/// The newly created account will be associated with `code`. `value` specifies the amount of
	/// value transferred from the caller to the newly created account.
	fn instantiate(
		&mut self,
		gas_limit: Weight,
		deposit_limit: BalanceOf<Self::T>,
		code: CodeHash<Self::T>,
		value: BalanceOf<Self::T>,
		input_data: Vec<u8>,
		salt: &[u8],
	) -> Result<(AccountIdOf<Self::T>, ExecReturnValue), ExecError>;
```

**File:** substrate/frame/contracts/src/exec.rs (L866-907)
```rust
				FrameArgs::Instantiate { sender, nonce, executable, salt, input_data } => {
					let account_id = Contracts::<T>::contract_address(
						&sender,
						&executable.code_hash(),
						input_data,
						salt,
					);
					let contract = ContractInfo::new(&account_id, nonce, *executable.code_hash())?;
					(
						account_id,
						contract,
						executable,
						None,
						ExportedFunction::Constructor,
						Some(nonce),
					)
				},
			};

		// `Relaxed` will only be ever set in case of off-chain execution.
		// Instantiations are never allowed even when executing off-chain.
		if !(executable.is_deterministic() ||
			(matches!(determinism, Determinism::Relaxed) &&
				matches!(entry_point, ExportedFunction::Call)))
		{
			return Err(Error::<T>::Indeterministic.into());
		}

		let frame = Frame {
			delegate_caller,
			value_transferred,
			contract_info: CachedContract::Cached(contract_info),
			account_id,
			entry_point,
			nested_gas: gas_meter.nested(gas_limit),
			nested_storage: storage_meter.nested(deposit_limit),
			allows_reentry: true,
			read_only,
		};

		Ok((frame, executable, nonce))
	}
```

**File:** substrate/frame/contracts/src/exec.rs (L909-948)
```rust
	/// Create a subsequent nested frame.
	fn push_frame(
		&mut self,
		frame_args: FrameArgs<T, E>,
		value_transferred: BalanceOf<T>,
		gas_limit: Weight,
		deposit_limit: BalanceOf<T>,
		read_only: bool,
	) -> Result<E, ExecError> {
		if self.frames.len() == T::CallStack::size() {
			return Err(Error::<T>::MaxCallDepthReached.into());
		}

		// We need to make sure that changes made to the contract info are not discarded.
		// See the `in_memory_changes_not_discarded` test for more information.
		// We do not store on instantiate because we do not allow to call into a contract
		// from its own constructor.
		let frame = self.top_frame();
		if let (CachedContract::Cached(contract), ExportedFunction::Call) =
			(&frame.contract_info, frame.entry_point)
		{
			<ContractInfoOf<T>>::insert(frame.account_id.clone(), contract.clone());
		}

		let frame = top_frame_mut!(self);
		let nested_gas = &mut frame.nested_gas;
		let nested_storage = &mut frame.nested_storage;
		let (frame, executable, _) = Self::new_frame(
			frame_args,
			value_transferred,
			nested_gas,
			gas_limit,
			nested_storage,
			deposit_limit,
			self.determinism,
			read_only,
		)?;
		self.frames.push(frame);
		Ok(executable)
	}
```
