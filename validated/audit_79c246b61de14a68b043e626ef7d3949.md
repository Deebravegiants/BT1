[1](#0-0) [2](#0-1)

### Citations

**File:** substrate/frame/revive/src/exec.rs (L1204-1224)
```rust
		// We need to make sure that changes made to the contract info are not discarded.
		// See the `in_memory_changes_not_discarded` test for more information.
		// We do not store on instantiate because we do not allow to call into a contract
		// from its own constructor.
		//
		// Additionally, we need to apply pending storage changes to the ContractInfo before
		// saving it, so that child frames can correctly calculate storage deposit refunds.
		// See: <https://github.com/paritytech/contract-issues/issues/213>
		let frame = self.top_frame();
		if let (CachedContract::Cached(contract), ExportedFunction::Call) =
			(&frame.contract_info, frame.entry_point)
		{
			let mut contract_with_pending_changes = contract.clone();
			frame
				.frame_meter
				.apply_pending_storage_changes(&mut contract_with_pending_changes);
			AccountInfo::<T>::insert_contract(
				&T::AddressMapper::to_address(&frame.account_id),
				contract_with_pending_changes,
			);
		}
```

**File:** substrate/frame/revive/src/exec.rs (L1238-1246)
```rust
			// EIP-684: an in-construction address is not in `AccountInfoOf` yet, so the
			// `is_contract` guard in `ContractInfo::new` misses this re-entrant collision.
			if frame.entry_point == ExportedFunction::Constructor &&
				self.frames().any(|f| {
					f.entry_point == ExportedFunction::Constructor &&
						f.account_id == frame.account_id
				}) {
				return Err(Error::<T>::DuplicateContract.into());
			}
```
