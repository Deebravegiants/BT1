# [?] Fix tx position crash

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2024-06-24
Source: https://github.com/mempool/mempool/commit/91ddf7ea98b97766ebd90a920e18e345d7b9c761
Type: security-commit

## Details
Fix tx position crash

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
