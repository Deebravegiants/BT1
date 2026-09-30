# [?] fix fees box theme pipe race condition error

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2026-01-06
Source: https://github.com/mempool/mempool/commit/1d00a3e6659c8423201e49544d02d5427d02742a
Type: security-commit

## Details
fix fees box theme pipe race condition error

## Patch
### frontend/src/app/components/fees-box/fees-box.component.ts
```diff
@@ -44,10 +44,13 @@ export class FeesBoxComponent implements OnInit, OnDestroy {
     );
     this.themeSubscription = this.themeService.themeChanged$.subscribe(() => {
       this.setFeeGradient();
-    })
+    });
   }
 
   setFeeGradient() {
+    if (!this.fees || !this.themeService.mempoolFeeColors) {
+      return;
+    }
     let feeLevelIndex = feeLevels.slice().reverse().findIndex((feeLvl) => this.fees.minimumFee >= feeLvl);
     feeLevelIndex = feeLevelIndex >= 0 ? feeLevels.length - feeLevelIndex : feeLevelIndex;
     const startColor = '#' + (this.themeService.mempoolFeeColors[feeLevelIndex - 1] || this.themeService.mempoolFeeColors[this.themeService.mempoolFeeColors.length - 1]);
```
