# [?] Added test for stack overflow fix (#3645)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2023-07-12
Source: https://github.com/starkware-libs/cairo/commit/d1a76d804546c46cd09ff61ddd771bc28c06a593
Type: security-commit

## Details
Added test for stack overflow fix (#3645)

## Patch
### crates/cairo-lang-sierra-gas/src/generate_equations_test.rs
```diff
@@ -6,7 +6,7 @@ use cairo_lang_sierra::program::StatementIdx;
 use indoc::indoc;
 use test_case::test_case;
 
-use super::generate_equations;
+use super::{generate_equations, get_reverse_topological_ordering};
 use crate::core_libfunc_cost_expr::CostExprMap;
 use crate::cost_expr::{CostExpr, Var};
 use crate::CostError;
@@ -114,3 +114,24 @@ fn generate(
     )?[CostTokenType::Const]
         .clone())
 }
+
+#[test]
+fn test_reverse_topological_ordering() {
+    let code = indoc! {"
+    branch() { 2() 4() 6() };
+    return();
+    jump() { 4() };
+    return();
+    jump() { 0() };
+    return();
+    return();
+    foo_a@0() -> ();
+    foo_b@2() -> ();
+    foo_c@4() -> ();
+    foo_d@6() -> ();
+"};
+    let program = cairo_lang_sierra::ProgramParser::new().parse(code).unwrap();
+    let ordering: Vec<usize> =
+        get_reverse_topological_ordering(&program).unwrap().into_iter().map(|x| x.0).collect();
+    assert_eq!(ordering, vec![4, 2, 6, 0]);
+}
```
