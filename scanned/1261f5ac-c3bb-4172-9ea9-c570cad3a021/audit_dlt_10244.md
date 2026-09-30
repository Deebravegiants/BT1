# [?] sidevm: Fix the panic in tokio thread while the runtime is shuting down.

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2022-06-20
Source: https://github.com/Phala-Network/phala-blockchain/commit/7785d9cb190134ec0101a44ffef43b28b602070a
Type: security-commit

## Details
sidevm: Fix the panic in tokio thread while the runtime is shuting down.

## Patch
### crates/pink/sidevm/host-runtime/src/service.rs
```diff
@@ -94,6 +94,10 @@ impl ServiceRun {
                 }
             }
         }
+
+        // To avoid: panicked at 'Cannot drop a runtime in a context where blocking is not allowed.'
+        let handle = self.runtime.handle().clone();
+        handle.spawn_blocking(move || drop(self));
     }
 }
 
```
