# [?] Avoid panic when estimate_size return isize::max. (#7917)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2025-07-06
Source: https://github.com/starkware-libs/cairo/commit/8fc7dae9db6745fedfe654f29ee043d61817531a
Type: security-commit

## Details
Avoid panic when estimate_size return isize::max. (#7917)

## Patch
### crates/cairo-lang-lowering/src/specialization.rs
```diff
@@ -209,5 +209,6 @@ pub fn priv_should_specialize(
     }
 
     // The heuristic is that the size is 8/10*orig_size > specialized_size of the original size.
-    Ok(8 * db.estimate_size(specialized_func.base)? > 10 * db.estimate_size(function_id)?)
+    Ok(db.estimate_size(specialized_func.base)?.saturating_mul(8)
+        > db.estimate_size(function_id)?.saturating_mul(10))
 }
```
