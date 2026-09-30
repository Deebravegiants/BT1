# [?] fix: tx-pool may panic after detached

## Summary
Severity: Unknown
Chain: Nervos
Component: nervosnetwork/ckb
Published: 2023-03-15
Source: https://github.com/nervosnetwork/ckb/commit/5b9c904d1fda7aac477215a112c57a64e1c27c64
Type: security-commit

## Details
fix: tx-pool may panic after detached

## Patch
### tx-pool/src/component/commit_txs_scanner.rs
```diff
@@ -200,14 +200,16 @@ impl<'a> CommitTxsScanner<'a> {
                 .iter()
                 .filter(|id| !already_added.contains_key(id))
             {
-                let mut desc = self.modified_entries.remove(desc_id).unwrap_or_else(|| {
-                    self.proposed_pool
-                        .get(desc_id)
-                        .map(ToOwned::to_owned)
-                        .expect("pool consistent")
-                });
-                desc.sub_entry_weight(entry);
-                self.modified_entries.insert(desc);
+                // Note: since https://github.com/nervosnetwork/ckb/pull/3706
+                // calc_descendants() may not consistent
+                if let Some(mut desc) = self
+                    .modified_entries
+                    .remove(desc_id)
+                    .or_else(|| self.proposed_pool.get(desc_id).cloned())
+                {
+                    desc.sub_entry_weight(entry);
+                    self.modified_entries.insert(desc);
+                }
             }
         }
     }
```
