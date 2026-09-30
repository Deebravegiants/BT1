# [?] [vm] Iterative Drop for nested Move values (security fix) (#415)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-24
Source: https://github.com/aptos-labs/aptos-core/commit/d0d10695c5df010fb632762f700b770e064b7fe2
Type: security-commit

## Details
[vm] Iterative Drop for nested Move values (security fix) (#415)

* [vm] Iterative Drop for nested Move values

Deeply-nested Move values (long chains of nested structs) previously
overflowed the Rust stack when dropped via compiler-generated recursive
Drop, crashing the validator with SIGABRT.

Wraps the three recursive Container variants (Locals, Vec, Struct) in
a NestedValues newtype whose custom Drop walks nested containers via a
heap work-stack instead of Rust recursion. The inner Vec<Value> is
drained in place via Rc::get_mut so no sentinel Rc is ever allocated,
and the work stack only allocates when nested work is actually queued.

Includes a regression test that previously SIGABRT'd on a small thread
stack; now cleanly fails with VM_MAX_VALUE_DEPTH_REACHED.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* Address review comments

- into_rc: use ManuallyDrop + ptr::read to skip the sentinel Rc allocation
  (george)
- NestedValues::drop: exhaustive match on Value and Container (george)
- NestedValues::drop: vec![] nit (george)
- PoC test: assert Keep(MiscellaneousError(VM_MAX_VALUE_DEPTH_REACHED))
  and fail on thread panic (bugbot + george)
- PoC test: spell out 512 KB (was mis-parenthesized as 2*1024*1024/4),
  explain that both module count (10 vs 40) and exec thread stack size
  (512KB vs 2MB) are downsized 4x to keep the test fast while preserving
  the overflow shape (bugbot + user)
- PoC test: drop commented-out gas-schedule block (george)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### aptos-move/e2e-move-tests/src/tests/memory_quota.rs
```diff
@@ -173,3 +173,190 @@ fn add_vec_to_table() {
         )))
     ));
 }
+
+use crate::MoveHarnessSend;
+use aptos_package_builder::PackageBuilder;
+
+/// Generates Move source for a module with `count` nested structs.
+/// If `prev_module` is provided, S0 wraps the deepest struct from that module.
+/// Returns (module_name, source_code).
+fn gen_nested_module(
+    addr: &str,
+    chunk_idx: usize,
+    count: usize,
+    prev_module: Option<(&str, usize)>,
+) -> (String, String) {
+    let module_name = format!("chunk_{}", chunk_idx);
+    let mut lines = vec![format!("module {}::{} {{", addr, module_name)];
+
+    // S0: either wraps previous module's deepest struct, or has a u8 field
+    if let Some((prev_mod, prev_count)) = prev_module {
+        lines.push(format!("    use {}::{};", addr, prev_mod));
+        lines.push(format!(
+            "    struct S0 has drop {{ i: {}::S{} }}",
+            prev_mod,
+            prev_count - 1
+        ));
+    } else {
+        lines.push("    struct S0 has drop { val: u8 }".to_string());
+    }
+
+    // S1..S(count-1): each wraps the previous
+    for i in 1..count {
+        lines.push(format!("    struct S{} has drop {{ i: S{} }}", i, i - 1));
+    }
+
+    // build() function: constructs the full nesting chain
+    lines.push(String::new());
+    lines.push(format!("    public fun build(): S{} {{", count - 1));
+    if let Some(prev) = prev_module {
+        lines.push(format!("        let s0 = S0 {{ i: {}::build() }};", prev.0));
+    } else {
+        lines.push("        let s0 = S0 { val: 0 };".to_string());
+    }
+    for i in 1..count {
+        lines.push(format!("        let s{} = S{} {{ i: s{} }};", i, i, i - 1));
+    }
+    lines.push(format!("        s{}", count - 1));
+    lines.push("    }".to_string());
+
+    lines.push("}".to_string());
+    (module_name, lines.join("\n"))
+}
+
+// NOTE:
+// Must use `--release` to mimick mainnet `Drop` recursion cost.
+// If --release is not used, the default debug uses ~500+ bytes
+// per Drop which is optimistically unrealistic. With release,
+// it uses Drop cost identical to mainnet (~64 bytes)
+
+// RUN: cargo test -p e2e-move-tests test_poc_nested_struct_drop_overflow_thread_diff --release -- --nocapture
+#[test]
+fn test_poc_nested_struct_drop_overflow_thread_diff() {
+    // Run everything on an 8MB thread so compilation succeeds,
+    // then spawn a 2MB thread for execution only.
+    let handle = std::thread::Builder::new()
+        .name("compile-thread".into())
+        .stack_size(8 * 1024 * 1024) // 8MB for compilation
+        .spawn(|| {
+            // === Step 1: Setup default harness ===
+            let mut h = MoveHarnessSend::new();
+            let addr = "0xbeef";
+            let acc = h.new_account_at(AccountAddress::from_hex_literal(addr).unwrap());
+
+            // Original bug-bounty PoC used 40 modules x 1000 structs = 40,000 depth
+            // against the validator's 2MB rayon thread (40k x ~64 B ≈ 2.5MB → overflow).
+            // Here we downsize BOTH to 1/4 to keep the test fast while preserving the
+            // overflow property:
+            //   - 10 modules x 1000 structs = 10,000 depth
+            //   - 512KB execution thread (see Step 4 below)
+            //   - 10k x ~64 B ≈ 640KB → overflows 512KB, same as mainnet shape.
+            let num_modules = 10;
+            let structs_per_module = 1000;
+
+            let base_dir = std::env::temp_dir()
+                .join(format!("nested_drop_thread_diff_{}", std::process::id()));
+            std::fs::create_dir_all(&base_dir).unwrap();
+            let mut prev: Option<(String, usize, std::path::PathBuf)> = None;
+
+            // === Step 2: Publish each chunk module in a separate tx ===
+            // If not in separate txs, this will hit max tx size limit
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
+
+                let prev_ref = prev
+                    .as_ref()
+                    .map(|(name, count, _)| (name.as_str(), *count));
+                let (mod_name, source) =
+                    gen_nested_module("attacker", chunk, structs_per_module, prev_ref);
+                builder.add_source(&format!("chunk_{}", chunk), &source);
+
+                let pkg_path = base_dir.join(&pkg_name);
+                builder.write_to_disk(&pkg_path).unwrap();
+
+                let result = h.publish_package(&acc, &pkg_path);
+                assert_success!(result);
+                println!("Published chunk_{} ({} structs)", chunk, structs_per_module);
+
+                prev = Some((mod_name, structs_per_module, pkg_path));
+            }
+
+            // === Step 3: Publish entry module ===
+            let (ref last_module, _, ref last_path) = *prev.as_ref().unwrap();
+            let mut entry_builder = PackageBuilder::new("attack");
+            entry_builder.add_alias("attacker", addr);
+            entry_builder.add_local_dep(
+                &format!("chunk_{}", num_modules - 1),
+                last_path.to_str().unwrap(),
+            );
+            let entry_source = format!(
+                "module attacker::attack {{\n    \
+                     use attacker::{};\n    \
+                     public entry fun run() {{\n        \
+                         let _v = {}::build();\n    \
+                     }}\n\
+                 }}",
+                last_module, last_module
+            );
+            entry_builder.add_source("attack", &entry_source);
+            let entry_path = base_dir.join("attack");
+            entry_builder.write_to_disk(&entry_path).unwrap();
+
+            let result = h.publish_package(&acc, &entry_path);
+            assert_success!(result);
+
+            let total_depth = num_modules * structs_per_module;
+            println!(
+                "All modules published. Total depth: {} ({} modules x {} structs)",
+                total_depth, num_modules, structs_per_module
+            );
+
+            // === Step 4: Execute on a 512KB thread (1/4 of validator's 2MB rayon
+            // default — downsized together with `num_modules` above to keep the test
+            // fast while preserving the overflow shape from mainnet). ===
+            const EXEC_STACK_BYTES: usize = 512 * 1024;
+            println!("Spawning {}-byte execution thread...", EXEC_STACK_BYTES);
+            let exec_handle = std::thread::Builder::new()
+                .name("exec-downsized".into())
+                .stack_size(EXEC_STACK_BYTES)
+                .spawn(move || {
+                    println!("Executing attack on downsized thread...");
+                    h.run_entry_function(
+                        &acc,
+                        str::parse(&format!("{}::attack::run", addr)).unwrap(),
+                        vec![],
+                        vec![],
+                    )
+                })
+                .unwrap();
+
+            // The fix must produce a clean VM error instead of an uncatchable SIGABRT.
+            // `Err` on join means the thread panicked (stack overflow on platforms
+            // where that surfaces as a thread panic), which would be a regression.
+            let status = exec_handle
+                .join()
+                .expect("execution thread panicked — possible stack overflow regression");
+            assert!(
+                matches!(
+                    status,
+                    TransactionStatus::Keep(ExecutionStatus::MiscellaneousError(Some(
+                        StatusCode::VM_MAX_VALUE_DEPTH_REACHED
+                    )))
+                ),
+                "expected VM_MAX_VALUE_DEPTH_REACHED, got: {:?}",
+                status
+            );
+        })
+        .unwrap();
+
+    handle.join().unwrap();
+}
```

### third_party/move/move-vm/types/src/values/values_impl.rs
```diff
@@ -125,6 +125,164 @@ pub enum Value {
     ClosureValue(Closure),
 }
 
+/// A heap-shared, mutable, recursively-droppable collection of Move values.
+///
+/// Wraps `Rc<RefCell<Vec<Value>>>` and carries a custom `Drop` that drains a deeply-nested
+/// value iteratively (via a heap work-stack) instead of using the compiler's recursive drop.
+/// This prevents a stack overflow when a deep Value chain is dropped via RAII.
+///
+/// Deref to `Rc<RefCell<Vec<Value>>>` keeps the common `.borrow()`/`.borrow_mut()` call
+/// sites unchanged. To move the inner Rc out (e.g., for `take_unique_ownership`), call
+/// [`NestedValues::into_rc`]. To clone (share), use `.clone()`.
+#[derive(Debug)]
+pub(crate) struct NestedValues(Rc<RefCell<Vec<Value>>>);
+
+impl NestedValues {
+    #[inline]
+    pub(crate) fn new(vals: Vec<Value>) -> Self {
+        Self(Rc::new(RefCell::new(vals)))
+    }
+
+    #[inline]
+    pub(crate) fn from_rc(rc: Rc<RefCell<Vec<Value>>>) -> Self {
+        Self(rc)
+    }
+
+    /// Extracts the inner `Rc` without running the custom `Drop`.
+    ///
+    /// Bypasses `Drop` (which would otherwise drain the contents) so we avoid both the
+    /// work and the sentinel Rc allocation on every value cast / pack unwrap. Uses the
+    /// standard `ManuallyDrop` + `ptr::read` destructuring idiom (see the `ManuallyDrop`
+    /// docs and `Box::into_raw` / `Pin::into_inner_unchecked` in std).
+    ///
+    /// NOTE (maintainers): this leaves no per-field `Drop` running on `self`. It is
+    /// sound only because `self.0` is `Rc<...>` which is trivially bitwise-movable, and
+    /// because `NestedValues` has exactly one field. If another non-trivial field is
+    /// added, this function must be updated to drop that field (e.g. via
+    /// `std::ptr::drop_in_place` on that field) or leak it.
+    #[inline]
+    pub(crate) fn into_rc(self) -> Rc<RefCell<Vec<Value>>> {
+        let this = std::mem::ManuallyDrop::new(self);
+        // SAFETY: `this` is `ManuallyDrop`, so its `Drop` (which would recurse/drain the
+        // inner Vec) never runs. The bits of `this.0` are therefore never re-observed
+        // after this read — in particular, they are never decremented again — and the
+        // returned `Rc` is the sole owner of the refcount that `this.0` previously held.
+        // No panic is possible between the `ManuallyDrop::new` and the return, so there
+        // is no unwinding window.
+        unsafe { std::ptr::read(&this.0) }
+    }
+}
+
+impl Clone for NestedValues {
+    #[inline]
+    fn clone(&self) -> Self {
+        Self(Rc::clone(&self.0))
+    }
+}
+
+impl std::ops::Deref for NestedValues {
+    type Target = Rc<RefCell<Vec<Value>>>;
+
+    #[inline]
+    fn deref(&self) -> &Self::Target {
+        &self.0
+    }
+}
+
+/// Iterative drop: walk nested `Value::Container(Container::{Locals,Vec,Struct})` via a
+/// heap work-stack rather than the Rust call stack. Only uniquely-owned Rcs are decomposed;
+/// shared containers (refcount > 1) fall through to the default Rc drop (refcount decrement).
+///
+/// We drain the inner `Vec<Value>` in place via `Rc::get_mut` — no replacement `Rc`/`RefCell`
+/// is ever allocated. The work stack holds owned `Vec<Value>`s rather than `Rc<...>`s, so the
+/// only possible heap allocation is the stack itself, which stays at `Vec::new()` capacity 0
+/// until the first push.
+impl Drop for NestedValues {
+    fn drop(&mut self) {
+        // Drain the root level in place: if we hold the sole reference, take the inner
+        // `Vec<Value>` out, leaving the `RefCell<Vec>` containing an empty Vec.  The
+        // `Rc` then drops normally (refcount 1 → 0, frees the RcBox) at the end of
+        // this function. No sentinel allocation.
+        let Some(cell) = Rc::get_mut(&mut self.0) else {
+            // Shared: other holders still reference this container; their view of
+            // the contents must be preserved. The Rc's default drop will just
+            // decrement the refcount.
+            return;
+        };
+        let mut cur_vec = std::mem::take(cell.get_mut());
+
+        // Lazy work stack: no heap until we actually queue a nested level. Shallow
+        // values never push, so this stays at capacity 0.
+        let mut stack: Vec<Vec<Value>> = vec![];
+        loop {
+            for v in cur_vec {
+                match v {
+                    Value::Container(c) => match c {
+                        Container::Locals(mut nv)
+                        | Container::Vec(mut nv)
+                        | Container::Struct(mut nv) => {
+                            // Drain `nv`'s inner Vec iff uniquely owned. `nv` then drops
+                            // normally — its own `Drop` re-enters this function, sees an
+                            // empty drained vec, pushes nothing, and exits.
+                            if let Some(inner_cell) = Rc::get_mut(&mut nv.0) {
+                                let inner = std::mem::take(inner_cell.get_mut());
+                                if !inner.is_empty() {
+                                    stack.push(inner);
+                                }
+                            }
+                            // Shared Rc (refcount > 1): fall through, nv drops normally.
+                        },
+                        // Primitive-vec variants cannot hold further `Value`s — their
+                        // default drop is non-recursive and bounded.
+                        Container::VecU8(_)
+                        | Container::VecU16(_)
+                        | Container::VecU32(_)
+                        | Container::VecU64(_)
+                        | Container::VecU128(_)
+                        | Container::VecU256(_)
+                        | Container::VecI8(_)
+                        | Container::VecI16(_)
+                        | Container::VecI32(_)
+                        | Container::VecI64(_)
+                        | Container::VecI128(_)
+                        | Container::VecI256(_)
+                        | Container::VecBool(_)
+                        | Container::VecAddress(_) => {},
+                    },
+                    // Non-container Values drop in O(1) or bounded size. Closures'
+                    // captured args are `Value`s inside a `Vec` owned by the closure; if
+                    // they are containers, their default drop invokes *this* `Drop`
+                    // iteratively on each, not recursively.
+                    Value::Invalid
+                    | Value::U8(_)
+                    | Value::U16(_)
+                    | Value::U32(_)
+                    | Value::U64(_)
+                    | Value::U128(_)
+                    | Value::U256(_)
+                    | Value::I8(_)
+                    | Value::I16(_)
+                    | Value::I32(_)
+                    | Value::I64(_)
+                    | Value::I128(_)
+                    | Value::I256(_)
+                    | Value::Bool(_)
+                    | Value::Address(_)
+                    | Value::ContainerRef(_)
+                    | Value::IndexedRef(_)
+                    | Value::DelayedFieldID { .. }
+                    | Value::ClosureValue(_) => {},
+                }
+            }
+
+            cur_vec = match stack.pop() {
+                Some(v) => v,
+                None => break,
+            };
+        }
+    }
+}
+
 /// A container is a collection of values. It is used to represent data structures like a
 /// Move vector or struct.
 ///
@@ -136,9 +294,9 @@ pub enum Value {
 /// making it possible to be shared by references.
 #[derive(Debug)]
 pub(crate) enum Container {
-    Locals(Rc<RefCell<Vec<Value>>>),
-    Vec(Rc<RefCell<Vec<Value>>>),
-    Struct(Rc<RefCell<Vec<Value>>>),
+    Locals(NestedValues),
+    Vec(NestedValues),
+    Struct(NestedValues),
     VecU8(Rc<RefCell<Vec<u8>>>),
     VecU64(Rc<RefCell<Vec<u64>>>),
     VecU128(Rc<RefCell<Vec<u128>>>),
@@ -439,10 +597,10 @@ impl Container {
     }
 
     fn master_signer(x: AccountAddress) -> Self {
-        Container::Struct(Rc::new(RefCell::new(vec![
+        Container::Struct(NestedValues::new(vec![
             Value::U16(MASTER_SIGNER_VARIANT),
             Value::Address(Box::new(x)),
-        ])))
+        ]))
     }
 }
 
@@ -628,22 +786,22 @@ impl Value {
 
 impl Container {
     fn copy_value(&self, depth: u64, max_depth: Option<u64>) -> PartialVMResult<Self> {
-        fn copy_rc_ref_vec_val(
-            r: &Rc<RefCell<Vec<Value>>>,
+        fn copy_nested_values(
+            r: &NestedValues,
             depth: u64,
             max_depth: Option<u64>,
-        ) -> PartialVMResult<Rc<RefCell<Vec<Value>>>> {
+        ) -> PartialVMResult<NestedValues> {
             let vals = r.borrow();
             let mut copied_vals = Vec::with_capacity(vals.len());
             for val in vals.iter() {
                 copied_vals.push(val.copy_value(depth + 1, max_depth)?);
             }
-            Ok(Rc::new(RefCell::new(copied_vals)))
+            Ok(NestedValues::new(copied_vals))
         }
 
         Ok(match self {
-            Self::Vec(r) => Self::Vec(copy_rc_ref_vec_val(r, depth, max_depth)?),
-            Self::Struct(r) => Self::Struct(copy_rc_ref_vec_val(r, depth, max_depth)?),
+            Self::Vec(r) => Self::Vec(copy_nested_values(r, depth, max_depth)?),
+            Self::Struct(r) => Self::Struct(copy_nested_values(r, depth, max_depth)?),
 
             Self::VecU8(r) => Self::VecU8(Rc::new(RefCell::new(r.borrow().clone()))),
             Self::VecU16(r) => Self::VecU16(Rc::new(RefCell::new(r.borrow().clone()))),
@@ -672,8 +830,8 @@ impl Container {
     // Note(inline): expensive to inline, +10s compile time
     fn copy_by_ref(&self) -> Self {
         match self {
-            Self::Vec(r) => Self::Vec(Rc::clone(r)),
-            Self::Struct(r) => Self::Struct(Rc::clone(r)),
+            Self::Vec(r) => Self::Vec(r.clone()),
+            Self::Struct(r) => Self::Struct(r.clone()),
 
             Self::VecU8(r) => Self::VecU8(Rc::clone(r)),
             Self::VecU16(r) => Self::VecU16(Rc::clone(r)),
@@ -690,7 +848,7 @@ impl Container {
             Self::VecBool(r) => Self::VecBool(Rc::clone(r)),
             Self::VecAddress(r) => Self::VecAddress(Rc::clone(r)),
 
-            Self::Locals(r) => Self::Locals(Rc::clone(r)),
+            Self::Locals(r) => Self::Locals(r.clone()),
         }
     }
 }
@@ -1701,10 +1859,29 @@ impl ContainerRef {
                         *$r1.borrow_mut() = take_unique_ownership(r)?;
                     }};
                 }
+                // Variant of `assign!` for `NestedValues`-carrying variants (Struct/Vec).
+                // Unwraps the Rc from `NestedValues` before delegating to `take_unique_ownership`.
+                macro_rules! assign_nested {
+                    ($r1:expr, $tc:ident) => {{
+                        let r = match c {
+                            Container::$tc(v) => v.into_rc(),
+                            _ => {
+                                return Err(PartialVMError::new(
+                                    StatusCode::UNKNOWN_INVARIANT_VIOLATION_ERROR,
+                                )
+                                .with_message(
+                                    "failed to write_ref: container type mismatch".to_string(),
+                                )
+                                .with_sub_status(move_core_types::vm_status::sub_status::unknown_invariant_violation::EPARANOID_FAILURE))
+                            },
+                        };
+                        *$r1.borrow_mut() = take_unique_ownership(r)?;
+                    }};
+                }
 
                 match self.container() {
-                    Container::Struct(r) => assign!(r, Struct),
-                    Container::Vec(r) => assign!(r, Vec),
+                    Container::Struct(r) => assign_nested!(r, Struct),
+                    Container::Vec(r) => assign_nested!(r, Vec),
                     Container::VecU8(r) => assign!(r, VecU8),
                     Container::VecU16(r) => assign!(r, VecU16),
                     Container::VecU32(r) => assign!(r, VecU32),
@@ -2317,7 +2494,9 @@ impl Locals {
             | Value::ClosureValue(_)
             | Value::DelayedFieldID { .. } => Ok(Value::IndexedRef(IndexedRef {
                 idx: idx as u32,
-                container_ref: ContainerRef::Local(Container::Locals(Rc::clone(&self.0))),
+                container_ref: ContainerRef::Local(Container::Locals(NestedValues::from_rc(
+                    Rc::clone(&self.0),
+                ))),
                 tag: None,
             })),
 
@@ -2565,7 +2744,7 @@ impl Value {
 
     #[cfg_attr(feature = "force-inline", inline(always))]
     pub fn struct_(s: Struct) -> Self {
-        Value::Container(Container::Struct(Rc::new(RefCell::new(s.fields))))
+        Value::Container(Container::Struct(NestedValues::new(s.fields)))
     }
 
     #[cfg_attr(feature = "force-inline", inline(always))]
@@ -2680,9 +2859,7 @@ impl Value {
                 Ok(v)
             })
             .collect::<PartialVMResult<Vec<_>>>()?;
-        Ok(Self::Container(Container::Vec(Rc::new(RefCell::new(
-            values,
-        )))))
+        Ok(Self::Container(Container::Vec(NestedValues::new(values))))
     }
 
     pub fn closure(
@@ -2821,7 +2998,7 @@ impl VMValueCast<Struct> for Value {
     fn cast(self) -> PartialVMResult<Struct> {
         match self {
             Value::Container(Container::Struct(r)) => Ok(Struct {
-                fields: take_unique_ownership(r)?,
+                fields: take_unique_ownership(r.into_rc())?,
             }),
             v => Err(PartialVMError::new(StatusCode::INTERNAL_TYPE_ERROR)
                 .with_message(format!("cannot cast {:?} to struct", v,))),
@@ -2863,7 +3040,7 @@ impl VMValueCast<Vec<Value>> for Value {
     fn cast(self) -> PartialVMResult<Vec<Value>> {
         match self {
             Value::Container(Container::Vec(c)) => {
-                Ok(take_unique_ownership(c)?.into_iter().collect())
+                Ok(take_unique_ownership(c.into_rc())?.into_iter().collect())
             },
             Value::Address(_)
             | Value::Bool(_)
@@ -4107,7 +4284,7 @@ impl Vector {
             | Type::Struct { .. }
             | Type::StructInstantiation { .. }
             | Type::Function { .. } => {
-                Value::Container(Container::Vec(Rc::new(RefCell::new(elements))))
+                Value::Container(Container::Vec(NestedValues::new(elements)))
             },
 
             Type::Reference(_) | Type::MutableReference(_) | Type::TyParam(_) => {
@@ -4179,7 +4356,7 @@ impl Vector {
                 .into_iter()
                 .map(Value::address)
                 .collect(),
-            Container::Vec(r) => take_unique_ownership(r)?.into_iter().collect(),
+            Container::Vec(r) => take_unique_ownership(r.into_rc())?.into_iter().collect(),
             Container::Locals(_) | Container::Struct(_) => {
                 return Err(PartialVMError::new_invariant_violation(
                     "Unexpected non-vector container",
@@ -4282,7 +4459,7 @@ impl Struct {
  **************************************************************************************/
 #[allow(clippy::unnecessary_wraps)]
 impl GlobalValueImpl {
-    fn expect_struct_fields(value: &Value) -> &Rc<RefCell<Vec<Value>>> {
+    fn expect_struct_fields(value: &Value) -> &NestedValues {
         match value {
             Value::Container(Container::Struct(fields)) => fields,
             _ => unreachable!("Global values must be structs"),
@@ -4366,13 +4543,13 @@ impl GlobalValueImpl {
             Self::Fresh { value } => {
                 let fields = Self::expect_struct_fields(value);
                 Ok(Value::ContainerRef(ContainerRef::Local(Container::Struct(
-                    Rc::clone(fields),
+                    fields.clone(),
                 ))))
             },
             Self::Cached { value, status } => {
                 let fields = Self::expect_struct_fields(value);
                 Ok(Value::ContainerRef(ContainerRef::Global {
-                    container: Container::Struct(Rc::clone(fields)),
+                    container: Container::Struct(fields.clone()),
                     status: Rc::clone(status),
                 }))
             },
@@ -5352,7 +5529,7 @@ impl<'d> serde::de::DeserializeSeed<'d> for DeserializationSeed<'_, &MoveTypeLay
                         layout,
                     };
                     let vector = deserializer.deserialize_seq(VectorElementVisitor(seed))?;
-                    Value::Container(Container::Vec(Rc::new(RefCell::new(vector))))
+                    Value::Container(Container::Vec(NestedValues::new(vector)))
                 },
             }),
 
@@ -6099,7 +6276,7 @@ pub mod prop {
                     })
                     .boxed(),
                 layout => vec(value_strategy_with_layout(layout), 0..10)
-                    .prop_map(|vals| Value::Container(Container::Vec(Rc::new(RefCell::new(vals)))))
+                    .prop_map(|vals| Value::Container(Container::Vec(NestedValues::new(vals))))
                     .boxed(),
             },
             L::Struct(struct_layout) => match struct_layout.as_ref() {
```
