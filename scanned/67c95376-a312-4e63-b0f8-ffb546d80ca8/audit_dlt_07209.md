# [?] Fix - Direct mapping CPI caller privilege escalation after ownership transfer (#6709)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2025-06-28
Source: https://github.com/anza-xyz/agave/commit/517971f427aac9d48648452f2e4b5ba4e84b7491
Type: security-commit

## Details
Fix - Direct mapping CPI caller privilege escalation after ownership transfer (#6709)

* Demonstrate the issue by giving a no-op callee a readonly instruction account instead of a writable one.

* Fixes the issue by updating the MemoryRegion of the caller if it changed the owner at the CPI call edge.

* Feature gates the change.

## Patch
### programs/bpf_loader/src/syscalls/cpi.rs
```diff
@@ -881,11 +881,12 @@ where
                 direct_mapping,
             )?;
 
-            let caller_account = if instruction_account.is_writable || update_caller {
-                Some(caller_account)
-            } else {
-                None
-            };
+            let caller_account =
+                if instruction_account.is_writable || (direct_mapping && update_caller) {
+                    Some(caller_account)
+                } else {
+                    None
+                };
             accounts.push((instruction_account.index_in_caller, caller_account));
         } else {
             ic_msg!(
@@ -1184,6 +1185,8 @@ fn update_callee_account(
     // Change the owner at the end so that we are allowed to change the lamports and data before
     if callee_account.get_owner() != caller_account.owner {
         callee_account.set_owner(caller_account.owner.as_ref())?;
+        // caller gave ownership and thus write access away, so caller must be updated
+        must_update_caller = true;
     }
 
     Ok(must_update_caller)
```

### programs/sbf/rust/invoke/src/lib.rs
```diff
@@ -742,7 +742,7 @@ fn process_instruction<'a>(
                 &create_instruction(
                     *invoked_program_id,
                     &[
-                        (accounts[ARGUMENT_INDEX].key, true, false),
+                        (accounts[ARGUMENT_INDEX].key, false, false),
                         (invoked_program_id, false, false),
                     ],
                     vec![RETURN_OK],
```
