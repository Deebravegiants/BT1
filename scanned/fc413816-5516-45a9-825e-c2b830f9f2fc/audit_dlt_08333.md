# [?] Update naming and prevent panic on unwrap

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-05-29
Source: https://github.com/aptos-labs/aptos-core/commit/5bf92249cb531a7f51b9fa6f688ccfdccb4114fd
Type: security-commit

## Details
Update naming and prevent panic on unwrap

## Patch
### third_party/move/tools/move-linter/src/model_ast_lints/redundant_boolean_expressions.rs
```diff
@@ -24,10 +24,7 @@ use move_model::{
 use ExpData::Call;
 use Operation::{And, Not, Or};
 
-#[derive(Default)]
-pub struct RedundantBooleanExpression;
-
-fn get_text_from_span(env: &GlobalEnv, exp_data: &ExpData) -> Option<String> {
+fn get_text_from_expr(env: &GlobalEnv, exp_data: &ExpData) -> Option<String> {
     let loc = env.get_node_loc(exp_data.node_id());
     let file_id = loc.file_id();
     let source = env.get_file_source(file_id);
@@ -47,14 +44,14 @@ struct RedundantPattern {
 impl RedundantPattern {
     fn new(env: &GlobalEnv, original: &ExpData, simplified: &ExpData) -> Self {
         Self {
-            original_expr: get_text_from_span(env, original).unwrap(),
-            simplified_expr: get_text_from_span(env, simplified).unwrap(),
+            original_expr: get_text_from_expr(env, original).unwrap_or_default(),
+            simplified_expr: get_text_from_expr(env, simplified).unwrap_or_default(),
         }
     }
 
     fn new_with_text(env: &GlobalEnv, original: &ExpData, simplified_text: String) -> Self {
         Self {
-            original_expr: get_text_from_span(env, original).unwrap(),
+            original_expr: get_text_from_expr(env, original).unwrap_or_default(),
             simplified_expr: simplified_text,
         }
     }
@@ -67,6 +64,9 @@ impl RedundantPattern {
     }
 }
 
+#[derive(Default)]
+pub struct RedundantBooleanExpression;
+
 impl RedundantBooleanExpression {
     /// Check if two expressions are structurally equal
     fn is_expression_equal(&self, expr1: &ExpData, expr2: &ExpData) -> bool {
@@ -169,9 +169,9 @@ impl RedundantBooleanExpression {
                         let other_right = &right_args[1 - j];
 
                         if let (Some(common_text), Some(left_text), Some(right_text)) = (
-                            get_text_from_span(env, left_elem.as_ref()),
-                            get_text_from_span(env, other_left.as_ref()),
-                            get_text_from_span(env, other_right.as_ref()),
+                            get_text_from_expr(env, left_elem.as_ref()),
+                            get_text_from_expr(env, other_left.as_ref()),
+                            get_text_from_expr(env, other_right.as_ref()),
                         ) {
                             let inner_op_str = match inner_op {
                                 And => " && ",
```
