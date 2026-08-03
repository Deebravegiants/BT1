No vulnerability found for this question.

**Analysis:**

The premise doesn't hold up against the actual control flow. `BoundMeter::new` is called exactly once per module (or script) verification pass in `CodeUnitVerifier::verify_module_impl` / `verify_script_impl`, and that single `meter` instance is threaded by mutable reference through every function-level verification call within that same module — it is never reconstructed mid-pass. [1](#0-0) 

The `VerifierConfig` itself is also passed by reference (`&VerifierConfig`) through the entire synchronous call chain — `verify_module_with_config` → `CodeUnitVerifier::verify_module` → `verify_module_impl` → `verify_function` — with no re-fetching of feature flags or timed features at any point in between. [2](#0-1) 

`aptos_prod_verifier_config` (which reads `Features`/`TimedFeatures` to compute `max_per_mod_meter_units`/`max_per_fun_meter_units`) is invoked once per VM session/config build, not per-scope during verification. [3](#0-2) 

For the described attack to work, a single module-publish transaction's bytecode verification would need to pause partway through and re-read feature flags with a different value before resuming — but verification is a single synchronous Rust call stack with no yield points, no async re-entry, and no code that reconstructs `BoundMeter` or re-derives `VerifierConfig` mid-pass. Feature flag changes take effect only at the reconfiguration boundary between transactions/blocks, not within one transaction's synchronous execution, and the module's own `VerifierConfig` is fixed for the whole verification call. There is no code path matching the "config change window within the same publish transaction" scenario described, so `mod_bounds.max` and `fun_bounds.max` are always derived from one consistent, frozen `VerifierConfig` for the entire pass — exactly as the question's own proof-idea investigation would confirm. This does not cross any custody boundary (no owner/balance/authority state is touched by the meter at all — it only enforces a complexity/gas-like limit during verification).

### Citations

**File:** third_party/move/move-bytecode-verifier/src/code_unit_verifier.rs (L52-95)
```rust
        let mut meter = BoundMeter::new(verifier_config);
        let mut name_def_map = HashMap::new();
        for (idx, func_def) in module.function_defs().iter().enumerate() {
            let fh = module.function_handle_at(func_def.function);
            name_def_map.insert(fh.name, FunctionDefinitionIndex(idx as u16));
        }

        // Struct API validation is only applicable to modules compiled with bytecode version 10
        // or later. Applying it to older modules would risk incorrectly rejecting functions
        // whose names happen to contain '$' (the struct API delimiter), since those names are
        // structurally valid but carry no struct API attribute.
        let struct_api_ctx = if module.version() >= VERSION_10 {
            Some(struct_api_checker::StructApiContext::new(module)?)
        } else {
            None
        };

        let mut total_back_edges = 0;
        for (idx, function_definition) in module.function_defs().iter().enumerate() {
            let index = FunctionDefinitionIndex(idx as TableIndex);

            // SECURITY: Check struct API attributes BEFORE verify_function runs.
            // This ensures that reference_safety (which runs inside verify_function) can
            // safely trust BorrowFieldMutable attributes, since they've been validated
            // to accurately match the bytecode before reference_safety sees them.
            // Only runs for VERSION_10+ modules (see guard above).
            if let Some(ctx) = &struct_api_ctx {
                struct_api_checker::check_function(module, function_definition, ctx)
                    .map_err(|err| err.at_index(IndexKind::FunctionDefinition, index.0))?;
            }

            // Now reference_safety can safely trust that BorrowFieldMutable attributes
            // accurately describe which field is being borrowed
            let num_back_edges = Self::verify_function(
                verifier_config,
                index,
                function_definition,
                module,
                &name_def_map,
                &mut meter,
            )
            .map_err(|err| err.at_index(IndexKind::FunctionDefinition, index.0))?;
            total_back_edges += num_back_edges;
        }
```

**File:** third_party/move/move-bytecode-verifier/src/verifier.rs (L135-159)
```rust
pub fn verify_module_with_config(config: &VerifierConfig, module: &CompiledModule) -> VMResult<()> {
    if config.verify_nothing() {
        return Ok(());
    }
    let prev_state = move_core_types::state::set_state(VMState::VERIFIER);
    let result = std::panic::catch_unwind(|| {
        // Always needs to run bound checker first as subsequent passes depend on it
        BoundsChecker::verify_module(module).map_err(|e| {
            // We can't point the error at the module, because if bounds-checking
            // failed, we cannot safely index into module's handle to itself.
            e.finish(Location::Undefined)
        })?;
        FeatureVerifier::verify_module(config, module)?;
        LimitsVerifier::verify_module(config, module)?;
        DuplicationChecker::verify_module(module)?;

        signature_v2::verify_module(config, module)?;

        InstructionConsistency::verify_module(module)?;
        constants::verify_module(module)?;
        friends::verify_module(module)?;

        RecursiveStructDefChecker::verify_module(module)?;
        InstantiationLoopChecker::verify_module(module)?;
        CodeUnitVerifier::verify_module(config, module)?;
```

**File:** aptos-move/aptos-vm-environment/src/prod_configs.rs (L164-220)
```rust
pub fn aptos_prod_verifier_config(
    gas_feature_version: u64,
    features: &Features,
    timed_features: &TimedFeatures,
) -> VerifierConfig {
    let sig_checker_v2_fix_script_ty_param_count =
        features.is_enabled(FeatureFlag::SIGNATURE_CHECKER_V2_SCRIPT_FIX);
    let sig_checker_v2_fix_function_signatures = gas_feature_version >= RELEASE_V1_34;
    let enable_enum_types = features.is_enabled(FeatureFlag::ENABLE_ENUM_TYPES);
    // Resource access control was never enabled and has been removed. Access specifiers
    // are permanently rejected by the verifier.
    let enable_resource_access_control = false;
    let enable_function_values = features.is_enabled(FeatureFlag::ENABLE_FUNCTION_VALUES);
    // Note: we reuse the `enable_function_values` flag to set various stricter limits on types.

    let strict_bounds = timed_features.is_enabled(TimedFeatureFlag::EnableStrictBoundsInProdConfig);
    let revised_bounds = timed_features.is_enabled(TimedFeatureFlag::RevisedBoundsInProdConfig);

    VerifierConfig {
        scope: VerificationScope::Everything,
        max_loop_depth: Some(5),
        max_generic_instantiation_length: Some(32),
        max_function_parameters: Some(128),
        max_basic_blocks: Some(1024),
        max_value_stack_size: 1024,
        max_type_nodes: if enable_function_values {
            Some(128)
        } else {
            Some(256)
        },
        max_push_size: Some(10000),
        max_struct_definitions: if strict_bounds {
            if revised_bounds {
                Some(1100)
            } else {
                Some(200)
            }
        } else {
            None
        },
        max_struct_variants: if strict_bounds {
            if revised_bounds {
                Some(127)
            } else {
                Some(64)
            }
        } else {
            None
        },
        max_fields_in_struct: if strict_bounds { Some(64) } else { None },
        max_function_definitions: if strict_bounds { Some(1000) } else { None },
        max_back_edges_per_function: None,
        max_back_edges_per_module: None,
        max_basic_blocks_in_script: if strict_bounds { Some(1024) } else { None },
        max_per_fun_meter_units: Some(1000 * 80000),
        max_per_mod_meter_units: Some(1000 * 80000),
        _use_signature_checker_v2: true,
```
