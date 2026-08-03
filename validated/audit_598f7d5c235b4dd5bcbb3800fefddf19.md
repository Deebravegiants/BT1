No vulnerability found for this question.

**Reasoning:**

The `charge_move_from` function in `aptos-move/aptos-gas-meter/src/meter.rs` charges a flat `MOVE_FROM_BASE`/`MOVE_FROM_GENERIC_BASE` cost regardless of the resource's contents, as shown in the implementation at [1](#0-0) . This is a genuine simplification in gas metering (the value size no longer factors into the cost, unlike the legacy `gas_schedule.rs` implementation which used `val.legacy_abstract_memory_size()` as shown at [2](#0-1) ).

However, this does not constitute a custody boundary breach for the following reasons:

1. **Gas cost does not gate authorization.** The `MoveFrom` bytecode instruction, dispatched via `interpreter.move_from` at [3](#0-2) , is invoked purely based on bytecode verification rules, not gas amount. Whether a call costs a flat fee or a size-proportional fee has zero bearing on *who* is permitted to execute that bytecode.

2. **Move's module encapsulation is the actual custody boundary, not the gas meter.** The `move_from<T>` operation can only be emitted in bytecode for a struct `T` from within the module that declares `T` (structs with the `key` ability restrict `MoveFrom`/`MoveTo` to their declaring module). This means an unprivileged attacker cannot arbitrarily call `move_from<MultisigAccount>(addr)` unless the `MultisigAccount`-defining module itself exposes a public/entry function that performs this operation — and any such function would have its own authority checks (e.g., signer verification) independent of gas metering. The gas meter has no visibility into or influence over these authority checks.

3. **No state corruption path exists via gas charging.** Even if gas cost is flat, actually removing a resource from global storage still requires that the calling code path (a Move function with `MoveFrom`) exists and is reachable by an unauthenticated caller — a precondition explicitly excluded by the Review Bounds ("Reject anything that needs pre-existing permissions"). The gas metering logic in `charge_move_from` cannot itself create such a callable path; it only prices an operation that must already be authorized by module/type-level access control.

4. **This is a pricing/DoS-adjacent concern at most, not custody.** Flat-rate charging for `move_from` on large or complex resources is a potential resource-accounting inaccuracy (e.g., underpricing large abstract values), but this affects transaction fee economics, not the question of "who can own, move, mint, burn, freeze, upgrade, or recover value." No custody state (ownership, transfer authority, freeze authority) changes as a result of how much gas is charged for the opcode.

Per the Decision Standard, this finding requires pre-existing permissions (a callable entry point with `MoveFrom` bytecode for the target resource type) and produces no actual change in asset control — it is a gas-pricing observation, not a custody-boundary crossing.

### Citations

**File:** aptos-move/aptos-gas-meter/src/meter.rs (L456-467)
```rust
    #[inline]
    fn charge_move_from(
        &mut self,
        is_generic: bool,
        _ty: impl TypeView,
        _val: Option<impl ValueView>,
    ) -> PartialVMResult<()> {
        match is_generic {
            false => self.algebra.charge_execution(MOVE_FROM_BASE),
            true => self.algebra.charge_execution(MOVE_FROM_GENERIC_BASE),
        }
    }
```

**File:** third_party/move/move-vm/test-utils/src/gas_schedule.rs (L447-466)
```rust
    fn charge_move_from(
        &mut self,
        is_generic: bool,
        _ty: impl TypeView,
        val: Option<impl ValueView>,
    ) -> PartialVMResult<()> {
        use Opcodes::*;

        if let Some(val) = val {
            let op = if is_generic {
                MOVE_FROM_GENERIC
            } else {
                MOVE_FROM
            };

            self.charge_instr_with_size(op, val.legacy_abstract_memory_size())?;
        }

        Ok(())
    }
```

**File:** third_party/move/move-vm/runtime/src/interpreter.rs (L1510-1552)
```rust
    /// MoveFrom opcode.
    fn move_from(
        &mut self,
        is_generic: bool,
        data_cache: &mut impl MoveVmDataCache,
        gas_meter: &mut impl GasMeter,
        traversal_context: &mut TraversalContext,
        addr: AccountAddress,
        ty: &Type,
    ) -> PartialVMResult<()> {
        let runtime_environment = self.loader.runtime_environment();
        let resource = match self
            .load_resource_mut(data_cache, gas_meter, traversal_context, addr, ty)?
            .move_from()
        {
            Ok(resource) => {
                gas_meter.charge_move_from(
                    is_generic,
                    TypeWithRuntimeEnvironment {
                        ty,
                        runtime_environment,
                    },
                    Some(&resource),
                )?;
                self.check_resource_reentrancy(runtime_environment, ty)?;
                resource
            },
            Err(err) => {
                let val: Option<&Value> = None;
                gas_meter.charge_move_from(
                    is_generic,
                    TypeWithRuntimeEnvironment {
                        ty,
                        runtime_environment,
                    },
                    val,
                )?;
                return Err(err.with_message(format!("Failed to move resource from {:?}", addr)));
            },
        };
        self.operand_stack.push(resource)?;
        Ok(())
    }
```
