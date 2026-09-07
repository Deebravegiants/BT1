# [M] Lack of protection when withdrawing Static Atoken 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-02
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/7
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L324-L365


# Vulnerability details

## Impact
The Aave plugin is associated with [an ever-increasing exchange rate](https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L26). The earlier a user wraps the AToken, the more Static Atoken will be minted and understandably no slippage protection is needed.

However, since the rate is not linearly increasing, withdrawing the Static Atoken (following RToken redemption) at the wrong time could mean a difference in terms of the amount of AToken redeemed. The rate could be in a transient mode of non-increasing or barely increasing and then a significant surge. Users with an equivalent amount of Static AToken making such calls at around the same time could end up having different percentage gains. 

Although the user could always deposit and wrap the AToken again, it's not going to help if the wrapping were to encounter a sudden surge (bad timing again) thereby thwarting the intended purpose.      

## Proof of Concept
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/aave/StaticATokenLM.sol#L338-L355

```solidity
        uint256 userBalance = balanceOf(owner);

        uint256 amountToWithdraw;
        uint256 amountToBurn;

        uint256 currentRate = rate();
        if (staticAmount > 0) {
            amountToBurn = (staticAmount > userBalance) ? userBalance : staticAmount;
            amountToWithdraw = _staticToDynamicAmount(amountToBurn, currentRate);
        } else {
            uint256 dynamicUserBalance = _staticToDynamicAmount(userBalance, currentRate);
            amountToWithdraw = (dynamicAmount > dynamicUserBalance)
                ? dynamicUserBalance
                : dynamicAmount;
            amountToBurn = _dynamicToStaticAmount(amountToWithdraw, currentRate);
        }

        _burn(owner, amountToBurn);
```
As can be seen in the code block of function `_withdraw` above, choosing `staticAmount > 0` will have a lesser amount of AToken to withdraw when the `currenRate` is stagnant.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/7_
