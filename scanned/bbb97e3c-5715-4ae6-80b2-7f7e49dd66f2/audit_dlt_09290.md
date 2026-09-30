# [?] fix(traces): avoid panic on invalid internal source spans (#14273)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-04-14
Source: https://github.com/foundry-rs/foundry/commit/9f465099b6d0d8597d4e191f633c7d9795c4c841
Type: security-commit

## Details
fix(traces): avoid panic on invalid internal source spans (#14273)

* fix(traces): avoid panic on invalid internal source spans

* fix(traces): place debug trace tests after helpers

## Patch
### crates/evm/traces/src/debug/mod.rs
```diff
@@ -143,18 +143,19 @@ impl<'a> DebugStepsWalker<'a> {
         // Try to decode function inputs and outputs from the stack and memory.
         let (inputs, outputs) = self
             .src_map(start_idx + 1)
-            .map(|(source_element, source)| {
+            .and_then(|(source_element, source)| {
                 let start = source_element.offset() as usize;
-                let end = start + source_element.length() as usize;
-                let fn_definition = source.source[start..end].replace('\n', "");
+                let (fn_definition, _) =
+                    source_span(&source.source, start, source_element.length() as usize)?;
+                let fn_definition = fn_definition.replace('\n', "");
                 let (inputs, outputs) = parse_types(&fn_definition);
 
-                (
+                Some((
                     inputs.and_then(|t| {
                         try_decode_args_from_step(&t, &self.node.trace.steps[start_idx + 1])
                     }),
                     outputs.and_then(|t| try_decode_args_from_step(&t, self.current_step())),
-                )
+                ))
             })
             .unwrap_or_default();
 
@@ -199,15 +200,8 @@ impl<'a> DebugStepsWalker<'a> {
 /// Returns string in the format `Contract::function`.
 fn parse_function_from_loc(source: &SourceData, loc: &SourceElement) -> Option<String> {
     let start = loc.offset() as usize;
-    let end = start + loc.length() as usize;
-    let src_len = source.source.len();
+    let (source_part, end) = source_span(&source.source, start, loc.length() as usize)?;
 
-    // Handle special case of preprocessed test sources.
-    if start > src_len || end > src_len {
-        return None;
-    }
-
-    let source_part = &source.source[start..end];
     if !source_part.starts_with("function") {
         return None;
     }
@@ -217,6 +211,12 @@ fn parse_function_from_loc(source: &SourceData, loc: &SourceElement) -> Option<S
     Some(format!("{contract_name}::{function_name}"))
 }
 
+fn source_span(source: &str, start: usize, len: usize) -> Option<(&str, usize)> {
+    let end = start.checked_add(len)?;
+
+    Some((source.get(start..end)?, end))
+}
+
 /// Parses function input and output types into [Parameters].
 fn parse_types(source: &str) -> (Option<Parameters<'_>>, Option<Parameters<'_>>) {
     let inputs = source.find('(').and_then(|params_start| {
@@ -329,3 +329,15 @@ fn decode_from_memory(ty: &DynSolType, memory: &[u8], location: usize) -> Option
         _ => ty.abi_decode(first_word).ok(),
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::source_span;
+
+    #[test]
+    fn source_span_returns_none_for_invalid_ranges() {
+        assert_eq!(source_span("abcdef", 2, 3), Some(("cde", 5)));
+        assert_eq!(source_span("abcdef", 7, 1), None);
+        assert_eq!(source_span("abcdef", usize::MAX, 1), None);
+    }
+}
```
