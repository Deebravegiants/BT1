# [?] fix bv panics (#20344)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-08-13
Source: https://github.com/aptos-labs/aptos-core/commit/453b848d847e9b9f878add3e773b114ccebeb4bf
Type: security-commit

## Details
fix bv panics (#20344)

## Patch
### third_party/move/move-model/src/ty.rs
```diff
@@ -1854,16 +1854,38 @@ impl Type {
     /// Normalize a function type into the canonical form used to index and
     /// compare function types: abilities are stripped (they are abstracted by
     /// the prover) and both argument and result tuples are unwrapped-if-
-    /// singleton. Panics if not called on a function type.
+    /// singleton, at every nesting depth — matching the erasure the Boogie
+    /// type name applies, so two types normalize equal exactly when their
+    /// names mangle equal. Panics if not called on a function type.
     pub fn normalize_fun(self) -> Type {
-        let Type::Fun(params, results, _) = self else {
-            panic!("expected fun type")
-        };
-        Type::Fun(
-            Box::new(Type::tuple(params.flatten())),
-            Box::new(Type::tuple(results.flatten())),
-            AbilitySet::EMPTY,
-        )
+        assert!(matches!(self, Type::Fun(..)), "expected fun type");
+        self.normalize_nested_funs()
+    }
+
+    /// Normalize every function type nested anywhere inside `self` into the
+    /// canonical form of `normalize_fun`, leaving other type constructors
+    /// unchanged.
+    pub fn normalize_nested_funs(self) -> Type {
+        match self {
+            Type::Fun(params, results, _) => Type::Fun(
+                Box::new(Type::tuple(params.flatten()).normalize_nested_funs()),
+                Box::new(Type::tuple(results.flatten()).normalize_nested_funs()),
+                AbilitySet::EMPTY,
+            ),
+            Type::Vector(et) => Type::Vector(Box::new(et.normalize_nested_funs())),
+            Type::Struct(mid, sid, ts) => Type::Struct(
+                mid,
+                sid,
+                ts.into_iter().map(Type::normalize_nested_funs).collect(),
+            ),
+            Type::Tuple(ts) => {
+                Type::Tuple(ts.into_iter().map(Type::normalize_nested_funs).collect())
+            },
+            Type::Reference(kind, bt) => {
+                Type::Reference(kind, Box::new(bt.normalize_nested_funs()))
+            },
+            _ => self,
+        }
     }
 
     /// If this is a vector of more than one type, make a tuple out of it, otherwise return the
```

### third_party/move/move-prover/boogie-backend/src/boogie_helpers.rs
```diff
@@ -24,7 +24,7 @@ use move_model::{
     ty::{PrimitiveType, ReferenceKind, Type},
 };
 use move_prover_bytecode_pipeline::number_operation::{
-    GlobalNumberOperationState, NumOperation::Bitwise,
+    GlobalNumberOperationState, NumOperation, NumOperation::Bitwise,
 };
 use move_stackless_bytecode::{function_target::FunctionTarget, stackless_bytecode::Constant};
 use num::BigUint;
@@ -150,10 +150,13 @@ pub fn boogie_variant_field_update(
     )
 }
 
-/// Return true if the field is a bitwise field
+/// Return whether the field renders as a bitvector. `ty` is the field's
+/// (instantiated) type; signed-containing types never render as bitvectors.
 pub fn field_bv_flag_global_state(
     global_state: &GlobalNumberOperationState,
     field_env: &FieldEnv,
+    env: &GlobalEnv,
+    ty: &Type,
 ) -> bool {
     // Ghost fields are model-only and never participate in number-operation
     // (bitvector) analysis; on enums they also carry no variant.
@@ -175,21 +178,21 @@ pub fn field_bv_flag_global_state(
     } else {
         field_env.get_id()
     };
-    if let Some(struct_info) = operation_map.get(&(mid, sid)) {
-        matches!(struct_info.get(&field_id), Some(&Bitwise))
-    } else {
-        false
-    }
+    operation_map
+        .get(&(mid, sid))
+        .and_then(|struct_info| struct_info.get(&field_id))
+        .is_some_and(|oper| bv_flag_for_type(env, oper, ty))
 }
 
-/// Return boogie type for given field
+/// Return boogie type for given field. `ty` is the field's (instantiated)
+/// type.
 pub fn boogie_type_for_struct_field(
     global_state: &GlobalNumberOperationState,
     field: &FieldEnv,
     env: &GlobalEnv,
     ty: &Type,
 ) -> String {
-    let bv_flag = field_bv_flag_global_state(global_state, field);
+    let bv_flag = field_bv_flag_global_state(global_state, field, env, ty);
     boogie_type(env, ty, bv_flag)
 }
 
@@ -353,6 +356,88 @@ pub fn boogie_make_vec_from_strings(args: &[String]) -> String {
     }
 }
 
+/// Return whether `ty`'s containment closure (vector elements, type arguments,
+/// struct fields) includes a signed integer. Signed integers are always Boogie
+/// `int` — they have no bitvector rendering — so such types must not select bv
+/// encodings; the prelude generates no bv twins for them. This mirrors the
+/// traversal of `Type::get_all_contained_types_with_skip_reference`, but
+/// short-circuits on the first signed integer instead of materializing the
+/// closure, and additionally checks the intrinsic-map value type argument: it
+/// is declared phantom, yet the Boogie representation (`Table int (V)`)
+/// embeds it. Keys are not checked — they encode to int regardless of the
+/// map's bv rendering.
+pub fn type_contains_signed_int(env: &GlobalEnv, ty: &Type) -> bool {
+    type_contains_prim(env, ty, &|p| p.is_signed())
+}
+
+/// Like `type_contains_signed_int`, for widthless `num`: it has no
+/// bitvector rendering either, and can appear nested (e.g. `vector<num>`
+/// in a spec-function instantiation whose slot acquired `Bitwise` from an
+/// unrelated caller).
+pub fn type_contains_widthless_num(env: &GlobalEnv, ty: &Type) -> bool {
+    type_contains_prim(env, ty, &|p| matches!(p, PrimitiveType::Num))
+}
+
+fn type_contains_prim(env: &GlobalEnv, ty: &Type, pred: &impl Fn(&PrimitiveType) -> bool) -> bool {
+    use Type::*;
+    match ty {
+        Primitive(p) => pred(p),
+        Tuple(ts) => ts.iter().any(|t| type_contains_prim(env, t, pred)),
+        Vector(et) => type_contains_prim(env, et, pred),
+        Struct(mid, sid, ts) => {
+            let struct_env = env.get_module(*mid).into_struct(*sid);
+            let args_contain = if struct_env.is_intrinsic_of(INTRINSIC_TYPE_MAP) {
+                // Only the value type is rendered: the representation is
+                // `Table int (V)` with keys encoded to int by `$EncodeKey`,
+                // and bv twin supply likewise keys on the value type alone.
+                // A signed key must not clamp an unsigned bitwise value to
+                // the int twin while value operands render bv.
+                ts.get(1).is_some_and(|t| type_contains_prim(env, t, pred))
+            } else {
+                // Phantom arguments cannot reach a field type of an ordinary
+                // struct, matching the containment closure.
+                ts.iter().enumerate().any(|(i, t)| {
+                    !struct_env.is_phantom_parameter(i) && type_contains_prim(env, t, pred)
+                })
+            };
+            if args_contain {
+                return true;
+            }
+            if struct_env.has_variants() {
+                struct_env.get_variants().any(|variant| {
+                    struct_env
+                        .get_fields_of_variant(variant)
+                        .any(|f| type_contains_prim(env, &f.get_type().instantiate(ts), pred))
+                })
+            } else {
+                struct_env
+                    .get_fields()
+                    .any(|f| type_contains_prim(env, &f.get_type().instantiate(ts), pred))
+            }
+        },
+        Fun(arg, result, _) => {
+            type_contains_prim(env, arg, pred) || type_contains_prim(env, result, pred)
+        },
+        Reference(_, bt) | TypeDomain(bt) => type_contains_prim(env, bt, pred),
+        ResourceDomain(_, _, Some(ts)) => ts.iter().any(|t| type_contains_prim(env, t, pred)),
+        ResourceDomain(_, _, None) | TypeParameter(_) | StateDomain | Error | Var(_) => false,
+    }
+}
+
+/// Effective bitvector flag for a value of type `ty`: a `Bitwise`
+/// classification selects bv rendering only for types that have one.
+/// Number-operation slots shared across generic instantiations (parameters,
+/// fields) can carry `Bitwise` acquired from an unsigned instantiation; values
+/// of signed instantiations must still render as `int`. Widthless `num`
+/// values (spec lets, spec fun results) have no bitvector rendering either:
+/// a caller's bitwise argument can mark a callee's parameter slot `Bitwise`
+/// and reach `num`-typed expressions in the callee's spec through it.
+pub fn bv_flag_for_type(env: &GlobalEnv, num_oper: &NumOperation, ty: &Type) -> bool {
+    *num_oper == Bitwise
+        && !type_contains_widthless_num(env, ty)
+        && !type_contains_signed_int(env, ty)
+}
+
 /// Returns `"bvN"` when `bv_flag` is true, `"int"` otherwise.
 fn uint_bv_type(bits: usize, bv_flag: bool) -> String {
     if bv_flag {
@@ -491,12 +576,14 @@ pub fn boogie_int_suffix(ty: &Type, bv_flag: bool) -> String {
         Type::Primitive(U64) => boogie_num_type_string_capital("U", "64", bv_flag),
         Type::Primitive(U128) => boogie_num_type_string_capital("U", "128", bv_flag),
         Type::Primitive(U256) => boogie_num_type_string_capital("U", "256", bv_flag),
-        Type::Primitive(I8) => boogie_num_type_string_capital("I", "8", bv_flag),
-        Type::Primitive(I16) => boogie_num_type_string_capital("I", "16", bv_flag),
-        Type::Primitive(I32) => boogie_num_type_string_capital("I", "32", bv_flag),
-        Type::Primitive(I64) => boogie_num_type_string_capital("I", "64", bv_flag),
-        Type::Primitive(I128) => boogie_num_type_string_capital("I", "128", bv_flag),
-        Type::Primitive(I256) => boogie_num_type_string_capital("I", "256", bv_flag),
+        // Signed integers have no bv rendering; ignore `bv_flag` rather than
+        // alias to the unsigned bv procedure names.
+        Type::Primitive(I8) => "I8".to_string(),
+        Type::Primitive(I16) => "I16".to_string(),
+        Type::Primitive(I32) => "I32".to_string(),
+        Type::Primitive(I64) => "I64".to_string(),
+        Type::Primitive(I128) => "I128".to_string(),
+        Type::Primitive(I256) => "I256".to_string(),
         _ => unreachable!("non-integer dest for arithmetic op"),
     }
 }
@@ -580,12 +667,14 @@ pub fn boogie_type_suffix(env: &GlobalEnv, ty: &Type, bv_flag: bool) -> String {
             U64 => boogie_num_type_string("u", "64", bv_flag),
             U128 => boogie_num_type_string("u", "128", bv_flag),
             U256 => boogie_num_type_string("u", "256", bv_flag),
-            I8 => boogie_num_type_string("i", "8", bv_flag),
-            I16 => boogie_num_type_string("i", "16", bv_flag),
-            I32 => boogie_num_type_string("i", "32", bv_flag),
-            I64 => boogie_num_type_string("i", "64", bv_flag),
-            I128 => boogie_num_type_string("i", "128", bv_flag),
-            I256 => boogie_num_type_string("i", "256", bv_flag),
+            // Signed integers have no bv rendering; ignore `bv_flag` rather
+            // than alias to the unsigned bv suffixes.
+            I8 => "i8".to_string(),
+            I16 => "i16".to_string(),
+            I32 => "i32".to_string(),
+            I64 => "i64".to_string(),
+            I128 => "i128".to_string(),
+            I256 => "i256".to_string(),
             Num => {
                 if bv_flag {
                     //TODO(#19036): add error message with accurate location info
```

### third_party/move/move-prover/boogie-backend/src/bytecode_translator.rs
```diff
@@ -22,7 +22,8 @@ use crate::{
         boogie_type_for_struct_field, boogie_type_param, boogie_type_suffix,
         boogie_type_suffix_for_struct, boogie_type_suffix_for_struct_variant,
         boogie_variant_field_update, boogie_well_formed_check, boogie_well_formed_expr,
-        compute_evaluator_memory_union, field_bv_flag_global_state, TypeIdentToken,
+        bv_flag_for_type, compute_evaluator_memory_union, field_bv_flag_global_state,
+        TypeIdentToken,
     },
     options::BoogieOptions,
     spec_translator::{LabelInfo, SpecTranslator},
@@ -33,7 +34,7 @@ use itertools::Itertools;
 use legacy_move_compiler::interface_generator::NATIVE_INTERFACE;
 #[allow(unused_imports)]
 use log::{debug, info, log, warn, Level};
-use move_core_types::{ability::AbilitySet, function::ClosureMask};
+use move_core_types::function::ClosureMask;
 use move_model::{
     ast::{
         Attribute, BehaviorKind, ConditionKind, Exp, ExpData, FrameAccessKind, FunParamAccessOf,
@@ -161,9 +162,21 @@ impl BpAxiomCtx<'_> {
                 field_sym,
             } => {
                 if kind == BehaviorKind::ResultOf {
-                    boogie_struct_field_result_fun_name(env, struct_id, *field_sym, &[], false)
+                    boogie_struct_field_result_fun_name(
+                        env,
+                        struct_id,
+                        *field_sym,
+                        &struct_id.inst,
+                        false,
+                    )
                 } else {
-                    boogie_struct_field_spec_fun_name(env, struct_id, *field_sym, kind, &[])
+                    boogie_struct_field_spec_fun_name(
+                        env,
+                        struct_id,
+                        *field_sym,
+                        kind,
+                        &struct_id.inst,
+                    )
                 }
             },
             BpAxiomCtx::FunParam { fun, param_sym, .. } => {
@@ -1262,27 +1275,27 @@ impl<'env> BoogieTranslator<'env> {
                 &info.struct_id,
                 info.field_sym,
                 BehaviorKind::AbortsOf,
-                &[],
+                &info.struct_id.inst,
             );
             let ensures_name = boogie_struct_field_spec_fun_name(
                 self.env,
                 &info.struct_id,
                 info.field_sym,
                 BehaviorKind::EnsuresOf,
-                &[],
+                &info.struct_id.inst,
             );
             let result_fun_name = boogie_struct_field_result_fun_name(
                 self.env,
                 &info.struct_id,
                 info.field_sym,
-                &[],
+                &info.struct_id.inst,
                 false,
             );
             let multi_result_fun_name = boogie_struct_field_result_fun_name(
                 self.env,
                 &info.struct_id,
                 info.field_sym,
-                &[],
+                &info.struct_id.inst,
                 true,
             );
             let explicit_results = results.clone().flatten();
@@ -2096,14 +2109,21 @@ impl<'env> BoogieTranslator<'env> {
             .collect();
         let eval_call = format!("{}({})", eval_fun_name, eval_call_args.join(", "));
 
-        emitln!(
-            self.writer,
-            "axiom (forall {} :: {{{}}} {} <==> {});",
-            quantifier.join(", "),
-            eval_call,
-            eval_call,
-            rhs
-        );
+        if quantifier.is_empty() {
+            // Zero-argument function value with no memory dependency: emit a
+            // plain axiom (Boogie requires at least one bound variable in a
+            // quantifier).
+            emitln!(self.writer, "axiom {} <==> {};", eval_call, rhs);
+        } else {
+            emitln!(
+                self.writer,
+                "axiom (forall {} :: {{{}}} {} <==> {});",
+                quantifier.join(", "),
+                eval_call,
+                eval_call,
+                rhs
+            );
+        }
     }
 
     /// Emit a guarded evaluator axiom for a struct-field variant. Struct
@@ -2128,8 +2148,13 @@ impl<'env> BoogieTranslator<'env> {
     ) {
         let env = self.env;
         let ctor_name = boogie_struct_field_name(env, &info.struct_id, info.field_sym);
-        let bp_name =
-            boogie_struct_field_spec_fun_name(env, &info.struct_id, info.field_sym, kind, &[]);
+        let bp_name = boogie_struct_field_spec_fun_name(
+            env,
+            &info.struct_id,
+            info.field_sym,
+            kind,
+            &info.struct_id.inst,
+        );
         let struct_env_for_field = env.get_struct_qid(info.struct_id.to_qualified_id());
         let field_access = struct_env_for_field.get_field_access_of();
         let access_decl = field_access.iter().find(|a| a.fun_param == info.field_sym);
@@ -3568,7 +3593,7 @@ impl<'env> BoogieTranslator<'env> {
                     &info.struct_id,
                     info.field_sym,
                     kind,
-                    &[],
+                    &info.struct_id.inst,
                 );
                 emitln!(
                     self.writer,
@@ -3592,7 +3617,7 @@ impl<'env> BoogieTranslator<'env> {
                 &info.struct_id,
                 info.field_sym,
                 BehaviorKind::EnsuresOf,
-                &[],
+                &info.struct_id.inst,
             );
 
             let mut full_param_decls = input_param_decls.clone();
@@ -3605,7 +3630,7 @@ impl<'env> BoogieTranslator<'env> {
                     self.env,
                     &info.struct_id,
                     info.field_sym,
-                    &[],
+                    &info.struct_id.inst,
                     false,
                 );
                 emitln!(
@@ -3692,7 +3717,7 @@ impl<'env> BoogieTranslator<'env> {
                     self.env,
                     &info.struct_id,
                     info.field_sym,
-                    &[],
+                    &info.struct_id.inst,
                     true,
                 );
                 let tuple_element_types = Self::deref_output_types(&all_result_type_refs);
@@ -4402,18 +4427,21 @@ impl StructTranslator<'_> {
     ) -> Option<String> {
         let env = self.parent.env;
         let field_ty = field.get_type().instantiate(self.type_inst);
-        if let Type::Fun(params, results, abilities) = &field_ty {
+        if let Type::Fun(_, _, abilities) = &field_ty {
             if abilities.has_store() {
                 let mono_info = mono_analysis::get_info(env);
-                let normalized = Type::Fun(
-                    Box::new(Type::tuple(params.clone().flatten())),
-                    Box::new(Type::tuple(results.clone().flatten())),
-                    AbilitySet::EMPTY,
+                // Keys must derive from the same canonical forms the
+                // registration uses (`check_struct_fun_field`): the deep
+                // `normalize_fun` for the function type, and
+                // ability-normalized instantiation arguments for the
+                // containing struct.
+                let normalized = field_ty.clone().normalize_fun();
+                let struct_qid = self.struct_env.get_qualified_id().instantiate(
+                    self.type_inst
+                        .iter()
+                        .map(|t| t.clone().normalize_nested_funs())
+                        .collect(),
                 );
-                let struct_qid = self
-                    .struct_env
-                    .get_qualified_id()
-                    .instantiate(self.type_inst.to_vec());
                 if let Some(field_infos) = mono_info.fun_struct_field_infos.get(&normalized) {
                     let has_entry = field_infos.iter().any(|info| {
                         info.struct_id == struct_qid && info.field_sym == field.get_name()
@@ -4797,14 +4825,19 @@ impl StructTranslator<'_> {
         );
     }
 
-    /// Return whether a field involves bitwise operations
+    /// Return whether a field renders as a bitvector.
     pub fn field_bv_flag(&self, field_env: &FieldEnv) -> bool {
         let global_state = &self
             .parent
             .env
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number operation state");
-        field_bv_flag_global_state(global_state, field_env)
+        field_bv_flag_global_state(
+            global_state,
+            field_env,
+            self.parent.env,
+            &self.inst(&field_env.get_type()),
+        )
     }
 
     /// Return boogie type for a struct
@@ -5082,17 +5115,44 @@ impl StructTranslator<'_> {
 // Function Translation
 
 impl FunctionTranslator<'_> {
-    /// Return whether a specific TempIndex involves in bitwise operations
-    pub fn bv_flag_from_map(&self, i: &usize, operation_map: &FuncOperationMap) -> bool {
+    /// Return whether a value at position i in the given operation map renders
+    /// as a bitvector. `ty` is the value's (instantiated) type; signed-containing
+    /// types never render as bitvectors even when classified `Bitwise`.
+    pub fn bv_flag_from_map(&self, i: &usize, operation_map: &FuncOperationMap, ty: &Type) -> bool {
         let mid = self.fun_target.module_env().get_id();
         let sid = self.fun_target.func_env.get_id();
-        let param_oper = operation_map.get(&(mid, sid)).unwrap().get(i);
-        matches!(param_oper, Some(&Bitwise))
+        operation_map
+            .get(&(mid, sid))
+            .unwrap()
+            .get(i)
+            .is_some_and(|oper| bv_flag_for_type(self.parent.env, oper, ty))
     }
 
-    /// Return whether a specific TempIndex involves in bitwise operations
-    pub fn bv_flag(&self, num_oper: &NumOperation) -> bool {
-        *num_oper == Bitwise
+    /// Return whether a value of type `ty` with the given number-operation
+    /// classification renders as a bitvector. Signed-containing types never
+    /// do; a `Bitwise` classification can reach them through number-operation
+    /// slots shared across generic instantiations.
+    pub fn bv_flag(&self, num_oper: &NumOperation, ty: &Type) -> bool {
+        bv_flag_for_type(self.parent.env, num_oper, ty)
+    }
+
+    /// Return whether the value of the given temp renders as a bitvector,
+    /// pairing the temp's number-operation slot with its instantiated type.
+    /// The classification is checked before the type fetch: `Bitwise` slots
+    /// are rare, and the type instantiation is only needed for them.
+    pub fn temp_bv_flag(&self, idx: TempIndex) -> bool {
+        let global_state = &self
+            .fun_target
+            .global_env()
+            .get_extension::<GlobalNumberOperationState>()
+            .expect("global number operation state");
+        let mid = self.fun_target.module_env().get_id();
+        let fid = self.fun_target.func_env.get_id();
+        let baseline_flag = self.fun_target.data.variant == FunctionVariant::Baseline;
+        let num_oper = global_state
+            .get_temp_index_oper(mid, fid, idx, baseline_flag)
+            .unwrap();
+        *num_oper == Bitwise && self.bv_flag(num_oper, &self.get_local_type(idx))
     }
 
     /// Return whether a return value at position i involves in bitwise operation
@@ -5103,7 +5163,8 @@ impl FunctionTranslator<'_> {
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number operation state");
         let operation_map = &global_state.get_ret_map();
-        self.bv_flag_from_map(i, operation_map)
+        let ty = self.inst(&self.fun_target.get_return_type(*i));
+        self.bv_flag_from_map(i, operation_map, &ty)
     }
 
     /// Return boogie type for a local with given signature token.
@@ -5113,7 +5174,7 @@ impl FunctionTranslator<'_> {
         ty: &Type,
         num_oper: &NumOperation,
     ) -> String {
-        let bv_flag = self.bv_flag(num_oper);
+        let bv_flag = self.bv_flag(num_oper, ty);
         boogie_type(env, ty, bv_flag)
     }
 
@@ -5141,8 +5202,17 @@ impl FunctionTranslator<'_> {
             .get_qualified_id()
             .instantiate(self.type_inst.to_owned());
         // Set current function on spec_translator so behavioral predicates can
-        // resolve parameter access specifiers for memory args.
+        // resolve parameter access specifiers for memory args, and the
+        // variant so temporary renderings resolve through the right map.
         self.parent.spec_translator.set_current_fun_qid(qid.clone());
+        self.parent
+            .spec_translator
+            .set_current_fun_baseline(fun_target.data.variant == FunctionVariant::Baseline);
+        self.parent.spec_translator.set_current_fun_local_types(
+            (0..fun_target.get_local_count())
+                .map(|i| fun_target.get_local_type(i).clone())
+                .collect(),
+        );
         emitln!(
             writer,
             "// fun {} [{}] {}",
@@ -5154,6 +5224,8 @@ impl FunctionTranslator<'_> {
         self.generate_function_sig();
         self.generate_function_body();
         self.parent.spec_translator.clear_current_fun_qid();
+        self.parent.spec_translator.clear_current_fun_baseline();
+        self.parent.spec_translator.clear_current_fun_local_types();
         emitln!(self.parent.writer);
     }
 
@@ -5900,7 +5972,8 @@ impl FunctionTranslator<'_> {
                 PropKind::Modifies => {
                     let ty = self.inst(&env.get_node_type(exp.node_id()));
                     let ty = ty.skip_reference();
-                    let bv_flag = global_state.get_node_num_oper(exp.node_id()) == Bitwise;
+                    let bv_flag =
+                        bv_flag_for_type(env, &global_state.get_node_num_oper(exp.node_id()), ty);
                     let (mid, sid, inst) = ty.require_struct();
                     let memory = boogie_resource_memory_name(
                         env,
@@ -5957,10 +6030,7 @@ impl FunctionTranslator<'_> {
                 emitln!(writer, "return;");
             },
             Load(_, dest, c) => {
-                let num_oper = global_state
-                    .get_temp_index_oper(mid, fid, *dest, baseline_flag)
-                    .unwrap();
-                let bv_flag = self.bv_flag(num_oper);
+                let bv_flag = self.temp_bv_flag(*dest);
                 let value = match c {
                     Constant::Bool(true) => "true".to_string(),
                     Constant::Bool(false) => "false".to_string(),
@@ -6160,27 +6230,14 @@ impl FunctionTranslator<'_> {
                                     }
                                 }
                             }
-                            let caller_mid = self.fun_target.module_env().get_id();
-                            let caller_fid = self.fun_target.get_id();
                             let fun_verified =
                                 !self.fun_target.func_env.is_explicitly_not_verified(
                                     &ProverOptions::get(self.fun_target.global_env()).verify_scope,
                                 );
                             let mut fun_name = boogie_function_name(&callee_env, inst, &[]);
                             // Helper function to check whether the idx corresponds to a bitwise operation
-                            let compute_flag = |idx: TempIndex| {
-                                targeted
-                                    && fun_verified
-                                    && *global_state
-                                        .get_temp_index_oper(
-                                            caller_mid,
-                                            caller_fid,
-                                            idx,
-                                            baseline_flag,
-                                        )
-                                        .unwrap()
-                                        == Bitwise
-                            };
+                            let compute_flag =
+                                |idx: TempIndex| targeted && fun_verified && self.temp_bv_flag(idx);
                             let instrument_bv2int =
                                 |idx: TempIndex, args_str_vec: &mut Vec<String>| {
                                     let local_ty_srcs_1 = self.get_local_type(idx);
@@ -6687,7 +6744,7 @@ impl FunctionTranslator<'_> {
                         let num_oper = global_state
                             .get_temp_index_oper(mid, fid, dests[0], baseline_flag)
                             .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.bv_flag(num_oper, ty);
                         let var_str = str_local(dests[0]);
                         let temp_str = boogie_temp(env, ty.skip_reference(), 0, bv_flag);
                         emitln!(writer, "havoc {};", temp_str);
@@ -6717,11 +6774,7 @@ impl FunctionTranslator<'_> {
                             _ => unreachable!(),
                         };
 
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, src, baseline_flag)
-                            .unwrap();
-
-                        if self.bv_flag(num_oper) {
+                        if self.temp_bv_flag(src) {
                             let src_type = self.get_local_type(src);
                             let src_base = boogie_num_type_base(
                                 self.parent.env,
@@ -6737,6 +6790,27 @@ impl FunctionTranslator<'_> {
                                 target_base,
                                 str_local(src)
                             );
+                        } else if self.temp_bv_flag(dest) {
+                            // Source renders as int (e.g. a signed value whose bv
+                            // classification is clamped) while the destination stays a
+                            // bitvector: cast in the int domain, then convert the
+                            // in-range result.
+                            let int_temp = boogie_temp(env, &self.get_local_type(dest), 0, false);
+                            emitln!(
+                                writer,
+                                "call {} := $Cast{}{}({});",
+                                int_temp,
+                                target_kind,
+                                target_base,
+                                str_local(src)
+                            );
+                            emitln!(
+                                writer,
+                                "{} := $int2bv.{}({});",
+                                str_local(dest),
+                                target_base,
+                                int_temp
+                            );
                         } else {
                             emitln!(
                                 writer,
@@ -6760,10 +6834,7 @@ impl FunctionTranslator<'_> {
                             CastI256 => ("I", "256"),
                             _ => unreachable!(),
                         };
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, src, baseline_flag)
-                            .unwrap();
-                        if self.bv_flag(num_oper) {
+                        if self.temp_bv_flag(src) {
                             // src is a bitvector: convert it to int and then do cast
                             let src_type = self.get_local_type(src);
                             let src_base = boogie_num_type_base(
@@ -6813,14 +6884,11 @@ impl FunctionTranslator<'_> {
                         } else {
                             ""
                         };
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, dest, baseline_flag)
-                            .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
-
-                        let suffix = boogie_int_suffix(&self.get_local_type(dest), bv_flag);
+                        let dest_ty = self.get_local_type(dest);
+                        let bv_flag = self.temp_bv_flag(dest);
+                        let suffix = boogie_int_suffix(&dest_ty, bv_flag);
                         // Quirk: U8 omits the _unchecked suffix even when set.
-                        let add_type = match &self.get_local_type(dest) {
+                        let add_type = match &dest_ty {
                             Type::Primitive(PrimitiveType::U8) => suffix,
                             _ => format!("{}{}", suffix, unchecked),
                         };
@@ -6837,10 +6905,7 @@ impl FunctionTranslator<'_> {
                         let dest = dests[0];
                         let op1 = srcs[0];
                         let op2 = srcs[1];
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, dest, baseline_flag)
-                            .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.temp_bv_flag(dest);
                         let sub_type = boogie_int_suffix(&self.get_local_type(dest), bv_flag);
                         emitln!(
                             writer,
@@ -6855,10 +6920,7 @@ impl FunctionTranslator<'_> {
                         let dest = dests[0];
                         let op1 = srcs[0];
                         let op2 = srcs[1];
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, dest, baseline_flag)
-                            .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.temp_bv_flag(dest);
                         let mul_type = boogie_int_suffix(&self.get_local_type(dest), bv_flag);
                         emitln!(
                             writer,
@@ -6873,10 +6935,7 @@ impl FunctionTranslator<'_> {
                         let dest = dests[0];
                         let op1 = srcs[0];
                         let op2 = srcs[1];
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, dest, baseline_flag)
-                            .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.temp_bv_flag(dest);
                         let div_type = boogie_int_suffix(&self.get_local_type(dest), bv_flag);
                         emitln!(
                             writer,
@@ -6891,10 +6950,7 @@ impl FunctionTranslator<'_> {
                         let dest = dests[0];
                         let op1 = srcs[0];
                         let op2 = srcs[1];
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, dest, baseline_flag)
-                            .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.temp_bv_flag(dest);
                         let mod_type = boogie_int_suffix(&self.get_local_type(dest), bv_flag);
                         emitln!(
                             writer,
@@ -6908,10 +6964,7 @@ impl FunctionTranslator<'_> {
                     Negate => {
                         let dest = dests[0];
                         let op = srcs[0];
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, dest, baseline_flag)
-                            .unwrap();
-                        if self.bv_flag(num_oper) {
+                        if self.temp_bv_flag(dest) {
                             bv_op_not_enabled_error!(bytecode, fun_target, env, loc);
                         }
                         let neg_type = match &self.get_local_type(dest) {
@@ -6947,10 +7000,7 @@ impl FunctionTranslator<'_> {
                         let op1 = srcs[0];
                         let op2 = srcs[1];
                         let sh_oper_str = if oper == &Shl { "Shl" } else { "Shr" };
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, dest, baseline_flag)
-                            .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.temp_bv_flag(dest);
                         if bv_flag {
                             let target_type = match &self.get_local_type(dest) {
                                 Type::Primitive(PrimitiveType::U8) => "Bv8",
@@ -7025,10 +7075,7 @@ impl FunctionTranslator<'_> {
                         let op1 = srcs[0];
                         let op2 = srcs[1];
                         let make_comparison = |comp_oper: &str, op1, op2, dest| {
-                            let num_oper = global_state
-                                .get_temp_index_oper(mid, fid, op1, baseline_flag)
-                                .unwrap();
-                            let bv_flag = self.bv_flag(num_oper);
+                            let bv_flag = self.temp_bv_flag(op1);
                             let lt_type = if bv_flag {
                                 match &self.get_local_type(op1) {
                                     Type::Primitive(PrimitiveType::U8) => "Bv8".to_string(),
@@ -7037,8 +7084,17 @@ impl FunctionTranslator<'_> {
                                     Type::Primitive(PrimitiveType::U64) => "Bv64".to_string(),
                                     Type::Primitive(PrimitiveType::U128) => "Bv128".to_string(),
                                     Type::Primitive(PrimitiveType::U256) => "Bv256".to_string(),
-                                    Type::Primitive(_)
-                                    | Type::Tuple(_)
+                                    // `bv_flag` is clamped for signed operands, so this arm is
+                                    // unreachable unless a new path marks them Bitwise again;
+                                    // degrade to a diagnostic instead of crashing.
+                                    Type::Primitive(_) => {
+                                        env.error(
+                                            &self.fun_target.get_bytecode_loc(attr_id),
+                                            "comparison operand cannot be turned into bit vector",
+                                        );
+                                        "".to_string()
+                                    },
+                                    Type::Tuple(_)
                                     | Type::Vector(_)
                                     | Type::Struct(_, _, _)
                                     | Type::TypeParameter(_)
@@ -7100,10 +7156,7 @@ impl FunctionTranslator<'_> {
                         let dest = dests[0];
                         let op1 = srcs[0];
                         let op2 = srcs[1];
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, op1, baseline_flag)
-                            .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.temp_bv_flag(op1);
                         let oper = boogie_equality_for_type(
                             env,
                             oper == &Eq,
@@ -7150,11 +7203,11 @@ impl FunctionTranslator<'_> {
                                 let num_oper_1 = global_state
                                     .get_temp_index_oper(mid, fid, op1, baseline_flag)
                                     .unwrap();
-                                let op1_bv_flag = self.bv_flag(num_oper_1);
+                                let op1_bv_flag = self.bv_flag(num_oper_1, op1_ty);
                                 let num_oper_2 = global_state
                                     .get_temp_index_oper(mid, fid, op2, baseline_flag)
                                     .unwrap();
-                                let op2_bv_flag = self.bv_flag(num_oper_2);
+                                let op2_bv_flag = self.bv_flag(num_oper_2, op2_ty);
                                 let op1_str = if !op1_bv_flag {
                                     format!(
                                         "$int2bv.{}({})",
@@ -7206,23 +7259,19 @@ impl FunctionTranslator<'_> {
                     },
                     Drop | Release => {},
                     TraceLocal(idx) => {
-                        let num_oper = global_state
-                            .get_temp_index_oper(mid, fid, srcs[0], baseline_flag)
-                            .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.temp_bv_flag(srcs[0]);
                         self.track_local(*idx, srcs[0], bv_flag);
                     },
                     TraceReturn(i) => {
-                        let oper_map = global_state.get_ret_map();
-                        let bv_flag = self.bv_flag_from_map(&srcs[0], oper_map);
+                        // The traced value is the TEMP: its rendering (not the
+                        // return slot's classification) decides the debug
+                        // temp's name, matching `compute_needed_temps`.
+                        let bv_flag = self.temp_bv_flag(srcs[0]);
                         self.track_return(*i, srcs[0], bv_flag);
                     },
                     TraceAbort => self.track_abort(&str_local(srcs[0])),
                     TraceExp(kind, node_id) => {
-                        let bv_flag = *global_state
-                            .get_temp_index_oper(mid, fid, srcs[0], baseline_flag)
-                            .unwrap()
-                            == Bitwise;
+                        let bv_flag = self.temp_bv_flag(srcs[0]);
                         self.track_exp(*kind, *node_id, srcs[0], bv_flag)
                     },
                     EmitEvent => {
@@ -7256,10 +7305,7 @@ impl FunctionTranslator<'_> {
                     writer.indent();
                     *last_tracked_loc = None;
                     self.track_loc(last_tracked_loc, &loc);
-                    let num_oper_code = global_state
-                        .get_temp_index_oper(mid, fid, *code, baseline_flag)
-                        .unwrap();
-                    let bv2int_str = if *num_oper_code == Bitwise {
+                    let bv2int_str = if self.temp_bv_flag(*code) {
                         format!(
                             "$int2bv.{}($abort_code)",
                             boogie_num_type_base(
@@ -7281,10 +7327,7 @@ impl FunctionTranslator<'_> {
                 }
             },
             Abort(_, src, _) => {
-                let num_oper_code = global_state
-                    .get_temp_index_oper(mid, fid, *src, baseline_flag)
-                    .unwrap();
-                let int2bv_str = if *num_oper_code == Bitwise {
+                let int2bv_str = if self.temp_bv_flag(*src) {
                     format!(
                         "$bv2int.{}({})",
                         boogie_num_type_base(
@@ -7571,6 +7614,8 @@ impl FunctionTranslator<'_> {
                                 .get_extension::<GlobalNumberOperationState>()
                                 .expect("global number operation state"),
                             &field_env,
+                            self.parent.env,
+                            &field_ty,
                         ),
                     );
                     let update_fun = if variant.is_none() {
@@ -7935,37 +7980,56 @@ impl FunctionTranslator<'_> {
             .global_env()
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number operation state");
-        let ret_oper_map = &global_state.get_ret_map();
         let mid = fun_target.func_env.module_env.get_id();
         let fid = fun_target.func_env.get_id();
 
         for bc in &fun_target.data.code {
             match bc {
                 Call(_, dests, oper, srcs, ..) => match oper {
-                    TraceExp(_, id) => {
-                        let ty = &self.inst(&env.get_node_type(*id));
-                        let bv_flag = global_state.get_node_num_oper(*id) == Bitwise;
+                    TraceExp(..) => {
+                        // Mirror the emission site (`track_exp`): both the
+                        // type and the flag derive from the traced LOCAL,
+                        // not the exp node — node types can be generalized
+                        // `num` where the local is concrete, and the node
+                        // classification can disagree with the local's.
+                        let ty = &self.get_local_type(srcs[0]);
+                        let num_oper = &global_state
+                            .get_temp_index_oper(mid, fid, srcs[0], baseline_flag)
+                            .unwrap();
+                        let bv_flag = self.bv_flag(num_oper, ty);
                         need(ty, bv_flag, 1)
                     },
-                    TraceReturn(idx) => {
-                        let ty = &self.inst(&fun_target.get_return_type(*idx));
-                        let bv_flag = self.bv_flag_from_map(idx, ret_oper_map);
+                    TraceReturn(_) => {
+                        // Mirror the emission site (`track_return`): type and
+                        // flag derive from the traced temp.
+                        let ty = &self.get_local_type(srcs[0]);
+                        let num_oper = &global_state
+                            .get_temp_index_oper(mid, fid, srcs[0], baseline_flag)
+                            .unwrap();
+                        let bv_flag = self.bv_flag(num_oper, ty);
                         need(ty, bv_flag, 1)
                     },
                     TraceLocal(_) => {
                         let ty = &self.get_local_type(srcs[0]);
                         let num_oper = &global_state
                             .get_temp_index_oper(mid, fid, srcs[0], baseline_flag)
                             .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.bv_flag(num_oper, ty);
                         need(ty, bv_flag, 1)
                     },
+                    CastU8 | CastU16 | CastU32 | CastU64 | CastU128 | CastU256 => {
+                        // An int-rendered source (clamped signed) cast into a
+                        // bv-classified dest goes through an int scratch temp.
+                        if self.temp_bv_flag(dests[0]) && !self.temp_bv_flag(srcs[0]) {
+                            need(&self.get_local_type(dests[0]), false, 1)
+                        }
+                    },
                     Havoc(HavocKind::MutationValue) => {
                         let ty = &self.get_local_type(dests[0]);
                         let num_oper = &global_state
                             .get_temp_index_oper(mid, fid, dests[0], baseline_flag)
                             .unwrap();
-                        let bv_flag = self.bv_flag(num_oper);
+                        let bv_flag = self.bv_flag(num_oper, ty);
                         need(ty, bv_flag, 1)
                     },
                     Pack(pack_mid, pack_sid, pack_inst)
@@ -7987,9 +8051,11 @@ impl FunctionTranslator<'_> {
                     _ => {},
                 },
                 Prop(_, PropKind::Modifies, exp) => {
-                    let bv_flag = global_state.get_node_num_oper(exp.node_id()) == Bitwise;
+                    let ty = self.inst(&env.get_node_type(exp.node_id()));
+                    let bv_flag =
+                        bv_flag_for_type(env, &global_state.get_node_num_oper(exp.node_id()), &ty);
                     need(&BOOL_TYPE, false, 1);
-                    need(&self.inst(&env.get_node_type(exp.node_id())), bv_flag, 1)
+                    need(&ty, bv_flag, 1)
                 },
                 _ => {},
             }
@@ -8057,15 +8123,16 @@ impl FunctionTranslator<'_> {
         };
         for field in &fields {
             let field_ty = field.get_type().instantiate(inst);
-            if let Type::Fun(params, results, abilities) = &field_ty {
+            if let Type::Fun(_, _, abilities) = &field_ty {
                 if abilities.has_store() {
-                    // Normalize to check against MonoInfo (same as mono_analysis::normalize_fun_ty)
-                    let normalized = Type::Fun(
-                        Box::new(Type::tuple(params.clone().flatten())),
-                        Box::new(Type::tuple(results.clone().flatten())),
-                        AbilitySet::EMPTY,
+                    // Same canonical keys as the registration; see
+                    // `boogie_field_identity_constraint`.
+                    let normalized = field_ty.clone().normalize_fun();
+                    let struct_qid = struct_env.get_qualified_id().instantiate(
+                        inst.iter()
+                            .map(|t| t.clone().normalize_nested_funs())
+                            .collect(),
                     );
-                    let struct_qid = struct_env.get_qualified_id().instantiate(inst.clone());
                     // Check if this field has a StructFieldInfo entry
                     if let Some(field_infos) = mono_info.fun_struct_field_infos.get(&normalized) {
                         let has_entry = field_infos.iter().any(|info| {
```

### third_party/move/move-prover/boogie-backend/src/lib.rs
```diff
@@ -7,7 +7,8 @@
 
 use crate::{
     boogie_helpers::{
-        boogie_field_sel, boogie_module_name, boogie_num_type_base, boogie_type, boogie_type_suffix,
+        boogie_field_sel, boogie_module_name, boogie_num_type_base, boogie_type,
+        boogie_type_suffix, type_contains_signed_int, type_contains_widthless_num,
     },
     bytecode_translator::has_native_equality,
     options::{BoogieOptions, VectorTheory},
@@ -293,15 +294,12 @@ pub fn add_prelude(
         bv_instances = vec![];
     }
 
-    // Signed integers are always Boogie `int`; they have no bv rendering. A bv
-    // rendering recurses into contained types (vector elements, type arguments),
-    // so a type is bv-renderable only when its whole containment closure is free
-    // of signed ints.
-    let contains_signed_int = |ty: &Type| {
-        ty.get_all_contained_types_with_skip_reference(env)
-            .iter()
-            .any(|t| t.is_signed_int())
-    };
+    // Signed integers and widthless `num` are always Boogie `int`; they have
+    // no bv rendering. A bv rendering recurses into contained types (vector
+    // elements, type arguments), so a type is bv-renderable only when its
+    // whole containment closure is free of both.
+    let never_renders_bv =
+        |ty: &Type| type_contains_signed_int(env, ty) || type_contains_widthless_num(env, ty);
 
     let mut all_types = mono_info
         .all_types
@@ -314,7 +312,7 @@ pub fn add_prelude(
     let mut bv_all_types = mono_info
         .all_types
         .iter()
-        .filter(|ty| ty.can_be_type_argument() && !contains_signed_int(ty))
+        .filter(|ty| ty.can_be_type_argument() && !never_renders_bv(ty))
         .map(|ty| TypeInfo::new(env, options, ty, true))
         .filter(|ty_info| !all_types.contains(ty_info))
         .collect::<BTreeSet<_>>()
@@ -358,26 +356,43 @@ pub fn add_prelude(
         .collect_vec();
     // If not using cvc5, generate vector functions for bv types
     if !options.use_cvc5 {
-        // Exclude signed-containing element/value types from bv twins (same
-        // guard as `bv_all_types` above).
+        // Exclude element/value types with no bv rendering from bv twins
+        // (same guard as `bv_all_types` above).
         let mut bv_vec_instances = mono_info
             .vec_inst
             .iter()
-            .filter(|ty| !contains_signed_int(ty))
+            .filter(|ty| !never_renders_bv(ty))
             .map(|ty| TypeInfo::new(env, options, ty, true))
             .filter(|ty_info| !vec_instances.contains(ty_info))
             .collect::<BTreeSet<_>>()
             .into_iter()
             .collect_vec();
+        // Twins are per-instance: each instantiation whose value type has a
+        // bv rendering gets a bv twin (same predicate as the rendering
+        // guard and the vec twins — nested unsigned values like
+        // `vector<u8>` included), independently of sibling instantiations
+        // of the same map type. Instances whose bv rendering coincides
+        // with the plain one are dropped by the dedup filter below.
         let mut bv_table_instances = mono_info
             .table_inst
             .iter()
-            .map(|(qid, ty_args)| {
-                let v_ty = ty_args.iter().map(|(_, vty)| vty).collect_vec();
-                let bv_flag = v_ty.iter().all(|ty| {
-                    ty.skip_reference().is_number() && !ty.skip_reference().is_signed_int()
-                });
-                MapImpl::new(env, options, *qid, ty_args, bv_flag)
+            .filter_map(|(qid, ty_args)| {
+                let bv_ty_args = ty_args
+                    .iter()
+                    .filter(|(_, vty)| {
+                        let vty = vty.skip_reference();
+                        // A twin exists only where the value's bv rendering
+                        // is legal and actually differs from the plain one
+                        // (struct/bool values render identically and would
+                        // duplicate the base instance).
+                        !never_renders_bv(vty)
+                            && boogie_type_suffix(env, vty, true)
+                                != boogie_type_suffix(env, vty, false)
+                    })
+                    .cloned()
+                    .collect::<BTreeSet<_>>();
+                (!bv_ty_args.is_empty())
+                    .then(|| MapImpl::new(env, options, *qid, &bv_ty_args, true))
             })
             .filter(|map_impl| !table_instances.contains(map_impl))
             .collect_vec();
@@ -455,7 +470,7 @@ pub fn add_prelude(
                 insts.iter().map(|inst| {
                     inst.iter()
                         .flat_map(|i| i.get_all_contained_types_with_skip_reference(env))
-                        .filter(|i| !bv_flag || !contains_signed_int(i))
+                        .filter(|i| !bv_flag || !never_renders_bv(i))
                         .map(|i| (i.clone(), TypeInfo::new(env, options, &i, bv_flag)))
                         .collect::<Vec<_>>()
                 })
```

### third_party/move/move-prover/boogie-backend/src/spec_translator.rs
```diff
@@ -14,7 +14,7 @@ use crate::{
         boogie_reflection_type_info, boogie_reflection_type_is_struct, boogie_reflection_type_name,
         boogie_resource_memory_name, boogie_spec_fun_name, boogie_spec_var_name,
         boogie_struct_name, boogie_struct_variant_name, boogie_type, boogie_type_suffix,
-        boogie_value_blob, boogie_variant_field_update, boogie_well_formed_expr,
+        boogie_value_blob, boogie_variant_field_update, boogie_well_formed_expr, bv_flag_for_type,
         compute_evaluator_memory_union, MAX_TUPLE_SIZE,
     },
     options::BoogieOptions,
@@ -99,6 +99,14 @@ pub struct SpecTranslator<'env> {
     /// The qualified instantiated ID of the function currently being verified, if any.
     /// Used to resolve behavioral predicates on function-typed parameters.
     current_fun_qid: RefCell<Option<QualifiedInstId<FunId>>>,
+    /// Whether the current function translation is the baseline variant;
+    /// selects the per-variant temporary classification map. `None` outside
+    /// per-function translation (e.g. evaluator/axiom contexts).
+    current_fun_baseline: RefCell<Option<bool>>,
+    /// Local (temporary) types of the current function target; the
+    /// authoritative type source for temporary renderings (exp nodes can
+    /// carry generalized `num` where the local is concrete, and vice versa).
+    current_fun_local_types: RefCell<Option<Vec<Type>>>,
     /// Map from state labels to their defining operation info.
     /// Used to resolve memory references at labeled states.
     label_info: RefCell<BTreeMap<MemoryLabel, LabelInfo>>,
@@ -173,6 +181,8 @@ impl<'env> SpecTranslator<'env> {
             lifted_choice_infos: Default::default(),
             arbitrary_values: Default::default(),
             current_fun_qid: RefCell::new(None),
+            current_fun_baseline: RefCell::new(None),
+            current_fun_local_types: RefCell::new(None),
             label_info: RefCell::new(BTreeMap::new()),
             declared_mem_names: RefCell::new(BTreeSet::new()),
             value_state_vars: RefCell::new(BTreeMap::new()),
@@ -181,6 +191,22 @@ impl<'env> SpecTranslator<'env> {
     }
 
     /// Sets the current function being verified, for resolving behavioral predicate memory.
+    pub fn set_current_fun_baseline(&self, baseline: bool) {
+        *self.current_fun_baseline.borrow_mut() = Some(baseline);
+    }
+
+    pub fn clear_current_fun_baseline(&self) {
+        *self.current_fun_baseline.borrow_mut() = None;
+    }
+
+    pub fn set_current_fun_local_types(&self, local_types: Vec<Type>) {
+        *self.current_fun_local_types.borrow_mut() = Some(local_types);
+    }
+
+    pub fn clear_current_fun_local_types(&self) {
+        *self.current_fun_local_types.borrow_mut() = None;
+    }
+
     pub fn set_current_fun_qid(&self, fun_qid: QualifiedInstId<FunId>) {
         *self.current_fun_qid.borrow_mut() = Some(fun_qid);
     }
@@ -554,7 +580,7 @@ impl SpecTranslator<'_> {
                 .get(&(module_env.get_id(), id))
                 .unwrap()
                 .1;
-            ret_oper_map[0] == Bitwise
+            bv_flag_for_type(self.env, &ret_oper_map[0], &self.inst(&fun.result_type))
         } else {
             false
         };
@@ -629,12 +655,15 @@ impl SpecTranslator<'_> {
                     .spec_fun_operation_map
                     .contains_key(&(module_env.get_id(), id))
                 {
-                    global_state
-                        .spec_fun_operation_map
-                        .get(&(module_env.get_id(), id))
-                        .unwrap()
-                        .0[i]
-                        == Bitwise
+                    bv_flag_for_type(
+                        self.env,
+                        &global_state
+                            .spec_fun_operation_map
+                            .get(&(module_env.get_id(), id))
+                            .unwrap()
+                            .0[i],
+                        &self.inst(ty),
+                    )
                 } else {
                     false
                 };
@@ -1193,6 +1222,20 @@ impl SpecTranslator<'_> {
         self.inst(&self.env.get_node_type(id))
     }
 
+    /// Return whether the value of the given expression node renders as a
+    /// bitvector, pairing the node's number-operation classification with its
+    /// instantiated type. The classification is checked before the type
+    /// fetch: `Bitwise` nodes are rare, and the instantiation is only needed
+    /// for them.
+    fn node_bv_flag(&self, id: NodeId) -> bool {
+        let global_state = &self
+            .env
+            .get_extension::<GlobalNumberOperationState>()
+            .expect("global number operation state");
+        let num_oper = global_state.get_node_num_oper(id);
+        num_oper == Bitwise && bv_flag_for_type(self.env, &num_oper, &self.get_node_type(id))
+    }
+
     fn get_node_instantiation(&self, id: NodeId) -> Vec<Type> {
         self.inst_slice(&self.env.get_node_instantiation(id))
     }
@@ -1283,19 +1326,10 @@ impl SpecTranslator<'_> {
     }
 
     fn translate_value(&self, node_id: NodeId, val: &Value) {
-        let global_state = &self
-            .env
-            .get_extension::<GlobalNumberOperationState>()
-            .expect("global number operation state");
-        let num_oper = global_state.get_node_num_oper(node_id);
         let mut suffix = "".to_string();
-        let bv_flag = num_oper == Bitwise;
+        let bv_flag = self.node_bv_flag(node_id);
         if bv_flag {
-            suffix = boogie_type(
-                self.env,
-                self.env.get_node_type(node_id).skip_reference(),
-                true,
-            );
+            suffix = boogie_type(self.env, self.get_node_type(node_id).skip_reference(), true);
         }
         match val {
             Value::Address(addr) => emit!(self.writer, "{}", boogie_address(self.env, addr)),
@@ -1556,9 +1590,14 @@ impl SpecTranslator<'_> {
             Operation::Not => self.translate_logical_unary_op("!", args),
             Operation::Cast => self.translate_cast(node_id, args),
             Operation::Int2Bv => {
-                let exp_arith_flag = global_state.get_node_num_oper(args[0].node_id()) != Bitwise;
-                if exp_arith_flag {
-                    let arg_node_type = self.env.get_node_type(args[0].node_id());
+                // Convert only when the argument renders as int AND this node
+                // renders as a bitvector; under the signed clamp both render
+                // as int and the conversion is the identity. The base comes
+                // from the instantiated type (a raw node type can still be a
+                // type parameter, which has no numeric base).
+                let wrap = self.node_bv_flag(node_id) && !self.node_bv_flag(args[0].node_id());
+                if wrap {
+                    let arg_node_type = self.get_node_type(args[0].node_id());
                     let literal = boogie_num_type_base(
                         self.env,
                         Some(self.env.get_node_loc(args[0].node_id())),
@@ -1568,14 +1607,17 @@ impl SpecTranslator<'_> {
                     emit!(self.writer, "$int2bv.{}(", literal);
                 }
                 self.translate_exp(&args[0]);
-                if exp_arith_flag {
+                if wrap {
                     emit!(self.writer, ")");
                 }
             },
             Operation::Bv2Int => {
-                let exp_bv_flag = global_state.get_node_num_oper(args[0].node_id()) == Bitwise;
-                if exp_bv_flag {
-                    let arg_node_type = self.env.get_node_type(args[0].node_id());
+                // See `Int2Bv`: convert only when the argument renders as a
+                // bitvector; under the signed clamp it renders as int and the
+                // conversion is the identity.
+                let wrap = self.node_bv_flag(args[0].node_id());
+                if wrap {
+                    let arg_node_type = self.get_node_type(args[0].node_id());
                     let literal = boogie_num_type_base(
                         self.env,
                         Some(self.env.get_node_loc(args[0].node_id())),
@@ -1585,7 +1627,7 @@ impl SpecTranslator<'_> {
                     emit!(self.writer, "$bv2int.{}(", literal);
                 }
                 self.translate_exp(&args[0]);
-                if exp_bv_flag {
+                if wrap {
                     emit!(self.writer, ")");
                 }
             },
@@ -1658,8 +1700,9 @@ impl SpecTranslator<'_> {
                 emit!(self.writer, &")".repeat(count));
             },
             Operation::Abort(_) => {
-                let exp_bv_flag = global_state.get_node_num_oper(node_id) == Bitwise;
                 let ty = self.get_node_type(node_id);
+                let exp_bv_flag =
+                    bv_flag_for_type(self.env, &global_state.get_node_num_oper(node_id), &ty);
                 // Track this arbitrary value for later function declaration
                 self.arbitrary_values.borrow_mut().insert((
                     node_id,
@@ -2580,17 +2623,14 @@ impl SpecTranslator<'_> {
         }
 
         // regular path
-        let global_state = &self
-            .env
-            .get_extension::<GlobalNumberOperationState>()
-            .expect("global number operation state");
         let is_vector_table_cmp_module =
             module_env.is_std_vector() || module_env.is_table() || module_env.is_cmp();
-        let bv_flag = if is_vector_table_cmp_module && !args.is_empty() {
-            global_state.get_node_num_oper(args[0].node_id()) == Bitwise
+        let flag_node = if is_vector_table_cmp_module && !args.is_empty() {
+            args[0].node_id()
         } else {
-            global_state.get_node_num_oper(node_id) == Bitwise
+            node_id
         };
+        let bv_flag = self.node_bv_flag(flag_node);
         let name = boogie_spec_fun_name(module_env, fun_id, inst, bv_flag);
         emit!(self.writer, "{}(", name);
         let mut first = true;
@@ -2732,7 +2772,8 @@ impl SpecTranslator<'_> {
                 } else {
                     let arg = arg_iter.next().expect("missing arg for non-mut param");
                     maybe_comma();
-                    self.translate_exp(arg);
+                    // Instantiated type, as in the non-doubled branch below.
+                    self.translate_spec_fun_arg(arg, &ty.instantiate(inst));
                 }
             }
         } else {
@@ -2769,13 +2810,49 @@ impl SpecTranslator<'_> {
                     }
                     mut_idx += 1;
                 } else {
-                    self.translate_exp(arg);
+                    // The `num`-boundary check must see the instantiated
+                    // parameter type: a generic parameter instantiated at
+                    // `num` converts like a declared `num` parameter.
+                    self.translate_spec_fun_arg(arg, &ty.instantiate(inst));
                 }
             }
         }
         emit!(self.writer, ")");
     }
 
+    /// Emit a spec fun argument for a by-value parameter, converting at the
+    /// representational boundary of widthless `num` parameters: a `num`
+    /// parameter always renders as int, while a bitwise-classified argument
+    /// renders as a bitvector (the number-operation analysis clamps `num`
+    /// parameter slots to `Arithmetic`, so the two sides legitimately
+    /// disagree exactly here). Other parameter types keep the propagated
+    /// classification and need no conversion (see the comment at the
+    /// argument-emission site).
+    fn translate_spec_fun_arg(&self, arg: &Exp, param_ty: &Type) {
+        // The operand's own rendering is authoritative (a schema binding
+        // can substitute a bitvector-rendered temporary under a node
+        // rewritten to `num`), and the conversion width comes from the
+        // same type that decided that rendering.
+        let (arg_is_bv, arg_ty) = self.operand_rendering(arg);
+        if matches!(
+            param_ty.skip_reference(),
+            Type::Primitive(PrimitiveType::Num)
+        ) && arg_is_bv
+        {
+            let base = boogie_num_type_base(
+                self.env,
+                Some(self.env.get_node_loc(arg.node_id())),
+                &arg_ty,
+                false,
+            );
+            emit!(self.writer, "$bv2int.{}(", base);
+            self.translate_exp(arg);
+            emit!(self.writer, ")");
+        } else {
+            self.translate_exp(arg);
+        }
+    }
+
     fn try_translate_spec_fun_reflection_call(
         &self,
         module_env: &ModuleEnv,
@@ -2907,8 +2984,8 @@ impl SpecTranslator<'_> {
             .env
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number operation state");
-        let exp_bv_flag = global_state.get_node_num_oper(node_id) == Bitwise;
         let ty = self.get_node_type(node_id);
+        let exp_bv_flag = bv_flag_for_type(self.env, &global_state.get_node_num_oper(node_id), &ty);
         // Track this arbitrary value for later function declaration
         self.arbitrary_values
             .borrow_mut()
@@ -3548,21 +3625,28 @@ impl SpecTranslator<'_> {
             let var_name_str = self.env.symbol_pool().string(var_name);
             let quant_ty = self.get_node_type(range.node_id());
             let num_oper = global_state.get_node_num_oper(range.node_id());
-            let bv_flag = num_oper == Bitwise;
-            let ty_str = |ty: _| boogie_type(self.env, ty, bv_flag);
+            let ty_str =
+                |ty: &Type| boogie_type(self.env, ty, bv_flag_for_type(self.env, &num_oper, ty));
             match quant_ty.skip_reference() {
                 Type::TypeDomain(ty) => {
                     emit!(self.writer, "{}{}: {}", comma, var_name_str, ty_str(ty));
                 },
                 Type::Struct(mid, sid, targs) => {
                     let struct_env = self.env.get_struct(mid.qualified(*sid));
                     if struct_env.is_intrinsic_of(INTRINSIC_TYPE_MAP) {
+                        // Clamp by the map type, matching the `$EncodeKey`
+                        // suffix in the range constraint below: both sides of
+                        // the pair must agree on the key rendering.
                         emit!(
                             self.writer,
                             "{}{}: {}",
                             comma,
                             var_name_str,
-                            ty_str(&targs[0])
+                            boogie_type(
+                                self.env,
+                                &targs[0],
+                                bv_flag_for_type(self.env, &num_oper, &quant_ty)
+                            )
                         );
                     } else {
                         panic!("unexpected type");
@@ -3712,7 +3796,14 @@ impl SpecTranslator<'_> {
                             separator,
                             range_tmps.get(&var_name).unwrap(),
                             unwrap,
-                            boogie_type_suffix(self.env, &targs[0], num_oper == Bitwise),
+                            // Clamp by the map type: its containment (including
+                            // the value type) decides whether bv key encodings
+                            // exist for it.
+                            boogie_type_suffix(
+                                self.env,
+                                &targs[0],
+                                bv_flag_for_type(self.env, &num_oper, &quant_ty)
+                            ),
                             var_name_str,
                         );
                     } else {
@@ -3896,10 +3987,27 @@ impl SpecTranslator<'_> {
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number operation state");
         let num_oper = global_state.get_node_num_oper(args[0].node_id());
-        // `Num` is a polymorphic spec-only integer type (e.g. quantifier range variables);
-        // it cannot be a bitvector regardless of the number operation classification.
-        let bv_flag = num_oper == Bitwise && !matches!(ty, Type::Primitive(PrimitiveType::Num));
+        // (`Num` never carries a bv rendering; `bv_flag_for_type` clamps it.)
+        let bv_flag = bv_flag_for_type(self.env, &num_oper, ty);
         let suffix = boogie_type_suffix(self.env, ty, bv_flag);
+        if ty.skip_reference().is_number() {
+            let op_base = if bv_flag {
+                boogie_num_type_base(
+                    self.env,
+                    Some(self.env.get_node_loc(args[0].node_id())),
+                    ty,
+                    false,
+                )
+            } else {
+                String::new()
+            };
+            emit!(self.writer, "{}'{}'(", boogie_val_fun, suffix);
+            self.translate_op_operand(&args[0], bv_flag, &op_base);
+            emit!(self.writer, ", ");
+            self.translate_op_operand(&args[1], bv_flag, &op_base);
+            emit!(self.writer, ")");
+            return;
+        }
         emit!(self.writer, "{}'{}'(", boogie_val_fun, suffix);
         self.translate_exp(&args[0]);
         emit!(self.writer, ", ");
@@ -3941,30 +4049,110 @@ impl SpecTranslator<'_> {
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number operation state");
         let num_oper = global_state.get_node_num_oper(args[0].node_id());
-        if num_oper == Bitwise {
+        let ty0 = self.get_node_type(args[0].node_id());
+        if bv_flag_for_type(self.env, &num_oper, &ty0) {
             let oper_base = boogie_num_type_base(
                 self.env,
                 Some(self.env.get_node_loc(args[0].node_id())),
-                &self.env.get_node_type(args[0].node_id()),
+                &ty0,
                 true,
             );
+            let conv_base = boogie_num_type_base(
+                self.env,
+                Some(self.env.get_node_loc(args[0].node_id())),
+                &ty0,
+                false,
+            );
             emit!(self.writer, "${}'{}'(", bv_op, oper_base);
-            self.translate_seq(args.iter(), ", ", |e| self.translate_exp(e));
+            self.translate_seq(args.iter(), ", ", |e| {
+                self.translate_op_operand(e, true, &conv_base)
+            });
             emit!(self.writer, ")");
-        } else if let Some(helper) = signed_helper.filter(|_| {
-            self.env
-                .get_node_type(args[0].node_id())
-                .skip_reference()
-                .is_signed_int()
-        }) {
+        } else if let Some(helper) = signed_helper.filter(|_| ty0.skip_reference().is_signed_int())
+        {
             emit!(self.writer, "{}(", helper);
-            self.translate_seq(args.iter(), ", ", |e| self.translate_exp(e));
+            self.translate_seq(args.iter(), ", ", |e| {
+                self.translate_op_operand(e, false, "")
+            });
             emit!(self.writer, ")");
         } else {
             emit!(self.writer, "(");
-            self.translate_exp(&args[0]);
+            self.translate_op_operand(&args[0], false, "");
             emit!(self.writer, " {} ", boogie_op);
-            self.translate_exp(&args[1]);
+            self.translate_op_operand(&args[1], false, "");
+            emit!(self.writer, ")");
+        }
+    }
+
+    /// Rendering flag for an operand expression, and the type that decided
+    /// it. For temporaries the per-function local declaration is
+    /// authoritative: shared spec-node classification (schema conditions
+    /// instantiated at many call sites) can disagree with the
+    /// procedure-local rendering, and the exp node type can be generalized
+    /// `num` where the local is concrete (and vice versa). Falls back to the
+    /// node classification and node type outside per-function translation.
+    fn operand_rendering(&self, e: &Exp) -> (bool, Type) {
+        if let ExpData::Temporary(_, idx) = e.as_ref() {
+            if let (Some(fun_qid), Some(baseline), Some(local_types)) = (
+                self.current_fun_qid.borrow().as_ref(),
+                *self.current_fun_baseline.borrow(),
+                self.current_fun_local_types.borrow().as_ref(),
+            ) {
+                if let Some(local_ty) = local_types.get(*idx) {
+                    let global_state = &self
+                        .env
+                        .get_extension::<GlobalNumberOperationState>()
+                        .expect("global number operation state");
+                    if let Some(num_oper) = global_state.get_temp_index_oper(
+                        fun_qid.module_id,
+                        fun_qid.id,
+                        *idx,
+                        baseline,
+                    ) {
+                        // Mirrors the procedure-local declaration:
+                        // `boogie_type(local_ty, bv_flag_for_type(..))`.
+                        let ty = local_ty.instantiate(&fun_qid.inst);
+                        let flag = bv_flag_for_type(self.env, num_oper, ty.skip_reference());
+                        return (flag, ty.skip_reference().clone());
+                    }
+                }
+            }
+        }
+        (
+            self.node_bv_flag(e.node_id()),
+            self.get_node_type(e.node_id()),
+        )
+    }
+
+    fn operand_bv_flag(&self, e: &Exp) -> bool {
+        self.operand_rendering(e).0
+    }
+
+    /// Translate one operand of a binary op, converting at the rendering
+    /// boundary when the operand's own rendering disagrees with the op's: a
+    /// widthless `num` operand renders as int while its (inlined) defining
+    /// expression can render as a bitvector of concrete width, and vice
+    /// versa. `op_base` is the op's numeric base, used for int-to-bv; the
+    /// bv-to-int width comes from the same type that decided the operand's
+    /// rendering (the node type can be generalized `num` where that type is
+    /// concrete).
+    fn translate_op_operand(&self, e: &Exp, op_is_bv: bool, op_base: &str) {
+        let (operand_is_bv, operand_ty) = self.operand_rendering(e);
+        if operand_is_bv == op_is_bv {
+            self.translate_exp(e);
+        } else if op_is_bv {
+            emit!(self.writer, "$int2bv.{}(", op_base);
+            self.translate_exp(e);
+            emit!(self.writer, ")");
+        } else {
+            let base = boogie_num_type_base(
+                self.env,
+                Some(self.env.get_node_loc(e.node_id())),
+                &operand_ty,
+                false,
+            );
+            emit!(self.writer, "$bv2int.{}(", base);
+            self.translate_exp(e);
             emit!(self.writer, ")");
         }
     }
@@ -4014,10 +4202,17 @@ impl SpecTranslator<'_> {
     }
 
     fn translate_rel_op(&self, boogie_op: &str, args: &[Exp]) {
+        // Infix operators need both sides in the same rendering; when they
+        // disagree the bv side converts to int (never the reverse: only the
+        // bv side has a concrete width by construction). Deriving `want_bv`
+        // from the operands' own renderings — not the node flags, which can
+        // disagree with procedure-local declarations — guarantees the
+        // int-to-bv branch (which would need a width) is unreachable here.
+        let want_bv = self.operand_bv_flag(&args[0]) && self.operand_bv_flag(&args[1]);
         emit!(self.writer, "(");
-        self.translate_exp(&args[0]);
+        self.translate_op_operand(&args[0], want_bv, "");
         emit!(self.writer, " {} ", boogie_op);
-        self.translate_exp(&args[1]);
+        self.translate_op_operand(&args[1], want_bv, "");
         emit!(self.writer, ")");
     }
 
@@ -4030,13 +4225,11 @@ impl SpecTranslator<'_> {
     }
 
     fn translate_arithmetic_unary_op(&self, boogie_op: &str, args: &[Exp]) {
-        let global_state = &self
-            .env
-            .get_extension::<GlobalNumberOperationState>()
-            .expect("global number operation state");
-        let num_oper_e = global_state.get_node_num_oper(args[0].node_id());
+        // Unary minus only applies to signed operands, whose bv rendering is
+        // clamped; a raw `Bitwise` classification here is an artifact of
+        // instantiation-shared number-operation slots.
         assert!(
-            num_oper_e != Bitwise,
+            !self.node_bv_flag(args[0].node_id()),
             "no bitwise unary arithmetic ops supported"
         );
         emit!(self.writer, "{}", boogie_op);
@@ -4060,19 +4253,18 @@ impl SpecTranslator<'_> {
                 global_state.get_node_num_oper(arg.node_id()),
             )
         };
-        let target_type = self.env.get_node_type(node_id).skip_reference().clone();
-        let source_type = self
-            .env
-            .get_node_type(arg.node_id())
-            .skip_reference()
-            .clone();
+        let target_type = self.get_node_type(node_id).skip_reference().clone();
+        let source_type = self.get_node_type(arg.node_id()).skip_reference().clone();
         let check_cast = |ty: &Type| ty.is_unsigned_int();
         // bv → int boundary: source produces a bitvector (bv-classified unsigned
-        // int) but target is non-bv (signed or `Num`). Wrap with
+        // int) but the cast renders as int (spec casts sever `Bitwise`
+        // propagation, so this includes unsigned targets). Wrap with
         // `$bv2int.N(...)`. We must NOT propagate `cast_oper` (Arithmetic) onto
         // the source first — a bv-classified literal arg would otherwise lose
         // its bv suffix in `translate_value` and feed an `int` into `$bv2int.N`.
-        if source_oper == Bitwise && source_type.is_unsigned_int() && !target_type.is_unsigned_int()
+        if source_oper == Bitwise
+            && source_type.is_unsigned_int()
+            && !bv_flag_for_type(self.env, &cast_oper, &target_type)
         {
             let source_base = boogie_num_type_base(
                 self.env,
@@ -4128,7 +4320,7 @@ impl SpecTranslator<'_> {
                 };
 
                 emit!(self.writer, "(if ($Gt'Bv{}'(", source_base);
-                self.translate_exp(&arg);
+                self.translate_op_operand(&arg, true, &source_base);
                 emit!(self.writer, ", {}bv{})) then ", max_val_target, source_base);
 
                 // Track and emit unique arbitrary function for this cast overflow
@@ -4146,17 +4338,35 @@ impl SpecTranslator<'_> {
                 );
 
                 // Extract lower bits
-                self.translate_exp(&arg);
+                self.translate_op_operand(&arg, true, &source_base);
                 emit!(self.writer, "[{}:0])", target_bits);
             } else if source_bits == target_bits {
                 // Same size: just pass through
-                self.translate_exp(&arg);
+                self.translate_op_operand(&arg, true, &source_base);
             } else {
-                // Upcast: zero-extend
+                // Upcast: zero-extend. The source can render as int under the
+                // per-procedure temp rendering even when the shared spec node
+                // is bv-classified; coerce at the boundary.
                 let extend_bits = target_bits - source_bits;
                 emit!(self.writer, "0bv{} ++ ", extend_bits);
-                self.translate_exp(&arg);
+                self.translate_op_operand(&arg, true, &source_base);
             }
+        } else if bv_flag_for_type(self.env, &cast_oper, &target_type)
+            && !bv_flag_for_type(self.env, &source_oper, &source_type)
+        {
+            // Int-rendered source (e.g. a signed value whose bv classification
+            // is clamped) into a bv-classified target: mirror the int-domain
+            // pass-through and convert the result. The operand's own
+            // rendering decides (a schema binding can substitute a
+            // bitvector-rendered temporary under a `num` node, which needs
+            // no conversion).
+            let target_base = boogie_num_type_base(
+                self.env,
+                Some(self.env.get_node_loc(node_id)),
+                &target_type,
+                false,
+            );
+            self.translate_op_operand(&arg, true, &target_base);
         } else {
             self.translate_exp(&arg);
         }
@@ -4174,17 +4384,18 @@ impl SpecTranslator<'_> {
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number operation state");
         let num_oper = global_state.get_node_num_oper(args[0].node_id());
-        if num_oper == Bitwise {
+        let ty0 = self.get_node_type(args[0].node_id());
+        if bv_flag_for_type(self.env, &num_oper, &ty0) {
             let oper_left_base = boogie_num_type_base(
                 self.env,
                 Some(self.env.get_node_loc(args[0].node_id())),
-                &self.env.get_node_type(args[0].node_id()),
+                &ty0,
                 true,
             );
             let oper_right_base = boogie_num_type_base(
                 self.env,
                 Some(self.env.get_node_loc(args[1].node_id())),
-                &self.env.get_node_type(args[1].node_id()),
+                &self.get_node_type(args[1].node_id()),
                 false,
             );
             emit!(
@@ -4194,25 +4405,41 @@ impl SpecTranslator<'_> {
                 oper_left_base,
                 oper_right_base
             );
-        } else {
-            let ty = self.get_node_type(args[0].node_id());
-            if matches!(
-                ty,
-                Type::Primitive(PrimitiveType::I8)
-                    | Type::Primitive(PrimitiveType::I16)
-                    | Type::Primitive(PrimitiveType::I32)
-                    | Type::Primitive(PrimitiveType::I64)
-                    | Type::Primitive(PrimitiveType::I128)
-                    | Type::Primitive(PrimitiveType::I256)
-            ) {
-                self.error(
-                    &self.env.get_node_loc(args[0].node_id()),
-                    &format!("signed integer types not supported in operation {}", fun),
-                );
-            }
-            emit!(self.writer, "{}(", fun);
+            // Both parameters are bitvectors; marshal operands whose own
+            // rendering is int (mirrors `translate_primitive_call_shl`).
+            let left_conv_base = boogie_num_type_base(
+                self.env,
+                Some(self.env.get_node_loc(args[0].node_id())),
+                &ty0,
+                false,
+            );
+            self.translate_op_operand(&args[0], true, &left_conv_base);
+            emit!(self.writer, ", ");
+            self.translate_op_operand(&args[1], true, &oper_right_base);
+            emit!(self.writer, ")");
+            return;
         }
-        self.translate_seq(args.iter(), ", ", |e| self.translate_exp(e));
+        let ty = self.get_node_type(args[0].node_id());
+        if matches!(
+            ty,
+            Type::Primitive(PrimitiveType::I8)
+                | Type::Primitive(PrimitiveType::I16)
+                | Type::Primitive(PrimitiveType::I32)
+                | Type::Primitive(PrimitiveType::I64)
+                | Type::Primitive(PrimitiveType::I128)
+                | Type::Primitive(PrimitiveType::I256)
+        ) {
+            self.error(
+                &self.env.get_node_loc(args[0].node_id()),
+                &format!("signed integer types not supported in operation {}", fun),
+            );
+        }
+        emit!(self.writer, "{}(", fun);
+        // Marshal operands whose own rendering is bv (mirrors the int path
+        // of `translate_primitive_call_shl`).
+        self.translate_seq(args.iter(), ", ", |e| {
+            self.translate_op_operand(e, false, "")
+        });
         emit!(self.writer, ")");
     }
 
@@ -4222,17 +4449,18 @@ impl SpecTranslator<'_> {
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number operation state");
         let num_oper = global_state.get_node_num_oper(args[0].node_id());
-        if num_oper == Bitwise {
+        let ty0 = self.get_node_type(args[0].node_id());
+        if bv_flag_for_type(self.env, &num_oper, &ty0) {
             let oper_left_base = boogie_num_type_base(
                 self.env,
                 Some(self.env.get_node_loc(args[0].node_id())),
-                &self.env.get_node_type(args[0].node_id()),
+                &ty0,
                 true,
             );
             let oper_right_base = boogie_num_type_base(
                 self.env,
                 Some(self.env.get_node_loc(args[1].node_id())),
-                &self.env.get_node_type(args[1].node_id()),
+                &self.get_node_type(args[1].node_id()),
                 false,
             );
             emit!(
@@ -4242,7 +4470,19 @@ impl SpecTranslator<'_> {
                 oper_left_base,
                 oper_right_base
             );
-        } else {
+            let left_conv_base = boogie_num_type_base(
+                self.env,
+                Some(self.env.get_node_loc(args[0].node_id())),
+                &ty0,
+                false,
+            );
+            self.translate_op_operand(&args[0], true, &left_conv_base);
+            emit!(self.writer, ", ");
+            self.translate_op_operand(&args[1], true, &oper_right_base);
+            emit!(self.writer, ")");
+            return;
+        }
+        {
             let ty = self.get_node_type(args[0].node_id());
             let fun_num = match ty {
                 Type::Primitive(PrimitiveType::U8) => "U8",
@@ -4268,7 +4508,9 @@ impl SpecTranslator<'_> {
             };
             emit!(self.writer, "{}(", format!("{}{}", fun, fun_num).as_str());
         }
-        self.translate_seq(args.iter(), ", ", |e| self.translate_exp(e));
+        self.translate_seq(args.iter(), ", ", |e| {
+            self.translate_op_operand(e, false, "")
+        });
         emit!(self.writer, ")");
     }
 
@@ -4285,7 +4527,11 @@ impl SpecTranslator<'_> {
             .get_extension::<GlobalNumberOperationState>()
             .expect("global number state");
         let ty = self.get_node_type(exp.node_id());
-        let bv_flag = global_state.get_node_num_oper(exp.node_id()) == Bitwise;
+        let bv_flag = bv_flag_for_type(
+            self.env,
+            &global_state.get_node_num_oper(exp.node_id()),
+            &ty,
+        );
         match exp.as_ref() {
             ExpData::Temporary(_, idx) => {
                 // For the special case of a temporary which can represent a
```

### third_party/move/move-prover/bytecode-pipeline/src/mono_analysis.rs
```diff
@@ -1694,8 +1694,22 @@ impl Analyzer<'_> {
         if let Type::Fun(_, _, abilities) = field_ty {
             if abilities.has_store() {
                 let normalized = self.normalize_fun_ty(field_ty.clone());
+                // Normalize fun-type elements of the containing struct's
+                // instantiation too: the constructor name is derived from
+                // the boogie struct name, which drops fun abilities at every
+                // nesting depth. Without normalizing here, two
+                // ability-variant instantiations of the same wrapper (e.g.
+                // `Option<|u64| has drop>` and
+                // `Option<|u64| has drop + copy + store>`, directly or
+                // nested as in `Option<Option<|u64| has drop>>`) would
+                // produce two `StructFieldInfo` set entries mangling to one
+                // datatype constructor.
+                let normalized_targs: Vec<Type> = targs
+                    .iter()
+                    .map(|t| t.clone().normalize_nested_funs())
+                    .collect();
                 let info = StructFieldInfo {
-                    struct_id: struct_env.get_qualified_id().instantiate(targs.to_vec()),
+                    struct_id: struct_env.get_qualified_id().instantiate(normalized_targs),
                     field_sym: field.get_name(),
                 };
                 self.info
```

### third_party/move/move-prover/bytecode-pipeline/src/number_operation_analysis.rs
```diff
@@ -604,7 +604,9 @@ impl NumberOperationAnalysis<'_> {
                             // signed types and `Num` are always represented as Boogie `int`,
                             // so a `Bitwise` source must not propagate past the cast. The
                             // boundary itself is then materialized as `$bv2int.N(...)` by
-                            // `translate_cast` in the spec backend.
+                            // `translate_cast` in the spec backend. Unsigned-target casts
+                            // keep the source classification: a bit-operation consumer
+                            // legitimately re-demands `Bitwise` on them.
                             let target_ty = self.func_target.global_env().get_node_type(*id);
                             let cast_oper = if target_ty.skip_reference().is_signed_int()
                                 || matches!(
@@ -648,6 +650,12 @@ impl NumberOperationAnalysis<'_> {
                                 // Analysis for general spec functions.
                                 let module = &self.func_target.global_env().get_module(*mid);
                                 let callee_spec_fun = module.get_spec_fun(*sid);
+                                // `num` guards below must evaluate on the
+                                // instantiated parameter types: a generic
+                                // parameter instantiated at `num` is a sink
+                                // just like a declared `num` parameter.
+                                let callee_inst =
+                                    self.func_target.global_env().get_node_instantiation(*id);
                                 // Try to get num_oper for signatures
                                 // If not exists, compute num_oper for this spec fun and update the exp_operation_map and spec_fun_map
                                 if let std::collections::btree_map::Entry::Vacant(_) =
@@ -658,6 +666,26 @@ impl NumberOperationAnalysis<'_> {
                                     // Default num oper is determined by the actual arguments
                                     para_vec.append(&mut arg_oper);
                                     ret_vec.push(Bottom);
+                                    // Widthless `num` parameters are Arithmetic sinks: they
+                                    // always render as int, so a bitwise-classified argument
+                                    // crosses a representational boundary at the call (the
+                                    // argument renders as a bitvector, materialized by
+                                    // `$bv2int.N` at the argument position) and `Bitwise`
+                                    // must not seed the parameter slot and infect the
+                                    // callee's spec expressions.
+                                    for (i, Parameter(_, ty, _)) in
+                                        callee_spec_fun.params.iter().enumerate()
+                                    {
+                                        if i < para_vec.len()
+                                            && para_vec[i] == Bitwise
+                                            && matches!(
+                                                ty.instantiate(&callee_inst).skip_reference(),
+                                                Type::Primitive(PrimitiveType::Num)
+                                            )
+                                        {
+                                            para_vec[i] = Arithmetic;
+                                        }
+                                    }
                                     if let Some(body_exp) = &callee_spec_fun.body {
                                         let local_map = body_exp.bound_local_vars_with_node_id();
                                         for (i, Parameter(sym, _, loc)) in
@@ -714,11 +742,26 @@ impl NumberOperationAnalysis<'_> {
                                         .unwrap()
                                         .0;
                                     assert_eq!(para_oper_vec.len(), arg_oper.len());
-                                    for (formal_oper, actual_oper) in
-                                        para_oper_vec.iter().zip(arg_oper.iter())
+                                    for (i, (formal_oper, actual_oper)) in
+                                        para_oper_vec.iter().zip(arg_oper.iter()).enumerate()
                                     {
+                                        // A widthless `num` parameter is an Arithmetic sink
+                                        // (see the seeding clamp above); a bitwise-classified
+                                        // argument is reconciled by `$bv2int.N` at the
+                                        // argument position, not a conflict.
+                                        let num_param = matches!(
+                                            callee_spec_fun.params.get(i),
+                                            Some(Parameter(_, ty, _))
+                                                if matches!(
+                                                    ty.instantiate(&callee_inst).skip_reference(),
+                                                    Type::Primitive(PrimitiveType::Num)
+                                                )
+                                        );
                                         // For simplicity, only check compatibility
-                                        if !allow_merge && formal_oper.conflict(actual_oper) {
+                                        if !allow_merge
+                                            && !num_param
+                                            && formal_oper.conflict(actual_oper)
+                                        {
                                             self.func_target.global_env().error(
                                                 &self.func_target.get_bytecode_loc(attr_id),
                                                 CONFLICT_ERROR_MSG,
@@ -769,6 +812,24 @@ impl NumberOperationAnalysis<'_> {
                                     .insert(field.get_id(), merged);
                             }
                         },
+                        move_model::ast::Operation::Vector | move_model::ast::Operation::Tuple => {
+                            // Aggregate constructors: the node's
+                            // classification is the join of its elements',
+                            // so a bitwise element makes the recorded
+                            // signature render the aggregate's elements as
+                            // bitvectors.
+                            let mut merged = Bottom;
+                            for num_oper in &arg_oper {
+                                if !allow_merge && num_oper.conflict(&merged) {
+                                    self.func_target.global_env().error(
+                                        &self.func_target.get_bytecode_loc(attr_id),
+                                        CONFLICT_ERROR_MSG,
+                                    );
+                                }
+                                merged = num_oper.merge(&merged);
+                            }
+                            global_state.update_node_oper(*id, merged, true);
+                        },
                         _ => {
                             // All args must have compatible number operations
                             // TODO(tengzhang): support converting int to bv
@@ -1273,8 +1334,9 @@ impl AbstractDomain for NumberOperationState {
 }
 
 /// Retype an integer literal carrying the spec-mode default type (u256/i256)
-/// to its sibling operand's unsigned type when the value fits; returns the
-/// adopted type. Sibling types are always covered by mono analysis.
+/// to its sibling operand's concrete integer type when the value fits;
+/// returns the adopted type. Sibling types are always covered by mono
+/// analysis.
 fn adopt_spec_defaulted_literal_type(
     env: &GlobalEnv,
     arg0: &Exp,
@@ -1323,10 +1385,12 @@ fn adopt_spec_defaulted_literal_type(
     };
     let try_adopt = |lit: &Exp, lit_ty: &Type, other_ty: &Type| -> Option<Type> {
         let other = other_ty.skip_reference();
-        // Unsigned siblings only: signed has no bv rendering and must keep
-        // surfacing a diagnostic.
+        // Concrete integer siblings only (`num` has no fixed width). Signed
+        // siblings are safe: the backend renders Bitwise-classified signed
+        // values as `int`, so the adopted literal renders as a plain int
+        // literal alongside them.
         if !is_defaulted_literal(lit, lit_ty)
-            || !other.is_unsigned_int()
+            || !(other.is_unsigned_int() || other.is_signed_int())
             || lit_ty.skip_reference() == other
         {
             return None;
```

### third_party/move/move-prover/tests/sources/functional/bitwise_table_mixed_instances.move
```diff
@@ -0,0 +1,43 @@
+// Twins are per-instance: a struct-valued sibling instantiation of the same
+// map type must not suppress the bv twin demanded by a bitwise-classified
+// numeric-valued instantiation.
+module 0x42::VerifyBitwiseTableMixedInstances {
+    use extensions::table::{Self, Table};
+    use extensions::table::spec_get;
+
+    struct Item has copy, drop, store {
+        a: u64,
+    }
+
+    fun structs(): Table<u8, Item> {
+        let t = table::new<u8, Item>();
+        table::add(&mut t, 1, Item { a: 2 });
+        t
+    }
+    spec structs {
+        ensures spec_get(result, 1).a == 2;
+    }
+
+    fun packed(): Table<u8, u64> {
+        let t = table::new<u8, u64>();
+        table::add(&mut t, 1, 3 & 7);
+        t
+    }
+    spec packed {
+        pragma bv_ret = b"0";
+        ensures spec_get(result, 1) == (3 as u64);
+    }
+
+    // Nested unsigned value types have a bv rendering too: the twin supply
+    // must cover them, or a Bitwise-classified instantiation selects an
+    // unemitted `Table int (Vec bvN)` representation.
+    fun packed_vec(x: u8): Table<u8, vector<u8>> {
+        let t = table::new<u8, vector<u8>>();
+        table::add(&mut t, 1, vector[x & 1]);
+        t
+    }
+    spec packed_vec {
+        aborts_if false;
+        ensures spec_get(result, 1) == vector[x & 1];
+    }
+}
```

### third_party/move/move-prover/tests/sources/functional/bv_num_spec_infection.move
```diff
@@ -0,0 +1,102 @@
+// A bitwise-classified caller argument must not force bitvector rendering
+// onto a callee spec's widthless `num` expressions: `num` is an int sink
+// (spec lets over shifts, `num`-typed spec fun parameters), and genuinely
+// bitvector values convert exactly at the crossing (cast source, spec fun
+// argument). One bitwise caller shares the callee's classification slots
+// with every clean caller, so both must verify. Mirrors the shape of
+// `fixed_point32::create_from_rational`'s abort schema.
+module 0x42::bv_num_spec_infection {
+    struct Fixed has copy, drop, store {
+        value: u64,
+    }
+
+    const EDENOM: u64 = 0x10001;
+    const ERANGE: u64 = 0x20001;
+
+    public fun create(numerator: u64, denominator: u64): Fixed {
+        let _ = denominator;
+        Fixed { value: numerator }
+    }
+    spec create {
+        pragma opaque;
+        pragma verify = false;
+        include CreateAbortsIf;
+        ensures result == spec_create(numerator, denominator);
+    }
+    spec schema CreateAbortsIf {
+        numerator: u64;
+        denominator: u64;
+        let scaled_numerator = (numerator as u128) << 64;
+        let scaled_denominator = (denominator as u128) << 32;
+        let quotient = scaled_numerator / scaled_denominator;
+        aborts_if scaled_denominator == 0 with EDENOM;
+        aborts_if quotient == 0 && scaled_numerator != 0 with ERANGE;
+        aborts_if quotient > MAX_U64 with ERANGE;
+    }
+    spec fun spec_create(numerator: num, denominator: num): Fixed {
+        Fixed {
+            value: ((numerator << 64) / (denominator << 32)) as u64,
+        }
+    }
+
+    fun mk_clean(n: u64, d: u64): Fixed {
+        create(n, d)
+    }
+
+    fun mk_bitwise(n: u64): Fixed {
+        create(n & 3, 7)
+    }
+}
+
+// The `num` clamp has containment-closure semantics: a spec-function slot
+// that acquired `Bitwise` from one caller can be instantiated at
+// `vector<num>` elsewhere; widthless `num` has no bitvector rendering at
+// any nesting depth, so that instantiation must render plainly.
+module 0x42::bv_num_vector_clamp {
+    spec fun accepts<T>(x: T): bool {
+        true
+    }
+
+    // Aggregate constructors propagate their element classification into
+    // the recorded signature.
+    spec fun wrap(x: u8): vector<u8> {
+        vector[x & 1]
+    }
+
+    spec fun bumped<T>(r: &mut u64, x: T): bool {
+        old(r) <= r
+    }
+
+    // An explicit schema binding substitutes a bitvector-rendered
+    // temporary under a schema field typed `num`; spec-fun arguments and
+    // casts consult the operand's own rendering at that boundary.
+    spec schema BitsBound {
+        n: num;
+        ensures accepts<num>(n);
+    }
+
+    fun mask(r: &mut u64, x: u8, y: u64): u8 {
+        *r = *r + 1;
+        (x & 1) + ((y & 1) as u8)
+    }
+    spec mask {
+        aborts_if r + 1 > MAX_U64;
+        ensures accepts<u8>(x & 1);
+        ensures accepts<vector<num>>(vector[MAX_U64]);
+        // A generic parameter instantiated at `num` is a sink like a
+        // declared `num` parameter: a bitwise argument converts at the
+        // boundary, and mixed bitwise/arithmetic uses of the `num`
+        // instantiation are not a classification conflict.
+        ensures accepts<num>(x & 1);
+        ensures accepts<num>(MAX_U64 + 1);
+        // The doubled-argument path (`uses_old` with a mutable-reference
+        // parameter) converts by-value arguments at the same instantiated
+        // boundary.
+        ensures bumped<num>(r, x & 1);
+        ensures wrap(x) == vector[x & 1];
+        // Note: included after the unsigned `accepts` calls above — the
+        // schema's `accepts<num>` call must not be the slot-seeding one
+        // (known order-dependence of the shared spec-fun slots).
+        include BitsBound { n: y };
+    }
+}
```

### third_party/move/move-prover/tests/sources/functional/bv_signed_generic.move
```diff
@@ -0,0 +1,182 @@
+// exclude_for: cvc5
+// Regression: number-operation slots of generic parameters, returns and
+// struct fields are shared across type instantiations, so a `Bitwise`
+// classification acquired through an unsigned instantiation leaks into
+// signed instantiations of the same generic. Signed integers have no
+// bitvector rendering and must render as `int` even when classified
+// `Bitwise`; the comparison arm of the backend used to hit `unreachable!()`.
+module 0x42::bv_signed_generic {
+
+    fun id<T>(x: T): T {
+        x
+    }
+
+    // Seeds `Bitwise` into `id`'s shared parameter and return slots via an
+    // unsigned instantiation.
+    fun seed(x: u8): u8 {
+        id(x & 1)
+    }
+    spec seed {
+        aborts_if false;
+        ensures result == (x & 1);
+    }
+
+    // Signed instantiation of the same generic: comparing the infected value
+    // used to panic the backend.
+    fun cmp_signed(a: i8): bool {
+        let b = id(a);
+        b > 0
+    }
+    spec cmp_signed {
+        aborts_if false;
+        ensures result == (a > 0);
+    }
+
+    // Same infection through a generic struct field slot.
+    struct Box<T> has drop { v: T }
+
+    fun seed_field(x: u8): u8 {
+        let b = Box { v: x & 1 };
+        b.v
+    }
+    spec seed_field {
+        aborts_if false;
+        ensures result == (x & 1);
+    }
+
+    fun cmp_field(a: i64): bool {
+        let b = Box { v: a };
+        b.v < 0
+    }
+    spec cmp_field {
+        aborts_if false;
+        ensures result == (a < 0);
+    }
+
+    // Negation, arithmetic and equality on infected signed values exercise
+    // the sibling rendering paths (declarations, `$Negate`/`$Add` dispatch,
+    // equality suffixes).
+    fun neg_signed(a: i64): i64 {
+        let b = id(a);
+        -b
+    }
+    spec neg_signed {
+        aborts_if a == MIN_I64;
+        ensures result == -a;
+    }
+
+    fun add_signed(a: i64): i64 {
+        let b = id(a);
+        b + 1
+    }
+    spec add_signed {
+        aborts_if a + 1 > MAX_I64;
+        ensures result == a + 1;
+    }
+
+    fun eq_signed(a: i32): bool {
+        let b = id(a);
+        b == 0
+    }
+    spec eq_signed {
+        aborts_if false;
+        ensures result == (a == 0);
+    }
+
+    // An int-rendered (clamped signed) source cast into a bv-classified
+    // unsigned destination needs int->bv marshaling, in code and in specs.
+    fun cast_infected(a: i64): u8 {
+        let b = id(a);
+        (b as u8)
+    }
+    spec cast_infected {
+        aborts_if a < 0 || a > 255;
+        ensures result == (a as u8);
+    }
+
+    // Spec functions share one number-operation slot across instantiations;
+    // declaration and call sites must agree on the (clamped) name for signed
+    // instantiations.
+    spec module {
+        fun sid<T>(x: T): T { x }
+    }
+
+    fun wrap<T: drop>(x: T): T {
+        x
+    }
+    spec wrap {
+        ensures result == sid(x);
+    }
+
+    fun wrap_seed(y: u8): u8 {
+        wrap(y & 1)
+    }
+
+    fun wrap_signed(a: i64): i64 {
+        wrap(a)
+    }
+}
+
+// Intrinsic maps declare their type parameters as phantom, so the signedness
+// clamp must inspect their instantiations directly: an infected signed table
+// value marks the whole table Bitwise, and `Table<u8, i8>` must still render
+// its value type as `int`.
+module 0x42::bv_signed_table {
+    use extensions::table::{Self, Table};
+
+    fun id<T>(x: T): T {
+        x
+    }
+
+    fun seed(x: u8): u8 {
+        id(x & 1)
+    }
+    spec seed {
+        aborts_if false;
+    }
+
+    fun put(t: &mut Table<u8, i8>, a: i8) {
+        table::add(t, 1, id(a));
+    }
+}
+
+// `int2bv`/`bv2int` conversion wrappers follow the same instantiation-aware
+// rendering as their operands: for a signed instantiation both sides render
+// as `int` and the conversions are identities (a raw `Bitwise` slot test
+// emitted a conversion whose numeric base came from an uninstantiated type
+// parameter — invalid Boogie).
+module 0x42::bv_conv_roundtrip {
+    fun id<T>(x: T): T {
+        x
+    }
+
+    fun seed(x: u8): u8 {
+        id(x & 1)
+    }
+    spec seed {
+        aborts_if false;
+    }
+
+    spec fun roundtrip<T>(x: T): T {
+        int2bv(bv2int(x))
+    }
+
+    fun victim(a: i8): i8 {
+        id(a)
+    }
+    spec victim {
+        ensures result == roundtrip(a);
+    }
+}
+
+// A signed KEY does not clamp the map: keys encode to int regardless of the
+// map's rendering, so only the value type participates in bv twin selection.
+// `Table<i8, u8>` with a bitwise value must render the bv twin consistently
+// with its bv-rendered value operands.
+module 0x42::bv_signed_key_table {
+    use extensions::table::{Self, Table};
+
+    fun put(t: &mut Table<i8, u8>, a: i8, x: u8) {
+        table::add(t, a, x & 1);
+    }
+}
```

### third_party/move/move-prover/tests/sources/functional/fun_field_nested_ability_variants.move
```diff
@@ -0,0 +1,48 @@
+// Function types normalize (ability-stripped, tuple-flattened) at every
+// nesting depth, matching the erasure Boogie type names apply: two wrapper
+// instantiations whose stored function fields differ only in the abilities
+// of a nested function type must produce a single canonical function type
+// (one closure datatype, one field constructor), not two that mangle to the
+// same Boogie name.
+module 0x42::fun_field_nested_ability_variants {
+    use std::option::{Self, Option};
+
+    struct A has drop {
+        f: Option<|(|u64| has drop)| has drop + store>,
+    }
+    struct B has drop {
+        f: Option<|(|u64| has drop + copy)| has drop + store>,
+    }
+
+    public fun run_a(g: |u64| has drop) {
+        g(1)
+    }
+    public fun run_b(g: |u64| has drop + copy) {
+        g(2)
+    }
+
+    fun mk_a(): A {
+        A { f: option::some(run_a) }
+    }
+    spec mk_a {
+        aborts_if false;
+    }
+
+    fun mk_b(): B {
+        B { f: option::some(run_b) }
+    }
+    spec mk_b {
+        aborts_if false;
+    }
+
+    // The identity-constraint lookup must use the same canonical keys as
+    // the registration: an ability-carrying function type argument
+    // (normalization strips abilities) previously missed the lookup,
+    // silently dropping the `is $struct_field` well-formedness assumption.
+    fun probe_identity(o: Option<|u64| has drop + store>): bool {
+        option::is_some(&o)
+    }
+    spec probe_identity {
+        aborts_if false;
+    }
+}
```
