# [?] set the correct max gas amount value to avoid vm crash

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-03-03
Source: https://github.com/starcoinorg/starcoin/commit/6d5b1e5e5c39d58677fa5b32cb59a8a05c0ea653
Type: security-commit

## Details
set the correct max gas amount value to avoid vm crash

## Patch
### types/src/transaction/mod.rs
```diff
@@ -237,7 +237,7 @@ impl RawUserTransaction {
             AccountAddress::default(),
             0,
             TransactionPayload::Script(Script::new(compiled_script, vec![])),
-            0,
+            600,
             0,
             Duration::new(0, 0),
         )
```

### vm/vm-runtime/src/starcoin_vm.rs
```diff
@@ -152,6 +152,7 @@ impl StarcoinVM {
                 .unwrap_or_else(discard_libra_error_output)
         });
         // TODO convert to starcoin type
+        info!("{:?}", output);
         TransactionHelper::to_starcoin_TransactionOutput(output)
     }
 
```
