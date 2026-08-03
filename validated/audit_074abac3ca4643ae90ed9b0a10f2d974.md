No vulnerability found for this question.

**Reasoning:**

`AptosModuleExtension::new` simply unpacks a `StateValue` that has already been fetched from the authenticated global state (via `state_view.get_state_value` / `get_state_slot`), splitting it into `(state_value_metadata, bytes)` and computing a hash over the bytes portion only [1](#0-0) . There is no code path here that lets unprivileged transaction, package, or bytecode input construct or forge a `StateValue`; the value comes from storage reads driven by `StateKey::module_id(&key)` against the actual state tree [2](#0-1)  and [3](#0-2) .

The `state_value_metadata` itself is set at slot-creation time by `DiskSpacePricing::charge_refund_write_op_v2`, which records `slot_deposit`/`bytes_deposit` on the metadata attached to the write op driven by the actual paying account's transaction context — not something derivable from arbitrary attacker bytes [4](#0-3) . On deletion, the refund is simply `op.metadata_mut.total_deposit()`, i.e., whatever deposit was already recorded in the state slot when it was created/last modified [5](#0-4) . The refund goes back into the gas/fee flow of the executing transaction sender (the one performing the deletion), which is the standard, intended custody-neutral mechanic — it is not "credited to the wrong holder" based on any manipulable field in `AptosModuleExtension`.

The premise that an "attacker-controlled StateValue construction" can be injected into this code path is not supported: `AptosModuleExtension::new` is only invoked on `StateValue`s already read back from committed, authenticated storage (state view / JMT), never on attacker-supplied raw bytes bypassing that read. There is no unprivileged entrypoint that lets a caller substitute a crafted `StateValue` for the one obtained from `state_view.get_state_value`/`get_state_slot`. The proposed unit test ("unpack a crafted StateValue and assert metadata matches original depositor") would trivially pass regardless, since `unpack()` is a pure destructuring operation with no logic that could corrupt or misattribute the metadata [6](#0-5) .

This does not cross a real custody boundary — it requires an attacker to already control the state store's content, which is excluded from scope (not an unprivileged transaction/API/bytecode-driven manipulation).

### Citations

**File:** types/src/vm/modules.rs (L22-37)
```rust
impl AptosModuleExtension {
    /// Creates new extension based on [StateValue].
    pub fn new(state_value: StateValue) -> Self {
        let (state_value_metadata, bytes) = state_value.unpack();
        let hash = sha3_256(&bytes);
        Self {
            bytes,
            hash,
            state_value_metadata,
        }
    }

    /// Returns the state value metadata stored in extension.
    pub fn state_value_metadata(&self) -> &StateValueMetadata {
        &self.state_value_metadata
    }
```

**File:** aptos-move/aptos-vm-types/src/module_and_script_storage/state_view_adapter.rs (L122-151)
```rust
        let (state_view, verified_modules_iter) = self
            .storage
            .into_module_storage()
            .unpack_into_verified_modules_iter();

        Ok(verified_modules_iter
            .map(|(key, verified_code)| {
                // We have cached the module previously, so we must be able to find it in storage.
                let extension = state_view
                    .get_state_value(&StateKey::module_id(&key))
                    .map_err(|err| {
                        let msg = format!(
                            "Failed to retrieve module {}::{} from storage {:?}",
                            key.address(),
                            key.name(),
                            err
                        );
                        PanicError::CodeInvariantError(msg)
                    })?
                    .map_or_else(
                        || {
                            let msg = format!(
                                "Module {}::{} should exist, but it does not anymore",
                                key.address(),
                                key.name()
                            );
                            Err(PanicError::CodeInvariantError(msg))
                        },
                        |state_value| Ok(AptosModuleExtension::new(state_value)),
                    )?;
```

**File:** aptos-move/aptos-resource-viewer/src/module_view.rs (L291-311)
```rust
    fn build(
        &self,
        key: &Self::Key,
    ) -> VMResult<Option<ModuleCode<Self::Deserialized, Self::Verified, Self::Extension>>> {
        let state_value = match self
            .state_view
            .get_state_value(&StateKey::module_id(key))
            .map_err(|err| module_storage_error!(key.address(), key.name(), err))?
        {
            Some(state_value) => state_value,
            None => return Ok(None),
        };
        let (compiled_module, extension) = self
            .try_override_bytes_and_deserialized_into_compiled_module_with_ext(
                state_value,
                key.address(),
                key.name(),
            )?;
        let module = ModuleCode::from_deserialized(compiled_module, extension);
        Ok(Some(module))
    }
```

**File:** aptos-move/aptos-vm-types/src/storage/space_pricing.rs (L163-213)
```rust
    fn charge_refund_write_op_v2(
        params: &TransactionGasParameters,
        op: WriteOpInfo,
    ) -> ChargeAndRefund {
        use WriteOpSize::*;

        let key_size = op.key.size() as u64;
        let num_bytes = key_size + op.op_size.write_len().unwrap_or(0);
        let target_bytes_deposit: u64 = num_bytes * u64::from(params.storage_fee_per_state_byte);

        match op.op_size {
            Creation { .. } => {
                // permanent storage fee
                let slot_deposit = u64::from(params.storage_fee_per_state_slot);

                op.metadata_mut.maybe_upgrade();
                op.metadata_mut.set_slot_deposit(slot_deposit);
                op.metadata_mut.set_bytes_deposit(target_bytes_deposit);

                ChargeAndRefund {
                    charge: (slot_deposit + target_bytes_deposit).into(),
                    refund: 0.into(),
                }
            },
            Modification { write_len } => {
                // Change of slot size or per byte price can result in a charge or refund of the bytes fee.
                let old_bytes_deposit = op.metadata_mut.bytes_deposit();
                let state_bytes_charge =
                    if write_len > op.prev_size && target_bytes_deposit > old_bytes_deposit {
                        let charge_by_increase: u64 = (write_len - op.prev_size)
                            * u64::from(params.storage_fee_per_state_byte);
                        let gap_from_target = target_bytes_deposit - old_bytes_deposit;
                        std::cmp::min(charge_by_increase, gap_from_target)
                    } else {
                        0
                    };
                op.metadata_mut.maybe_upgrade();
                op.metadata_mut
                    .set_bytes_deposit(old_bytes_deposit + state_bytes_charge);

                ChargeAndRefund {
                    charge: state_bytes_charge.into(),
                    refund: 0.into(),
                }
            },
            Deletion => ChargeAndRefund {
                charge: 0.into(),
                refund: op.metadata_mut.total_deposit().into(),
            },
        }
    }
```
