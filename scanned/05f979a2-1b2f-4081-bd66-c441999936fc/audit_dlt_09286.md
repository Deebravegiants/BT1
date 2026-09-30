# [?] fix(lint): bound reentrancy helper analysis (#15063)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-06-05
Source: https://github.com/foundry-rs/foundry/commit/dea99c55914d010b22d3f5532fca180a8ecafda1
Type: security-commit

## Details
fix(lint): bound reentrancy helper analysis (#15063)

* fix(lint): bound reentrancy helper analysis

* address steven's comments

* fix reentrancy events clippy

* address steven's comments

## Patch
### Cargo.lock
```diff
@@ -1183,7 +1183,7 @@ version = "1.1.5"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "40c48f72fd53cd289104fc64099abca73db4166ad86ea0b4341abe65af83dadc"
 dependencies = [
- "windows-sys 0.61.2",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
@@ -1207,7 +1207,7 @@ checksum = "291e6a250ff86cd4a820112fb8898808a366d8f9f58ce16d1f538353ad55747d"
 dependencies = [
  "anstyle",
  "once_cell_polyfill",
- "windows-sys 0.61.2",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
@@ -6113,7 +6113,7 @@ dependencies = [
  "libc",
  "log",
  "rustversion",
- "windows-link 0.2.1",
+ "windows-link 0.1.3",
  "windows-result 0.4.1",
 ]
 
@@ -8099,7 +8099,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b685c8311c9171d1bd2895222965d25616b2de2cb5819dd3504ed9250df9fecd"
 dependencies = [
  "ahash",
- "hashbrown 0.17.1",
+ "hashbrown 0.16.1",
  "parking_lot",
  "stable_deref_trait",
 ]
@@ -11354,13 +11354,13 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "3a766e1110788c36f4fa1c2b71b387a7815aa65f88ce0229841826633d93723e"
 dependencies = [
  "libc",
- "windows-sys 0.61.2",
+ "windows-sys 0.60.2",
 ]
 
 [[package]]
 name = "solar-ast"
 version = "0.1.8"
-source = "git+https://github.com/paradigmxyz/solar?rev=4393d0dbb8d37df4df5c2840350a73a189441988#4393d0dbb8d37df4df5c2840350a73a189441988"
+source = "git+https://github.com/paradigmxyz/solar?rev=da6b0c3a8c0edd23f8b1414c61418ba78d6c4670#da6b0c3a8c0edd23f8b1414c61418ba78d6c4670"
 dependencies = [
  "alloy-primitives",
  "bumpalo",
@@ -11376,7 +11376,7 @@ dependencies = [
 [[package]]
 name = "solar-compiler"
 version = "0.1.8"
-source = "git+https://github.com/paradigmxyz/solar?rev=4393d0dbb8d37df4df5c2840350a73a189441988#4393d0dbb8d37df4df5c2840350a73a189441988"
+source = "git+https://github.com/paradigmxyz/solar?rev=da6b0c3a8c0edd23f8b1414c61418ba78d6c4670#da6b0c3a8c0edd23f8b1414c61418ba78d6c4670"
 dependencies = [
  "alloy-primitives",
  "solar-ast",
@@ -11391,7 +11391,7 @@ dependencies = [
 [[package]]
 name = "solar-config"
 version = "0.1.8"
-source = "git+https://github.com/paradigmxyz/solar?rev=4393d0dbb8d37df4df5c2840350a73a189441988#4393d0dbb8d37df4df5c2840350a73a189441988"
+source = "git+https://github.com/paradigmxyz/solar?rev=da6b0c3a8c0edd23f8b1414c61418ba78d6c4670#da6b0c3a8c0edd23f8b1414c61418ba78d6c4670"
 dependencies = [
  "colorchoice",
  "strum 0.28.0",
@@ -11400,7 +11400,7 @@ dependencies = [
 [[package]]
 name = "solar-data-structures"
 version = "0.1.8"
-source = "git+https://github.com/paradigmxyz/solar?rev=4393d0dbb8d37df4df5c2840350a73a189441988#4393d0dbb8d37df4df5c2840350a73a189441988"
+source = "git+https://github.com/paradigmxyz/solar?rev=da6b0c3a8c0edd23f8b1414c61418ba78d6c4670#da6b0c3a8c0edd23f8b1414c61418ba78d6c4670"
 dependencies = [
  "bumpalo",
  "indexmap 2.14.0",
@@ -11414,7 +11414,7 @@ dependencies = [
 [[package]]
 name = "solar-interface"
 version = "0.1.8"
-source = "git+https://github.com/paradigmxyz/solar?rev=4393d0dbb8d37df4df5c2840350a73a189441988#4393d0dbb8d37df4df5c2840350a73a189441988"
+source = "git+https://github.com/paradigmxyz/solar?rev=da6b0c3a8c0edd23f8b1414c61418ba78d6c4670#da6b0c3a8c0edd23f8b1414c61418ba78d6c4670"
 dependencies = [
  "annotate-snippets 0.12.16",
  "anstream 1.0.0",
@@ -11442,7 +11442,7 @@ dependencies = [
 [[package]]
 name = "solar-macros"
 version = "0.1.8"
-source = "git+https://github.com/paradigmxyz/solar?rev=4393d0dbb8d37df4df5c2840350a73a189441988#4393d0dbb8d37df4df5c2840350a73a189441988"
+source = "git+https://github.com/paradigmxyz/solar?rev=da6b0c3a8c0edd23f8b1414c61418ba78d6c4670#da6b0c3a8c0edd23f8b1414c61418ba78d6c4670"
 dependencies = [
  "proc-macro2",
  "quote",
@@ -11452,7 +11452,7 @@ dependencies = [
 [[package]]
 name = "solar-parse"
 version = "0.1.8"
-source = "git+https://github.com/paradigmxyz/solar?rev=4393d0dbb8d37df4df5c2840350a73a189441988#4393d0dbb8d37df4df5c2840350a73a189441988"
+source = "git+https://github.com/paradigmxyz/solar?rev=da6b0c3a8c0edd23f8b1414c61418ba78d6c4670#da6b0c3a8c0edd23f8b1414c61418ba78d6c4670"
 dependencies = [
  "alloy-primitives",
  "bitflags 2.11.1",
@@ -11473,7 +11473,7 @@ dependencies = [
 [[package]]
 name = "solar-sema"
 version = "0.1.8"
-source = "git+https://github.com/paradigmxyz/solar?rev=4393d0dbb8d37df4df5c2840350a73a189441988#4393d0dbb8d37df4df5c2840350a73a189441988"
+source = "git+https://github.com/paradigmxyz/solar?rev=da6b0c3a8c0edd23f8b1414c61418ba78d6c4670#da6b0c3a8c0edd23f8b1414c61418ba78d6c4670"
 dependencies = [
  "alloy-json-abi",
  "alloy-primitives",
@@ -11799,7 +11799,7 @@ dependencies = [
  "serde_json",
  "sha2 0.10.9",
  "tempfile",
- "thiserror 2.0.18",
+ "thiserror 1.0.69",
  "url",
  "zip",
 ]
```

### Cargo.toml
```diff
@@ -604,10 +604,10 @@ tempo-alloy = { git = "https://github.com/tempoxyz/tempo", rev = "4d3f1db11a496d
 tempo-contracts = { git = "https://github.com/tempoxyz/tempo", rev = "4d3f1db11a496d5fc98bb33d8055de102e5f5e11" }
 
 # solar
-solar = { package = "solar-compiler", git = "https://github.com/paradigmxyz/solar", rev = "4393d0dbb8d37df4df5c2840350a73a189441988" }
-solar-interface = { package = "solar-interface", git = "https://github.com/paradigmxyz/solar", rev = "4393d0dbb8d37df4df5c2840350a73a189441988" }
-solar-ast = { package = "solar-ast", git = "https://github.com/paradigmxyz/solar", rev = "4393d0dbb8d37df4df5c2840350a73a189441988" }
-solar-sema = { package = "solar-sema", git = "https://github.com/paradigmxyz/solar", rev = "4393d0dbb8d37df4df5c2840350a73a189441988" }
+solar = { package = "solar-compiler", git = "https://github.com/paradigmxyz/solar", rev = "da6b0c3a8c0edd23f8b1414c61418ba78d6c4670" }
+solar-interface = { package = "solar-interface", git = "https://github.com/paradigmxyz/solar", rev = "da6b0c3a8c0edd23f8b1414c61418ba78d6c4670" }
+solar-ast = { package = "solar-ast", git = "https://github.com/paradigmxyz/solar", rev = "da6b0c3a8c0edd23f8b1414c61418ba78d6c4670" }
+solar-sema = { package = "solar-sema", git = "https://github.com/paradigmxyz/solar", rev = "da6b0c3a8c0edd23f8b1414c61418ba78d6c4670" }
 
 [workspace.metadata.cargo-shear]
 ignored = ["idna_adapter", "cast", "chisel", "forge", "alloy-contract"]
```

### crates/lint/src/sol/analysis/helper_cache.rs
```diff
@@ -0,0 +1,62 @@
+use std::{
+    collections::{HashMap, HashSet, VecDeque},
+    hash::Hash,
+};
+
+pub const DEFAULT_HELPER_ANALYSIS_CACHE_LIMIT: usize = 65_536;
+
+/// Bounded memo table for lint analyses that inline internal helper calls.
+#[derive(Debug)]
+pub struct HelperAnalysisCache<K, V> {
+    entries: HashMap<K, V>,
+    in_progress: HashSet<K>,
+    order: VecDeque<K>,
+    max_entries: usize,
+}
+
+impl<K, V> HelperAnalysisCache<K, V>
+where
+    K: Clone + Eq + Hash,
+{
+    pub fn new(max_entries: usize) -> Self {
+        Self {
+            entries: HashMap::new(),
+            in_progress: HashSet::new(),
+            order: VecDeque::new(),
+            max_entries,
+        }
+    }
+
+    pub fn is_in_progress(&self, key: &K) -> bool {
+        self.in_progress.contains(key)
+    }
+
+    pub fn get(&self, key: &K) -> Option<&V> {
+        self.entries.get(key)
+    }
+
+    pub fn start(&mut self, key: K) {
+        self.in_progress.insert(key);
+    }
+
+    pub fn finish(&mut self, key: K, value: V) {
+        self.in_progress.remove(&key);
+        if self.max_entries == 0 {
+            return;
+        }
+
+        if !self.entries.contains_key(&key) {
+            self.order.push_back(key.clone());
+        }
+        self.entries.insert(key, value);
+
+        while self.entries.len() > self.max_entries {
+            if let Some(oldest) = self.order.pop_front() {
+                self.entries.remove(&oldest);
+                self.in_progress.remove(&oldest);
+            } else {
+                break;
+            }
+        }
+    }
+}
```

### crates/lint/src/sol/analysis/mod.rs
```diff
@@ -7,5 +7,6 @@
 //!
 //! All helpers borrow HIR and never mutate it.
 
+pub mod helper_cache;
 pub mod interface;
 pub mod primitives;
```

### crates/lint/src/sol/high/reentrancy.rs
```diff
@@ -1,7 +1,10 @@
 use super::ReentrancyEth;
 use crate::{
     linter::{LateLintPass, LintContext},
-    sol::{Severity, SolLint},
+    sol::{
+        Severity, SolLint,
+        analysis::helper_cache::{DEFAULT_HELPER_ANALYSIS_CACHE_LIMIT, HelperAnalysisCache},
+    },
 };
 use solar::{
     ast::{
@@ -17,7 +20,7 @@ use solar::{
         ty::{TyFnKind, TyKind},
     },
 };
-use std::collections::{BTreeSet, HashSet};
+use std::collections::{BTreeSet, HashMap, HashSet};
 
 declare_forge_lint!(
     REENTRANCY_ETH,
@@ -69,20 +72,20 @@ fn is_entry_point(func: &hir::Function<'_>) -> bool {
     func.kind.is_function() && matches!(func.visibility, Visibility::Public | Visibility::External)
 }
 
-#[derive(Clone, Debug, Default)]
+#[derive(Clone, Debug, Default, PartialEq, Eq, Hash)]
 struct FlowState {
     state_reads: BTreeSet<VariableId>,
     pending_calls: Vec<PendingCall>,
 }
 
-#[derive(Clone, Debug)]
+#[derive(Clone, Debug, PartialEq, Eq, Hash)]
 struct PendingCall {
     span: Span,
     kind: ReentrantCallKind,
     state_reads: BTreeSet<VariableId>,
 }
 
-#[derive(Clone, Copy, Debug, Eq, PartialEq)]
+#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
 enum ReentrantCallKind {
     Eth,
     NoEth,
@@ -118,10 +121,27 @@ struct Analyzer<'ctx, 's, 'c, 'hir> {
     hir: &'hir hir::Hir<'hir>,
     emitted: HashSet<Span>,
     call_stack: Vec<FunctionId>,
+    inline_cache: HelperAnalysisCache<InlineCallKey, FlowState>,
+    recursive_cut_frontiers: HashMap<RecursiveFrontierKey, Vec<FunctionId>>,
+    direct_internal_calls: HashMap<FunctionId, Vec<FunctionId>>,
     reentrancy_eth_enabled: bool,
     reentrancy_no_eth_enabled: bool,
 }
 
+#[derive(Clone, Debug, PartialEq, Eq, Hash)]
+struct InlineCallKey {
+    func_id: FunctionId,
+    /// First active function that can cut recursion from this callee.
+    recursive_cut: Option<FunctionId>,
+    state: FlowState,
+}
+
+#[derive(Clone, Debug, PartialEq, Eq, Hash)]
+struct RecursiveFrontierKey {
+    func_id: FunctionId,
+    active_call_stack: Vec<FunctionId>,
+}
+
 impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
     fn new(ctx: &'ctx LintContext<'s, 'c>, gcx: Gcx<'hir>, hir: &'hir hir::Hir<'hir>) -> Self {
         Self {
@@ -130,6 +150,9 @@ impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
             hir,
             emitted: HashSet::new(),
             call_stack: Vec::new(),
+            inline_cache: HelperAnalysisCache::new(DEFAULT_HELPER_ANALYSIS_CACHE_LIMIT),
+            recursive_cut_frontiers: HashMap::new(),
+            direct_internal_calls: HashMap::new(),
             reentrancy_eth_enabled: ctx.is_lint_enabled(REENTRANCY_ETH.id),
             reentrancy_no_eth_enabled: ctx.is_lint_enabled(REENTRANCY_NO_ETH.id),
         }
@@ -415,9 +438,219 @@ impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
         let func = self.hir.function(func_id);
         let Some(body) = func.body else { return };
 
+        let key = InlineCallKey {
+            func_id,
+            recursive_cut: self.first_recursive_cut(func_id),
+            state: state.clone(),
+        };
+        if self.inline_cache.is_in_progress(&key) {
+            return;
+        }
+        if let Some(cached) = self.inline_cache.get(&key) {
+            *state = cached.clone();
+            return;
+        }
+
+        let mut after = state.clone();
+        self.inline_cache.start(key.clone());
         self.call_stack.push(func_id);
-        self.analyze_callable(func, body, state);
+        self.analyze_callable(func, body, &mut after);
         self.call_stack.pop();
+
+        self.inline_cache.finish(key, after.clone());
+        *state = after;
+    }
+
+    fn first_recursive_cut(&mut self, func_id: FunctionId) -> Option<FunctionId> {
+        let active_call_stack = self.call_stack.iter().copied().collect::<BTreeSet<_>>();
+        if active_call_stack.is_empty() {
+            return None;
+        }
+
+        let active_call_stack = active_call_stack.into_iter().collect::<Vec<_>>();
+        let key = RecursiveFrontierKey { func_id, active_call_stack };
+        if let Some(frontier) = self.recursive_cut_frontiers.get(&key) {
+            return frontier.first().copied();
+        }
+
+        let active_call_stack = key.active_call_stack.iter().copied().collect::<BTreeSet<_>>();
+        let mut seen = HashSet::new();
+        let cut = self.first_recursive_cut_function(func_id, &active_call_stack, &mut seen);
+        self.recursive_cut_frontiers.insert(key, cut.into_iter().collect::<Vec<_>>());
+        cut
+    }
+
+    fn first_recursive_cut_function(
+        &mut self,
+        func_id: FunctionId,
+        active_call_stack: &BTreeSet<FunctionId>,
+        seen: &mut HashSet<FunctionId>,
+    ) -> Option<FunctionId> {
+        if !seen.insert(func_id) {
+            return None;
+        }
+
+        for callee_id in self.direct_internal_calls(func_id) {
+            if active_call_stack.contains(&callee_id) {
+                return Some(callee_id);
+            }
+            if let Some(cut) = self.first_recursive_cut_function(callee_id, active_call_stack, seen)
+            {
+                return Some(cut);
+            }
+        }
+        None
+    }
+
+    fn direct_internal_calls(&mut self, func_id: FunctionId) -> Vec<FunctionId> {
+        if let Some(calls) = self.direct_internal_calls.get(&func_id) {
+            return calls.clone();
+        }
+
+        let mut calls = BTreeSet::new();
+        let func = self.hir.function(func_id);
+        for modifier in func.modifiers {
+            for arg in modifier.args.exprs() {
+                self.collect_direct_internal_calls_expr(arg, &mut calls);
+            }
+            if let Some(modifier_id) = modifier.id.as_function() {
+                calls.insert(modifier_id);
+            }
+        }
+        if let Some(body) = func.body {
+            self.collect_direct_internal_calls_block(body, &mut calls);
+        }
+
+        let calls = calls.into_iter().collect::<Vec<_>>();
+        self.direct_internal_calls.insert(func_id, calls.clone());
+        calls
+    }
+
+    fn collect_direct_internal_calls_block(
+        &mut self,
+        block: hir::Block<'hir>,
+        calls: &mut BTreeSet<FunctionId>,
+    ) {
+        for stmt in block.stmts {
+            self.collect_direct_internal_calls_stmt(stmt, calls);
+        }
+    }
+
+    fn collect_direct_internal_calls_stmt(
+        &mut self,
+        stmt: &'hir hir::Stmt<'hir>,
+        calls: &mut BTreeSet<FunctionId>,
+    ) {
+        match stmt.kind {
+            StmtKind::DeclSingle(var_id) => {
+                if let Some(init) = self.hir.variable(var_id).initializer {
+                    self.collect_direct_internal_calls_expr(init, calls);
+                }
+            }
+            StmtKind::DeclMulti(_, expr)
+            | StmtKind::Expr(expr)
+            | StmtKind::Emit(expr)
+            | StmtKind::Revert(expr) => {
+                self.collect_direct_internal_calls_expr(expr, calls);
+            }
+            StmtKind::Return(expr) => {
+                if let Some(expr) = expr {
+                    self.collect_direct_internal_calls_expr(expr, calls);
+                }
+            }
+            StmtKind::Block(block) | StmtKind::UncheckedBlock(block) | StmtKind::Loop(block, _) => {
+                self.collect_direct_internal_calls_block(block, calls);
+            }
+            StmtKind::If(cond, then_stmt, else_stmt) => {
+                self.collect_direct_internal_calls_expr(cond, calls);
+                self.collect_direct_internal_calls_stmt(then_stmt, calls);
+                if let Some(else_stmt) = else_stmt {
+                    self.collect_direct_internal_calls_stmt(else_stmt, calls);
+                }
+            }
+            StmtKind::Try(try_stmt) => {
+                self.collect_direct_internal_calls_expr(&try_stmt.expr, calls);
+                for clause in try_stmt.clauses {
+                    self.collect_direct_internal_calls_block(clause.block, calls);
+                }
+            }
+            StmtKind::Break
+            | StmtKind::Continue
+            | StmtKind::Placeholder
+            | StmtKind::AssemblyBlock(_)
+            | StmtKind::Switch(_)
+            | StmtKind::Err(_) => {}
+        }
+    }
+
+    fn collect_direct_internal_calls_expr(
+        &mut self,
+        expr: &'hir hir::Expr<'hir>,
+        calls: &mut BTreeSet<FunctionId>,
+    ) {
+        match &expr.kind {
+            ExprKind::Assign(lhs, _, rhs) | ExprKind::Binary(lhs, _, rhs) => {
+                self.collect_direct_internal_calls_expr(lhs, calls);
+                self.collect_direct_internal_calls_expr(rhs, calls);
+            }
+            ExprKind::Unary(_, inner)
+            | ExprKind::Delete(inner)
+            | ExprKind::Member(inner, _)
+            | ExprKind::Payable(inner) => {
+                self.collect_direct_internal_calls_expr(inner, calls);
+            }
+            ExprKind::Call(callee, args, opts) => {
+                self.collect_direct_internal_calls_expr(callee, calls);
+                if let Some(opts) = opts {
+                    for opt in opts.args {
+                        self.collect_direct_internal_calls_expr(&opt.value, calls);
+                    }
+                }
+                for arg in args.exprs() {
+                    self.collect_direct_internal_calls_expr(arg, calls);
+                }
+                for func_id in resolved_function_ids(callee) {
+                    calls.insert(func_id);
+                }
+            }
+            ExprKind::Index(base, index) => {
+                self.collect_direct_internal_calls_expr(base, calls);
+                if let Some(index) = index {
+                    self.collect_direct_internal_calls_expr(index, calls);
+                }
+            }
+            ExprKind::Slice(base, start, end) => {
+                self.collect_direct_internal_calls_expr(base, calls);
+                if let Some(start) = start {
+                    self.collect_direct_internal_calls_expr(start, calls);
+                }
+                if let Some(end) = end {
+                    self.collect_direct_internal_calls_expr(end, calls);
+                }
+            }
+            ExprKind::Ternary(cond, true_expr, false_expr) => {
+                self.collect_direct_internal_calls_expr(cond, calls);
+                self.collect_direct_internal_calls_expr(true_expr, calls);
+                self.collect_direct_internal_calls_expr(false_expr, calls);
+            }
+            ExprKind::Array(exprs) => {
+                for expr in *exprs {
+                    self.collect_direct_internal_calls_expr(expr, calls);
+                }
+            }
+            ExprKind::Tuple(exprs) => {
+                for expr in exprs.iter().copied().flatten() {
+                    self.collect_direct_internal_calls_expr(expr, calls);
+                }
+            }
+            ExprKind::Ident(_)
+            | ExprKind::Lit(_)
+            | ExprKind::New(_)
+            | ExprKind::TypeCall(_)
+            | ExprKind::Type(_)
+            | ExprKind::YulMember(..)
+            | ExprKind::Err(_) => {}
+        }
     }
 
     fn analyze_lhs_indices(&mut self, expr: &'hir hir::Expr<'hir>, state: &mut FlowState) {
```

### crates/lint/src/sol/low/calls_loop.rs
```diff
@@ -8,6 +8,7 @@ use solar::{
     interface::{kw, sym},
     sema::{
         Gcx, Ty,
+        builtins::Builtin,
         hir::{
             self, Block, ContractId, Expr, ExprKind, Function, FunctionId, Hir, ItemId, Res, Stmt,
             StmtKind, TypeKind,
@@ -564,7 +565,7 @@ fn type_is_address_like(ty: Ty<'_>) -> bool {
 }
 
 fn semantic_expr_ty<'gcx>(gcx: Gcx<'gcx>, hir: &Hir<'gcx>, expr: &Expr<'gcx>) -> Option<Ty<'gcx>> {
-    if !is_super(expr)
+    if !is_typeless_builtin_expr(expr)
         && let Some(ty) = gcx.type_of_expr(expr.peel_parens().id)
     {
         return Some(ty);
@@ -578,6 +579,9 @@ fn semantic_expr_ty<'gcx>(gcx: Gcx<'gcx>, hir: &Hir<'gcx>, expr: &Expr<'gcx>) ->
                         res.as_variable().map(|var_id| Res::Item(ItemId::Variable(var_id)))
                     }))
                 })?;
+            if matches!(res, Res::Builtin(builtin) if is_typeless_builtin(builtin)) {
+                return None;
+            }
             let ty = gcx.type_of_res(res);
             Some(match res {
                 Res::Item(ItemId::Variable(var_id)) => {
@@ -604,6 +608,31 @@ fn semantic_expr_ty<'gcx>(gcx: Gcx<'gcx>, hir: &Hir<'gcx>, expr: &Expr<'gcx>) ->
     }
 }
 
+fn is_typeless_builtin_expr(expr: &Expr<'_>) -> bool {
+    matches!(
+        &expr.peel_parens().kind,
+        ExprKind::Ident(reses)
+            if reses.iter().any(|res| {
+                matches!(res, Res::Builtin(builtin) if is_typeless_builtin(*builtin))
+            })
+    )
+}
+
+const fn is_typeless_builtin(builtin: Builtin) -> bool {
+    matches!(
+        builtin,
+        Builtin::This
+            | Builtin::Super
+            | Builtin::ArrayPush0
+            | Builtin::ArrayPush
+            | Builtin::ArrayPop
+            | Builtin::TypeMin
+            | Builtin::TypeMax
+            | Builtin::UdvtWrap
+            | Builtin::UdvtUnwrap
+    )
+}
+
 fn semantic_index_ty<'gcx>(gcx: Gcx<'gcx>, hir: &Hir<'gcx>, base: &Expr<'gcx>) -> Option<Ty<'gcx>> {
     let base_ty = semantic_expr_ty(gcx, hir, base)?;
     let loc = indexed_base_data_location(base_ty);
```

### crates/lint/src/sol/low/reentrancy_events.rs
```diff
@@ -7,7 +7,10 @@ use super::{
 };
 use crate::{
     linter::{LateLintPass, LintContext},
-    sol::{Severity, SolLint},
+    sol::{
+        Severity, SolLint,
+        analysis::helper_cache::{DEFAULT_HELPER_ANALYSIS_CACHE_LIMIT, HelperAnalysisCache},
+    },
 };
 use solar::{
     ast::LitKind,
@@ -19,7 +22,7 @@ use solar::{
         },
     },
 };
-use std::collections::HashSet;
+use std::collections::{HashMap, HashSet};
 
 declare_forge_lint!(
     REENTRANCY_EVENTS,
@@ -113,6 +116,13 @@ const fn merge_opt(dst: &mut Option<FlowState>, src: Option<FlowState>) {
     }
 }
 
+#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
+struct InlineCallKey {
+    func_id: FunctionId,
+    external_call_seen: bool,
+    suppress_inline_reports: bool,
+}
+
 struct Analyzer<'ctx, 's, 'c, 'hir> {
     ctx: &'ctx LintContext<'s, 'c>,
     gcx: Gcx<'hir>,
@@ -122,6 +132,11 @@ struct Analyzer<'ctx, 's, 'c, 'hir> {
     enclosing_contract: Option<ContractId>,
     /// Call stack to break recursion when inlining internal helpers and modifiers.
     call_stack: Vec<FunctionId>,
+    /// Cached summaries for transitive helper analysis. This keeps shared helper graphs from
+    /// being rescanned for every call edge in a function.
+    inline_cache: HelperAnalysisCache<InlineCallKey, Exits>,
+    /// Cached conservative summaries used only when a recursive edge is cut.
+    external_call_reachability: HashMap<FunctionId, bool>,
     /// Spans already reported, to dedupe diagnostics across paths/iterations.
     emitted: HashSet<Span>,
     /// When `true`, suppress emit diagnostics: we are inside an inlined helper that was
@@ -145,6 +160,8 @@ impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
             hir,
             enclosing_contract,
             call_stack: Vec::new(),
+            inline_cache: HelperAnalysisCache::new(DEFAULT_HELPER_ANALYSIS_CACHE_LIMIT),
+            external_call_reachability: HashMap::new(),
             emitted: HashSet::new(),
             suppress_inline_reports: false,
             expr_aborted: false,
@@ -512,24 +529,52 @@ impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
 
     fn analyze_internal_call(&mut self, func_id: FunctionId, state: &mut FlowState) {
         if self.call_stack.contains(&func_id) {
+            // Keep inline summaries stack-insensitive by replacing cut recursive edges with a
+            // conservative cached "can this helper ever taint by external call?" summary.
+            if self.helper_may_reach_external_call(func_id) {
+                state.external_call_seen = true;
+            }
             return;
         }
 
         let func = self.hir.function(func_id);
         let Some(body) = func.body else { return };
 
+        let suppress_inline_reports = self.suppress_inline_reports || !state.external_call_seen;
+        let key = InlineCallKey {
+            func_id,
+            external_call_seen: state.external_call_seen,
+            suppress_inline_reports,
+        };
+
+        if self.inline_cache.is_in_progress(&key) {
+            return;
+        }
+
+        if let Some(summary) = self.inline_cache.get(&key).cloned() {
+            self.apply_inline_summary(summary, state);
+            return;
+        }
+
         // Suppress diagnostics inside helpers entered with a clean state — the helper's
         // own self-pass will independently catch any intra-helper taint, avoiding
         // duplicate reports across callers.
         let prev_suppress = self.suppress_inline_reports;
-        self.suppress_inline_reports = prev_suppress || !state.external_call_seen;
+        self.suppress_inline_reports = suppress_inline_reports;
 
+        self.inline_cache.start(key);
         self.call_stack.push(func_id);
         let summary = self.analyze_callable(func, body, state.clone());
         self.call_stack.pop();
 
+        self.inline_cache.finish(key, summary.clone());
+
         self.suppress_inline_reports = prev_suppress;
 
+        self.apply_inline_summary(summary, state);
+    }
+
+    fn apply_inline_summary(&mut self, summary: Exits, state: &mut FlowState) {
         // Caller inherits the state of paths that return normally. If the callee has no
         // normal exits (always aborts), signal abort to the enclosing statement.
         let any_normal = summary.fallthrough.is_some() || summary.return_.is_some();
@@ -546,6 +591,282 @@ impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
             self.expr_aborted = true;
         }
     }
+
+    fn helper_may_reach_external_call(&mut self, func_id: FunctionId) -> bool {
+        self.helper_may_reach_external_call_inner(func_id, &mut HashSet::new()).0
+    }
+
+    fn helper_may_reach_external_call_inner(
+        &mut self,
+        func_id: FunctionId,
+        seen: &mut HashSet<FunctionId>,
+    ) -> (bool, bool) {
+        if let Some(cached) = self.external_call_reachability.get(&func_id) {
+            return (*cached, false);
+        }
+        if !seen.insert(func_id) {
+            return (false, true);
+        }
+
+        let func = self.hir.function(func_id);
+        let mut may_reach = false;
+        let mut cut_recursive_edge = false;
+        for modifier in func.modifiers {
+            for arg in modifier.args.exprs() {
+                let (arg_may_reach, arg_cut_recursive_edge) =
+                    self.expr_may_reach_external_call(arg, seen);
+                cut_recursive_edge |= arg_cut_recursive_edge;
+                if arg_may_reach {
+                    may_reach = true;
+                    break;
+                }
+            }
+            if may_reach {
+                break;
+            }
+            if let Some(modifier_id) = modifier.id.as_function() {
+                let (modifier_may_reach, modifier_cut_recursive_edge) =
+                    self.helper_may_reach_external_call_inner(modifier_id, seen);
+                cut_recursive_edge |= modifier_cut_recursive_edge;
+                if modifier_may_reach {
+                    may_reach = true;
+                    break;
+                }
+            }
+        }
+        if !may_reach && let Some(body) = func.body {
+            let (body_may_reach, body_cut_recursive_edge) =
+                self.block_may_reach_external_call(body, seen);
+            may_reach = body_may_reach;
+            cut_recursive_edge |= body_cut_recursive_edge;
+        }
+
+        seen.remove(&func_id);
+        if may_reach || !cut_recursive_edge {
+            self.external_call_reachability.insert(func_id, may_reach);
+        }
+        (may_reach, cut_recursive_edge)
+    }
+
+    fn block_may_reach_external_call(
+        &mut self,
+        block: Block<'hir>,
+        seen: &mut HashSet<FunctionId>,
+    ) -> (bool, bool) {
+        let mut cut_recursive_edge = false;
+        for stmt in block.stmts {
+            let (may_reach, stmt_cut_recursive_edge) =
+                self.stmt_may_reach_external_call(stmt, seen);
+            cut_recursive_edge |= stmt_cut_recursive_edge;
+            if may_reach {
+                return (true, cut_recursive_edge);
+            }
+        }
+        (false, cut_recursive_edge)
+    }
+
+    fn stmt_may_reach_external_call(
+        &mut self,
+        stmt: &'hir Stmt<'hir>,
+        seen: &mut HashSet<FunctionId>,
+    ) -> (bool, bool) {
+        match stmt.kind {
+            StmtKind::DeclSingle(var_id) => match self.hir.variable(var_id).initializer {
+                Some(expr) => self.expr_may_reach_external_call(expr, seen),
+                None => (false, false),
+            },
+            StmtKind::DeclMulti(_, expr)
+            | StmtKind::Expr(expr)
+            | StmtKind::Emit(expr)
+            | StmtKind::Revert(expr) => self.expr_may_reach_external_call(expr, seen),
+            StmtKind::Return(expr) => match expr {
+                Some(expr) => self.expr_may_reach_external_call(expr, seen),
+                None => (false, false),
+            },
+            StmtKind::Block(block) | StmtKind::UncheckedBlock(block) | StmtKind::Loop(block, _) => {
+                self.block_may_reach_external_call(block, seen)
+            }
+            StmtKind::If(cond, then_stmt, else_stmt) => Self::any_may_reach_external_call([
+                self.expr_may_reach_external_call(cond, seen),
+                self.stmt_may_reach_external_call(then_stmt, seen),
+                else_stmt
+                    .map(|else_stmt| self.stmt_may_reach_external_call(else_stmt, seen))
+                    .unwrap_or((false, false)),
+            ]),
+            StmtKind::Try(try_stmt) => {
+                let mut cut_recursive_edge = false;
+                let (expr_may_reach, expr_cut_recursive_edge) =
+                    self.expr_may_reach_external_call(&try_stmt.expr, seen);
+                cut_recursive_edge |= expr_cut_recursive_edge;
+                if expr_may_reach {
+                    return (true, cut_recursive_edge);
+                }
+                for clause in try_stmt.clauses {
+                    let (clause_may_reach, clause_cut_recursive_edge) =
+                        self.block_may_reach_external_call(clause.block, seen);
+                    cut_recursive_edge |= clause_cut_recursive_edge;
+                    if clause_may_reach {
+                        return (true, cut_recursive_edge);
+                    }
+                }
+                (false, cut_recursive_edge)
+            }
+            StmtKind::AssemblyBlock(_) | StmtKind::Switch(_) => (true, false),
+            StmtKind::Break | StmtKind::Continue | StmtKind::Placeholder | StmtKind::Err(_) => {
+                (false, false)
+            }
+        }
+    }
+
+    fn expr_may_reach_external_call(
+        &mut self,
+        expr: &'hir Expr<'hir>,
+        seen: &mut HashSet<FunctionId>,
+    ) -> (bool, bool) {
+        match &expr.kind {
+            ExprKind::Call(callee, args, opts) => {
+                let mut cut_recursive_edge = false;
+                let (callee_may_reach, callee_cut_recursive_edge) =
+                    self.expr_may_reach_external_call(callee, seen);
+                cut_recursive_edge |= callee_cut_recursive_edge;
+                if callee_may_reach {
+                    return (true, cut_recursive_edge);
+                }
+                if let Some(opts) = opts {
+                    for opt in opts.args {
+                        let (opt_may_reach, opt_cut_recursive_edge) =
+                            self.expr_may_reach_external_call(&opt.value, seen);
+                        cut_recursive_edge |= opt_cut_recursive_edge;
+                        if opt_may_reach {
+                            return (true, cut_recursive_edge);
+                        }
+                    }
+                }
+                for arg in args.exprs() {
+                    let (arg_may_reach, arg_cut_recursive_edge) =
+                        self.expr_may_reach_external_call(arg, seen);
+                    cut_recursive_edge |= arg_cut_recursive_edge;
+                    if arg_may_reach {
+                        return (true, cut_recursive_edge);
+                    }
+                }
+                if is_state_mutating_external_call(
+                    self.gcx,
+                    self.hir,
+                    callee,
+                    args.len(),
+                    self.enclosing_contract,
+                ) {
+                    return (true, cut_recursive_edge);
+                }
+
+                let internal: Vec<_> = resolved_internal_function_ids(self.hir, callee).collect();
+                for func_id in internal {
+                    let (func_may_reach, func_cut_recursive_edge) =
+                        self.helper_may_reach_external_call_inner(func_id, seen);
+                    cut_recursive_edge |= func_cut_recursive_edge;
+                    if func_may_reach {
+                        return (true, cut_recursive_edge);
+                    }
+                }
+
+                for func_id in resolved_super_function_ids(
+                    self.hir,
+                    self.enclosing_contract,
+                    callee,
+                    args.len(),
+                ) {
+                    let (func_may_reach, func_cut_recursive_edge) =
+                        self.helper_may_reach_external_call_inner(func_id, seen);
+                    cut_recursive_edge |= func_cut_recursive_edge;
+                    if func_may_reach {
+                        return (true, cut_recursive_edge);
+                    }
+                }
+
+                (false, cut_recursive_edge)
+            }
+            ExprKind::Assign(lhs, _, rhs) | ExprKind::Binary(lhs, _, rhs) => {
+                Self::any_may_reach_external_call([
+                    self.expr_may_reach_external_call(lhs, seen),
+                    self.expr_may_reach_external_call(rhs, seen),
+                ])
+            }
+            ExprKind::Unary(_, inner)
+            | ExprKind::Delete(inner)
+            | ExprKind::Payable(inner)
+            | ExprKind::Member(inner, _) => self.expr_may_reach_external_call(inner, seen),
+            ExprKind::Index(base, index) => Self::any_may_reach_external_call([
+                self.expr_may_reach_external_call(base, seen),
+                index
+                    .map(|index| self.expr_may_reach_external_call(index, seen))
+                    .unwrap_or((false, false)),
+            ]),
+            ExprKind::Slice(base, start, end) => Self::any_may_reach_external_call([
+                self.expr_may_reach_external_call(base, seen),
+                start
+                    .map(|start| self.expr_may_reach_external_call(start, seen))
+                    .unwrap_or((false, false)),
+                end.map(|end| self.expr_may_reach_external_call(end, seen))
+                    .unwrap_or((false, false)),
+            ]),
+            ExprKind::Ternary(cond, then_expr, else_expr) => Self::any_may_reach_external_call([
+                self.expr_may_reach_external_call(cond, seen),
+                self.expr_may_reach_external_call(then_expr, seen),
+                self.expr_may_reach_external_call(else_expr, seen),
+            ]),
+            ExprKind::Array(exprs) => self.exprs_may_reach_external_call(exprs, seen),
+            ExprKind::Tuple(exprs) => {
+                let mut cut_recursive_edge = false;
+                for expr in exprs.iter().copied().flatten() {
+                    let (expr_may_reach, expr_cut_recursive_edge) =
+                        self.expr_may_reach_external_call(expr, seen);
+                    cut_recursive_edge |= expr_cut_recursive_edge;
+                    if expr_may_reach {
+                        return (true, cut_recursive_edge);
+                    }
+                }
+                (false, cut_recursive_edge)
+            }
+            ExprKind::Ident(_)
+            | ExprKind::Lit(_)
+            | ExprKind::New(_)
+            | ExprKind::TypeCall(_)
+            | ExprKind::Type(_)
+            | ExprKind::YulMember(..)
+            | ExprKind::Err(_) => (false, false),
+        }
+    }
+
+    fn exprs_may_reach_external_call(
+        &mut self,
+        exprs: &'hir [Expr<'hir>],
+        seen: &mut HashSet<FunctionId>,
+    ) -> (bool, bool) {
+        let mut cut_recursive_edge = false;
+        for expr in exprs {
+            let (expr_may_reach, expr_cut_recursive_edge) =
+                self.expr_may_reach_external_call(expr, seen);
+            cut_recursive_edge |= expr_cut_recursive_edge;
+            if expr_may_reach {
+                return (true, cut_recursive_edge);
+            }
+        }
+        (false, cut_recursive_edge)
+    }
+
+    fn any_may_reach_external_call(
+        results: impl IntoIterator<Item = (bool, bool)>,
+    ) -> (bool, bool) {
+        let mut cut_recursive_edge = false;
+        for (may_reach, result_cut_recursive_edge) in results {
+            cut_recursive_edge |= result_cut_recursive_edge;
+            if may_reach {
+                return (true, cut_recursive_edge);
+            }
+        }
+        (false, cut_recursive_edge)
+    }
 }
 
 /// Returns `true` when the expression-statement is a builtin call that always terminates
```

### crates/lint/testdata/ReentrancyEth.sol
```diff
@@ -60,6 +60,21 @@ contract ReentrancyEth {
         balances[receiver] = 0;
     }
 
+    function helperHeavyCallThenWrite(address payable receiver) external {
+        uint256 amount = balances[receiver];
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        sendValueHeavy(receiver, amount);
+        balances[receiver] = 0;
+    }
+
     function gasleftIsNotACap(address payable receiver) external {
         uint256 amount = balances[receiver];
         (bool ok,) = receiver.call{value: amount, gas: gasleft()}(""); //~WARN: uncapped ETH transfer can be reentered before `balances` is updated
@@ -199,6 +214,11 @@ contract ReentrancyEth {
         require(ok, "transfer failed");
     }
 
+    function sendValueHeavy(address payable receiver, uint256 amount) internal {
+        (bool ok,) = receiver.call{value: amount}(""); //~WARN: uncapped ETH transfer can be reentered before `balances` is updated
+        require(ok, "transfer failed");
+    }
+
     function recordPayment(address receiver) internal {
         totalPaid[receiver] += 1 ether;
     }
@@ -218,3 +238,33 @@ contract ReentrancyEthNameOnlyGuard {
         _;
     }
 }
+
+contract ReentrancyEthRecursiveStackRepro {
+    uint256 x;
+
+    function entry(bool flag) public {
+        if (flag) {
+            a(1);
+            return;
+        }
+        c(1);
+        x = 1;
+    }
+
+    function a(uint256 depth) internal {
+        if (depth > 0) {
+            c(depth - 1);
+        }
+        uint256 y = x;
+        (bool ok,) = msg.sender.call{value: y}(""); //~WARN: uncapped ETH transfer can be reentered before `x` is updated
+        require(ok);
+    }
+
+    function c(uint256 depth) internal {
+        h(depth);
+    }
+
+    function h(uint256 depth) internal {
+        a(depth);
+    }
+}
```

### crates/lint/testdata/ReentrancyEth.stderr
```diff
@@ -30,6 +30,14 @@ LL │         (bool ok,) = receiver.call{value: amount}("");
    │
    ╰ help: https://getfoundry.sh/forge/linting/reentrancy-eth
 
+warning[reentrancy-eth]: uncapped ETH transfer can be reentered before `balances` is updated
+   ╭▸ ROOT/testdata/ReentrancyEth.sol:LL:CC
+   │
+LL │         (bool ok,) = receiver.call{value: amount}("");
+   │                      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
+   │
+   ╰ help: https://getfoundry.sh/forge/linting/reentrancy-eth
+
 warning[reentrancy-eth]: uncapped ETH transfer can be reentered before `balances` is updated
    ╭▸ ROOT/testdata/ReentrancyEth.sol:LL:CC
    │
@@ -94,3 +102,11 @@ LL │ …     (bool ok,) = payable(msg.sender).call{value: amount}("");
    │
    ╰ help: https://getfoundry.sh/forge/linting/reentrancy-eth
 
+warning[reentrancy-eth]: uncapped ETH transfer can be reentered before `x` is updated
+   ╭▸ ROOT/testdata/ReentrancyEth.sol:LL:CC
+   │
+LL │         (bool ok,) = msg.sender.call{value: y}("");
+   │                      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
+   │
+   ╰ help: https://getfoundry.sh/forge/linting/reentrancy-eth
+
```

### crates/lint/testdata/ReentrancyEvents.sol
```diff
@@ -17,12 +17,101 @@ interface IBus {
     function peek(uint256, uint256) external view returns (uint256);
 }
 
+interface ICall {
+    function poke() external;
+}
+
 contract Other {
     function action(uint256) external returns (bool) {
         return true;
     }
 }
 
+contract SuperTransferBase {
+    function transfer(IExternal d) public virtual {
+        d.notify(0);
+    }
+}
+
+contract SuperTransferChild is SuperTransferBase {
+    event Tick();
+
+    function emitAfterSuperTransfer(IExternal d) external {
+        super.transfer(d);
+        emit Tick(); //~WARN: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
+    }
+}
+
+contract RecursiveCacheKeyRepro {
+    event Tick();
+
+    ICall ext;
+    bool once;
+
+    function entry(bool flag) external {
+        once = false;
+        if (flag) {
+            helperA();
+            return;
+        }
+        noOp();
+        emit Tick(); //~WARN: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
+    }
+
+    function noOp() internal {
+        if (!once) {
+            once = true;
+            helperA();
+        }
+    }
+
+    function helperA() internal {
+        noOp();
+        ext.poke();
+    }
+}
+
+contract ModifierArgReachabilityRepro {
+    event Tick();
+
+    bool flag;
+
+    function ext() external returns (bool) {
+        flag = true;
+        return true;
+    }
+
+    modifier m(bool ok) {
+        _;
+    }
+
+    function entry(uint256 depth, bool useCache) external {
+        if (useCache) {
+            f(depth);
+            return;
+        }
+        c(depth);
+        emit Tick(); //~WARN: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
+    }
+
+    function f(uint256 depth) internal {
+        if (depth > 0) {
+            c(depth - 1);
+        }
+        hh();
+    }
+
+    function hh() internal m(this.ext()) {}
+
+    function c(uint256 depth) internal {
+        h(depth);
+    }
+
+    function h(uint256 depth) internal {
+        f(depth);
+    }
+}
+
 library NotifyLib {
     function notifyVia(IExternal d, uint256 v) internal {
         d.notify(v);
@@ -127,6 +216,20 @@ contract ReentrancyEvents {
         emit Tick(); //~WARN: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
     }
 
+    function emitAfterHelperHeavyFanout() external {
+        _doExternalWork();
+        _doExternalWork();
+        _doExternalWork();
+        _doExternalWork();
+        _doExternalWork();
+        _doExternalWork();
+        _doExternalWork();
+        _doExternalWork();
+        _doExternalWork();
+        _doExternalWork();
+        emit Tick(); //~WARN: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
+    }
+
     function emitAfterChainedCall() external {
         counter += 1;
         Other(other).action(counter);
```

### crates/lint/testdata/ReentrancyEvents.stderr
```diff
@@ -1,3 +1,27 @@
+warning[reentrancy-events]: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
+   ╭▸ ROOT/testdata/ReentrancyEvents.sol:LL:CC
+   │
+LL │ …     emit Tick();
+   │       ━━━━━━━━━━━━
+   │
+   ╰ help: https://getfoundry.sh/forge/linting/reentrancy-events
+
+warning[reentrancy-events]: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
+   ╭▸ ROOT/testdata/ReentrancyEvents.sol:LL:CC
+   │
+LL │ …     emit Tick();
+   │       ━━━━━━━━━━━━
+   │
+   ╰ help: https://getfoundry.sh/forge/linting/reentrancy-events
+
+warning[reentrancy-events]: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
+   ╭▸ ROOT/testdata/ReentrancyEvents.sol:LL:CC
+   │
+LL │ …     emit Tick();
+   │       ━━━━━━━━━━━━
+   │
+   ╰ help: https://getfoundry.sh/forge/linting/reentrancy-events
+
 warning[reentrancy-events]: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
    ╭▸ ROOT/testdata/ReentrancyEvents.sol:LL:CC
    │
@@ -94,6 +118,14 @@ LL │ …     emit Tick();
    │
    ╰ help: https://getfoundry.sh/forge/linting/reentrancy-events
 
+warning[reentrancy-events]: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
+   ╭▸ ROOT/testdata/ReentrancyEvents.sol:LL:CC
+   │
+LL │ …     emit Tick();
+   │       ━━━━━━━━━━━━
+   │
+   ╰ help: https://getfoundry.sh/forge/linting/reentrancy-events
+
 warning[reentrancy-events]: event emitted after an external call; reentrancy can reorder or fabricate logs that off-chain consumers rely on
    ╭▸ ROOT/testdata/ReentrancyEvents.sol:LL:CC
    │
```

### crates/lint/testdata/ReentrancyNoEth.sol
```diff
@@ -42,6 +42,21 @@ contract ReentrancyNoEth {
         balances[msg.sender] = 0;
     }
 
+    function helperHeavyCallThenWrite(IHook hook) external {
+        uint256 amount = balances[msg.sender];
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        notifyHookHeavy(hook, amount);
+        balances[msg.sender] = 0;
+    }
+
     function modifierWriteAfterCall(IHook hook) external writeAfter {
         uint256 amount = balances[msg.sender];
         hook.notify(amount); //~WARN: external call can be reentered before `balances` is updated
@@ -127,4 +142,8 @@ contract ReentrancyNoEth {
     function notifyHook(IHook hook, uint256 amount) internal {
         hook.notify(amount); //~WARN: external call can be reentered before `balances` is updated
     }
+
+    function notifyHookHeavy(IHook hook, uint256 amount) internal {
+        hook.notify(amount); //~WARN: external call can be reentered before `balances` is updated
+    }
 }
```
