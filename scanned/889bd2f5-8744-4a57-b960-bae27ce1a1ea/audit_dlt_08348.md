# [?] Fix for accumulator settlement DoS

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-08-11
Source: https://github.com/MystenLabs/sui/commit/dea5a4ae6fdc2e606f89e17d55091bb0cbb17ba0
Type: security-commit

## Details
Fix for accumulator settlement DoS

## Patch
### crates/sui-types/src/accumulator_root.rs
```diff
@@ -17,6 +17,7 @@ use crate::{
     storage::{ObjectStore, RuntimeObjectResolver},
 };
 use move_core_types::{
+    account_address::AccountAddress,
     ident_str,
     identifier::IdentStr,
     language_storage::{StructTag, TypeTag},
@@ -36,6 +37,18 @@ pub const ACCUMULATOR_ROOT_SETTLEMENT_SETTLE_EVENTS_FUNC: &IdentStr = ident_str!
 const ACCUMULATOR_KEY_TYPE: &IdentStr = ident_str!("Key");
 const ACCUMULATOR_U128_TYPE: &IdentStr = ident_str!("U128");
 
+pub const SETTLEMENT_MAX_TYPE_INSTANTIATION_NODES: u64 = 512;
+
+pub fn is_settle_u128_call(
+    module_address: &AccountAddress,
+    module: &IdentStr,
+    function: &IdentStr,
+) -> bool {
+    *module_address == SUI_FRAMEWORK_ADDRESS
+        && module == ACCUMULATOR_SETTLEMENT_MODULE
+        && function == ACCUMULATOR_ROOT_SETTLE_U128_FUNC
+}
+
 pub fn get_accumulator_root_obj_initial_shared_version(
     object_store: &dyn ObjectStore,
 ) -> SuiResult<Option<SequenceNumber>> {
```

### external-crates/move/crates/move-vm-runtime/src/execution/interpreter/eval.rs
```diff
@@ -109,6 +109,7 @@ pub(super) fn run(
         operand_stack,
         call_stack,
         interner: _,
+        type_limits: _,
         callstack_highwatermark,
         valuestack_highwatermark,
     } = state;
@@ -242,6 +243,7 @@ fn step(
                 )
             });
             let ty_args = instantiate_generic_function(
+                &state.type_limits,
                 fun_inst_ptr,
                 state.call_stack.current_frame.ty_args(),
             )
@@ -557,8 +559,11 @@ fn op_step_impl(
         }
         Bytecode::PackGeneric(struct_inst_ptr) => {
             let field_count = struct_inst_ptr.field_count;
-            let ty =
-                instantiate_struct_type(struct_inst_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_struct_type(
+                &state.type_limits,
+                struct_inst_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             check_depth_of_type(run_context, &ty)?;
             gas_meter.charge_pack(true, state.last_n_operands(field_count as usize)?)?;
             let args = state.pop_n_operands(field_count)?;
@@ -736,7 +741,11 @@ fn op_step_impl(
         }
         Bytecode::VecPack(ty_ptr, num) => {
             let num = checked_as!(*num, u16)?;
-            let ty = instantiate_single_type(ty_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_single_type(
+                &state.type_limits,
+                ty_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             check_depth_of_type(run_context, &ty)?;
             gas_meter.charge_vec_pack(state.last_n_operands(num as usize)?)?;
             let elements = state.pop_n_operands(num)?;
@@ -746,31 +755,47 @@ fn op_step_impl(
         }
         Bytecode::VecLen(ty_ptr) => {
             let vec_ref = state.pop_operand_as::<VectorRef>()?;
-            let ty = instantiate_single_type(ty_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_single_type(
+                &state.type_limits,
+                ty_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             gas_meter.charge_vec_len()?;
             let value = vec_ref.len(&ty)?;
             state.push_operand(value)?;
         }
         Bytecode::VecImmBorrow(ty_ptr) => {
             let idx = checked_as!(state.pop_operand_as::<u64>()?, usize)?;
             let vec_ref = state.pop_operand_as::<VectorRef>()?;
-            let ty = instantiate_single_type(ty_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_single_type(
+                &state.type_limits,
+                ty_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             let res = vec_ref.borrow_elem(idx, &ty);
             gas_meter.charge_vec_borrow(false, res.is_ok())?;
             state.push_operand(res?)?;
         }
         Bytecode::VecMutBorrow(ty_ptr) => {
             let idx = checked_as!(state.pop_operand_as::<u64>()?, usize)?;
             let vec_ref = state.pop_operand_as::<VectorRef>()?;
-            let ty = instantiate_single_type(ty_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_single_type(
+                &state.type_limits,
+                ty_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             let res = vec_ref.borrow_elem(idx, &ty);
             gas_meter.charge_vec_borrow(true, res.is_ok())?;
             state.push_operand(res?)?;
         }
         Bytecode::VecPushBack(ty_ptr) => {
             let elem = state.pop_operand()?;
             let vec_ref = state.pop_operand_as::<VectorRef>()?;
-            let ty = instantiate_single_type(ty_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_single_type(
+                &state.type_limits,
+                ty_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             gas_meter.charge_vec_push_back(&elem)?;
             vec_ref.push_back(
                 elem,
@@ -780,14 +805,22 @@ fn op_step_impl(
         }
         Bytecode::VecPopBack(ty_ptr) => {
             let vec_ref = state.pop_operand_as::<VectorRef>()?;
-            let ty = instantiate_single_type(ty_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_single_type(
+                &state.type_limits,
+                ty_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             let res = vec_ref.pop(&ty);
             gas_meter.charge_vec_pop_back(res.as_ref().ok())?;
             state.push_operand(res?)?;
         }
         Bytecode::VecUnpack(ty_ptr, num) => {
             let vec_val = state.pop_operand_as::<Vector>()?;
-            let ty = instantiate_single_type(ty_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_single_type(
+                &state.type_limits,
+                ty_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             gas_meter.charge_vec_unpack(NumArgs::new(*num), vec_val.elem_views()?)?;
             let elements = vec_val.unpack(&ty, *num)?;
             for value in elements {
@@ -798,8 +831,11 @@ fn op_step_impl(
             let idx2 = checked_as!(state.pop_operand_as::<u64>()?, usize)?;
             let idx1 = checked_as!(state.pop_operand_as::<u64>()?, usize)?;
             let vec_ref = state.pop_operand_as::<VectorRef>()?;
-            let ty =
-                instantiate_single_type(ty_ptr.to_ref(), state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_single_type(
+                &state.type_limits,
+                ty_ptr.to_ref(),
+                state.call_stack.current_frame.ty_args(),
+            )?;
             gas_meter.charge_vec_swap()?;
             vec_ref.swap(idx1, idx2, &ty)?;
         }
@@ -814,7 +850,11 @@ fn op_step_impl(
         Bytecode::PackVariantGeneric(vinst_ptr) => {
             let variant = &vinst_ptr.variant;
             let (field_count, variant_tag) = (variant.field_count(), variant.variant_tag);
-            let ty = instantiate_enum_type(vinst_ptr, state.call_stack.current_frame.ty_args())?;
+            let ty = instantiate_enum_type(
+                &state.type_limits,
+                vinst_ptr,
+                state.call_stack.current_frame.ty_args(),
+            )?;
             check_depth_of_type(run_context, &ty)?;
             gas_meter.charge_pack(true, state.last_n_operands(field_count)?)?;
             let args = state.pop_n_operands(checked_as!(field_count, u16)?)?;
```

### external-crates/move/crates/move-vm-runtime/src/execution/interpreter/helpers.rs
```diff
@@ -14,78 +14,84 @@ use crate::{
         ArenaType, FunctionInstantiation, StructInstantiation, Type, TypeNodeCount, TypeSubst,
         VariantInstantiation,
     },
-    shared::constants::MAX_TYPE_INSTANTIATION_NODES,
+    shared::TypeLimits,
 };
 
 use move_binary_format::{errors::PartialVMResult, partial_vm_error};
 
 pub fn instantiate_generic_function(
+    limits: &TypeLimits,
     fun_inst: &FunctionInstantiation,
     type_params: &[Type],
 ) -> PartialVMResult<Vec<Type>> {
     let instantiation: Vec<_> = fun_inst
         .instantiation
         .to_ref()
         .iter()
-        .map(|ty| ty.subst(type_params))
+        .map(|ty| ty.subst_with_limits(limits, type_params))
         .collect::<PartialVMResult<_>>()?;
 
-    // Check if the function instantiation over all generics is larger
-    // than MAX_TYPE_INSTANTIATION_NODES.
+    // Check if the function instantiation over all generics exceeds the type node limit.
     let mut sum_nodes = 1u64;
     for ty in type_params.iter().chain(instantiation.iter()) {
         sum_nodes = sum_nodes.saturating_add(ty.count_type_nodes()?);
-        if sum_nodes > MAX_TYPE_INSTANTIATION_NODES {
+        if sum_nodes > limits.max_type_nodes() {
             return Err(partial_vm_error!(VM_MAX_TYPE_NODES_REACHED));
         }
     }
     Ok(instantiation)
 }
 
-pub fn instantiate_single_type(ty: &ArenaType, ty_args: &[Type]) -> PartialVMResult<Type> {
+pub fn instantiate_single_type(
+    limits: &TypeLimits,
+    ty: &ArenaType,
+    ty_args: &[Type],
+) -> PartialVMResult<Type> {
     if !ty_args.is_empty() {
-        ty.subst(ty_args)
+        ty.subst_with_limits(limits, ty_args)
     } else {
-        ty.to_type()
+        ty.to_type_with_limits(limits)
     }
 }
 
 pub fn instantiate_struct_type(
+    limits: &TypeLimits,
     struct_inst: &StructInstantiation,
     ty_args: &[Type],
 ) -> PartialVMResult<Type> {
     let type_params = struct_inst.type_params.to_ref();
-    instantiate_datatype_common(&struct_inst.def_vtable_key, type_params, ty_args)
+    instantiate_datatype_common(limits, &struct_inst.def_vtable_key, type_params, ty_args)
 }
 
 pub fn instantiate_enum_type(
+    limits: &TypeLimits,
     variant_inst: &VariantInstantiation,
     ty_args: &[Type],
 ) -> PartialVMResult<Type> {
     let enum_inst = variant_inst.enum_inst.to_ref();
     let type_params = enum_inst.type_params.to_ref();
-    instantiate_datatype_common(&enum_inst.def_vtable_key, type_params, ty_args)
+    instantiate_datatype_common(limits, &enum_inst.def_vtable_key, type_params, ty_args)
 }
 
 fn instantiate_datatype_common(
+    limits: &TypeLimits,
     datatype_key: &VirtualTableKey,
     type_params: &[ArenaType],
     ty_args: &[Type],
 ) -> PartialVMResult<Type> {
     // Before instantiating the type, count the # of nodes of all type arguments plus
     // existing type instantiation.
-    // If that number is larger than MAX_TYPE_INSTANTIATION_NODES, refuse to construct this type.
     // This prevents constructing larger and larger types via datatype instantiation.
     let mut sum_nodes = 1u64;
     for ty in type_params.iter() {
         sum_nodes = sum_nodes.saturating_add(ty.count_type_nodes()?);
-        if sum_nodes > MAX_TYPE_INSTANTIATION_NODES {
+        if sum_nodes > limits.max_type_nodes() {
             return Err(partial_vm_error!(VM_MAX_TYPE_NODES_REACHED));
         }
     }
     for ty in ty_args.iter() {
         sum_nodes = sum_nodes.saturating_add(ty.count_type_nodes()?);
-        if sum_nodes > MAX_TYPE_INSTANTIATION_NODES {
+        if sum_nodes > limits.max_type_nodes() {
             return Err(partial_vm_error!(VM_MAX_TYPE_NODES_REACHED));
         }
     }
@@ -94,7 +100,7 @@ fn instantiate_datatype_common(
         datatype_key.clone(),
         type_params
             .iter()
-            .map(|ty| ty.subst(ty_args))
+            .map(|ty| ty.subst_with_limits(limits, ty_args))
             .collect::<PartialVMResult<_>>()?,
     ))))
 }
```

### external-crates/move/crates/move-vm-runtime/src/execution/interpreter/mod.rs
```diff
@@ -11,7 +11,7 @@ use crate::{
     jit::execution::ast::{Function, Type},
     natives::extensions::NativeContextExtensions,
     runtime::telemetry::TransactionTelemetryContext,
-    shared::{gas::GasMeter, vm_pointer::VMPointer},
+    shared::{TypeLimits, gas::GasMeter, vm_pointer::VMPointer},
     try_block,
 };
 use move_binary_format::errors::*;
@@ -31,6 +31,7 @@ pub(crate) fn run(
     vtables: &mut VMDispatchTables,
     telemetry: &mut TransactionTelemetryContext,
     vm_config: Arc<VMConfig>,
+    type_limits: TypeLimits,
     extensions: &mut NativeContextExtensions,
     tracer: &mut Option<VMTracer<'_>>,
     gas_meter: &mut impl GasMeter,
@@ -80,7 +81,8 @@ pub(crate) fn run(
                         fun_ref.module_id(&vtables.interner).clone(),
                     ))
             })?;
-            let state = MachineState::new(Arc::clone(&vtables.interner), call_stack);
+            let state =
+                MachineState::new(Arc::clone(&vtables.interner), type_limits, call_stack);
             eval::run(state, vtables, telemetry, vm_config, extensions, tracer, gas_meter)
         }
     };
```

### external-crates/move/crates/move-vm-runtime/src/execution/interpreter/state.rs
```diff
@@ -13,6 +13,7 @@ use crate::{
     },
     jit::execution::ast::{Function, InternedDisplay, Type},
     shared::{
+        TypeLimits,
         constants::{CALL_STACK_SIZE_LIMIT, OPERAND_STACK_SIZE_LIMIT},
         safe_ops::{SafeArithmetic as _, SafeIndex as _},
         vm_pointer::VMPointer,
@@ -49,6 +50,7 @@ pub(crate) struct MachineState {
     /// Operand stack, where Move `Value`s are stored for stack operations.
     pub(crate) operand_stack: ValueStack,
     pub(crate) interner: Arc<IdentifierInterner>,
+    pub(crate) type_limits: TypeLimits,
     pub(crate) callstack_highwatermark: usize,
     pub(crate) valuestack_highwatermark: usize,
 }
@@ -84,12 +86,17 @@ pub(crate) struct CallFrame {
 // -------------------------------------------------------------------------------------------------
 
 impl MachineState {
-    pub(super) fn new(interner: Arc<IdentifierInterner>, call_stack: CallStack) -> Self {
+    pub(super) fn new(
+        interner: Arc<IdentifierInterner>,
+        type_limits: TypeLimits,
+        call_stack: CallStack,
+    ) -> Self {
         let callstack_highwatermark = call_stack.heap.cur_size();
         MachineState {
             operand_stack: ValueStack::new(),
             call_stack,
             interner,
+            type_limits,
             callstack_highwatermark,
             valuestack_highwatermark: 0,
         }
```

### external-crates/move/crates/move-vm-runtime/src/execution/tracing/tracer.rs
```diff
@@ -1393,6 +1393,7 @@ impl VMTracer<'_> {
             B::PackGeneric(struct_inst_ptr) => {
                 let field_count = struct_inst_ptr.field_count as usize;
                 let struct_type = instantiate_struct_type(
+                    &machine.type_limits,
                     struct_inst_ptr,
                     &machine.call_stack.current_frame.ty_args,
                 )
@@ -1587,8 +1588,12 @@ impl VMTracer<'_> {
                     .instruction(instruction, ty_args, effects, *remaining_gas, pc);
             }
             B::VecPack(ty_ptr, n) => {
-                let ty = instantiate_single_type(ty_ptr, &machine.call_stack.current_frame.ty_args)
-                    .ok()?;
+                let ty = instantiate_single_type(
+                    &machine.type_limits,
+                    ty_ptr,
+                    &machine.call_stack.current_frame.ty_args,
+                )
+                .ok()?;
                 let ty = vtables.type_to_fully_annotated_layout(&ty).ok()?;
                 let ty = AnnotatedTypeLayout::Vector(Box::new(ty));
                 let stack_len = self.type_stack.len();
@@ -1746,6 +1751,7 @@ impl VMTracer<'_> {
                 let ty = vtables
                     .type_to_fully_annotated_layout(
                         &instantiate_enum_type(
+                            &machine.type_limits,
                             variant_inst_ptr,
                             &machine.call_stack.current_frame.ty_args,
                         )
```

### external-crates/move/crates/move-vm-runtime/src/execution/vm.rs
```diff
@@ -11,6 +11,7 @@ use crate::{
     natives::extensions::NativeExtensions,
     runtime::telemetry::{TelemetryContext, TransactionTelemetryContext},
     shared::{
+        TypeLimits,
         gas::GasMeter,
         linkage_context::LinkageContext,
         types::{DefiningTypeId, OriginalId},
@@ -143,6 +144,7 @@ impl<'extensions> MoveVM<'extensions> {
             None,
             gas_meter,
             bypass_declared_entry_check,
+            TypeLimits::VM_DEFAULT,
         )
     }
 
@@ -157,6 +159,32 @@ impl<'extensions> MoveVM<'extensions> {
         gas_meter: &mut impl GasMeter,
         tracer: Option<&mut MoveTraceBuilder>,
     ) -> VMResult<Vec<Value>> {
+        self.execute_function_bypass_visibility_with_max_type_nodes(
+            module,
+            function_name,
+            ty_args,
+            args,
+            gas_meter,
+            tracer,
+            None,
+        )
+    }
+
+    #[instrument(level = "trace", skip_all)]
+    pub fn execute_function_bypass_visibility_with_max_type_nodes(
+        &mut self,
+        module: &ModuleId,
+        function_name: &IdentStr,
+        ty_args: Vec<Type>,
+        args: Vec<Value>,
+        gas_meter: &mut impl GasMeter,
+        tracer: Option<&mut MoveTraceBuilder>,
+        max_type_nodes: Option<u64>,
+    ) -> VMResult<Vec<Value>> {
+        let type_limits = match max_type_nodes {
+            Some(max_type_nodes) => TypeLimits::VM_DEFAULT.raise_max_type_nodes_to(max_type_nodes),
+            None => TypeLimits::VM_DEFAULT,
+        };
         let tracer = if cfg!(feature = "tracing") {
             tracer
         } else {
@@ -179,6 +207,7 @@ impl<'extensions> MoveVM<'extensions> {
             tracer,
             gas_meter,
             bypass_declared_entry_check,
+            type_limits,
         )
     }
 
@@ -337,6 +366,7 @@ impl<'extensions> MoveVM<'extensions> {
         tracer: Option<&mut MoveTraceBuilder>,
         gas_meter: &mut impl GasMeter,
         bypass_declared_entry_check: bool,
+        type_limits: TypeLimits,
     ) -> VMResult<Vec<Value>> {
         let telemetry = Arc::clone(&self.telemetry);
         telemetry.with_transaction_telemetry(|txn_telemetry| {
@@ -386,6 +416,7 @@ impl<'extensions> MoveVM<'extensions> {
                     function,
                     type_arguments,
                     args,
+                    type_limits,
                 )
             };
 
@@ -455,11 +486,13 @@ impl<'extensions> MoveVM<'extensions> {
         func: VMPointer<Function>,
         ty_args: Vec<Type>,
         args: Vec<Value>,
+        type_limits: TypeLimits,
     ) -> VMResult<Vec<Value>> {
         interpreter::run(
             &mut self.virtual_tables,
             txn_telemetry,
             self.vm_config.clone(),
+            type_limits,
             &mut *self.native_extensions.try_borrow_mut().map_err(|e| {
                 partial_vm_error!(
                     UNKNOWN_INVARIANT_VIOLATION_ERROR,
```

### external-crates/move/crates/move-vm-runtime/src/jit/execution/ast.rs
```diff
@@ -12,7 +12,7 @@ use crate::{
     },
     natives::functions::{NativeFunction, UnboxedNativeFunction},
     shared::{
-        TypeSize,
+        TypeLimits, TypeSize,
         safe_ops::SafeArithmetic as _,
         types::{OriginalId, VersionId},
         vm_pointer::VMPointer,
@@ -983,7 +983,11 @@ impl VariantInstantiation {
 impl ArenaType {
     /// Convert to a runtime type by performing a deep copy
     pub fn to_type(&self) -> PartialVMResult<Type> {
-        self.to_type_impl(&mut TypeSize::for_type_traversal())
+        self.to_type_with_limits(&TypeLimits::VM_DEFAULT)
+    }
+
+    pub fn to_type_with_limits(&self, limits: &TypeLimits) -> PartialVMResult<Type> {
+        self.to_type_impl(&mut limits.traversal())
     }
 
     fn to_type_impl(&self, type_size: &mut TypeSize) -> PartialVMResult<Type> {
@@ -1246,6 +1250,7 @@ pub trait TypeSubst {
     where
         F: Fn(u16, &mut TypeSize) -> PartialVMResult<Type> + Copy;
     fn subst(&self, ty_args: &[Type]) -> PartialVMResult<Type>;
+    fn subst_with_limits(&self, limits: &TypeLimits, ty_args: &[Type]) -> PartialVMResult<Type>;
 }
 
 // Macro that generates the implementations.
@@ -1303,6 +1308,14 @@ macro_rules! impl_deep_subst {
             }
 
             fn subst(&self, ty_args: &[Type]) -> PartialVMResult<Type> {
+                self.subst_with_limits(&$crate::shared::TypeLimits::VM_DEFAULT, ty_args)
+            }
+
+            fn subst_with_limits(
+                &self,
+                limits: &$crate::shared::TypeLimits,
+                ty_args: &[Type],
+            ) -> PartialVMResult<Type> {
                 self.apply_subst(
                     |idx, type_size| match ty_args.get(idx as usize) {
                         Some(ty) => ty.clone_impl(type_size),
@@ -1313,7 +1326,7 @@ macro_rules! impl_deep_subst {
                             idx
                         )),
                     },
-                    &mut $crate::shared::TypeSize::for_type_traversal(),
+                    &mut limits.traversal(),
                 )
             }
         }
```

### external-crates/move/crates/move-vm-runtime/src/shared/mod.rs
```diff
@@ -51,6 +51,39 @@ pub fn unique_map<Key: Hash + Eq, Value>(
     Ok(map)
 }
 
+#[derive(Copy, Clone, Debug)]
+pub struct TypeLimits {
+    max_type_nodes: u64,
+    max_type_depth: u64,
+}
+
+impl TypeLimits {
+    pub const VM_DEFAULT: Self = Self {
+        max_type_nodes: MAX_TYPE_INSTANTIATION_NODES,
+        max_type_depth: TYPE_DEPTH_MAX,
+    };
+
+    pub fn raise_max_type_nodes_to(self, max_type_nodes: u64) -> Self {
+        Self {
+            max_type_nodes: max_type_nodes.max(self.max_type_nodes),
+            ..self
+        }
+    }
+
+    pub fn max_type_nodes(&self) -> u64 {
+        self.max_type_nodes
+    }
+
+    pub fn traversal(&self) -> TypeSize {
+        TypeSize {
+            depth: 0,
+            node_count: 0,
+            max_depth: self.max_type_depth,
+            max_nodes: self.max_type_nodes,
+        }
+    }
+}
+
 /// Tracks depth and node count during recursive type traversal, enforcing configurable
 /// limits on both.
 pub struct TypeSize {
@@ -64,12 +97,7 @@ impl TypeSize {
     /// Standard limits for normal type traversal (i.e., not factoring in field types or
     /// "values"/layouts of that type): `TYPE_DEPTH_MAX` depth, `MAX_TYPE_INSTANTIATION_NODES` nodes.
     pub fn for_type_traversal() -> Self {
-        Self {
-            depth: 0,
-            node_count: 0,
-            max_depth: TYPE_DEPTH_MAX,
-            max_nodes: MAX_TYPE_INSTANTIATION_NODES,
-        }
+        TypeLimits::VM_DEFAULT.traversal()
     }
 
     /// Custom limits for "value"/layout traversal.
```

### sui-execution/latest/sui-adapter/src/static_programmable_transactions/execution/context.rs
```diff
@@ -67,7 +67,9 @@ use sui_protocol_config::ProtocolConfig;
 use sui_types::{
     TypeTag,
     accumulator_event::AccumulatorEvent,
-    accumulator_root::{self, AccumulatorObjId},
+    accumulator_root::{
+        self, AccumulatorObjId, SETTLEMENT_MAX_TYPE_INSTANTIATION_NODES, is_settle_u128_call,
+    },
     balance::Balance,
     base_types::{
         MoveObjectType, ObjectID, RESOLVED_ASCII_STR, RESOLVED_UTF8_STR, SequenceNumber,
@@ -981,6 +983,12 @@ where
                         .map_err(|e| self.env.convert_linked_vm_error(e, &function.linkage))
                 })
                 .collect::<Result<Vec<_>, Mode::Error>>()?;
+            let max_type_nodes = is_settle_u128_call(
+                function.original_mid.address(),
+                function.original_mid.name(),
+                &function.name,
+            )
+            .then_some(SETTLEMENT_MAX_TYPE_INSTANTIATION_NODES);
             let result = self.execute_function_bypass_visibility_with_vm(
                 vm,
                 &function.original_mid,
@@ -989,6 +997,7 @@ where
                 args,
                 &function.linkage,
                 trace_builder_opt,
+                max_type_nodes,
             )?;
             self.take_user_events(
                 vm,
@@ -1010,16 +1019,18 @@ where
         args: Vec<CtxValue>,
         linkage: &ExecutableLinkage,
         tracer: &mut Option<MoveTraceBuilder>,
+        max_type_nodes: Option<u64>,
     ) -> Result<Vec<CtxValue>, Mode::Error> {
         let gas_status = self.gas_charger.move_gas_status_mut();
         let values = vm
-            .execute_function_bypass_visibility(
+            .execute_function_bypass_visibility_with_max_type_nodes(
                 original_mid,
                 function_name,
                 ty_args,
                 args.into_iter().map(|v| v.0.into()).collect(),
                 &mut SuiGasMeter(gas_status),
                 tracer.as_mut(),
+                max_type_nodes,
             )
             .map_err(|e| self.env.convert_linked_vm_error(e, linkage))?;
         Ok(values.into_iter().map(|v| CtxValue(v.into())).collect())
@@ -1243,6 +1254,7 @@ where
                 args,
                 linkage,
                 trace_builder_opt,
+                None,
             )?;
             trace_utils::trace_move_call_end(trace_builder_opt);
 
```
