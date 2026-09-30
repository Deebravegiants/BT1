# [?] fix `debug.local` panic and incorrect value printing (#1859)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2025-06-11
Source: https://github.com/0xMiden/miden-vm/commit/5342e93b28e4fcd4983ae9e242ba8301bdb3c9c8
Type: security-commit

## Details
fix `debug.local` panic and incorrect value printing (#1859)

* refactor compilation of DebugOptions and reflect what is implemented

This should be no functional change. The `expect_value()` calls replace
the `.expect("unresolved constant")`, and the unimplemented match arms
`LocalRangeFrom` and `LocalAll` still error, but now with an accurate
message.

miden_assembly::ast::DebugOptions::compile() will be extended in a
future commit to fix other issues.

* fix: pass the real number of proc locals to DebugOptions compilation

This does not yet fully fix `debug.local.<n>.<m>`, but makes doing so
possible.

* fix: calculate local memory offsets for `debug.local.<n>.<m>` correctly

This fixes `debug.local.<n>.<m>` for real!

* fix: correctly implement `debug.local` to show all locals

* refactor: use previously unused LocalRangeFrom to repr debug.local.<n>

Should be no functional change.

* add CHANGELOG entry for debug.local fixes

## Patch
### CHANGELOG.md
```diff
@@ -27,6 +27,7 @@
 
 - `miden debug` rewind command no longer panics at clock 0 (#1751)
 - Prevent overflow in ACE circuit evaluation (#1820)
+- `debug.local` decorators no longer panic or print incorrect values (#1859)
 
 ## 0.14.0 (2025-05-07)
 
```

### assembly/src/assembler/instruction/mod.rs
```diff
@@ -529,9 +529,7 @@ impl Assembler {
 
             Instruction::Debug(options) => {
                 if self.in_debug_mode() {
-                    block_builder.push_decorator(Decorator::Debug(
-                        options.clone().try_into().expect("unresolved constant"),
-                    ))?;
+                    block_builder.push_decorator(Decorator::Debug(options.compile(proc_ctx)?))?;
                 }
             },
 
```

### assembly/src/ast/instruction/debug.rs
```diff
@@ -1,6 +1,10 @@
 use core::fmt;
 
-use crate::ast::{ImmU8, ImmU16, ImmU32};
+use crate::{
+    AssemblyError,
+    assembler::ProcedureContext,
+    ast::{ImmU8, ImmU16, ImmU32},
+};
 
 // DEBUG OPTIONS
 // ================================================================================================
@@ -18,31 +22,50 @@ pub enum DebugOptions {
     AdvStackTop(ImmU16),
 }
 
-impl crate::prettier::PrettyPrint for DebugOptions {
-    fn render(&self) -> crate::prettier::Document {
-        crate::prettier::display(self)
-    }
-}
-
-impl TryFrom<DebugOptions> for vm_core::DebugOptions {
-    type Error = ();
+impl DebugOptions {
+    /// Compiles the AST representation of a `debug` instruction into its VM representation.
+    ///
+    /// This function does not currently return any errors, but may in the future.
+    ///
+    /// See [crate::Assembler] for an overview of AST compilation.
+    pub fn compile(
+        &self,
+        proc_ctx: &ProcedureContext,
+    ) -> Result<vm_core::DebugOptions, AssemblyError> {
+        type Ast = DebugOptions;
+        type Vm = vm_core::DebugOptions;
 
-    fn try_from(options: DebugOptions) -> Result<Self, Self::Error> {
-        match options {
-            DebugOptions::StackAll => Ok(Self::StackAll),
-            DebugOptions::StackTop(ImmU8::Value(n)) => Ok(Self::StackTop(n.into_inner())),
-            DebugOptions::MemAll => Ok(Self::MemAll),
-            DebugOptions::MemInterval(ImmU32::Value(start), ImmU32::Value(end)) => {
-                Ok(Self::MemInterval(start.into_inner(), end.into_inner()))
+        // NOTE: these `ast::Immediate::expect_value()` calls *should* be safe, because by the time
+        // we're compiling debug options all immediate-constant arguments should be resolved.
+        let compiled = match self {
+            Ast::StackAll => Vm::StackAll,
+            Ast::StackTop(n) => Vm::StackTop(n.expect_value()),
+            Ast::MemAll => Vm::MemAll,
+            Ast::MemInterval(start, end) => {
+                Vm::MemInterval(start.expect_value(), end.expect_value())
             },
-            DebugOptions::LocalInterval(ImmU16::Value(start), ImmU16::Value(end)) => {
-                let start = start.into_inner();
-                let end = end.into_inner();
-                Ok(Self::LocalInterval(start, end, end - start))
+            Ast::LocalInterval(start, end) => {
+                let (start, end) = (start.expect_value(), end.expect_value());
+                Vm::LocalInterval(start, end, proc_ctx.num_locals())
             },
-            DebugOptions::AdvStackTop(ImmU16::Value(n)) => Ok(Self::AdvStackTop(n.into_inner())),
-            _ => Err(()),
-        }
+            Ast::LocalRangeFrom(index) => {
+                let index = index.expect_value();
+                Vm::LocalInterval(index, index, proc_ctx.num_locals())
+            },
+            Ast::LocalAll => {
+                let end_exclusive = Ord::min(1, proc_ctx.num_locals());
+                Vm::LocalInterval(0, end_exclusive - 1, proc_ctx.num_locals())
+            },
+            Ast::AdvStackTop(n) => Vm::AdvStackTop(n.expect_value()),
+        };
+
+        Ok(compiled)
+    }
+}
+
+impl crate::prettier::PrettyPrint for DebugOptions {
+    fn render(&self) -> crate::prettier::Document {
+        crate::prettier::display(self)
     }
 }
 
```

### assembly/src/parser/grammar.lalrpop
```diff
@@ -742,7 +742,7 @@ Debug: Instruction = {
     "debug" "." "local" <n:Imm<U16>> <m:Imm<U16>> => Instruction::Debug(DebugOptions::LocalInterval(n, m)),
     "debug" "." "local" <n:MaybeImm<U16>> => {
         match n {
-            Some(n) => Instruction::Debug(DebugOptions::LocalInterval(n.clone(), n)),
+            Some(n) => Instruction::Debug(DebugOptions::LocalRangeFrom(n)),
             None => Instruction::Debug(DebugOptions::LocalAll),
         }
     },
```

### processor/src/host/debug.rs
```diff
@@ -141,33 +141,34 @@ impl Printer {
     }
 
     /// Prints locals in provided indexes interval.
+    ///
+    /// The interval given is inclusive on *both* ends.
     fn print_local_interval(&self, process: ProcessState, interval: (u32, u32), num_locals: u32) {
-        let mut local_mem_interval = Vec::new();
-        let local_memory_offset = self.fmp - num_locals + 1;
+        let local_memory_offset = self.fmp - num_locals;
 
-        // in case start index is 0 and end index is 2^16, we should print all available locals.
-        let (start, end) = if interval.0 == 0 && interval.1 == u16::MAX as u32 {
+        let (start, end) = interval;
+        // Account for a case where start is 0 and end is 2^16. In that case we should simply print
+        // all available locals.
+        let (start, end) = if start == 0 && end == u16::MAX as u32 {
             (0, num_locals - 1)
         } else {
-            interval
+            (start, end)
         };
-        for index in start..end + 1 {
-            local_mem_interval
-                .push((index, process.get_mem_value(self.ctx, index + local_memory_offset)))
-        }
 
-        if interval.0 == 0 && interval.1 == u16::MAX as u32 {
-            println!("State of procedure locals before step {}:", self.clk)
-        } else if interval.0 == interval.1 {
-            println!("State of procedure local at index {} before step {}:", interval.0, self.clk,)
-        } else {
-            println!(
-                "State of procedure locals [{}, {}] before step {}:",
-                interval.0, interval.1, self.clk,
-            )
-        };
+        let locals: Vec<(u32, Option<Felt>)> = (start..=end)
+            .map(|local_idx| {
+                let addr = local_memory_offset + local_idx;
+                let value = process.get_mem_value(self.ctx, addr);
+                (local_idx, value)
+            })
+            .collect();
 
-        print_interval(local_mem_interval, true);
+        if start != end {
+            println!("State of procedure locals [{start}, {end}] before step {}:", self.clk);
+        } else {
+            println!("State of procedure local {start} before step {}:", self.clk);
+        }
+        print_interval(locals, true);
     }
 }
 
```
