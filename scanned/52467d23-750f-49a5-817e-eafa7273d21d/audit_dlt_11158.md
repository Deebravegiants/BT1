# [?] fix panic on empty trait impl (#838)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2022-02-24
Source: https://github.com/FuelLabs/sway/commit/06b5bc488833fdf5bea5617dcdd4746b79bf5575
Type: security-commit

## Details
fix panic on empty trait impl (#838)

## Patch
### sway-core/src/parse_tree/declaration/impl_trait.rs
```diff
@@ -76,11 +76,14 @@ impl ImplTrait {
             errors
         );
 
-        let where_clause_pair = if iter.peek().unwrap().as_rule() == Rule::trait_bounds {
-            iter.next()
-        } else {
-            None
+        let where_clause_pair = match iter.peek() {
+            Some(r) => match r.as_rule() {
+                Rule::trait_bounds => iter.next(),
+                _ => None,
+            },
+            None => None,
         };
+
         let type_arguments_span = match type_params_pair {
             Some(ref x) => Span {
                 span: x.as_span(),
```
