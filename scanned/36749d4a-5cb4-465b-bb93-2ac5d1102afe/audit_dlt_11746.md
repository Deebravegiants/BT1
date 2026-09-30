# [?] Merge pull request #4640 from mempool/fix-liquid-frontend-crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-02-04
Source: https://github.com/mempool/mempool/commit/a15729c38f2c67c844d9694bcba2533bdda63fa2
Type: security-commit

## Details
Merge pull request #4640 from mempool/fix-liquid-frontend-crash

Fix Liquid frontend crash

## Patch
### frontend/src/app/components/transaction/transaction.component.ts
```diff
@@ -507,7 +507,7 @@ export class TransactionComponent implements OnInit, AfterViewInit, OnDestroy {
           }
         }
       }
-      if (!found && txFeePerVSize < mempoolBlocks[mempoolBlocks.length - 1].feeRange[0]) {
+      if (!found && mempoolBlocks.length && txFeePerVSize < mempoolBlocks[mempoolBlocks.length - 1].feeRange[0]) {
         this.txInBlockIndex = 7;
       }
     });
```
