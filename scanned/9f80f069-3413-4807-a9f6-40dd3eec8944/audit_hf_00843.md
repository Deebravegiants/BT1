# [M] M-16 | Liquidator Can Seize Non-PositionAssets

## Summary
Severity: Medium
Contest weight: 0.1607
Dataset id: 2579
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquidate function in the PositionManager contract allows anyone to liquidate an unhealthy position. Specifically, a user can select the amount and assets of debt to repay from the position and the amount and assets to seize from the position in return. The requirements being that the position must initially be unhealthy and end up being healthy after the liquidation, while also enforcing a maximum limit on the asset value that can be seized by the liquidator. The issue is that, with the current implementation, the liquidator can seize assets not included in the position’s positionAssets list, as long as they are known assets. This should not be allowed, as the health check performed on the position only considers the assets in the position’s positionAssets list. Consequently, a user could unfairly lose assets that they did not intend to risk in a position by leaving them out of the asset list.

## Proof of Concept
https://github.com/GuardianAudits/sentiment-team-2/blob/POC_SEIZE_ASSETS_NOT_IN_POS_LIST/test/guardian/pocs/pocSeizeAssetsNotInPosList.t.sol

## Recommendation
Modify the liquidate function to ensure that liquidators can only seize assets from a position's positionAssets list.
