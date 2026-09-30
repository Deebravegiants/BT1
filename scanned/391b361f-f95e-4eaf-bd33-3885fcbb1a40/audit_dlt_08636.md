# [?] [actors consensus fix] F23 fix gas calculation overflow, add a nice error message (#100)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/ref-fvm
Published: 2021-12-07
Source: https://github.com/filecoin-project/ref-fvm/commit/a0ee3410026e7f657f7aa7475c02c41cd489b76b
Type: security-commit

## Details
[actors consensus fix] F23 fix gas calculation overflow, add a nice error message (#100)

* fix gas calculation overflow error, add a nice error message

* adding changes to FVM as well

## Patch
### _forest/vm/interpreter/src/gas_tracker/mod.rs
```diff
@@ -25,16 +25,27 @@ impl GasTracker {
     /// enough gas remaining for charge.
     pub fn charge_gas(&mut self, charge: GasCharge) -> Result<(), ActorError> {
         let to_use = charge.total();
-        let used = self.gas_used + to_use;
-        if used > self.gas_available {
-            self.gas_used = self.gas_available;
-            Err(actor_error!(SysErrOutOfGas;
-                    "not enough gas (used={}) (available={})",
-               used, self.gas_available
-            ))
-        } else {
-            self.gas_used += to_use;
-            Ok(())
+        let used_or = self.gas_used.checked_add(to_use);
+         match used_or {
+             None => {
+                 self.gas_used = self.gas_available;
+                 Err(actor_error!(SysErrOutOfGas;
+                     "adding gas_used={} and to_use={} overflowed",
+                     self.gas_used, to_use
+                 ))
+             },
+             Some(used) => {        
+                 if used > self.gas_available {
+                     self.gas_used = self.gas_available;
+                     Err(actor_error!(SysErrOutOfGas;
+                             "not enough gas (used={}) (available={})",
+                        used, self.gas_available
+                     ))
+                 } else {
+                     self.gas_used += to_use;
+                     Ok(())
+                 }
+             }
         }
     }
 
```

### fvm/src/gas/mod.rs
```diff
@@ -27,16 +27,27 @@ impl GasTracker {
     /// enough gas remaining for charge.
     pub fn charge_gas(&mut self, charge: GasCharge) -> Result<(), ActorError> {
         let to_use = charge.total();
-        let used = self.gas_used + to_use;
-        if used > self.gas_available {
-            self.gas_used = self.gas_available;
-            Err(actor_error!(SysErrOutOfGas;
-                    "not enough gas (used={}) (available={})",
-               used, self.gas_available
-            ))
-        } else {
-            self.gas_used += to_use;
-            Ok(())
+        let used_or = self.gas_used.checked_add(to_use);
+        match used_or {
+            None => {
+                self.gas_used = self.gas_available;
+                Err(actor_error!(SysErrOutOfGas;
+                    "adding gas_used={} and to_use={} overflowed",
+                    self.gas_used, to_use
+                ))
+            }
+            Some(used) => {
+                if used > self.gas_available {
+                    self.gas_used = self.gas_available;
+                    Err(actor_error!(SysErrOutOfGas;
+                            "not enough gas (used={}) (available={})",
+                       used, self.gas_available
+                    ))
+                } else {
+                    self.gas_used += to_use;
+                    Ok(())
+                }
+            }
         }
     }
 
```
