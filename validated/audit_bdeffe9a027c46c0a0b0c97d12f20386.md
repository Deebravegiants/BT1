No vulnerability found for this question.

**Reasoning:**

The premise that `view_filter` allowlisting a module exposes "every public(friend)-exposed-as-view function" is incorrect. The view-function API does not gate execution on visibility (`public`/`public(friend)`) — it gates on an explicit, compile-time `#[view]` metadata attribute that the module author must deliberately add to each function.

1. **API-level filter is only an additional restriction, not the authorization boundary.** `ViewFilter::allows` in [1](#0-0)  just matches `(address, module, function_name)` strings to decide whether the API layer forwards the request at all.

2. **The real gate is enforced inside the VM, independent of `view_filter`.** `execute_view_function_in_vm` loads the function and calls `view_function::validate_view_function`, which requires `determine_is_view(module_metadata, fun_name)` to be true, checking the function's `RuntimeModuleMetadataV1.fun_attributes` for the `ViewFunction`/`LegacyViewFunction` known-attribute kind: [2](#0-1) . If the attribute is absent — which is the case for ordinary internal helper or `public(friend)` functions that were never annotated `#[view]` — the call is rejected with `INVALID_MAIN_FUNCTION_SIGNATURE`, regardless of what `view_filter` allows at the module level.

3. **The `#[view]` attribute is only set by the module's own compiler-checked declaration**, not inferred from visibility. `check_and_record_view_functions` in the Move compiler's extended checks only records the attribute for functions explicitly written with `#[view]`, and additionally enforces that such functions must return values and cannot take a `signer`/`&signer` parameter: [3](#0-2) . There is no mechanism by which an unprivileged caller can force an unmarked internal function to be treated as a view function just because its enclosing module is allow-listed.

4. **View function state changes are never persisted.** Execution runs in a `SessionId::Void` session whose output is never committed to the state view (see `run_view_function`/`execute_view_function_in_vm` in `aptos-move/aptos-vm/src/aptos_vm.rs`), so even if an internal function incidentally touched capability-bearing resources during read-only execution, no custody state is altered on-chain.

Given this, the proof idea in the question — "call every public(friend)-exposed-as-view function" and expect the raw `SignerCapability` or upgrade-authority address to leak — does not describe a framework-level bypass: any function that could actually be invoked via `/view` must have been explicitly marked `#[view]` by the module author, and whether such a function chooses to return a capability's address is a module-design decision, not a corruption of a custody boundary controlled by `view_filter` or the API layer. Additionally, merely disclosing an `address` field (e.g., the `account: address` inside a `SignerCapability`, or a code object's owner address) does not by itself grant impersonation capability — obtaining a real `signer` for that address, or successfully invoking upgrade logic, still requires satisfying the actual authority checks (e.g., `create_signer_with_capability`, or the code-object's `UpgradeInfo`/owner check) elsewhere, none of which are weakened by knowledge of the address alone.

### Citations

**File:** config/src/config/api_config.rs (L230-241)
```rust
impl ViewFilter {
    /// Returns true if the given function is allowed by the filter.
    pub fn allows(&self, address: &AccountAddress, module: &str, function: &str) -> bool {
        match self {
            ViewFilter::Allowlist(ids) => ids.iter().any(|id| {
                &id.address == address && id.module == module && id.function_name == function
            }),
            ViewFilter::Blocklist(ids) => !ids.iter().any(|id| {
                &id.address == address && id.module == module && id.function_name == function
            }),
        }
    }
```

**File:** aptos-move/aptos-vm/src/verifier/view_function.rs (L17-53)
```rust
/// Based on the function attributes in the module metadata, determine whether a
/// function is a view function.
pub fn determine_is_view(
    module_metadata: Option<&RuntimeModuleMetadataV1>,
    fun_name: &IdentStr,
) -> bool {
    if let Some(data) = module_metadata {
        data.fun_attributes
            .get(fun_name.as_str())
            .map(|attrs| attrs.iter().any(|attr| attr.is_view_function()))
            .unwrap_or_default()
    } else {
        false
    }
}

/// Validate view function call. This checks whether the function is marked as a view
/// function, and validates the arguments.
pub(crate) fn validate_view_function(
    session: &mut SessionExt<impl AptosMoveResolver>,
    loader: &impl Loader,
    gas_meter: &mut impl GasMeter,
    traversal_context: &mut TraversalContext,
    args: Vec<Vec<u8>>,
    fun_name: &IdentStr,
    func: &LoadedFunction,
    module_metadata: Option<&RuntimeModuleMetadataV1>,
    struct_constructors_feature: bool,
) -> PartialVMResult<Vec<Vec<u8>>> {
    // Must be marked as view function.
    let is_view = determine_is_view(module_metadata, fun_name);
    if !is_view {
        return Err(
            PartialVMError::new(StatusCode::INVALID_MAIN_FUNCTION_SIGNATURE)
                .with_message("function not marked as view function".to_string()),
        );
    }
```

**File:** aptos-move/framework/src/extended_checks.rs (L753-805)
```rust
impl ExtendedChecker<'_> {
    fn check_and_record_view_functions(&mut self, module: &ModuleEnv) {
        for ref fun in module.get_functions() {
            if !self.has_attribute(fun, VIEW_FUN_ATTRIBUTE) {
                continue;
            }
            self.check_transaction_args(&fun.get_parameters());
            if fun.get_return_count() == 0 {
                self.env
                    .error(&fun.get_id_loc(), "`#[view]` function must return values")
            }

            fun.get_parameters()
                .iter()
                .for_each(
                    |Parameter(_sym, parameter_type, param_loc)| match parameter_type {
                        Type::Primitive(inner) => {
                            if inner == &PrimitiveType::Signer {
                                self.env.error(
                                    param_loc,
                                    "`#[view]` function cannot use a `signer` parameter",
                                )
                            }
                        },
                        Type::Reference(mutability, inner) => {
                            if let Type::Primitive(inner) = inner.as_ref() {
                                if inner == &PrimitiveType::Signer
                                // Avoid a redundant error message for `&mut signer`, which is
                                // always disallowed for transaction entries, not just for
                                // `#[view]`.
                                    && mutability == &ReferenceKind::Immutable
                                {
                                    self.env.error(
                                        param_loc,
                                        "`#[view]` function cannot use the `&signer` parameter",
                                    )
                                }
                            }
                        },
                        _ => (),
                    },
                );

            // Remember the runtime info that this is a view function
            let module_id = self.get_runtime_module_id(module);
            self.output
                .entry(module_id)
                .or_default()
                .fun_attributes
                .entry(fun.get_simple_name_string().to_string())
                .or_default()
                .push(KnownAttribute::view_function());
        }
```
