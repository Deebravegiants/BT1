# [?] Merge pull request #5204 from mempool/simon/fix-tx-position-crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-06-24
Source: https://github.com/mempool/mempool/commit/e4c9b67239639a82ceaaff6541591c2fd21dafc0
Type: security-commit

## Details
Merge pull request #5204 from mempool/simon/fix-tx-position-crash

Fix tx position frontend error

## Patch
### frontend/src/app/components/mempool-blocks/mempool-blocks.component.ts
```diff
@@ -412,7 +412,7 @@ export class MempoolBlocksComponent implements OnInit, OnChanges, OnDestroy {
   }
 
   calculateTransactionPosition() {
-    if ((!this.txPosition && !this.txFeePerVSize && (this.markIndex === undefined || this.markIndex === -1)) || !this.mempoolBlocks) {
+    if ((!this.txPosition && !this.txFeePerVSize && (this.markIndex === undefined || this.markIndex === -1)) || !this.mempoolBlocks?.length) {
       this.arrowVisible = false;
       return;
     } else if (this.markIndex > -1) {
```
