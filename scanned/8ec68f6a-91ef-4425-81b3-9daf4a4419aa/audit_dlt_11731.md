# [?] fixes crash with missing pool partner

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-07-28
Source: https://github.com/mempool/mempool/commit/e3bb812203e317e96aaa9423c742e5da01ea871e
Type: security-commit

## Details
fixes crash with missing pool partner

fixes #5379

## Patch
### frontend/src/app/components/transaction/transaction.component.ts
```diff
@@ -844,7 +844,7 @@ export class TransactionComponent implements OnInit, AfterViewInit, OnDestroy {
     }
     if (this.isAcceleration) {
       // this immediately returns cached stats if we fetched them recently
-      this.miningService.getMiningStats('1w').subscribe(stats => {
+      this.miningService.getMiningStats('1m').subscribe(stats => {
         this.miningStats = stats;
         this.isAccelerated$.next(this.isAcceleration); // hack to trigger recalculation of ETA without adding another source observable
       });
```
