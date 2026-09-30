# [?] runtime: fix possible deadlock in in_mem_accounts_index (#26046)

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-06-23
Source: https://github.com/solana-labs/solana/commit/355e09e1fb5630f8487afe640ba9b12067057999
Type: security-commit

## Details
runtime: fix possible deadlock in in_mem_accounts_index (#26046)

## Patch
### runtime/src/in_mem_accounts_index.rs
```diff
@@ -147,6 +147,7 @@ impl<T: IndexValue> InMemAccountsIndex<T> {
                 result.push((*k, Arc::clone(v)));
             }
         });
+        drop(map);
         self.hold_range_in_memory(range, false);
         Self::update_stat(&self.stats().items, 1);
         Self::update_time_stat(&self.stats().items_us, m);
```
