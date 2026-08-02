No vulnerability found for this question.

The premise doesn't hold up against the actual code. The Rust `FunctionInfo` struct's derived `Eq`/`Hash` in [1](#0-0)  are field-wise, exact comparisons — not a cryptographic hash subject to "collisions." Two `FunctionInfo` values are equal if and only if `module_address`, `module_name`, and `function_name` are literally identical strings/addresses, which is exactly the correct identity criterion for a Move function; there is no scenario where "identical field values" point to two functions with "different resolved behavior" — identical fields mean the same fully-qualified function name.

More importantly, actual dispatch resolution never relies on this Rust struct's cached equality at all. The Move-side `FunctionInfo` in [2](#0-1)  only has `copy, drop, store` abilities (no derived hash used for caching), and every dispatch call re-resolves the target function fresh via native calls: `load_module_from_function`/`load_function_impl` and `reflect::resolve` in [3](#0-2) , and the native dispatch path in [4](#0-3)  which checks that the module has been freshly loaded/visited *within the current transaction* before dispatching — there is no persistent, cross-transaction cache keyed by struct equality that could serve stale resolution after a module upgrade.

The referenced comment in the VM loader also explicitly documents the invariant that dispatch targets must be persistent functions with signatures frozen by upgrade-compatibility checks, precisely to prevent this class of type confusion: [5](#0-4) .

No unprivileged, custody-crossing path was found that relies on the Rust `FunctionInfo` derive to make stale or mismatched dispatch decisions.

### Citations

**File:** types/src/function_info.rs (L18-24)
```rust
#[derive(Serialize, Deserialize, Eq, PartialEq, Debug, Clone, Hash)]
#[cfg_attr(any(test, feature = "fuzzing"), derive(Arbitrary))]
pub struct FunctionInfo {
    pub module_address: AccountAddress,
    pub module_name: String,
    pub function_name: String,
}
```

**File:** aptos-move/framework/aptos-framework/sources/function_info.move (L17-21)
```text
    struct FunctionInfo has copy, drop, store {
        module_address: address,
        module_name: String,
        function_name: String,
    }
```

**File:** aptos-move/framework/aptos-framework/sources/function_info.move (L83-98)
```text
    public(friend) fun load_module_from_function(f: &FunctionInfo) {
        load_function_impl(f)
    }

    /// Resolves the function referenced by `self` into a function value of type `FuncType`.
    /// Aborts with `EINVALID_FUNCTION` on failure; unreachable for targets validated via
    /// `check_dispatch_type_compatibility`, whose signatures are frozen by upgrade rules.
    public(friend) fun load_function_value<FuncType>(self: &FunctionInfo): FuncType {
        let result = reflect::resolve<FuncType>(
            self.module_address,
            &self.module_name,
            &self.function_name,
        );
        assert!(result.is_ok(), EINVALID_FUNCTION);
        result.unwrap()
    }
```

**File:** aptos-move/framework/natives/src/dispatchable_fungible_asset.rs (L27-68)
```rust
pub(crate) fn native_dispatch(
    context: &mut SafeNativeContext,
    ty_args: &[Type],
    mut arguments: VecDeque<Value>,
) -> SafeNativeResult<SmallVec<[Value; 1]>> {
    let (module_name, func_name) = extract_function_info(&mut arguments)?;

    // Check if the module is already properly charged in this transaction.
    let check_visited = |a, n| {
        let special_addresses_considered_visited =
            context.get_feature_flags().is_account_abstraction_enabled()
                || context
                    .get_feature_flags()
                    .is_derivable_account_abstraction_enabled();
        if special_addresses_considered_visited {
            context
                .traversal_context()
                .check_is_special_or_visited(a, n)
        } else {
            context.traversal_context().legacy_check_visited(a, n)
        }
    };
    check_visited(module_name.address(), module_name.name()).map_err(|_| {
        SafeNativeError::abort_with_message(
            abort_codes::ENOT_LOADED,
            format!(
                "Module {}::{} is not loaded prior to native dispatch",
                module_name.address(),
                module_name.name()
            ),
        )
    })?;

    context.charge(DISPATCHABLE_FUNGIBLE_ASSET_DISPATCH_BASE)?;

    // Use Error to instruct the VM to perform a function call dispatch.
    Err(SafeNativeError::FunctionDispatch {
        module_name,
        func_name,
        ty_args: ty_args.to_vec(),
        args: arguments.into_iter().collect(),
    })
```

**File:** third_party/move/move-vm/runtime/src/loader/function.rs (L453-473)
```rust
                // A closure can only be stored if its function is persistent (public
                // or has #[persistent] attribute). Persistent functions have their
                // signatures frozen by the upgrade compatibility check, so captured
                // argument types are guaranteed to match across different upgraded
                // module versions.
                // Here, we check that loaded function is indeed persistent. It might not
                // be the case for `init_module` that stores a closure:
                //   1. Function `foo` is private in original module A.
                //   2. Module B is published which calls now public `foo`.
                // As a result, there is a speculative resource write which resolves
                // to older (still private) function because Block-STM makes module
                // upgrades visible only at commit. Such behavior should be caught
                // immediately because private function can change signature, so there
                // is some room for type confusion via captured arguments.
                if !fun.function.is_persistent() {
                    return Err(PartialVMError::new_invariant_violation(format!(
                        "Stored closure references non-persistent function `{}::{}`",
                        module_id.short_str_lossless(),
                        fun_id
                    )));
                }
```
