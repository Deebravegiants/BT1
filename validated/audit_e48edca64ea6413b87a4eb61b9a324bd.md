Confirmed: `set_epoch_length` (`modules/ismp/clients/bsc/src/pallet.rs:79-94`) writes `EpochLength::<T>::put(params.epoch_length)` with no bound checks, and `verify_consensus` (`modules/ismp/clients/bsc/src/lib.rs:95-98`) unconditionally divides by that value via `compute_epoch(number, epoch_length)` (`modules/consensus/bsc/verifier/src/primitives.rs:206-208`, `number / epoch_length`), and `get_rotation_block` also computes `% epoch_length`. This is the same bug class as the report: an unvalidated numeric parameter feeding an unconditional arithmetic operation on the hot path, permanently DOSing the BSC consensus route.

### Title
BSC `epoch_length` is settable to zero, causing every subsequent BSC consensus update to panic on division-by-zero and permanently freezing the BSC light client route - (File: modules/ismp/clients/bsc/src/pallet.rs, modules/ismp/clients/bsc/src/lib.rs, modules/consensus/bsc/verifier/src/primitives.rs)

### Summary
`pallet_ismp_bsc::set_epoch_length` stores an admin/governance-supplied `epoch_length` value into `EpochLength<T>` storage without validating it is non-zero. `BscClient::verify_consensus` reads this stored value and passes it into `compute_epoch(number, epoch_length) = number / epoch_length` and `get_rotation_block(...)`, both of which perform integer division/modulo by `epoch_length` unconditionally on every consensus proof submission. If `epoch_length` is ever set to `0`, every subsequent `update_client` extrinsic carrying a BSC consensus proof will panic with a division-by-zero, and there is no way to correct the parameter because `set_epoch_length` itself does not go through `verify_consensus`, but any attempt to update the BSC light client thereafter is permanently broken until a runtime upgrade or storage migration fixes the value.

### Finding Description
`set_epoch_length` in `modules/ismp/clients/bsc/src/pallet.rs`:
```rust
pub fn set_epoch_length(origin: OriginFor<T>, params: UpdateParams) -> DispatchResult {
    <T as Config>::AdminOrigin::ensure_origin(origin)?;
    let host = <T as Config>::IsmpHost::default();
    EpochLength::<T>::put(params.epoch_length);
    ...
}
```
performs no validation whatsoever on `params.epoch_length` — it accepts and stores `0` just as readily as any other value.

`BscClient::verify_consensus` in `modules/ismp/clients/bsc/src/lib.rs` reads this value on the hot path of every consensus update:
```rust
let epoch_length = Pallet::<T>::epoch_length().ok_or(Error::EpochLengthNotSet)?;
if let Some(next_validators) = consensus_state.next_validators.clone() {
    let attested_epoch = compute_epoch(attested_number, epoch_length);
    let rotation_epoch = compute_epoch(next_validators.rotation_block, epoch_length);
    ...
}
```
and `compute_epoch` in `modules/consensus/bsc/verifier/src/primitives.rs`:
```rust
pub fn compute_epoch(number: u64, epoch_length: u64) -> u64 {
    number / epoch_length
}
```
divides unconditionally with no zero-check. Once `epoch_length == 0`, this function panics (Rust always traps on integer division by zero, regardless of build profile). `get_rotation_block` (`modules/consensus/bsc/prover/src/lib.rs:216-223`), used by relayer tooling and mirrored on-chain via `ensure_finalized_epoch_consistent`, likewise computes `block % epoch_length`, which also panics at `epoch_length == 0`.

This exactly mirrors the reported bug class: a privileged-but-unvalidated setter writes a numeric parameter that a downstream, frequently and permissionlessly triggered code path unconditionally divides/multiplies by, with no floor/guard, resulting in an unrecoverable failure state once an unprivileged party (a relayer) exercises that path.

### Impact Explanation
Once `epoch_length` is `0`, any relayer submitting a legitimate `ConsensusMessage` for the BSC client causes `verify_consensus` to panic. Because this is invoked from the consensus-message handling path (`update_client` in `modules/ismp/core/src/handlers/consensus.rs`) which is reachable by any relayer submitting a proof, this permanently prevents the BSC light client from ever advancing again — freezing all state commitments, and therefore all cross-chain messages, requests, and responses that depend on BSC state proofs. This is a "route unable to deliver messages" condition as described in the validation criteria, and it cannot be self-healed since the only fix (calling `set_epoch_length` again) does not go through the panicking path, but the client itself remains stuck at its last finalized state until governance intervenes — meanwhile funds/messages relying on the BSC route are frozen for an indefinite period.

### Likelihood Explanation
This requires an admin/governance action (`AdminOrigin`) to misconfigure `epoch_length` as `0`, either by mistake (fat-fingering, migration error, or copy-paste from a template expecting a different unit) or by any other pathway that causes the parameter to be zero. There is no on-chain guard preventing this, unlike `EvmHost.updateHostParamsInternal`, which validates similar parameters (e.g. `unStakingPeriod`, `stateMachines.length`) to explicitly "prevent the host from getting bricked." The BSC epoch-length setter has no equivalent safeguard, so likelihood is non-trivial given the sensitivity of the value and the total absence of validation.

### Recommendation
Add a validation check in `set_epoch_length` (and anywhere else `EpochLength` can be set) that rejects `epoch_length == 0`, mirroring the defensive checks already present in `EvmHost::updateHostParamsInternal` for other critical parameters (e.g., `InvalidUnstakingPeriod`). Additionally, consider adding a defensive `checked_div`/explicit zero-check inside `compute_epoch` and `get_rotation_block` so that a future caller cannot reintroduce this panic path.

### Proof of Concept
1. Governance/`AdminOrigin` calls `pallet_ismp_bsc::set_epoch_length` with `UpdateParams { epoch_length: 0, consensus_state: None, consensus_state_id: None }`. This succeeds and overwrites `EpochLength<T>` with `0` (`modules/ismp/clients/bsc/src/pallet.rs:79-94`).
2. Any relayer subsequently submits a `ConsensusMessage` for the BSC consensus client (a normal, permissionless action) via `update_client` (`modules/ismp/core/src/handlers/consensus.rs:29`).
3. This calls `BscClient::verify_consensus` (`modules/ismp/clients/bsc/src/lib.rs:95-98`), which calls `compute_epoch(attested_number, 0)` → `attested_number / 0` → panics.
4. Every subsequent legitimate consensus update for BSC panics identically; the BSC light client can never advance again, freezing all messages/state proofs that depend on it. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** modules/ismp/clients/bsc/src/pallet.rs (L76-94)
```rust
		/// Sets the new BSC epoch length and resets the consensus state
		#[pallet::call_index(0)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 3))]
		pub fn set_epoch_length(origin: OriginFor<T>, params: UpdateParams) -> DispatchResult {
			<T as Config>::AdminOrigin::ensure_origin(origin)?;
			let host = <T as Config>::IsmpHost::default();
			EpochLength::<T>::put(params.epoch_length);
			if let Some((consensus_state_id, consensus_state)) = params
				.consensus_state_id
				.and_then(|id| params.consensus_state.map(|state| (id, state)))
			{
				host.store_consensus_state(consensus_state_id, consensus_state)
					.map_err(|_| Error::<T>::ErrorStoringConsensusState)?;
			}

			Self::deposit_event(Event::<T>::NewEpochLength { epoch_length: params.epoch_length });

			Ok(())
		}
```

**File:** modules/ismp/clients/bsc/src/lib.rs (L88-99)
```rust
		if consensus_state.finalized_height >= bsc_client_update.source_header.number.low_u64() {
			Err(Error::ExpiredUpdate {
				current: consensus_state.finalized_height,
				update: bsc_client_update.source_header.number.low_u64(),
			})?
		}

		let epoch_length = Pallet::<T>::epoch_length().ok_or(Error::EpochLengthNotSet)?;
		if let Some(next_validators) = consensus_state.next_validators.clone() {
			let attested_number = bsc_client_update.attested_header.number.low_u64();
			let attested_epoch = compute_epoch(attested_number, epoch_length);
			let rotation_epoch = compute_epoch(next_validators.rotation_block, epoch_length);
```

**File:** modules/consensus/bsc/verifier/src/primitives.rs (L206-208)
```rust
pub fn compute_epoch(number: u64, epoch_length: u64) -> u64 {
	number / epoch_length
}
```

**File:** modules/consensus/bsc/prover/src/lib.rs (L216-223)
```rust
pub fn get_rotation_block(block: u64, validator_size: u64, epoch_length: u64) -> u64 {
	let target = validator_size / 2;
	let current = block % epoch_length;
	// Distance forward to the next slot `epoch * epoch_length + target`, wrapping
	// to the next epoch if we're already past `target` inside the current one.
	let offset = (target + epoch_length - current) % epoch_length;
	block + offset
}
```

**File:** modules/ismp/core/src/handlers/consensus.rs (L29-49)
```rust
pub fn update_client<H>(host: &H, msg: ConsensusMessage) -> Result<MessageResult, anyhow::Error>
where
	H: IsmpHost,
{
	let consensus_client_id = host.consensus_client_id(msg.consensus_state_id).ok_or(
		Error::ConsensusStateIdNotRecognized { consensus_state_id: msg.consensus_state_id },
	)?;
	let consensus_client = host.consensus_client(consensus_client_id)?;
	let trusted_state = host.consensus_state(msg.consensus_state_id)?;
	host.is_consensus_client_frozen(msg.consensus_state_id)?;
	host.is_expired(msg.consensus_state_id)?;

	let (new_state, intermediate_states) = consensus_client.verify_consensus(
		host,
		msg.consensus_state_id,
		trusted_state,
		msg.consensus_proof,
	)?;
	host.store_consensus_state(msg.consensus_state_id, new_state)?;
	let timestamp = host.timestamp();
	host.store_consensus_update_time(msg.consensus_state_id, timestamp)?;
```
