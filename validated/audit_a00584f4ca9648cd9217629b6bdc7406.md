[1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L218-227)
```text
    fun dispatch_withdraw_hook<T: key>(
        store: Object<T>,
        amount: u64,
        transfer_ref: &TransferRef,
        function: &FunctionInfo,
    ): FungibleAsset {
        let f = function.load_function_value<
            |Object<T>, u64, &TransferRef|FungibleAsset has copy + drop>();
        f(store, amount, transfer_ref)
    }
```

**File:** third_party/move/move-vm/runtime/src/reentrancy_checker.rs (L52-61)
```rust
impl CallType {
    /// Returns true of the call to callee needs to lock the module. This is the case if:
    ///   1. we are dispatching via native,
    ///   2. the callee has `#[module_lock]` attribute.
    fn is_locking(&self, callee: &LoadedFunction) -> bool {
        match self {
            Self::NativeDynamicDispatch => true,
            Self::Regular | Self::ClosureDynamicDispatch => callee.function.has_module_lock(),
        }
    }
```

**File:** third_party/move/move-vm/runtime/src/reentrancy_checker.rs (L64-152)
```rust
impl ReentrancyChecker {
    // note(inline): as `call_type` is sometimes a fixed value, this inline is very valuable
    #[inline(always)]
    pub fn enter_function(
        &mut self,
        caller_module: Option<&ModuleId>,
        callee: &LoadedFunction,
        call_type: CallType,
    ) -> PartialVMResult<()> {
        if call_type.is_locking(callee) {
            self.enter_module_lock();
        }

        let callee_module = callee.module_or_script_id();
        if Some(callee_module) != caller_module {
            // Cross module call.
            // When module lock is active, and we have already called into this module, this
            // reentry is disallowed
            match self
                .active_modules
                .entry(callee.owner.interned_module_or_script_id())
            {
                Entry::Occupied(mut e) => {
                    if self.module_lock_count > 0 {
                        return Err(PartialVMError::new(StatusCode::RUNTIME_DISPATCH_ERROR)
                            .with_message(format!(
                                "Reentrancy disallowed: reentering `{}` via function `{}` \
                     (module lock is active)",
                                callee_module,
                                callee.name()
                            )));
                    }
                    *e.get_mut() += 1
                },
                Entry::Vacant(e) => {
                    e.insert(1);
                },
            }
        } else if call_type == CallType::ClosureDynamicDispatch || caller_module.is_none() {
            // If this is closure dispatch, or we have no caller module (i.e. top-level entry).
            // Count the intra-module call like an inter-module call, as reentrance.
            // A static local call is governed by Move's `acquire` static semantics; however,
            // a dynamic dispatched local call has accesses not known at the caller side, so needs
            // the runtime reentrancy check. Note that this doesn't apply to NativeDynamicDispatch
            // which already has a check in place preventing a dispatch into the same module.
            *self
                .active_modules
                .entry(callee.owner.interned_module_or_script_id())
                .or_default() += 1;
        }
        Ok(())
    }

    // note(inline): bloats code, not a hot path
    pub fn exit_function(
        &mut self,
        caller_module: &ModuleId,
        callee: &LoadedFunction,
        call_type: CallType,
    ) -> PartialVMResult<()> {
        let callee_module = callee.module_or_script_id();
        if caller_module != callee_module || call_type == CallType::ClosureDynamicDispatch {
            // If this is an exit from cross-module call, or exit from closure dispatch,
            // decrement counter.
            match self
                .active_modules
                .entry(callee.owner.interned_module_or_script_id())
            {
                Entry::Occupied(mut e) => {
                    let val = e.get_mut();
                    if *val == 1 {
                        e.remove_entry();
                    } else {
                        *val -= 1;
                    }
                },
                Entry::Vacant(_) => {
                    return Err(PartialVMError::new_invariant_violation(
                        "Unbalanced reentrancy stack operation",
                    ))
                },
            }
        }

        if call_type.is_locking(callee) {
            self.exit_module_lock()?;
        }
        Ok(())
    }
```

**File:** third_party/move/move-vm/runtime/src/loader/function.rs (L693-695)
```rust

        // For now, just framework code considered trusted, but this could be expanded.
        let is_trusted = module.address().is_special();
```
