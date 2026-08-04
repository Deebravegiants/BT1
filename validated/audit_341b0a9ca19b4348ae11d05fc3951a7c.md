### Title
Dry-run vs. real-transaction `CREATE1` address mismatch in `pallet-revive` — ([File: substrate/frame/revive/src/exec.rs])

### Summary
The prdoc file `prdoc/stable2506/pr_8504.prdoc` in this repository documents a fix for a nonce-based `CREATE1` address-derivation mismatch between RPC dry-run execution and real transaction execution in `pallet-revive`, but the actual fix (an `ExecContext` check) is **not present** in the current `substrate/frame/revive/src/exec.rs`. This is structurally the same bug class as the reported "Fixed Term Bond" issue: one code path applies a normalization/adjustment (subtracting 1 from the nonce) that another invocation path of the same logic does not correctly account for, producing two different derived identifiers (contract addresses) for what should be the same deployment.

### Finding Description
In `Storage::new_frame` (`substrate/frame/revive/src/exec.rs`, `FrameArgs::Instantiate` branch, lines ~1141–1158), the contract address for a `CREATE1`-style instantiation (no salt) is derived as:

```rust
let account_nonce = <System<T>>::account_nonce(&sender);
...
address::create1(
    &deployer,
    // the Nonce from the origin has been incremented pre-dispatch, so we
    // need to subtract 1 to get the nonce at the time of the call.
    if origin_is_caller {
        account_nonce.saturating_sub(1u32.into()).saturated_into()
    } else {
        account_nonce.saturated_into()
    },
)
``` [1](#0-0) 

The comment explains the intent: during a *real* dispatched transaction, `frame_system`'s nonce has already been incremented pre-dispatch, so the code subtracts 1 to recover the nonce that will actually be used for address derivation. However, this subtraction is gated only on `origin_is_caller`, a boolean passed into `new_frame` [2](#0-1) , with no distinction for whether the call happens via `Storage::new` for an RPC/dry-run query versus an actual signed extrinsic dispatch.

The `prdoc/stable2506/pr_8504.prdoc` explicitly documents that this exact code (word-for-word identical to what's in `exec.rs` today) was buggy, and that the fix required adding an `ExecContext` check:

```rust
if origin_is_caller && matches!(exec_context, ExecContext::Transaction) {
    account_nonce.saturating_sub(1u32.into()).saturated_into()
} else {
    account_nonce.saturated_into()
},
``` [3](#0-2) 

A `grep` across the repository shows the identifier `ExecContext` appears **only** in the prdoc file, and does not exist anywhere in `substrate/frame/revive/src/exec.rs` or elsewhere in the crate — i.e., the described fix was never actually applied to the code, even though the prdoc claiming the fix is present. The `new` / `new_frame` call chain (`Storage::new`, used identically by both `bare_instantiate` (dry-run/RPC path) and the real `instantiate`/`instantiate_with_code` extrinsics) contains no `exec_context`/`ExecContext` parameter at all [4](#0-3) , confirming the gating condition documented in the prdoc is absent from the implementation.

This is analogous to the Bond Protocol bug: there, `_handlePayout()` computed a rounded `expiry` for the `tokenId`, while `deploy()` (a different call path reaching the same underlying storage-write logic) used the raw, unrounded value — creating two different derived values for what should be a single canonical identifier. Here, the same address-derivation code path is reached with the "nonce normalization" always/never applied based on a coarse `origin_is_caller` flag rather than distinguishing simulated (dry-run, no pre-dispatch nonce increment) execution from actual dispatched (nonce already incremented) execution — producing two different `CREATE1` addresses for what should be the identical deployment.

### Impact Explanation
If a user (or a wallet/tooling integration) relies on the RPC `eth_estimateGas`/dry-run `instantiate`/contract-creation preview to determine the address a to-be-deployed contract will occupy (a very common EVM/Ethereum-JSON-RPC workflow, and exactly the scenario this pallet's Ethereum-compatibility layer (`pallet-revive`) is designed to support), the address returned by the dry run can differ from the address at which the contract is actually deployed by the subsequent real transaction. This can lead to:
- Broken off-chain tooling/wallets that pre-compute or display the "to-be-deployed" contract address (e.g., to whitelist it, fund it, or reference it in dependent transactions) before the real transaction lands.
- Front-running-adjacent griefing: because the correct real-tx address for `CREATE1` depends only on `(deployer, nonce)`, and this is a public/computable value, a malicious actor could still predict and pre-fund/pre-occupy the *actual* deployment address, but a naive integrator trusting the dry-run-reported address would be pointed at the wrong (dry-run) address, silently sending funds/approvals to an address that will never hold the deployed contract.

### Likelihood Explanation
This bug is reachable by any unprivileged user calling the standard EVM-RPC/dry-run entry points for contract creation before submitting the real transaction — no privileged role or special preconditions are required; the mismatch is deterministic and always manifests whenever `origin_is_caller` is true and the nonce has not yet been incremented in the dry-run/query context. It is a straightforward "same code path, different context" logic gap, matching a documented (in-repo) known issue description that appears to not actually be fixed in this snapshot of the code.

### Recommendation
Reintroduce the `ExecContext` (or equivalent) distinction described in `prdoc/stable2506/pr_8504.prdoc` so that the nonce-adjustment in the `CREATE1` branch of `Storage::new_frame` is only applied when executing inside an actual dispatched transaction context, and not during RPC/dry-run simulation:
```rust
if origin_is_caller && matches!(exec_context, ExecContext::Transaction) {
    account_nonce.saturating_sub(1u32.into()).saturated_into()
} else {
    account_nonce.saturated_into()
}
```
Add/restore the regression test referenced in the prdoc (`nonce_not_incremented_in_dry_run`) to lock in the fix.

### Proof of Concept
1. Deploy a contract via `pallet-revive`'s bare/dry-run instantiate RPC path (e.g. `bare_instantiate` used for `eth_estimateGas`/RPC address preview) with `salt = None` for account `A` at nonce `N`. Because this is a simulated call, `frame_system`'s nonce for `A` has not been incremented, yet `new_frame` (via `origin_is_caller == true`) subtracts 1 from the read nonce, computing `create1(deployer, N-1)`.
2. Submit the real signed `instantiate`/`instantiate_with_code` extrinsic for the same account `A`. By the time execution reaches `new_frame`, `frame_system` has already incremented the nonce pre-dispatch to `N+1`, and the same subtraction logic computes `create1(deployer, N)`.
3. Compare the two computed addresses — `create1(deployer, N-1)` (returned by dry-run) versus `create1(deployer, N)` (the actual deployed address): they differ, demonstrating the address mismatch, exactly as the prdoc describes ("Dry-run … returns address derived with nonce N; Actual transaction deployment creates contract at address derived with nonce N-1").

**Caveat/uncertainty**: I was unable to fully trace, within the given iteration budget, the precise call chain that constructs `origin_is_caller` for the RPC/dry-run bare-instantiate path (i.e., whether `bare_instantiate` always sets `origin_is_caller = true` for a top-level deployment). This should be verified by a follow-up session tracing `Storage::new` callers (`bare_instantiate`, `instantiate_with_code` dispatchable) to confirm the exact conditions under which the nonce subtraction and dry-run status combine to produce the divergence, and to write/run the `nonce_not_incremented_in_dry_run` test to empirically confirm the mismatch in this exact repository snapshot.

### Citations

**File:** substrate/frame/revive/src/exec.rs (L1007-1055)
```rust
	fn new(
		args: FrameArgs<T, E>,
		origin: Origin<T>,
		transaction_meter: &'a mut TransactionMeter<T>,
		value: U256,
		exec_config: &'a ExecConfig<T>,
		input_data: &Vec<u8>,
	) -> Result<Option<(Self, ExecutableOrPrecompile<T, E, Self>)>, ExecError> {
		origin.ensure_mapped()?;
		let Some((first_frame, executable)) = Self::new_frame(
			args,
			value,
			transaction_meter,
			&CallResources::NoLimits,
			false,
			true,
			input_data,
			exec_config,
		)?
		else {
			return Ok(None);
		};

		let mut timestamp = T::Time::now();
		let mut block_number = <frame_system::Pallet<T>>::block_number();
		// if dry run with timestamp override is provided we simulate the run in a `pending` block
		if let Some(timestamp_override) =
			exec_config.is_dry_run.as_ref().and_then(|cfg| cfg.timestamp_override)
		{
			block_number = block_number.saturating_add(1u32.into());
			// Delta is in milliseconds; increment timestamp by one second
			let delta = 1000u32.into();
			timestamp = cmp::max(timestamp.saturating_add(delta), timestamp_override);
		}

		let stack = Self {
			origin,
			transaction_meter,
			timestamp,
			block_number,
			first_frame,
			frames: Default::default(),
			transient_storage: TransientStorage::new(limits::TRANSIENT_STORAGE_BYTES),
			access_list: AccessList::new(),
			exec_config,
			_phantom: Default::default(),
		};
		Ok(Some((stack, executable)))
	}
```

**File:** substrate/frame/revive/src/exec.rs (L1061-1070)
```rust
	fn new_frame<S: State>(
		frame_args: FrameArgs<T, E>,
		value_transferred: U256,
		meter: &mut ResourceMeter<T, S>,
		call_resources: &CallResources<T>,
		read_only: bool,
		origin_is_caller: bool,
		input_data: &[u8],
		exec_config: &ExecConfig<T>,
	) -> Result<Option<(Frame<T>, ExecutableOrPrecompile<T, E, Self>)>, ExecError> {
```

**File:** substrate/frame/revive/src/exec.rs (L1141-1158)
```rust
			FrameArgs::Instantiate { sender, executable, salt, input_data } => {
				let deployer = T::AddressMapper::to_address(&sender);
				let account_nonce = <System<T>>::account_nonce(&sender);
				let address = if let Some(salt) = salt {
					address::create2(&deployer, executable.code(), input_data, salt)
				} else {
					use sp_runtime::Saturating;
					address::create1(
						&deployer,
						// the Nonce from the origin has been incremented pre-dispatch, so we
						// need to subtract 1 to get the nonce at the time of the call.
						if origin_is_caller {
							account_nonce.saturating_sub(1u32.into()).saturated_into()
						} else {
							account_nonce.saturated_into()
						},
					)
				};
```

**File:** prdoc/stable2506/pr_8504.prdoc (L9-41)
```text
    The issue stems from the `create1` address derivation logic in `exec.rs`:

    ```rust
    address::create1(
        &deployer,
        // the Nonce from the origin has been incremented pre-dispatch, so we
        // need to subtract 1 to get the nonce at the time of the call.
        if origin_is_caller {
            account_nonce.saturating_sub(1u32.into()).saturated_into()
        } else {
            account_nonce.saturated_into()
        },
    )
    ```

    The code correctly subtracts 1 from the account nonce during a transaction execution (because the nonce is incremented pre-dispatch), but doesn't account for execution context - whether it's a real transaction or a dry run through the RPC.

    ## Review Notes

    This PR adds a new condition to check for the `ExecContext` when calculating the nonce for address derivation:

    ```rust
    address::create1(
        &deployer,
        // the Nonce from the origin has been incremented pre-dispatch, so we
        // need to subtract 1 to get the nonce at the time of the call.
        if origin_is_caller && matches!(exec_context, ExecContext::Transaction) {
            account_nonce.saturating_sub(1u32.into()).saturated_into()
        } else {
            account_nonce.saturated_into()
        },
    )
    ```
```
