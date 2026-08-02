No vulnerability found for this question.

**Why this doesn't hold up:**

The `exists`/`move_from` functions in `type_safety.rs` are part of the bytecode verifier, which runs once at module publish time to statically check that any `MoveFrom`/`MoveFromGeneric`/`ExistsGeneric` instruction operates on a type instantiation with the key ability, computed via `materialize_type` and `verifier.abilities()` [1](#0-0) .

At runtime, the interpreter performs an equivalent, independently-derived check in `runtime_type_checks.rs`, using `ty_cache.get_struct_type(*idx, frame)` and `paranoid_check_has_ability(Ability::Key)` for `MoveFromGeneric`, mirroring the verifier's logic exactly [2](#0-1) . Both computations derive abilities from the same struct handle/type-parameter substitution machinery, so there is no divergent code path that would let a generic instantiation pass the compile-time key-ability check but fail (or differ) at runtime.

More fundamentally, the "address argument the attacker controls" only selects *which account's* global storage slot is probed for `struct_type` — this is standard, intentional Move semantics (`exists<T>(addr)` / `move_from<T>(addr)` are defined to operate on arbitrary addresses) [3](#0-2) . The actual access-control boundary in Move is that `MoveFrom`/`MoveFromGeneric`/`ExistsGeneric` reference a `StructDefinitionIndex`/`StructDefInstantiationIndex` that can only resolve to a struct defined in the *currently executing module* — i.e., only the module that declares a resource type can execute bytecode that moves it out of any account's storage. An external/unprivileged caller cannot inject an address into a `MoveFromGeneric` inside someone else's module to extract resources they don't own; they can only call into entry/public functions of the resource-owning module, and it is that module's own logic (e.g., Aptos framework's coin/fungible-asset modules) that decides whether the caller-supplied address is authorized to have its resource withdrawn. That authorization is enforced by the calling module's Move source logic, not by `type_safety.rs`.

There is no evidence of divergence between the verifier's static ability computation and the VM's runtime ability computation — both use the same `AbilitySet` substitution logic — so the described custody-takeover scenario does not correspond to an actual bug in this code.

### Citations

**File:** third_party/move/move-bytecode-verifier/src/type_safety.rs (L527-547)
```rust
fn move_from(
    verifier: &mut TypeSafetyChecker,
    meter: &mut impl Meter,
    offset: CodeOffset,
    struct_def: &StructDefinition,
    type_args: &Signature,
) -> PartialVMResult<()> {
    let struct_type = materialize_type(struct_def.struct_handle, type_args);
    if !verifier.abilities(&struct_type)?.has_key() {
        return Err(verifier.error(StatusCode::MOVEFROM_WITHOUT_KEY_ABILITY, offset));
    }

    let struct_type = materialize_type(struct_def.struct_handle, type_args);
    let operand = safe_unwrap!(verifier.stack.pop());
    if operand != ST::Address {
        return Err(verifier.error(StatusCode::MOVEFROM_TYPE_MISMATCH_ERROR, offset));
    }

    verifier.push(meter, struct_type)?;
    Ok(())
}
```

**File:** third_party/move/move-vm/runtime/src/runtime_type_checks.rs (L888-893)
```rust
            Instruction::MoveFromGeneric(idx) => {
                operand_stack.pop_ty()?.paranoid_check_is_address_ty()?;
                let ty = ty_cache.get_struct_type(*idx, frame)?.0.clone();
                ty.paranoid_check_has_ability(Ability::Key)?;
                operand_stack.push_ty(ty)?;
            },
```

**File:** third_party/move/move-binary-format/src/file_format.rs (L2538-2560)
```rust
    #[group = "global"]
    #[static_operands = "[struct_def_idx]"]
    #[description = r#"
        Move the value of the specified type under the address in the global storage onto the top of the stack.

        Abort execution if such an value does not exist.
    "#]
    #[semantics = r#"
        stack >> addr

        if global_state[addr] contains struct_type
            stack << global_state[addr][struct_type]
            delete global_state[addr][struct_type]
        else
            error
    "#]
    #[runtime_check_epilogue = r#"
        ty_stack >> ty
        assert ty == address
        assert struct_ty has key
        ty_stack << struct_ty
    "#]
    MoveFrom(StructDefinitionIndex),
```
