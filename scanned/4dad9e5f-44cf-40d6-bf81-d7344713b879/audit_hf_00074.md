# [M] M-06 | _triggerRebalance Does Not Account For Liquidation Rewards

## Summary
Severity: Medium
Contest weight: 0.1947
Dataset id: 150
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _triggerRebalance function is responsible for initiating a rebalance when the imbalance on the long side becomes too significant, aiming to restore the protocol to a balanced state. It calculates the tick of the rebalancer position to open using the _calcRebalancerPositionTick function. However, this function relies on an outdated value of cache.vaultBalance, as the actual s._balanceVault state variable is reduced in the _sendRewardsToLiquidator function.
By ignoring the s._balanceVault decrease caused by the liquidation rewards, it is possible that after the rewards are paid out and removed from the s._balanceVault the protocol enters again an unbalanced state especially if the s._balanceVault's liquidity is low. Although the maximum liquidation rewards are currently capped at 0.5 Ether, and the protocol is expected to hold significantly more in its vault, this value could still be updated by a privileged account to a higher one.
Finally, the _usdnRebase function is also affected by this as it uses the s._balanceVault to calculate the USDN price. This calculation will not be accurate as the s._balanceVault has not been updated/decreased by the time _usdnRebase function is called.

## Recommendation
Consider revising the calculation of liquidation rewards by dividing it into two components:
1. Fixed component: A fixed portion of the liquidation reward based on the number of ticks liquidated. This component should be slightly optimistic, providing a small excess to account for potential future events such as a triggerRebase or usdnRebase.
2. Variable component: A variable portion of the liquidation reward, calculated based on the remaining collateral after liquidation.
This way, the exact liquidation reward will be known beforehand and the _triggerRebalance and _usdnRebase functions can account for the exact s._balanceVault decrease caused by the liquidation rewards distribution.
