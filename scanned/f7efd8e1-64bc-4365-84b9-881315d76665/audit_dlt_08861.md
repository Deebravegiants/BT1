# [?] Prevented `cairo-test` crash on bad test attributes. (#6572)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-11-03
Source: https://github.com/starkware-libs/cairo/commit/03cf46e2c2f8db0050d1872d8a894683f6eed40b
Type: security-commit

## Details
Prevented `cairo-test` crash on bad test attributes. (#6572)

## Patch
### crates/cairo-lang-test-plugin/src/lib.rs
```diff
@@ -263,7 +263,7 @@ fn find_all_tests(
                 else {
                     return None;
                 };
-                Some((*func_id, try_extract_test_config(db.upcast(), attrs).unwrap()?))
+                Some((*func_id, try_extract_test_config(db.upcast(), attrs).ok()??))
             }));
         }
     }
```
