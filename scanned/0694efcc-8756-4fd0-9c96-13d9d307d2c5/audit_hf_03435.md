# [M] DPCU-6 | Position Price Impact Not Offset

## Summary
Severity: Medium
Contest weight: 0.1905
Dataset id: 18748
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the force closure of a position during a liquidation or ADL order, the accounting for the position impact pool with applyDeltaToPositionImpactPool is skipped. However the effects of the price impact were already felt on the position’s resulting PnL. This results in scenarios where a user is significantly negatively/positively impacted during a liquidation/ADL and this amount is not reflected by the position impact pool and so the pool value is asymmetrically affected. For instance, a user’s PnL is positively impacted by $100 during a force close liquidation. This positive impact is translated to a decrease of the pool value by $100. The positive impact is not offset by a decrease in the position impact pool, and therefore the pool realizes immediate losses from PI. Vice-versa for the pool realizing immediate gains on negative price impact, although when a position is negatively impacted, it contributes to the collateral + pnl not being sufficient and therefore the necessary accounting becomes less straightforward. In these scenarios, the position impact pool ought to only be increased by the amount that the position actually experienced, as it wasn’t able to cover its entire losses/negative impact — effectively exactly offsetting whatever amount was “payable” (or actually was able to take effect) of the negative impact.

## Recommendation
This is somewhat non-trivial to address in the negative impact case as mentioned above, however for the positive impact case, the full impact amount should be applied to the position impact pool, as this full amount is experienced by the trader.
