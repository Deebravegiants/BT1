# [?] fix(ssa): Overflow in inclusive range for loops (#10567)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-22
Source: https://github.com/noir-lang/noir/commit/89c8d3923cb195d7be955b97e2653684d71db076
Type: security-commit

## Details
fix(ssa): Overflow in inclusive range for loops (#10567)

Co-authored-by: Ary Borenszweig <asterite@gmail.com>

## Patch
### compiler/noirc_evaluator/src/ssa/opt/pure.rs
```diff
@@ -363,7 +363,7 @@ mod tests {
                 v1 = lt v0, u32 1
                 jmpif v1 then: b1, else: b2
               b1():
-                jmp b3(Field 0)
+                jmp b3(u32 0)
               b2():
                 v3 = call f7(v0) -> u32
                 call f6()
@@ -437,7 +437,7 @@ mod tests {
             v3 = lt v0, u32 1
             jmpif v3 then: b1, else: b2
           b1():
-            jmp b3(Field 0)
+            jmp b3(u32 0)
           b2():
             v5 = call f7(v0) -> u32
             call f6()
```

### compiler/noirc_evaluator/src/ssa/opt/remove_unreachable_instructions.rs
```diff
@@ -1032,7 +1032,7 @@ mod tests {
           b1():
             v2 = add Field 1, Field 2
             jmp b2(v2)
-          b2():
+          b2(v3: Field):
             jmpif u1 0 then: b3, else: b4
           b3():
             constrain u1 0 == u1 1, "Index out of bounds"
@@ -1050,16 +1050,16 @@ mod tests {
           b0():
             jmp b1()
           b1():
-            v2 = add Field 1, Field 2
-            jmp b2(v2)
-          b2():
+            v3 = add Field 1, Field 2
+            jmp b2(v3)
+          b2(v0: Field):
             jmpif u1 0 then: b3, else: b4
           b3():
             constrain u1 0 == u1 1, "Index out of bounds"
             unreachable
           b4():
-            v4 = add Field 1, Field 2
-            return v4
+            v5 = add Field 1, Field 2
+            return v5
         }
         "#);
     }
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -39,6 +39,7 @@ use rustc_hash::FxHashMap as HashMap;
 /// is the only part of the context that needs to be shared between threads.
 pub(super) struct FunctionContext<'a> {
     definitions: HashMap<LocalId, Values>,
+    pub(super) redefinitions_allowed: bool,
 
     pub(super) builder: FunctionBuilder,
     shared_context: &'a SharedContext,
@@ -94,6 +95,18 @@ pub(super) struct Loop {
     /// The loop index will be `Some` for a `for` and `None` for a `loop`
     pub(super) loop_index: Option<ValueId>,
     pub(super) loop_end: BasicBlockId,
+    /// A variable that tracks whether a `break` was hit or not:
+    /// `false` if a `break` was hit, `true` if not.
+    /// This is only `Some` in the case of an inclusive for loop which is
+    /// generated as an exclusive for loop with an extra iteration for the
+    /// end of the loop. This extra iteration is only done if no `break` was hit
+    /// in the exclusive iterations (and if `start <= end`).
+    /// We track the negated value because we execute the last iteration
+    /// if we did not hit a break, in the end being `did_not_hit_break && (start <= end)`.
+    /// If we tracked whether we hit a break or not, the condition to execute
+    /// the last iteration would be `(not hit_break) && (start <= end)`, which is larger
+    /// by one instruction.
+    pub(super) did_not_hit_break_var: Option<ValueId>,
 }
 
 /// The queue of functions remaining to compile
@@ -126,7 +139,13 @@ impl<'a> FunctionContext<'a> {
         builder.set_runtime(runtime);
 
         let definitions = HashMap::default();
-        let mut this = Self { definitions, builder, shared_context, loops: Vec::new() };
+        let mut this = Self {
+            definitions,
+            builder,
+            shared_context,
+            loops: Vec::new(),
+            redefinitions_allowed: false,
+        };
         this.add_parameters_to_scope(parameters);
         this
     }
@@ -555,7 +574,9 @@ impl<'a> FunctionContext<'a> {
     /// by calling self.lookup(id)
     pub(super) fn define(&mut self, id: LocalId, value: Values) {
         let existing = self.definitions.insert(id, value);
-        assert!(existing.is_none(), "Variable {id:?} was defined twice in ssa-gen pass");
+        if !self.redefinitions_allowed && existing.is_some() {
+            panic!("Variable {id:?} was defined twice in ssa-gen pass");
+        }
     }
 
     /// Looks up the value of a given local variable. Expects the variable to have
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -628,15 +628,22 @@ impl FunctionContext<'_> {
         let start_index = self.codegen_non_tuple_expression(&for_expr.start_range)?;
 
         self.builder.set_location(for_expr.end_range_location);
-        let end_index = self.codegen_non_tuple_expression(&for_expr.end_range)?;
+        let mut end_index = self.codegen_non_tuple_expression(&for_expr.end_range)?;
 
         let range_bound = |id| self.builder.current_function.dfg.get_integer_constant(id);
 
         if let (Some(start_constant), Some(end_constant)) =
             (range_bound(start_index), range_bound(end_index))
         {
-            // If we can determine that the loop contains zero iterations then there's no need to codegen the loop.
-            if start_constant >= end_constant {
+            // For inclusive ranges (e.g., `0..=255`), the loop should run if start <= end.
+            // For exclusive ranges (e.g., `0..256`), the loop should run if start < end.
+            // If the condition is false, skip the loop entirely.
+            let should_skip = if for_expr.inclusive {
+                start_constant > end_constant
+            } else {
+                start_constant >= end_constant
+            };
+            if should_skip {
                 return Ok(Self::unit_value());
             }
         }
@@ -647,11 +654,86 @@ impl FunctionContext<'_> {
 
         // this is the 'i' in `for i in start .. end { block }`
         let index_type = Self::convert_non_tuple_type(&for_expr.index_type);
-        let loop_index = self.builder.add_block_parameter(loop_entry, index_type);
+        let loop_index = self.builder.add_block_parameter(loop_entry, index_type.clone());
+
+        let mut inclusive = for_expr.inclusive;
+
+        // If this is an inclusive for loop, check if the end index is not the maximum value for its type.
+        // In that case we can generate an exclusive for loop up to `end + 1`, which is simpler than
+        // the code of an inclusive loop.
+        if inclusive {
+            if let Some(end_constant) =
+                self.builder.current_function.dfg.get_integer_constant(end_index)
+            {
+                let index_type = index_type.unwrap_numeric();
+                let bit_size = match index_type {
+                    NumericType::Signed { bit_size } => bit_size - 1,
+                    NumericType::Unsigned { bit_size } => bit_size,
+                    NumericType::NativeField => panic!("Cannot iterate over Field"),
+                };
+                let max_value = if bit_size == 128 { u128::MAX } else { (1u128 << bit_size) - 1 };
+
+                if end_constant.into_numeric_constant().0.to_u128() < max_value {
+                    let end_constant_plus_one = end_constant.inc();
+                    end_index = self.builder.numeric_constant(
+                        end_constant_plus_one.into_numeric_constant().0,
+                        index_type,
+                    );
+                    inclusive = false;
+                }
+            }
+        }
+
+        // For inclusive ranges we could generate a loop like:
+        //
+        // ```noir
+        // let index = start;
+        // while start <= end {
+        //   body;
+        //   if index == end { break; }
+        //   index += 1;
+        // }
+        // ``
+        //
+        // We could do that in order to avoid an overflow at `index += 1` when `end` is the maximum
+        // value for the range type.
+        //
+        // However, an SSA like above breaks some assumptions in the unrolling optimization pass.
+        //
+        // Instead, we generate something like this:
+        //
+        // ```noir
+        // let index = start;
+        // // did_not_hit_break is set to false if a break is hit in the for body
+        // let did_not_hit_break = true;
+        // for index in start..end {
+        //   body;
+        // }
+        // if start <= end && did_not_hit_break {
+        //   index = end;
+        //   body;
+        // }
+        // ```
+        //
+        // That is, we generate an exclusive for loop and include an extra final iteration that
+        // is only executed if the start is less than the end, and if no break was hit in the loop body.
+        let did_not_hit_break_var = if inclusive {
+            let did_not_hit_break_var = self.builder.insert_allocate(Type::bool());
+            let zero = self.builder.numeric_constant(true, NumericType::bool());
+            self.builder.insert_store(did_not_hit_break_var, zero);
+            Some(did_not_hit_break_var)
+        } else {
+            None
+        };
 
         // Remember the blocks and variable used in case there are break/continue instructions
         // within the loop which need to jump to them.
-        self.enter_loop(Loop { loop_entry, loop_index: Some(loop_index), loop_end });
+        self.enter_loop(Loop {
+            loop_entry,
+            loop_index: Some(loop_index),
+            loop_end,
+            did_not_hit_break_var,
+        });
 
         // Set the location of the initial jmp instruction to the start range. This is the location
         // used to issue an error if the start range cannot be determined at compile-time.
@@ -661,7 +743,7 @@ impl FunctionContext<'_> {
         // Compile the loop entry block
         self.builder.switch_to_block(loop_entry);
 
-        // Set the location of the ending Lt instruction and the jmpif back-edge of the loop to the
+        // Set the location of the ending comparison instruction and the jmpif back-edge of the loop to the
         // end range. These are the instructions used to issue an error if the end of the range
         // cannot be determined at compile-time.
         self.builder.set_location(for_expr.end_range_location);
@@ -673,14 +755,71 @@ impl FunctionContext<'_> {
         self.define(for_expr.index_variable, loop_index.into());
 
         let result = self.codegen_expression(&for_expr.block);
-        self.codegen_unless_break_or_continue(result, |this, _| {
+        self.codegen_unless_break_or_continue(result.clone(), |this, _| {
             let new_loop_index = this.make_offset(loop_index, 1, true);
             this.builder.terminate_with_jmp(loop_entry, vec![new_loop_index]);
         })?;
 
         // Finish by switching back to the end of the loop
         self.builder.switch_to_block(loop_end);
         self.exit_loop();
+
+        // Generate the final iteration for inclusive ranges
+        if let Some(did_not_hit_break_var) = did_not_hit_break_var {
+            let final_iteration = self.builder.insert_block();
+            let final_iteration_end = self.builder.insert_block();
+
+            let did_not_hit_break = self.builder.insert_load(did_not_hit_break_var, Type::bool());
+            // `start <= end` is equivalent to `!(start > end)`
+            let end_is_less_than_start =
+                self.builder.insert_binary(end_index, BinaryOp::Lt, start_index);
+            let start_is_less_than_or_equal_to_end =
+                self.builder.insert_not(end_is_less_than_start);
+            let should_execute_loop_body = self.builder.insert_binary(
+                did_not_hit_break,
+                BinaryOp::And,
+                start_is_less_than_or_equal_to_end,
+            );
+            self.builder.terminate_with_jmpif(
+                should_execute_loop_body,
+                final_iteration,
+                final_iteration_end,
+            );
+
+            self.builder.switch_to_block(final_iteration);
+
+            // We need to be in the context of a loop because a `break` in the loop, in the final
+            // iteration, has to jump somewhere.
+            // We set both `loop_entry` and `loop_end` to `final_iteration_end` because:
+            // - `break` will jump to `loop_end`
+            // - `continue` will jump to `loop_entry`, but here we also want to jump to the end
+            self.enter_loop(Loop {
+                loop_entry: final_iteration_end,
+                loop_index: None,
+                loop_end: final_iteration_end,
+                did_not_hit_break_var: None,
+            });
+
+            // Temporarily allow redefinitions because:
+            // 1. We'll override the index variable
+            // 2. We'll generate the for loop body again
+            let old_redefinitions_allowed = self.redefinitions_allowed;
+            self.redefinitions_allowed = true;
+
+            self.define(for_expr.index_variable, end_index.into());
+
+            let result = self.codegen_expression(&for_expr.block);
+            self.codegen_unless_break_or_continue(result, |this, _| {
+                this.builder.terminate_with_jmp(final_iteration_end, vec![]);
+            })?;
+
+            self.redefinitions_allowed = old_redefinitions_allowed;
+
+            self.builder.switch_to_block(final_iteration_end);
+
+            self.exit_loop();
+        }
+
         Ok(Self::unit_value())
     }
 
@@ -701,7 +840,12 @@ impl FunctionContext<'_> {
         let loop_body = self.builder.insert_block();
         let loop_end = self.builder.insert_block();
 
-        self.enter_loop(Loop { loop_entry: loop_body, loop_index: None, loop_end });
+        self.enter_loop(Loop {
+            loop_entry: loop_body,
+            loop_index: None,
+            loop_end,
+            did_not_hit_break_var: None,
+        });
 
         self.builder.terminate_with_jmp(loop_body, vec![]);
 
@@ -746,7 +890,12 @@ impl FunctionContext<'_> {
         let condition = self.codegen_non_tuple_expression(&while_.condition)?;
         self.builder.terminate_with_jmpif(condition, while_body, while_end);
 
-        self.enter_loop(Loop { loop_entry: while_entry, loop_index: None, loop_end: while_end });
+        self.enter_loop(Loop {
+            loop_entry: while_entry,
+            loop_index: None,
+            loop_end: while_end,
+            did_not_hit_break_var: None,
+        });
 
         // Codegen the body
         self.builder.switch_to_block(while_body);
@@ -1241,7 +1390,15 @@ impl FunctionContext<'_> {
     }
 
     fn codegen_break(&mut self) -> Result<Values, RuntimeError> {
-        let loop_end = self.current_loop().loop_end;
+        let current_loop = self.current_loop();
+
+        if let Some(did_not_hit_break_var) = current_loop.did_not_hit_break_var {
+            // `did_not_hit_break_var = false` means we hit a break
+            let zero = self.builder.numeric_constant(false, NumericType::bool());
+            self.builder.insert_store(did_not_hit_break_var, zero);
+        }
+
+        let loop_end = current_loop.loop_end;
         self.builder.terminate_with_jmp(loop_end, Vec::new());
 
         Err(RuntimeError::BreakOrContinue { call_stack: CallStack::default() })
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/tests.rs
```diff
@@ -1,6 +1,6 @@
 #![cfg(test)]
 
-use crate::{errors::RuntimeError, ssa::opt::assert_normalized_ssa_equals};
+use crate::{assert_ssa_snapshot, errors::RuntimeError, ssa::opt::assert_normalized_ssa_equals};
 
 use super::{Ssa, generate_ssa};
 
@@ -264,3 +264,344 @@ fn foreign_call_args_do_not_get_cloned() {
     "#;
     assert_normalized_ssa_equals(ssa, expected);
 }
+
+#[test]
+fn for_loop_exclusive() {
+    let assert_src = "
+    fn main() -> pub u32 {
+        let mut sum = 0;
+        for i in 0..5 {
+          sum += i;
+        }
+        sum
+    }
+    ";
+    let ssa = get_initial_ssa(assert_src).unwrap();
+
+    // This is a regular for loop, nothing special here
+    assert_ssa_snapshot!(ssa, @r"
+    acir(inline) fn main f0 {
+      b0():
+        v1 = allocate -> &mut u32
+        store u32 0 at v1
+        jmp b1(u32 0)
+      b1(v0: u32):
+        v4 = lt v0, u32 5
+        jmpif v4 then: b2, else: b3
+      b2():
+        v6 = load v1 -> u32
+        v7 = add v6, v0
+        store v7 at v1
+        v9 = unchecked_add v0, u32 1
+        jmp b1(v9)
+      b3():
+        v5 = load v1 -> u32
+        return v5
+    }
+    ");
+}
+
+#[test]
+fn for_loop_inclusive_max_value_without_break() {
+    let assert_src = "
+    fn main() -> pub u8 {
+        let mut sum = 0;
+        for i in 0..=255_u8 {
+          sum += i;
+        }
+        sum
+    }
+    ";
+    let ssa = get_initial_ssa(assert_src).unwrap();
+
+    // - b1 is the loop header
+    // - b2 is the loop body
+    // - b3 is the loop exit, but it performs a check to determine whether the final iteration
+    //   should be executed. In this case we check if no break was hit. It's multiplied by
+    //   one because that "one" is (start < end) which is true in this case.
+    // - b4 is the final iteration where `index == end`
+    assert_ssa_snapshot!(ssa, @r"
+    acir(inline) fn main f0 {
+      b0():
+        v1 = allocate -> &mut u8
+        store u8 0 at v1
+        v3 = allocate -> &mut u1
+        store u1 1 at v3
+        jmp b1(u8 0)
+      b1(v0: u8):
+        v6 = lt v0, u8 255
+        jmpif v6 then: b2, else: b3
+      b2():
+        v12 = load v1 -> u8
+        v13 = add v12, v0
+        store v13 at v1
+        v15 = unchecked_add v0, u8 1
+        jmp b1(v15)
+      b3():
+        v7 = load v3 -> u1
+        v8 = unchecked_mul v7, u1 1
+        jmpif v8 then: b4, else: b5
+      b4():
+        v9 = load v1 -> u8
+        v10 = add v9, u8 255
+        store v10 at v1
+        jmp b5()
+      b5():
+        v11 = load v1 -> u8
+        return v11
+    }
+    ");
+}
+
+#[test]
+fn for_loop_inclusive_end_is_known_and_not_a_maximum() {
+    let assert_src = "
+    fn main() -> pub u8 {
+        let mut sum = 0;
+        for i in 0..=254_u8 {
+          sum += i;
+        }
+        sum
+    }
+    ";
+    let ssa = get_initial_ssa(assert_src).unwrap();
+
+    // We end up generating an exclusive for loop up to 255
+    assert_ssa_snapshot!(ssa, @r"
+    acir(inline) fn main f0 {
+      b0():
+        v1 = allocate -> &mut u8
+        store u8 0 at v1
+        jmp b1(u8 0)
+      b1(v0: u8):
+        v4 = lt v0, u8 255
+        jmpif v4 then: b2, else: b3
+      b2():
+        v6 = load v1 -> u8
+        v7 = add v6, v0
+        store v7 at v1
+        v9 = unchecked_add v0, u8 1
+        jmp b1(v9)
+      b3():
+        v5 = load v1 -> u8
+        return v5
+    }
+    ");
+}
+
+#[test]
+fn for_loop_inclusive_max_value_with_break() {
+    let assert_src = "
+    unconstrained fn main(cond: bool) -> pub u8 {
+        let mut sum = 0;
+        for i in 0..=255_u8 {
+          if cond {
+              break;
+          }
+          sum += i;
+        }
+        sum
+    }
+    ";
+    let ssa = get_initial_ssa(assert_src).unwrap();
+
+    // - b1 is the loop header
+    // - b2, b4  and b5 are the loop body
+    // - b4 has the logic that happens when a break is hit. In this case we store 0 at v3
+    //   to signal this.
+    // - b3 is the loop exit, but it performs a check to determine whether the final iteration
+    //   should be executed. In this case we check if no break was hit. It's multiplied by
+    //   one because that "one" is (start < end) which is true in this case.
+    // - b6 is the final loop iteration where `index == end`. Note that the code for
+    //   `if cond { break; }` now has the break take us to b8, which jumps to b7, which
+    //   exits main (that is, the break skips the final iteration).
+    assert_ssa_snapshot!(ssa, @r"
+    brillig(inline) fn main f0 {
+      b0(v0: u1):
+        v2 = allocate -> &mut u8
+        store u8 0 at v2
+        v4 = allocate -> &mut u1
+        store u1 1 at v4
+        jmp b1(u8 0)
+      b1(v1: u8):
+        v7 = lt v1, u8 255
+        jmpif v7 then: b2, else: b3
+      b2():
+        jmpif v0 then: b4, else: b5
+      b3():
+        v13 = load v4 -> u1
+        v14 = unchecked_mul v13, u1 1
+        jmpif v14 then: b6, else: b7
+      b4():
+        store u1 0 at v4
+        jmp b3()
+      b5():
+        v8 = load v2 -> u8
+        v9 = add v8, v1
+        store v9 at v2
+        v11 = unchecked_add v1, u8 1
+        jmp b1(v11)
+      b6():
+        jmpif v0 then: b8, else: b9
+      b7():
+        v17 = load v2 -> u8
+        return v17
+      b8():
+        jmp b7()
+      b9():
+        v15 = load v2 -> u8
+        v16 = add v15, u8 255
+        store v16 at v2
+        jmp b7()
+    }
+    ");
+}
+
+#[test]
+fn for_loop_inclusive_unknown_range_with_break() {
+    let assert_src = "
+    unconstrained fn main(start: u8, end: u8) -> pub u8 {
+        let mut sum = 0;
+        for i in start..=end {
+          if i == 10 { 
+              break; 
+          }
+          sum += i;
+        }
+        sum
+    }
+    ";
+    let ssa = get_initial_ssa(assert_src).unwrap();
+
+    // Here we can see in b3 that we do `lt v0, v1`, which is the condition that checks
+    // `start < end` to determine whether the final iteration should be executed
+    // (in addition to checking if a break was hit or not).
+    assert_ssa_snapshot!(ssa, @r"
+    brillig(inline) fn main f0 {
+      b0(v0: u8, v1: u8):
+        v3 = allocate -> &mut u8
+        store u8 0 at v3
+        v5 = allocate -> &mut u1
+        store u1 1 at v5
+        jmp b1(v0)
+      b1(v2: u8):
+        v7 = lt v2, v1
+        jmpif v7 then: b2, else: b3
+      b2():
+        v9 = eq v2, u8 10
+        jmpif v9 then: b4, else: b5
+      b3():
+        v15 = load v5 -> u1
+        v16 = lt v1, v0
+        v17 = not v16
+        v18 = unchecked_mul v15, v17
+        jmpif v18 then: b6, else: b7
+      b4():
+        store u1 0 at v5
+        jmp b3()
+      b5():
+        v10 = load v3 -> u8
+        v11 = add v10, v2
+        store v11 at v3
+        v13 = unchecked_add v2, u8 1
+        jmp b1(v13)
+      b6():
+        v19 = eq v1, u8 10
+        jmpif v19 then: b8, else: b9
+      b7():
+        v22 = load v3 -> u8
+        return v22
+      b8():
+        jmp b7()
+      b9():
+        v20 = load v3 -> u8
+        v21 = add v20, v1
+        store v21 at v3
+        jmp b7()
+    }
+    ");
+}
+
+#[test]
+fn for_loop_inclusive_with_continue() {
+    let assert_src = "
+    unconstrained fn main() {
+        for _ in 0..=255_u8 {
+            continue;
+        }
+    }
+    ";
+    let ssa = get_initial_ssa(assert_src).unwrap();
+
+    // Here we can see that the `continue` in the final iteration jumps
+    // to the end of the loop (from b4 to b5).
+    assert_ssa_snapshot!(ssa, @r"
+    brillig(inline) fn main f0 {
+      b0():
+        v1 = allocate -> &mut u1
+        store u1 1 at v1
+        jmp b1(u8 0)
+      b1(v0: u8):
+        v5 = lt v0, u8 255
+        jmpif v5 then: b2, else: b3
+      b2():
+        v9 = unchecked_add v0, u8 1
+        jmp b1(v9)
+      b3():
+        v6 = load v1 -> u1
+        v7 = unchecked_mul v6, u1 1
+        jmpif v7 then: b4, else: b5
+      b4():
+        jmp b5()
+      b5():
+        return
+    }
+    ");
+}
+
+#[test]
+fn for_loop_inclusive_max_value_to_max_value() {
+    let assert_src = "
+    fn main() -> pub u8 {
+        let mut sum = 0;
+        for i in 255_u8..=255_u8 {
+          sum += i;
+        }
+        sum
+    }
+    ";
+    let ssa = get_initial_ssa(assert_src).unwrap();
+
+    // Check that the final iteration is included
+    assert_ssa_snapshot!(ssa, @r"
+    acir(inline) fn main f0 {
+      b0():
+        v1 = allocate -> &mut u8
+        store u8 0 at v1
+        v3 = allocate -> &mut u1
+        store u1 1 at v3
+        jmp b1(u8 255)
+      b1(v0: u8):
+        v6 = lt v0, u8 255
+        jmpif v6 then: b2, else: b3
+      b2():
+        v12 = load v1 -> u8
+        v13 = add v12, v0
+        store v13 at v1
+        v15 = unchecked_add v0, u8 1
+        jmp b1(v15)
+      b3():
+        v7 = load v3 -> u1
+        v8 = unchecked_mul v7, u1 1
+        jmpif v8 then: b4, else: b5
+      b4():
+        v9 = load v1 -> u8
+        v10 = add v9, u8 255
+        store v10 at v1
+        jmp b5()
+      b5():
+        v11 = load v1 -> u8
+        return v11
+    }
+    ");
+}
```

### compiler/noirc_evaluator/src/ssa/validation/mod.rs
```diff
@@ -1029,8 +1029,22 @@ impl<'f> Validator<'f> {
                     "JmpIf conditions should have boolean type"
                 );
             }
-            TerminatorInstruction::Jmp { destination, .. } => {
+            TerminatorInstruction::Jmp { destination, arguments, call_stack: _ } => {
                 assert_ne!(*destination, entry_block, "Entry block cannot be the target of a jump");
+                let block_parameters = self.function.dfg.block_parameters(*destination);
+                assert_eq!(
+                    arguments.len(),
+                    block_parameters.len(),
+                    "Number of arguments in jmp must match number of block parameters"
+                );
+                for (argument, paramete) in arguments.iter().zip(block_parameters) {
+                    let argument_type = self.function.dfg.type_of_value(*argument);
+                    let parameter_type = self.function.dfg.type_of_value(*paramete);
+                    assert_eq!(
+                        argument_type, parameter_type,
+                        "Argument type in jmp must match block parameter type"
+                    );
+                }
             }
             TerminatorInstruction::Return { return_values, .. } => {
                 if let Some(return_data_id) = self.function.dfg.data_bus.return_data {
@@ -2008,4 +2022,32 @@ mod tests {
         ";
         let _ = Ssa::from_str(src).unwrap();
     }
+
+    #[test]
+    #[should_panic(expected = "Number of arguments in jmp must match number of block parameters")]
+    fn jmp_incorrect_block_arguments_length() {
+        let src = "
+        acir(inline) pure fn main f0 {
+          b0():
+            jmp b1()
+          b1(v0: u32):
+            return
+        }
+        ";
+        let _ = Ssa::from_str(src).unwrap();
+    }
+
+    #[test]
+    #[should_panic(expected = "Argument type in jmp must match block parameter type")]
+    fn jmp_incorrect_block_arguments_type() {
+        let src = "
+        acir(inline) pure fn main f0 {
+          b0():
+            jmp b1(u8 0)
+          b1(v0: u32):
+            return
+        }
+        ";
+        let _ = Ssa::from_str(src).unwrap();
+    }
 }
```

### compiler/noirc_frontend/src/ast/statement.rs
```diff
@@ -6,9 +6,8 @@ use iter_extended::vecmap;
 use noirc_errors::{Located, Location, Span};
 
 use super::{
-    BinaryOpKind, BlockExpression, ConstructorExpression, Expression, ExpressionKind,
-    GenericTypeArgs, IndexExpression, InfixExpression, ItemVisibility, MemberAccessExpression,
-    MethodCallExpression, UnresolvedType,
+    BlockExpression, ConstructorExpression, Expression, ExpressionKind, GenericTypeArgs,
+    IndexExpression, ItemVisibility, MemberAccessExpression, MethodCallExpression, UnresolvedType,
 };
 use crate::elaborator::types::SELF_TYPE_NAME;
 use crate::graph::CrateId;
@@ -737,31 +736,6 @@ pub struct ForBounds {
     pub inclusive: bool,
 }
 
-impl ForBounds {
-    /// Create a half-open range bounded inclusively below and exclusively above (`start..end`),
-    /// desugaring `start..=end` into `start..end+1` if necessary.
-    ///
-    /// Returns the `start` and `end` expressions.
-    pub(crate) fn into_half_open(self) -> (Expression, Expression) {
-        let end = if self.inclusive {
-            let end_location = self.end.location;
-            let end = ExpressionKind::Infix(Box::new(InfixExpression {
-                lhs: self.end,
-                operator: Located::from(end_location, BinaryOpKind::Add),
-                rhs: Expression::new(
-                    ExpressionKind::integer(FieldElement::from(1u32), None),
-                    end_location,
-                ),
-            }));
-            Expression::new(end, end_location)
-        } else {
-            self.end
-        };
-
-        (self.start, end)
-    }
-}
-
 #[derive(Debug, PartialEq, Eq, Clone)]
 pub enum ForRange {
     Range(ForBounds),
@@ -770,8 +744,8 @@ pub enum ForRange {
 
 impl ForRange {
     /// Create a half-open range, bounded inclusively below and exclusively above.
-    pub fn range(start: Expression, end: Expression) -> Self {
-        Self::Range(ForBounds { start, end, inclusive: false })
+    pub fn range(start: Expression, end: Expression, inclusive: bool) -> Self {
+        Self::Range(ForBounds { start, end, inclusive })
     }
 
     /// Create a 'for' expression taking care of desugaring a 'for e in array' loop
@@ -873,7 +847,7 @@ impl ForRange {
                 let for_loop = Statement {
                     kind: StatementKind::For(ForLoopStatement {
                         identifier: fresh_identifier,
-                        range: ForRange::range(start_range, end_range),
+                        range: ForRange::range(start_range, end_range, false),
                         block: new_block,
                         location: for_loop_location,
                     }),
```

### compiler/noirc_frontend/src/elaborator/statements.rs
```diff
@@ -224,8 +224,8 @@ impl Elaborator<'_> {
     }
 
     pub(super) fn elaborate_for(&mut self, for_loop: ForLoopStatement) -> (HirStatement, Type) {
-        let (start, end) = match for_loop.range {
-            ForRange::Range(bounds) => bounds.into_half_open(),
+        let (start, end, inclusive) = match for_loop.range {
+            ForRange::Range(bounds) => (bounds.start, bounds.end, bounds.inclusive),
             ForRange::Array(_) => {
                 let for_stmt =
                     for_loop.range.into_for(for_loop.identifier, for_loop.block, for_loop.location);
@@ -283,8 +283,13 @@ impl Elaborator<'_> {
         self.pop_scope();
         self.current_loop = old_loop;
 
-        let statement =
-            HirStatement::For(HirForStatement { start_range, end_range, block, identifier });
+        let statement = HirStatement::For(HirForStatement {
+            start_range,
+            end_range,
+            block,
+            identifier,
+            inclusive,
+        });
 
         (statement, Type::Unit)
     }
```

### compiler/noirc_frontend/src/hir/comptime/hir_to_display_ast.rs
```diff
@@ -43,6 +43,7 @@ impl HirStatement {
                 range: ForRange::range(
                     for_stmt.start_range.to_display_ast(interner),
                     for_stmt.end_range.to_display_ast(interner),
+                    for_stmt.inclusive,
                 ),
                 block: for_stmt.block.to_display_ast(interner),
                 location,
```

### compiler/noirc_frontend/src/hir/comptime/interpreter.rs
```diff
@@ -1508,7 +1508,11 @@ impl<'local, 'interner> Interpreter<'local, 'interner> {
             let start = to_i128(start_value).expect("Checked above that value is signed type");
             let end = to_i128(end_value).expect("Checked above that types match");
 
-            self.evaluate_for_loop(start..end, get_index, for_.identifier.id, for_.block)
+            if for_.inclusive {
+                self.evaluate_for_loop(start..=end, get_index, for_.identifier.id, for_.block)
+            } else {
+                self.evaluate_for_loop(start..end, get_index, for_.identifier.id, for_.block)
+            }
         } else if start_type.is_unsigned() {
             let get_index = match start_value {
                 Value::U1(_) => |i| Value::U1(i == 1),
@@ -1524,7 +1528,11 @@ impl<'local, 'interner> Interpreter<'local, 'interner> {
             let start = to_u128(start_value).expect("Checked above that value is unsigned type");
             let end = to_u128(end_value).expect("Checked above that types match");
 
-            self.evaluate_for_loop(start..end, get_index, for_.identifier.id, for_.block)
+            if for_.inclusive {
+                self.evaluate_for_loop(start..=end, get_index, for_.identifier.id, for_.block)
+            } else {
+                self.evaluate_for_loop(start..end, get_index, for_.identifier.id, for_.block)
+            }
         } else {
             let location = self.elaborator.interner.expr_location(&for_.start_range);
             let typ = start_type.into_owned();
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/builtin.rs
```diff
@@ -1947,7 +1947,7 @@ fn expr_as_for(
     })
 }
 
-// fn as_for_range(self) -> Option<(Quoted, Expr, Expr, Expr)>
+// fn as_for_range(self) -> Option<(Quoted, Expr, Expr, bool, Expr)>
 fn expr_as_for_range(
     interner: &NodeInterner,
     arguments: Vec<(Value, Location)>,
@@ -1957,14 +1957,14 @@ fn expr_as_for_range(
     expr_as(interner, arguments, return_type, location, |expr| {
         if let ExprValue::Statement(StatementKind::For(for_statement)) = expr {
             if let ForRange::Range(bounds) = for_statement.range {
-                let (from, to) = bounds.into_half_open();
                 let token = Token::Ident(for_statement.identifier.into_string());
                 let token = LocatedToken::new(token, location);
                 let identifier = Shared::new(Value::Quoted(Rc::new(vec![token])));
-                let from = Shared::new(Value::expression(from.kind));
-                let to = Shared::new(Value::expression(to.kind));
+                let from = Shared::new(Value::expression(bounds.start.kind));
+                let to = Shared::new(Value::expression(bounds.end.kind));
+                let inclusive = Shared::new(Value::Bool(bounds.inclusive));
                 let body = Shared::new(Value::expression(for_statement.block.kind));
-                Some(Value::Tuple(vec![identifier, from, to, body]))
+                Some(Value::Tuple(vec![identifier, from, to, inclusive, body]))
             } else {
                 None
             }
```

### compiler/noirc_frontend/src/hir/printer/items/hir_def.rs
```diff
@@ -580,7 +580,11 @@ impl ItemPrinter<'_, '_> {
                 self.show_hir_ident(hir_for_statement.identifier, None);
                 self.push_str(" in ");
                 self.show_hir_expression_id(hir_for_statement.start_range);
-                self.push_str("..");
+                if hir_for_statement.inclusive {
+                    self.push_str("..=");
+                } else {
+                    self.push_str("..");
+                }
                 self.show_hir_expression_id(hir_for_statement.end_range);
                 self.push(' ');
                 self.show_hir_expression_id(hir_for_statement.block);
```
