# [?] [vm] Prevent Display recursion stack overflow on deep Values (security fix) (#427) (#19774)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-05-15
Source: https://github.com/aptos-labs/aptos-core/commit/a21a09960bc0aec97689458feee8e5d2d1822fcc
Type: security-commit

## Details
[vm] Prevent Display recursion stack overflow on deep Values (security fix) (#427) (#19774)

* [vm] Gate state dump on enable_debugging (security fix)

The interpreter's attach_state_if_invariant_violation walks every
local and operand-stack Value via Display when an InvariantViolation
fires. Display for Container recurses without depth bound, and a
deeply nested Value (e.g., a long chain of nested structs built via
Pack on user-published modules) overflows the executor thread's
2 MiB Rust stack, aborting the validator process with SIGABRT.

The dump is purely a diagnostic affordance. Gate the entire branch
on vm_config.enable_debugging -- production validators run with this
flag off (DEBUGGING_ENABLED.get().unwrap_or(false) in
prod_configs.rs), so the user-controlled attack surface is closed on
mainnet. The aptos-debugger and any dev tool that calls
set_debugging_enabled(true) still gets the full dump.

No consensus impact: the dump only ever flows into VMError.message,
which is dropped on the way to TransactionStatus for
InvariantViolation paths -- KeptVMStatus::MiscellaneousError carries
no message field, From<KeptVMStatus> for ExecutionStatus discards
the message via `message: _` on the ExecutionFailure arm, and
TransactionAuxiliaryData::detail_error_message is #[serde(skip)] in
TransactionOutput. Nothing reachable from internal_state_str's
output enters the BCS-hashed TransactionInfo, so the gate is safe
to roll out asymmetrically across the validator set.

Includes a regression test that mirrors the iterative-Drop PoC:
builds a 10,000-deep Value, then triggers TOO_MANY_TYPE_NODES via
borrow_global<W> on a wide-W resource (931 layout nodes > 512). On
a 512 KB exec thread, the pre-fix path SIGABRTs from Display
recursion inside the dump path; the fix produces
Keep(MiscellaneousError(Some(VERIFICATION_ERROR))).



* [vm] Cap Display recursion depth on Value (security fix)

`Display for Value` recurses without depth bound through
`Display for Container` and back, so any caller that formats a deeply
nested `Value` (e.g. the `internal_state_str` dump that the prior
commit gated on `enable_debugging`) blows the formatting thread's
Rust stack and SIGABRTs the validator process. The prior commit
removes the only known user-controlled trigger; this commit removes
the underlying recursion bug class so that future `format!("{}", v)`
sites cannot reintroduce it.

Approach: extract each recursive `Display` body into a free function
that threads an explicit `depth` parameter (`fmt_value` /
`fmt_container` / `fmt_locals` in `values_impl.rs`, `fmt_closure` in
`function_values_impl.rs`). The trait `Display::fmt` impls become
1-line wrappers that call the helper with depth 0. Each helper
checks `depth > MAX_DISPLAY_DEPTH` at entry and emits `"..."`
instead of recursing. `MAX_DISPLAY_DEPTH = 8` is conservative; legit
diagnostic dumps of mainnet-shaped values fit comfortably below it.

A small `DepthDisplay<'a>(&'a Value, usize)` adapter keeps the
existing `format!` / `Vec<String>::join` plumbing in `Locals` and
`Closure` intact -- the only call-site changes there are
`val` -> `DepthDisplay(val, depth + 1)` and
`v.to_string()` -> `DepthDisplay(v, depth + 1).to_string()`.
`ContainerRef`, `IndexedRef`, and `display_list_of_items` are
untouched (already shallow / used only by primitive-`Vec` variants).

Audit of consensus exposure: the only `Display`-on-`Value` sites
reachable from non-test code are `internal_state_str`
(`interpreter.rs:1761`, gated by `enable_debugging`) and the
serialization-failure path in `into_effects` (`data_cache.rs:216`,
partially guarded by `enable_closure_depth_check`). Both write
output to `VMError.message`, which is dropped on the way to
`TransactionStatus` for the `InvariantViolation` paths
(`KeptVMStatus::MiscellaneousError` carries no message;
`From<KeptVMStatus> for ExecutionStatus` drops the message via
`message: _` for `ExecutionFailure`; and
`TransactionAuxiliaryData::detail_error_message` is `#[serde(skip)]`
in `TransactionOutput`). Nothing reachable from `Display for Value`
enters the BCS-hashed `TransactionInfo`, so the bound is safe to
deploy asymmetrically across the validator set with no feature gate.
The publicly-callable `aptos_std::string_utils::format` /
`format_debug` natives use their own typed dispatch over
`MoveTypeLayout` and never call `Display for Value`; the move-stdlib
`debug::print` native is `#[cfg(feature = "testing")]`. The PoC test
from the prior commit continues to pass with this change alone (gate
temporarily disabled to verify).

Also rename `derived_string_snapshot::to_utf8_bytes` ->
`to_utf8_bytes_for_test` and document it -- the sole caller is a
unit test in `block-executor`. The production path constructs
`DerivedStringSnapshot` values through other means; surfacing the
test-only nature of this helper in its name prevents future
production callers from accidentally pulling in a `Display`-based
encoder.



---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

### aptos-move/aptos-vm/src/move_vm_ext/session/mod.rs
```diff
@@ -197,19 +197,7 @@ where
                 } else {
                     StatusCode::INTERNAL_TYPE_ERROR
                 };
-                // Note: When enable_closure_depth_check is enabled, do not format
-                // `value` here - deeply nested closures can cause stack overflow
-                // during Display formatting.
-                let enable_closure_depth_check = module_storage
-                    .runtime_environment()
-                    .vm_config()
-                    .enable_closure_depth_check;
-                let message = if enable_closure_depth_check {
-                    "Error when serializing resource.".to_string()
-                } else {
-                    format!("Error when serializing resource {}.", value)
-                };
-                PartialVMError::new(status_code).with_message(message)
+                PartialVMError::new(status_code).with_message("Error when serializing resource.")
             })
         };
 
```

### aptos-move/block-executor/src/view.rs
```diff
@@ -2021,7 +2021,9 @@ mod test {
     use move_vm_types::{
         delayed_values::{
             delayed_field_id::DelayedFieldID,
-            derived_string_snapshot::{bytes_and_width_to_derived_string_struct, to_utf8_bytes},
+            derived_string_snapshot::{
+                bytes_and_width_to_derived_string_struct, to_utf8_bytes_for_test,
+            },
         },
         values::{Struct, Value},
     };
@@ -2649,7 +2651,7 @@ mod test {
     }
 
     fn create_derived_value(value: impl ToString, width: usize) -> Value {
-        bytes_and_width_to_derived_string_struct(to_utf8_bytes(value), width).unwrap()
+        bytes_and_width_to_derived_string_struct(to_utf8_bytes_for_test(value), width).unwrap()
     }
 
     fn create_struct_value(inner: Value) -> Value {
```

### aptos-move/e2e-move-tests/src/tests/memory_quota.rs
```diff
@@ -360,3 +360,184 @@ fn test_poc_nested_struct_drop_overflow_thread_diff() {
 
     handle.join().unwrap();
 }
+
+/// Generates a Move module with a resource `W` whose expanded layout exceeds
+/// `layout_max_size = 512`, so any `borrow_global<W>(...)` triggers
+/// `TOO_MANY_TYPE_NODES` from the layout converter. The status sits in the
+/// Verification range and gets remapped to `VERIFICATION_ERROR` (InvariantViolation),
+/// which is exactly what reaches the `internal_state_str` dump path inside
+/// `attach_state_if_invariant_violation`.
+///
+/// Layout count when expanded:
+///   1 (W) + 30 (Ti structs) + 30*30 (u8 fields inside Ti's) = 931  > 512.
+/// Each `Ti` is a distinct struct so the local layout cache cannot dedup them.
+///
+/// Also exposes `trigger<T: drop>(_v: T)` which takes the deep value as its
+/// sole local: at the moment `borrow_global<W>` fails inside `trigger`, the
+/// deep value sits in `current_frame.locals` and the Display walk overflows
+/// the exec thread's stack.
+fn gen_wide_w_module(addr: &str) -> String {
+    let num_tiers = 30;
+    let fields_per_tier = 30;
+    let mut lines = vec![format!("module {}::wide {{", addr)];
+
+    for i in 0..num_tiers {
+        let fields: Vec<String> = (0..fields_per_tier)
+            .map(|j| format!("a{}: u8", j))
+            .collect();
+        lines.push(format!(
+            "    struct T{} has store, drop {{ {} }}",
+            i,
+            fields.join(", ")
+        ));
+    }
+
+    let fields: Vec<String> = (0..num_tiers).map(|i| format!("f{}: T{}", i, i)).collect();
+    lines.push(format!(
+        "    struct W has key, drop {{ {} }}",
+        fields.join(", ")
+    ));
+
+    lines.push("    public fun trigger<T: drop>(_v: T) acquires W {".into());
+    lines.push("        let _r = borrow_global<W>(@attacker);".into());
+    lines.push("    }".into());
+
+    lines.push("}".into());
+    lines.join("\n")
+}
+
+// NOTE:
+// Same `--release` rationale as the Drop PoC above — debug builds use much larger
+// per-frame stack, which would distort the overflow shape vs. mainnet.
+//
+// RUN: cargo test -p e2e-move-tests test_poc_display_recursion_overflow_thread_diff --release -- --nocapture
+#[test]
+fn test_poc_display_recursion_overflow_thread_diff() {
+    // Same thread-diff pattern as the Drop PoC: 8MB thread for compilation,
+    // 512KB thread for execution.
+    //
+    // Pre-fix: deep value is built into `wide::trigger`'s local 0 via the function
+    //   parameter; `borrow_global<W>` then fails with TOO_MANY_TYPE_NODES; the dump
+    //   path inside `attach_state_if_invariant_violation` calls `Display` on the
+    //   deep value, recursing past the 512KB guard page → SIGABRT (surfaces as a
+    //   thread panic on `join` on platforms where Rust's stack-overflow handler
+    //   reroutes through panic; otherwise the process aborts entirely and the test
+    //   binary exits with non-zero).
+    // Post-fix: dump path is gated and the exec thread joins cleanly with some
+    //   `TransactionStatus`. We don't assert a specific status code — the point
+    //   is the absence of a crash.
+    let handle = std::thread::Builder::new()
+        .name("compile-thread".into())
+        .stack_size(8 * 1024 * 1024)
+        .spawn(|| {
+            let mut h = MoveHarnessSend::new();
+            let addr = "0xbeef";
+            let acc = h.new_account_at(AccountAddress::from_hex_literal(addr).unwrap());
+
+            // Mirrors the Drop PoC: 10 modules x 1000 nested structs = 10,000 deep.
+            // With a 512KB exec stack and ~64 B per Display frame in release, this
+            // is comfortably past the overflow threshold pre-fix.
+            let num_modules = 10;
+            let structs_per_module = 1000;
+
+            let base_dir = std::env::temp_dir()
+                .join(format!("display_recursion_{}", std::process::id()));
+            std::fs::create_dir_all(&base_dir).unwrap();
+            let mut prev: Option<(String, usize, std::path::PathBuf)> = None;
+
+            // === Step 1: Publish chunk_0..chunk_{N-1}, each chained to the previous.
+            for chunk in 0..num_modules {
+                let pkg_name = format!("chunk_{}", chunk);
+                let mut builder = PackageBuilder::new(&pkg_name);
+                builder.add_alias("attacker", addr);
+
+                if let Some((_, _, ref prev_path)) = prev {
+                    builder.add_local_dep(
+                        &format!("chunk_{}", chunk - 1),
+                        prev_path.to_str().unwrap(),
+                    );
+                }
+                let prev_ref = prev
+                    .as_ref()
+                    .map(|(name, count, _)| (name.as_str(), *count));
+                let (mod_name, source) =
+                    gen_nested_module("attacker", chunk, structs_per_module, prev_ref);
+                builder.add_source(&format!("chunk_{}", chunk), &source);
+                let pkg_path = base_dir.join(&pkg_name);
+                builder.write_to_disk(&pkg_path).unwrap();
+                let result = h.publish_package(&acc, &pkg_path);
+                assert_success!(result);
+                println!("Published chunk_{} ({} structs)", chunk, structs_per_module);
+                prev = Some((mod_name, structs_per_module, pkg_path));
+            }
+
+            // === Step 2: Publish the wide-W module (the invariant-violation trigger).
+            let wide_source = gen_wide_w_module("attacker");
+            let mut wide_builder = PackageBuilder::new("wide_w");
+            wide_builder.add_alias("attacker", addr);
+            wide_builder.add_source("wide", &wide_source);
+            let wide_path = base_dir.join("wide_w");
+            wide_builder.write_to_disk(&wide_path).unwrap();
+            let result = h.publish_package(&acc, &wide_path);
+            assert_success!(result);
+            println!("Published wide_w");
+
+            // === Step 3: Publish the entry module. `attack::run` builds the deep
+            // value and immediately hands it to `wide::trigger`, so it lands in the
+            // current frame's locals just before the trigger fires.
+            let (ref last_module, _, ref last_path) = *prev.as_ref().unwrap();
+            let mut entry_builder = PackageBuilder::new("attack");
+            entry_builder.add_alias("attacker", addr);
+            entry_builder.add_local_dep(
+                &format!("chunk_{}", num_modules - 1),
+                last_path.to_str().unwrap(),
+            );
+            entry_builder.add_local_dep("wide_w", wide_path.to_str().unwrap());
+            let entry_source = format!(
+                "module attacker::attack {{\n    \
+                     use attacker::{};\n    \
+                     use attacker::wide;\n    \
+                     public entry fun run() {{\n        \
+                         wide::trigger<{}::S{}>({}::build());\n    \
+                     }}\n\
+                 }}",
+                last_module,
+                last_module,
+                structs_per_module - 1,
+                last_module
+            );
+            entry_builder.add_source("attack", &entry_source);
+            let entry_path = base_dir.join("attack");
+            entry_builder.write_to_disk(&entry_path).unwrap();
+            let result = h.publish_package(&acc, &entry_path);
+            assert_success!(result);
+            println!("Published attack");
+
+            // === Step 4: Execute on a 512KB thread (same downsizing as the Drop PoC).
+            const EXEC_STACK_BYTES: usize = 512 * 1024;
+            println!("Spawning {}-byte execution thread...", EXEC_STACK_BYTES);
+            let exec_handle = std::thread::Builder::new()
+                .name("exec-downsized".into())
+                .stack_size(EXEC_STACK_BYTES)
+                .spawn(move || {
+                    h.run_entry_function(
+                        &acc,
+                        str::parse(&format!("{}::attack::run", addr)).unwrap(),
+                        vec![],
+                        vec![],
+                    )
+                })
+                .unwrap();
+
+            // Pre-fix: stack overflow inside attach_state_if_invariant_violation;
+            //   `join` surfaces as Err on platforms where Rust reroutes the SIGSEGV
+            //   through a thread panic, and the expect() fires.
+            // Post-fix: dump path is gated; exec thread joins cleanly.
+            let status = exec_handle
+                .join()
+                .expect("execution thread panicked — likely Display recursion stack overflow in attach_state_if_invariant_violation");
+            println!("Post-fix txn status: {:?}", status);
+        })
+        .unwrap();
+    handle.join().unwrap();
+}
```

### third_party/move/move-vm/runtime/src/data_cache.rs
```diff
@@ -251,19 +251,8 @@ impl TransactionDataCache {
                 .serialize(&value, &layout)?
                 .map(Into::into)
                 .ok_or_else(|| {
-                    // Note: When enable_closure_depth_check is enabled, do not format
-                    // `value` here - deeply nested closures can cause stack overflow
-                    // during Display formatting.
-                    let enable_closure_depth_check = module_storage
-                        .runtime_environment()
-                        .vm_config()
-                        .enable_closure_depth_check;
-                    let message = if enable_closure_depth_check {
-                        "Error when serializing resource.".to_string()
-                    } else {
-                        format!("Error when serializing resource {}.", value)
-                    };
-                    PartialVMError::new(StatusCode::INTERNAL_TYPE_ERROR).with_message(message)
+                    PartialVMError::new(StatusCode::INTERNAL_TYPE_ERROR)
+                        .with_message("Error when serializing resource.")
                 })
         };
         self.into_custom_effects(&resource_converter)
```

### third_party/move/move-vm/runtime/src/interpreter.rs
```diff
@@ -1656,9 +1656,15 @@ where
         }
 
         // We do not consider speculative invariant violations.
+        // The Display walk over `current_frame.locals` / operand stack inside
+        // `internal_state_str` is unbounded — a deeply nested Move value can
+        // recurse past the executor thread's stack guard page (SIGABRT). The
+        // dump is a diagnostic affordance, so gate it on `enable_debugging`;
+        // production validators run with this off and never reach the walk.
         if err.status_type() == StatusType::InvariantViolation
             && err.major_status() != StatusCode::SPECULATIVE_EXECUTION_ABORT_ERROR
             && !errors::is_stable_test_display()
+            && self.vm_config.enable_debugging
         {
             let location = err.location().clone();
             let state = self.internal_state_str(current_frame);
```

### third_party/move/move-vm/types/src/delayed_values/derived_string_snapshot.rs
```diff
@@ -40,7 +40,12 @@ pub fn is_derived_string_struct_layout(layout: &MoveTypeLayout) -> bool {
     false
 }
 
-pub fn to_utf8_bytes(value: impl ToString) -> Vec<u8> {
+/// Test-only helper: encodes a value via its `Display` and returns the UTF-8
+/// bytes. Used in `block-executor`'s tests to construct fixture
+/// `DerivedStringSnapshot` values. Not called from production code; the
+/// production path constructs these values by other means (e.g. via the
+/// aggregator natives in `aptos-move/framework`).
+pub fn to_utf8_bytes_for_test(value: impl ToString) -> Vec<u8> {
     value.to_string().into_bytes()
 }
 
```

### third_party/move/move-vm/types/src/values/function_values_impl.rs
```diff
@@ -1,7 +1,9 @@
 // Copyright (c) Aptos Foundation
 // Licensed pursuant to the Innovation-Enabling Source Code License, available at https://github.com/aptos-labs/aptos-core/blob/main/LICENSE
 
-use crate::values::{DeserializationSeed, SerializationReadyValue, VMValueCast, Value};
+use crate::values::{
+    DepthDisplay, DeserializationSeed, SerializationReadyValue, VMValueCast, Value,
+};
 use better_any::Tid;
 use move_binary_format::errors::{PartialVMError, PartialVMResult};
 use move_core_types::{
@@ -96,13 +98,20 @@ impl Debug for Closure {
     }
 }
 
+pub(crate) fn fmt_closure(c: &Closure, f: &mut Formatter<'_>, depth: usize) -> fmt::Result {
+    let Closure(fun, captured) = c;
+    let captured = fun.closure_mask().format_arguments(
+        captured
+            .iter()
+            .map(|v| DepthDisplay(v, depth + 1).to_string())
+            .collect(),
+    );
+    write!(f, "{}({})", fun.to_canonical_string(), captured.join(", "))
+}
+
 impl Display for Closure {
     fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
-        let Self(fun, captured) = self;
-        let captured = fun
-            .closure_mask()
-            .format_arguments(captured.iter().map(|v| v.to_string()).collect());
-        write!(f, "{}({})", fun.to_canonical_string(), captured.join(", "))
+        fmt_closure(self, f, 0)
     }
 }
 
```

### third_party/move/move-vm/types/src/values/values_impl.rs
```diff
@@ -4728,37 +4728,61 @@ impl Debug for Value {
 *
 **************************************************************************************/
 
-impl Display for Value {
+/// Cap recursive `Display` of a `Value` so deeply nested values cannot blow the
+/// formatting thread's stack. Every recursive path (Value↔Container, Locals→Value,
+/// Closure→Value) flows through `fmt_value`, so a single check at its entry is
+/// sufficient; intermediate `fmt_*` helpers just thread `depth + 1` through.
+const MAX_DISPLAY_DEPTH: usize = 8;
+
+/// Adapter that re-enters depth-bounded `Display` on a `&Value`. Lets call sites
+/// that build up `format!` / `Vec<String>` plumbing (e.g. `Locals`, `Closure`)
+/// keep their existing shape while still participating in depth bounding.
+pub(crate) struct DepthDisplay<'a>(pub &'a Value, pub usize);
+
+impl<'a> Display for DepthDisplay<'a> {
     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
-        match self {
-            Self::Invalid => write!(f, "Invalid"),
+        fmt_value(self.0, f, self.1)
+    }
+}
 
-            Self::U8(x) => write!(f, "U8({})", x),
-            Self::U16(x) => write!(f, "U16({})", x),
-            Self::U32(x) => write!(f, "U32({})", x),
-            Self::U64(x) => write!(f, "U64({})", x),
-            Self::U128(x) => write!(f, "U128({})", x),
-            Self::U256(x) => write!(f, "U256({})", x),
-            Self::I8(x) => write!(f, "I8({})", x),
-            Self::I16(x) => write!(f, "I16({})", x),
-            Self::I32(x) => write!(f, "I32({})", x),
-            Self::I64(x) => write!(f, "I64({})", x),
-            Self::I128(x) => write!(f, "I128({})", x),
-            Self::I256(x) => write!(f, "I256({})", x),
-            Self::Bool(x) => write!(f, "{}", x),
-            Self::Address(addr) => write!(f, "Address({})", addr.short_str_lossless()),
-
-            Self::Container(r) => write!(f, "{}", r),
-
-            Self::ContainerRef(r) => write!(f, "{}", r),
-            Self::IndexedRef(r) => write!(f, "{}", r),
-
-            Self::ClosureValue(c) => write!(f, "{}", c),
-
-            // Display information must be deterministic, so we cannot print
-            // inner fields.
-            Self::DelayedFieldID { .. } => write!(f, "Delayed(?)"),
-        }
+fn fmt_value(v: &Value, f: &mut fmt::Formatter, depth: usize) -> fmt::Result {
+    if depth > MAX_DISPLAY_DEPTH {
+        return write!(f, "...");
+    }
+    match v {
+        Value::Invalid => write!(f, "Invalid"),
+
+        Value::U8(x) => write!(f, "U8({})", x),
+        Value::U16(x) => write!(f, "U16({})", x),
+        Value::U32(x) => write!(f, "U32({})", x),
+        Value::U64(x) => write!(f, "U64({})", x),
+        Value::U128(x) => write!(f, "U128({})", x),
+        Value::U256(x) => write!(f, "U256({})", x),
+        Value::I8(x) => write!(f, "I8({})", x),
+        Value::I16(x) => write!(f, "I16({})", x),
+        Value::I32(x) => write!(f, "I32({})", x),
+        Value::I64(x) => write!(f, "I64({})", x),
+        Value::I128(x) => write!(f, "I128({})", x),
+        Value::I256(x) => write!(f, "I256({})", x),
+        Value::Bool(x) => write!(f, "{}", x),
+        Value::Address(addr) => write!(f, "Address({})", addr.short_str_lossless()),
+
+        Value::Container(r) => fmt_container(r, f, depth + 1),
+
+        Value::ContainerRef(r) => write!(f, "{}", r),
+        Value::IndexedRef(r) => write!(f, "{}", r),
+
+        Value::ClosureValue(c) => super::function_values_impl::fmt_closure(c, f, depth + 1),
+
+        // Display information must be deterministic, so we cannot print
+        // inner fields.
+        Value::DelayedFieldID { .. } => write!(f, "Delayed(?)"),
+    }
+}
+
+impl Display for Value {
+    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
+        fmt_value(self, f, 0)
     }
 }
 
@@ -4796,47 +4820,54 @@ impl Display for IndexedRef {
     }
 }
 
-impl Display for Container {
-    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
-        write!(f, "(container: ")?;
+fn fmt_container(c: &Container, f: &mut fmt::Formatter, depth: usize) -> fmt::Result {
+    write!(f, "(container: ")?;
 
-        match self {
-            Self::Locals(r) | Self::Vec(r) | Self::Struct(r) => {
-                display_list_of_items(r.borrow().iter(), f)
-            },
-            Self::VecU8(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecU16(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecU32(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecU64(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecU128(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecU256(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecI8(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecI16(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecI32(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecI64(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecI128(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecI256(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecBool(r) => display_list_of_items(r.borrow().iter(), f),
-            Self::VecAddress(r) => display_list_of_items(r.borrow().iter(), f),
-        }?;
+    match c {
+        Container::Locals(r) | Container::Vec(r) | Container::Struct(r) => {
+            display_list_of_items(r.borrow().iter().map(|v| DepthDisplay(v, depth + 1)), f)
+        },
+        Container::VecU8(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecU16(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecU32(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecU64(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecU128(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecU256(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecI8(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecI16(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecI32(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecI64(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecI128(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecI256(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecBool(r) => display_list_of_items(r.borrow().iter(), f),
+        Container::VecAddress(r) => display_list_of_items(r.borrow().iter(), f),
+    }?;
+
+    write!(f, ")")
+}
 
-        write!(f, ")")
+impl Display for Container {
+    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
+        fmt_container(self, f, 0)
     }
 }
 
+fn fmt_locals(l: &Locals, f: &mut fmt::Formatter, depth: usize) -> fmt::Result {
+    write!(
+        f,
+        "{}",
+        l.0.borrow()
+            .iter()
+            .enumerate()
+            .map(|(idx, val)| format!("[{}] {}", idx, DepthDisplay(val, depth + 1)))
+            .collect::<Vec<_>>()
+            .join("\n")
+    )
+}
+
 impl Display for Locals {
     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
-        write!(
-            f,
-            "{}",
-            self.0
-                .borrow()
-                .iter()
-                .enumerate()
-                .map(|(idx, val)| format!("[{}] {}", idx, val))
-                .collect::<Vec<_>>()
-                .join("\n")
-        )
+        fmt_locals(self, f, 0)
     }
 }
 
```
