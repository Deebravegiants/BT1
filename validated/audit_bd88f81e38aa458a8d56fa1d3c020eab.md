No vulnerability found for this question.

**Reasoning:**

The described path is real from a mechanics standpoint — `dispatchable_fungible_asset::register_dispatch_functions` calls `function_info::check_dispatch_type_compatibility` once at registration time to validate that the withdraw hook's *signature* matches `dispatchable_withdraw`, and stores only a `FunctionInfo` (address + module name + function name) in `DispatchFunctionStore`, not a snapshot of the function body. [1](#0-0)  At actual withdraw time, `dispatch_withdraw_hook` re-resolves that `FunctionInfo` via `function.load_function_value<...>()`, which calls `reflect::resolve` → `native_resolve`, which loads whatever code currently exists at that address/module/function name at execution time. [2](#0-1) [3](#0-2)  So yes, if the module at that address is republished with a new body (same type signature) between registration and a later withdraw call, the new body runs.

However, this does **not** cross an unprivileged custody boundary:

1. **Republishing a module at that address requires the address owner's/upgrade authority's signature** — this is not an unprivileged action. The module compatibility checker (`compatibility.rs`) only enforces that a function's *signature* (parameter/return types, visibility, entry-ness) stays compatible across upgrades; it says nothing about behavior, precisely because upgrades are gated by the module owner's own publish authority. [4](#0-3) 
2. **Only the fungible asset creator can register a dispatch hook in the first place**, since `register_dispatch_functions` takes a `ConstructorRef`, obtainable only at object-creation time by the creator. [5](#0-4) 
3. The withdraw/deposit dispatch hook is explicitly a **trusted-issuer extensibility point** (AIP-73): the hook receives the store's `TransferRef` and is *designed* to implement arbitrary withdraw semantics (e.g., deflation tokens burning extra, loyalty tokens paying out extra) — the module owner already has full control over what the hook does merely by writing that logic in the first place, without needing an upgrade at all. [6](#0-5) [7](#0-6) 

Since exploiting this requires the pre-existing privilege of controlling/upgrading the withdraw-hook module (the FA issuer's own authority), and the review bounds explicitly reject findings that "need pre-existing permissions," this does not qualify as an unprivileged custody-boundary violation. The `check_dispatch_type_compatibility` check is a type-safety gate, not a behavioral-immutability guarantee, and the framework never claims the hook body is frozen post-registration — only that its signature stays compatible.

### Citations

**File:** aptos-move/framework/aptos-framework/sources/fungible_asset.move (L369-392)
```text
    /// Create a fungible asset store whose transfer rule would be overloaded by the provided function.
    public(friend) fun register_dispatch_functions(
        constructor_ref: &ConstructorRef,
        withdraw_function: Option<FunctionInfo>,
        deposit_function: Option<FunctionInfo>,
        derived_balance_function: Option<FunctionInfo>
    ) {
        // Verify that caller type matches callee type so wrongly typed function cannot be registered.
        withdraw_function.for_each_ref(|withdraw_function| {
                let dispatcher_withdraw_function_info =
                    function_info::new_function_info_from_address(
                        @aptos_framework,
                        string::utf8(b"dispatchable_fungible_asset"),
                        string::utf8(b"dispatchable_withdraw")
                    );

                assert!(
                    function_info::check_dispatch_type_compatibility(
                        &dispatcher_withdraw_function_info,
                        withdraw_function
                    ),
                    error::invalid_argument(EWITHDRAW_FUNCTION_SIGNATURE_MISMATCH)
                );
            });
```

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L1-16)
```text
/// This defines the fungible asset module that can issue fungible asset of any `Metadata` object. The
/// metadata object can be any object that equipped with `Metadata` resource.
///
/// The dispatchable_fungible_asset wraps the existing fungible_asset module and adds the ability for token issuer
/// to customize the logic for withdraw and deposit operations. For example:
///
/// - Deflation token: a fixed percentage of token will be destructed upon transfer.
/// - Transfer allowlist: token can only be transfered to addresses in the allow list.
/// - Predicated transfer: transfer can only happen when some certain predicate has been met.
/// - Loyalty token: a fixed loyalty will be paid to a designated address when a fungible asset transfer happens
///
/// The api listed here intended to be an in-place replacement for defi applications that uses fungible_asset api directly
/// and is safe for non-dispatchable (aka vanilla) fungible assets as well.
///
/// See AIP-73 for further discussion
///
```

**File:** aptos-move/framework/aptos-framework/sources/dispatchable_fungible_asset.move (L216-227)
```text
    /// Runs a withdraw hook as a function value, replacing the legacy native dispatch, as
    /// do the following runners; `#[module_lock]` preserves AIP-73 reentrancy semantics.
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

**File:** aptos-move/framework/move-stdlib/sources/reflect.move (L31-43)
```text
    ///
    /// The resolved function can be generic, in which case the instantiation must be inferrible
    /// from the provided `FuncType`. For example, `public fun foo<T>(T)`, with `FunType = |u64|`,
    /// `T = u64` can be derived. If not all type parameters can be inferred, an error will be
    /// produced.
    public fun resolve<FuncType>(
        addr: address, module_name: &String, func_name: &String
    ): Result<FuncType, ReflectionError> {
        assert!(
            features::is_function_reflection_enabled(),
            error::invalid_state(E_FEATURE_NOT_ENABLED)
        );
        native_resolve(addr, module_name, func_name)
```

**File:** third_party/move/move-binary-format/src/compatibility.rs (L424-439)
```rust
    fn signature_compatible(
        &self,
        old_module: &CompiledModule,
        old_sig: &Signature,
        new_module: &CompiledModule,
        new_sig: &Signature,
    ) -> bool {
        old_sig.0.len() == new_sig.0.len()
            && old_sig
                .0
                .iter()
                .zip(new_sig.0.iter())
                .all(|(old_tok, new_tok)| {
                    self.signature_token_compatible(old_module, old_tok, new_module, new_tok)
                })
    }
```
