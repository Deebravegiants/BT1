[1](#0-0) [2](#0-1)

### Citations

**File:** third_party/move/move-vm/runtime/src/runtime_type_checks.rs (L42-54)
```rust
    fn check_call_visibility(
        caller: &LoadedFunction,
        callee: &LoadedFunction,
        call_type: CallType,
    ) -> PartialVMResult<()> {
        match call_type {
            CallType::Regular => {
                // We only need to check cross-contract calls.
                if caller.module_id() == callee.module_id() {
                    return Ok(());
                }
                Self::check_cross_module_regular_call_visibility(caller, callee)
            },
```

**File:** third_party/move/move-vm/runtime/src/runtime_type_checks.rs (L984-1020)
```rust
    fn check_cross_module_regular_call_visibility(
        caller: &LoadedFunction,
        callee: &LoadedFunction,
    ) -> PartialVMResult<()> {
        if callee.is_private() {
            let msg = format!(
                "Function {}::{} cannot be called because it is private",
                callee.module_or_script_id(),
                callee.name()
            );
            return Err(
                PartialVMError::new_invariant_violation(msg).with_sub_status(EPARANOID_FAILURE)
            );
        }

        if callee.is_friend() {
            let callee_module = callee.owner_as_module().map_err(|err| err.to_partial())?;
            if !caller
                .module_id()
                .is_some_and(|id| callee_module.friends.contains(id))
            {
                let msg = format!(
                    "Function {}::{} cannot be called because it has friend visibility, but {} \
                     is not {}'s friend",
                    callee.module_or_script_id(),
                    callee.name(),
                    caller.module_or_script_id(),
                    callee.module_or_script_id()
                );
                return Err(
                    PartialVMError::new_invariant_violation(msg).with_sub_status(EPARANOID_FAILURE)
                );
            }
        }

        Ok(())
    }
```
