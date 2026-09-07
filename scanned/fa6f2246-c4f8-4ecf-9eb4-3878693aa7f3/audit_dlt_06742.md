# [M] Replace old_sum_bias by old_bias

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-08-verwa
Published: 2023-08-09
Source: https://github.com/code-423n4/2023-08-verwa-findings/issues/140
Type: code-finding

## Details
```diff
diff --git a/src/GaugeController.sol b/src/GaugeController.sol
index 68b832a..1794639 100644
--- a/src/GaugeController.sol
+++ b/src/GaugeController.sol
@@ -250,7 +250,7 @@ contract GaugeController {
         uint256 old_sum_slope = points_sum[next_time].slope;
 
         points_weight[_gauge_addr][next_time].bias = Math.max(old_weight_bias + new_bias, old_bias) - old_bias;
-        points_sum[next_time].bias = Math.max(old_sum_bias + new_bias, old_sum_bias) - old_bias;
+        points_sum[next_time].bias = Math.max(old_sum_bias + new_bias, old_bias) - old_bias;
         if (old_slope.end > next_time) {
             points_weight[_gauge_addr][next_time].slope =
                 Math.max(old_weight_slope + new_slope.slope, old_slope.slope) -
```

_Originally posted by @iFrostizz in https://github.com/OpenCoreCH/test-squad-verwa/issues/111#issuecomment-1655611968_
