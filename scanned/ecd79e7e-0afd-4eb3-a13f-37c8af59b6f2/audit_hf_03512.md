# [M] Replace `old_sum_bias` by `old_bias`

## Summary
Severity: Medium
Contest weight: 0.2174
Dataset id: 19220
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_Note: This audit was preceded by a [Code4rena Test Coverage competition](https://code4rena.com/test-coverage). While auditing was not the purpose of the testing phase, relevant and valuable findings reported during that phase were eligible to be judged. This finding [M-03] was discovered during that period and is being included here for completeness._
    
diff --git a/src/GaugeController.sol b/src/GaugeController.sol
index 68b832a..1794639 100644
--- a/src/GaugeController.sol
+++ b/src/GaugeController.sol
@@ -250,7 +250,7 @@ contract GaugeController {
        uint256 old_sum_slope = points_sum[next_time].slope;

        points_weight[_gauge_addr][next_time].bias = Math.max(old_weight_bias + new_bias, old_bias) - old_bias;
-       points_sum[next_time].bias = Math.max(old_sum_bias + new_bias, old_sum_bias) - old_bias;
+       points_sum[next_time].bias = Math.max(old_sum_bias + new_bias, old_bias) - old_bias;
        if (old_slope.end > next_time) {
            points_weight[_gauge_addr][next_time].slope =
                Math.max(old_weight_slope + new_slope.slope, old_slope.slope) -

This was discovered during the testing contest and fixed before the auditing contest.

@OpenCoreCH, since the warden didn’t really submit a report, would you be so kind as to explain the impact of this bug?

The `Math.max` there is an underflow protection for `points_sum`. This wrong implementation would have lead to an underflow in some edge cases (`points_sum` is near 0 / low, i.e. there is not a lot of voting power in the system), preventing votes for the user. Because `old_bias` decreases over time (and eventually reaches 0), the error would generally have been recoverable, but it could have taken some time.

## Recommendation
No recommendation
