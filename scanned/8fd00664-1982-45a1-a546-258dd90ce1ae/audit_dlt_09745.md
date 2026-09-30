# [?] fix(recurringd): panic on parallel requests registering the same payment code

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2025-03-30
Source: https://github.com/fedimint/fedimint/commit/e91d47ddd11d1b40a84b65c052ce66b9433841de
Type: security-commit

## Details
fix(recurringd): panic on parallel requests registering the same payment code

## Patch
### fedimint-recurringd/src/lib.rs
```diff
@@ -188,7 +188,7 @@ impl RecurringInvoiceServer {
             &0,
         )
         .await;
-        dbtx.commit_tx().await;
+        dbtx.commit_tx_result().await?;
 
         Ok(payment_code)
     }
```
