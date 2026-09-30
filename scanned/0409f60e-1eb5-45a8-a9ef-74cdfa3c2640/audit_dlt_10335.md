# [?] fix(vault_transaction_execute): static_accounts subtraction overflow

## Summary
Severity: Unknown
Chain: Solana
Component: Squads-Protocol/v4
Published: 2023-08-16
Source: https://github.com/Squads-Protocol/v4/commit/2ddacd28915528e6c85054de7b90407e40adffc9
Type: security-commit

## Details
fix(vault_transaction_execute): static_accounts subtraction overflow

## Patch
### programs/multisig/src/utils/executable_transaction_message.rs
```diff
@@ -240,6 +240,11 @@ impl<'a, 'info> ExecutableTransactionMessage<'a, 'info> {
             return true;
         }
 
+        if index < self.static_accounts.len() {
+            // Index is within static accounts but is not writable.
+            return false;
+        }
+
         // "Skip" the static account indexes.
         let index = index - self.static_accounts.len();
 
```
