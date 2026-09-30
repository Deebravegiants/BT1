# [?] Merge pull request #5876 from mempool/natsoni/fix-hashrate-chart-overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2025-04-16
Source: https://github.com/mempool/mempool/commit/f218ff26ab1e18209117b9de25b8219a95e1d542
Type: security-commit

## Details
Merge pull request #5876 from mempool/natsoni/fix-hashrate-chart-overflow

Fix cropped difficulty series in hashrate chart

## Patch
### frontend/src/app/components/hashrate-chart/hashrate-chart.component.ts
```diff
@@ -370,9 +370,10 @@ export class HashrateChartComponent implements OnInit {
             const newMin = Math.floor(firstYAxisMin / selectedPowerOfTen.divider / 10)
             return 600 / 2 ** 32 * newMin * selectedPowerOfTen.divider * 10;
           },
-          max: (_) => {
+          max: (value) => {
             const firstYAxisMax = this.chartInstance.getModel().getComponent('yAxis', 0).axis.scale.getExtent()[1];
-            return 600 / 2 ** 32 * firstYAxisMax;
+            const scaledMax = 600 / 2 ** 32 * firstYAxisMax;
+            return Math.max(scaledMax, value.max);
           },
           axisLabel: {
             color: 'rgb(110, 112, 121)',
```
