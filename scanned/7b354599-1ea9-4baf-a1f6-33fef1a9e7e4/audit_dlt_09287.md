# [?] fix(lint): avoid unnecessary reentrancy call classification (#15042)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-06-03
Source: https://github.com/foundry-rs/foundry/commit/e7c5dafd09b352ff9c6806693a2c4dad0c5d424c
Type: security-commit

## Details
fix(lint): avoid unnecessary reentrancy call classification (#15042)

## Patch
### crates/forge/tests/cli/verify_bytecode.rs
```diff
@@ -322,8 +322,9 @@ forgetest_async!(flaky_can_verify_bytecode_fails_on_source_mismatch, |prj, cmd|
         bytecode_hash: BytecodeHash::None,
         ..Default::default()
     });
-    // Build once with correct source (creates cache)
-    cmd.forge_fuse().arg("build").assert_success();
+    // Build once with correct source (creates cache). Linting is unrelated to bytecode
+    // verification here and can dominate runtime on the flattened Etherscan source.
+    cmd.forge_fuse().args(["build", "--no-lint"]).assert_success();
 
     let source_code = r#"
     contract SystemConfig {
```

### crates/lint/src/sol/high/reentrancy.rs
```diff
@@ -48,6 +48,9 @@ impl<'hir> LateLintPass<'hir> for ReentrancyEth {
         let Some(body) = func.body else { return };
 
         let mut analyzer = Analyzer::new(ctx, gcx, hir);
+        if !analyzer.has_enabled_lints() {
+            return;
+        }
         let mut state = FlowState::default();
         analyzer.analyze_callable(func, body, &mut state);
     }
@@ -115,11 +118,25 @@ struct Analyzer<'ctx, 's, 'c, 'hir> {
     hir: &'hir hir::Hir<'hir>,
     emitted: HashSet<Span>,
     call_stack: Vec<FunctionId>,
+    reentrancy_eth_enabled: bool,
+    reentrancy_no_eth_enabled: bool,
 }
 
 impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
     fn new(ctx: &'ctx LintContext<'s, 'c>, gcx: Gcx<'hir>, hir: &'hir hir::Hir<'hir>) -> Self {
-        Self { ctx, gcx, hir, emitted: HashSet::new(), call_stack: Vec::new() }
+        Self {
+            ctx,
+            gcx,
+            hir,
+            emitted: HashSet::new(),
+            call_stack: Vec::new(),
+            reentrancy_eth_enabled: ctx.is_lint_enabled(REENTRANCY_ETH.id),
+            reentrancy_no_eth_enabled: ctx.is_lint_enabled(REENTRANCY_NO_ETH.id),
+        }
+    }
+
+    const fn has_enabled_lints(&self) -> bool {
+        self.reentrancy_eth_enabled || self.reentrancy_no_eth_enabled
     }
 
     fn analyze_callable(
@@ -325,7 +342,9 @@ impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
                 for func_id in resolved_function_ids(callee) {
                     self.analyze_internal_call(func_id, state);
                 }
-                if let Some(kind) = reentrant_call_kind(self.gcx, self.hir, callee, args, *opts) {
+                if !state.state_reads.is_empty()
+                    && let Some(kind) = self.reentrant_call_kind(callee, args, *opts)
+                {
                     state.push_call(expr.span, kind);
                 }
             }
@@ -462,6 +481,23 @@ impl<'ctx, 's, 'c, 'hir> Analyzer<'ctx, 's, 'c, 'hir> {
             }
         }
     }
+
+    fn reentrant_call_kind(
+        &self,
+        callee: &'hir hir::Expr<'hir>,
+        args: &CallArgs<'hir>,
+        opts: Option<&'hir [hir::NamedArg<'hir>]>,
+    ) -> Option<ReentrantCallKind> {
+        if self.reentrancy_eth_enabled && is_uncapped_value_call(self.hir, callee, opts) {
+            return Some(ReentrantCallKind::Eth);
+        }
+        if self.reentrancy_no_eth_enabled
+            && is_no_eth_reentrant_call(self.gcx, self.hir, callee, args, opts)
+        {
+            return Some(ReentrantCallKind::NoEth);
+        }
+        None
+    }
 }
 
 impl FlowState {
@@ -486,19 +522,6 @@ impl FlowState {
     }
 }
 
-fn reentrant_call_kind<'hir>(
-    gcx: Gcx<'hir>,
-    hir: &'hir hir::Hir<'hir>,
-    callee: &'hir hir::Expr<'hir>,
-    args: &CallArgs<'hir>,
-    opts: Option<&'hir [hir::NamedArg<'hir>]>,
-) -> Option<ReentrantCallKind> {
-    if is_uncapped_value_call(hir, callee, opts) {
-        return Some(ReentrantCallKind::Eth);
-    }
-    is_no_eth_reentrant_call(gcx, hir, callee, args, opts).then_some(ReentrantCallKind::NoEth)
-}
-
 fn is_uncapped_value_call(
     hir: &hir::Hir<'_>,
     callee: &hir::Expr<'_>,
```
