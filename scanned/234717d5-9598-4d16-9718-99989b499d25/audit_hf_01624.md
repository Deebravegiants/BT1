# [H] Full liquidation from minor insolvency incurs significant loss to users

## Summary
Severity: High
Contest weight: 0.3819
Dataset id: 8730
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Full liquidation of positions with minor insolvency can lead to significant losses for users. In the current system, once a position becomes liquidatable, a liquidator can repay all cvTokens regardless of the extent to which the health factor has decreased. In return, the liquidator receives an equivalent value of LRT along with a certain percentage of the seized collateral as a liquidation bonus. Consequently, the larger the repaid amount, the greater the liquidation bonus.
However, in cases where the health factor has only slightly decreased, repaying a small portion of the assets should be sufficient to restore the position to a healthy state.
Example:
Let’s assume the following:
- The current price of AgETH is 1.02 ETH.
- The max loan-to-value (LTV) percentage of AgETH is set to 80%.
- The liquidation threshold percentage is set to 2%.
Scenario:
1. The user deposits 100 AgETH into the protocol.
2. The user mints the maximum possible amount, which is 81.6 cvETH.
3. Due to a price decrease (due to slashing), the price of AgETH drops to 1 AgETH = 0.97 ETH.
4. As a result, the collateral value becomes: 100 AgETH * 0.97 ETH = 97 ETH
5. The health factor becomes: (81.6 / 97) * 100 = 84%. This crosses the liquidation threshold of 82%, making the position liquidatable.
6. The liquidator repays 81.6 cvETH, and in return, they receive: (100 * 81.6 * 1.02) / 97 = 85.78 AgETH. This includes a bonus of 1.63 AgETH (worth 4337.43 USD).
However, to restore the position to a healthy state, the liquidator only needs to repay 18.8 cvETH. This brings the health factor close to 80%.
In this case, the liquidator receives: (100 * 18.8 * 1.02) / 97 = 19.76 AgETH, including a bonus of 0.38 AgETH (worth 1011.18 USD).
After this partial repayment, the position becomes healthy again, with the new health factor: (81.6 - 18.8) / (97 - 19.76) = 0.81
So the user will lose nearly 3326.25 USD in the above case due to full liquidation.

## Recommendation
This can be addressed in two steps:
1. Implement support for partial liquidations.
2. When liquidating a position, calculate the maximum liquidation amount. This should be determined based on the amount the liquidator needs to repay in order to restore the position to a healthy state. Only allow the liquidator to repay up to this calculated maximum liquidation amount.
