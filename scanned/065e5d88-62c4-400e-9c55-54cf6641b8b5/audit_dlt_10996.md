# [?] Fix compiler panic on exit modified variables not in env

## Summary
Severity: Unknown
Chain: ZK
Component: iden3/circom
Published: 2022-05-23
Source: https://github.com/iden3/circom/commit/abbacdcaf258db86e06740071de6c381ef2766bb
Type: security-commit

## Details
Fix compiler panic on exit modified variables not in env

## Patch
### type_analysis/src/analyzers/unknown_known_analysis.rs
```diff
@@ -213,8 +213,10 @@ fn analyze(stmt: &Statement, entry_information: EntryInformation) -> ExitInforma
 
             if tag_out == Unknown{
                 for var in &exit.modified_variables{
-                    let value = environment.get_mut_variable_or_break(var, file!(), line!());
-                    *value = Unknown;
+                    if environment.has_variable(var){
+                        let value = environment.get_mut_variable_or_break(var, file!(), line!());
+                        *value = Unknown;
+                    }
                 }   
             }
 
```
