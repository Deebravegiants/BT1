# [?] fix(mempool): attribute peer-pushed invalid transactions for misbehavior scoring (GHSA-g7c4-2w6c-cr3r)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-07-16
Source: https://github.com/ZcashFoundation/zebra/commit/fb3e9ec7b3b86f4be862f30ba06fbbeb9ad54ec0
Type: security-commit

## Details
fix(mempool): attribute peer-pushed invalid transactions for misbehavior scoring (GHSA-g7c4-2w6c-cr3r)

Co-Authored-By: evan-forbes <evan.samuel.forbes@gmail.com>

## Patch
### zebrad/src/components/mempool/downloads.rs
```diff
@@ -376,6 +376,7 @@ where
         let network = self.network.clone();
         let verifier = self.verifier.clone();
         let mut state = self.state.clone();
+        let pushed_advertiser_addr = source.map(PeerSocketAddr::from);
 
         let gossiped_tx_req = gossiped_tx.clone();
 
@@ -431,7 +432,7 @@ where
                         "mempool.pushed.transactions.total",
                         "version" => format!("{}",tx.transaction.version()),
                     ).increment(1);
-                    (tx, None)
+                    (tx, pushed_advertiser_addr)
                 }
             };
 
```
