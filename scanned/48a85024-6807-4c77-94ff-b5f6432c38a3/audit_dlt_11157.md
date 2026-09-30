# [?] Avoid a panic when a Sway file starts with something unexpected (#843)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2022-02-26
Source: https://github.com/FuelLabs/sway/commit/18d4e5896de3a962a11bdac60009083919ee0b68
Type: security-commit

## Details
Avoid a panic when a Sway file starts with something unexpected (#843)

## Patch
### forc/src/utils/helpers.rs
```diff
@@ -308,6 +308,7 @@ fn construct_window<'a>(
     const NUM_LINES_BUFFER: usize = 2;
 
     let total_lines_in_input = input.chars().filter(|x| *x == '\n').count();
+    debug_assert!(end.line >= start.line);
     let total_lines_of_highlight = end.line - start.line;
     debug_assert!(total_lines_in_input > total_lines_of_highlight);
 
@@ -320,7 +321,7 @@ fn construct_window<'a>(
             current_line += 1
         }
 
-        if current_line >= start.line - NUM_LINES_BUFFER && calculated_start_ix.is_none() {
+        if current_line + NUM_LINES_BUFFER >= start.line && calculated_start_ix.is_none() {
             calculated_start_ix = Some(ix);
             lines_to_start_of_snippet = current_line;
         }
@@ -336,8 +337,8 @@ fn construct_window<'a>(
     let calculated_start_ix = calculated_start_ix.unwrap_or(0);
     let calculated_end_ix = calculated_end_ix.unwrap_or(input.len());
 
-    *start_ix -= calculated_start_ix;
-    *end_ix -= calculated_start_ix;
+    *start_ix -= std::cmp::min(calculated_start_ix, *start_ix);
+    *end_ix -= std::cmp::min(calculated_start_ix, *end_ix);
     start.line = lines_to_start_of_snippet;
     &input[calculated_start_ix..calculated_end_ix]
 }
```
