# [?] Fix tx page crash when accelerationHistory errors

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-06-23
Source: https://github.com/mempool/mempool/commit/06f60df4cf02c2c21977877e88d6e941a3a45e8c
Type: security-commit

## Details
Fix tx page crash when accelerationHistory errors

## Patch
### frontend/src/app/components/transaction/transaction.component.ts
```diff
@@ -294,7 +294,7 @@ export class TransactionComponent implements OnInit, AfterViewInit, OnDestroy {
         return this.servicesApiService.getAccelerationHistory$({ blockHeight });
       }),
       catchError(() => {
-        return of(null);
+        return of([]);
       })
     ).subscribe((accelerationHistory) => {
       for (const acceleration of accelerationHistory) {
```
