# [?] Correct panic message

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-04-28
Source: https://github.com/penumbra-zone/penumbra/commit/bf409fb108e27e830a077d2c9f42185afa4ca80a
Type: security-commit

## Details
Correct panic message

## Patch
### tct/src/internal/frontier/item.rs
```diff
@@ -117,7 +117,7 @@ impl Forget for Item {
                 false
             }
         } else {
-            panic!("non-zero index when forgetting leaf");
+            panic!("non-zero index when forgetting item");
         }
     }
 }
```
