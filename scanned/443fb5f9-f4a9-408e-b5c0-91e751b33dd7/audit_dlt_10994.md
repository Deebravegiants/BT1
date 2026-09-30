# [?] Fixing panic: handling case array of components with different signals (signals defined inside blocks ifs)

## Summary
Severity: Unknown
Chain: ZK
Component: iden3/circom
Published: 2023-11-14
Source: https://github.com/iden3/circom/commit/a2c67649759437adf692c0f8d6773e364a47efd8
Type: security-commit

## Details
Fixing panic: handling case array of components with different signals (signals defined inside blocks ifs)

## Patch
### compiler/src/hir/analysis_utilities.rs
```diff
@@ -54,15 +54,24 @@ pub fn build_component_info(triggers: &Vec<Trigger>) -> HashMap<String, HashMap<
             Some(old) => max_vct(signals, old),
         };
         external_signals.insert(trigger.component_name.clone(), signals);
+
     }
     external_signals
 }
 fn max_vct(l: HashMap<String, VCT>, mut r: HashMap<String, VCT>) -> HashMap<String, VCT> {
     let mut result = HashMap::new();
+
     for (s, tl) in l {
-        let tr = r.remove(&s).unwrap();
-        let max = std::cmp::max(tl, tr);
-        result.insert(s, max);
+        if r.contains_key(&s) {
+            let tr = r.remove(&s).unwrap();
+            let max = std::cmp::max(tl, tr);
+            result.insert(s, max);
+        } else{
+            result.insert(s, tl);
+        }
+    }
+    for (s, tr) in r{
+        result.insert(s, tr);
     }
     result
 }
```
