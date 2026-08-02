No vulnerability found for this question.

**Analysis:**

The premise doesn't hold up against the actual code in `transaction_arg_validation.rs`.

1. **No shared/corruptible buffer across arguments.** Each top-level transaction argument gets its own independent output buffer (`let mut new_arg = vec![]`) created fresh in `construct_arg` [1](#0-0) . Nested construction (e.g., `Vector<String>`) only appends into *that same argument's* buffer via `arg.append(&mut bytes)` in `recursively_construct_arg` [2](#0-1) . There is no mechanism by which constructing strings inside one parameter (e.g. `Vector<String>`) can write into, pad, or otherwise alter a *different* parameter's buffer (e.g. a separate `vector<u8>` seed argument for `create_named_object`). A cursor-position check (`cursor.position() != initial_cursor_len`) further guarantees each argument's serialized bytes are fully and exactly consumed with no overflow into adjacent data [3](#0-2) .

2. **The "ability-copy check bypass" premise is false.** There is no copy-ability check performed for whitelisted structs (String, Object, Option, FixedPoint) in `validate_and_construct` at all — that check only exists for the separate `construct_public_copy_struct` path used for arbitrary public copy structs [4](#0-3) . Whitelisted constructors are trusted native/framework functions (`utf8`, `address_to_object`, etc.), so no such check is being "bypassed" by the utf8 shortcut — it never existed for this path.

3. **The `invocations_remaining` skip for `utf8` is an intentional, documented mitigation**, not a bug: the comment explicitly states it exists to allow `vector<string>` and similar patterns without triggering the invocation cap, while remaining bounded by other limits (`MAX_NUM_BYTES = 1_000_000` per `read_n_bytes` call, plus overall transaction size limits) [5](#0-4) . It bounds string count to be linear in total transaction payload size — not unbounded — and has no bearing on other arguments' contents.

4. Since a resource-account seed is passed as its own dedicated argument that the caller already fully controls (any bytes they want, directly), there is no additional attack surface gained by manipulating unrelated `String`/`Object` arguments elsewhere in the call — the attacker cannot influence the seed bytes any more than by simply choosing the seed value directly.

No custody boundary (resource-account address derivation, ownership, or asset control) is crossed by this shortcut; it is an isolated, per-argument parsing optimization with no cross-argument buffer interaction.

### Citations

**File:** aptos-move/aptos-vm/src/verifier/transaction_arg_validation.rs (L366-374)
```rust
    // Require copy using the struct's *declared* abilities (not the instantiated type's).
    // This is intentional: Container<T> declares copy even when T lacks it, so
    // Container<NoCopyData>::Empty is accepted (no inner value to construct). The NoCopyData
    // field is checked when recursively constructing a Value variant. A struct whose definition
    // itself lacks copy (like NoCopyData) is always rejected here.
    // Also reject resources (structs with key ability).
    if !struct_type.abilities.has_copy() || struct_type.abilities.has_key() {
        return Err(invalid_signature());
    }
```

**File:** aptos-move/aptos-vm/src/verifier/transaction_arg_validation.rs (L526-552)
```rust
        Vector(_) | Struct { .. } | StructInstantiation { .. } => {
            let initial_cursor_len = arg.len();
            let mut cursor = Cursor::new(&arg[..]);
            let mut new_arg = vec![];
            // Increase invocation
            let mut invocations_remaining = if loader
                .runtime_environment()
                .vm_config()
                .enable_public_struct_args
            {
                MAX_PACK_INVOCATIONS_WITH_PUBLIC_STRUCT_ARGS
            } else {
                MAX_PACK_INVOCATIONS
            };
            recursively_construct_arg(
                session,
                loader,
                gas_meter,
                traversal_context,
                ty,
                allowed_structs,
                &mut cursor,
                initial_cursor_len,
                &mut invocations_remaining,
                &mut new_arg,
                pack_fn_cache,
            )?;
```

**File:** aptos-move/aptos-vm/src/verifier/transaction_arg_validation.rs (L553-562)
```rust
            // Check cursor has parsed everything
            // Unfortunately, is_empty is only enabled in nightly, so we check this way.
            if cursor.position() != initial_cursor_len as u64 {
                return Err(VMStatus::error(
                    StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT,
                    Some(String::from(
                        "The serialized arguments to constructor contained extra data",
                    )),
                ));
            }
```

**File:** aptos-move/aptos-vm/src/verifier/transaction_arg_validation.rs (L618-671)
```rust
        Struct { .. } | StructInstantiation { .. } => {
            let (module_id, identifier) = loader
                .runtime_environment()
                .get_struct_name(ty)
                .map_err(|_| {
                    // Note: The original behaviour was to map all errors to an invalid signature
                    //       error, here we want to preserve it for now.
                    invalid_signature()
                })?
                .ok_or_else(invalid_signature)?;
            let full_name = format!("{}::{}", module_id.short_str_lossless(), identifier);

            if *invocations_remaining == 0 {
                return Err(VMStatus::error(
                    StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT,
                    Some("exceeded maximum number of struct constructor invocations per transaction argument".to_string()),
                ));
            }

            // By appending the BCS to the output parameter we construct the correct BCS format
            // of the argument.
            let mut bytes = if let Some(constructor) = allowed_structs.get(&full_name) {
                // Whitelisted struct - use the legacy constructor function.
                validate_and_construct(
                    session,
                    loader,
                    gas_meter,
                    traversal_context,
                    ty,
                    constructor,
                    allowed_structs,
                    cursor,
                    initial_cursor_len,
                    invocations_remaining,
                    pack_fn_cache,
                )?
            } else {
                // Public copy struct - construct by calling the cached pack function.
                construct_public_copy_struct(
                    session,
                    loader,
                    gas_meter,
                    traversal_context,
                    ty,
                    &module_id,
                    &identifier,
                    allowed_structs,
                    cursor,
                    initial_cursor_len,
                    invocations_remaining,
                    pack_fn_cache,
                )?
            };
            arg.append(&mut bytes);
```

**File:** aptos-move/aptos-vm/src/verifier/transaction_arg_validation.rs (L820-860)
```rust
) -> Result<Vec<u8>, VMStatus> {
    // HACK mitigation of performance attack
    // To maintain compatibility with vector<string> or so on, we need to allow unlimited strings.
    // So we do not count the string constructor against the max_invocations, instead we
    // shortcut the string case to avoid the performance attack.
    if constructor.func_name.as_str() == "utf8" {
        let constructor_error = || {
            // A slight hack, to prevent additional piping of the feature flag through all
            // function calls. We know the feature is active when more structs then just strings are
            // allowed.
            let are_struct_constructors_enabled = allowed_structs.len() > 1;
            if are_struct_constructors_enabled {
                PartialVMError::new(StatusCode::ABORTED)
                    .with_sub_status(1)
                    .at_code_offset(FunctionDefinitionIndex::new(0), 0)
                    .finish(Location::Module(constructor.module_id.clone()))
                    .into_vm_status()
            } else {
                VMStatus::error(StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT, None)
            }
        };
        // Short cut for the utf8 constructor, which is a special case.
        let len = get_len(cursor)?;
        if cursor
            .position()
            .checked_add(len as u64)
            .is_none_or(|l| l > initial_cursor_len as u64)
        {
            // We need to make sure we do not allocate more bytes than
            // needed.
            return Err(VMStatus::error(
                StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT,
                Some("String argument is too long".to_string()),
            ));
        }

        let mut arg = vec![];
        read_n_bytes(len, cursor, &mut arg)?;
        std::str::from_utf8(&arg).map_err(|_| constructor_error())?;
        return bcs::to_bytes(&arg)
            .map_err(|_| VMStatus::error(StatusCode::FAILED_TO_DESERIALIZE_ARGUMENT, None));
```
