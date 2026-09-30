# [?] Fix race condition between accelerations and block audit api calls

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-09-20
Source: https://github.com/mempool/mempool/commit/e41829d5e02ce8af002a06505c09dd7134481e7f
Type: security-commit

## Details
Fix race condition between accelerations and block audit api calls

## Patch
### frontend/src/app/components/block/block.component.ts
```diff
@@ -327,7 +327,7 @@ export class BlockComponent implements OnInit, OnDestroy {
       })
     ).subscribe((accelerations) => {
       this.accelerations = accelerations;
-      if (accelerations.length) {
+      if (accelerations.length && this.strippedTransactions) { // Don't call setupBlockAudit if we don't have transactions yet; it will be called later in overviewSubscription
         this.setupBlockAudit();
       }
     });
```
