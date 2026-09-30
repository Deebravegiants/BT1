# [M] Incorrect Fee Collection in TargetVaultPancake::_collectFees()

## Summary
Severity: Medium
Contest weight: 0.4550
Dataset id: 12064
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.5, the Feeder protocol supports a number of target vaults and each vault essentially acts as the corresponding investment strategy. Each target vault needs to implements the standard APIs, including deposit(), withdraw(), emergencyWithdrawAll(), harvest(), and collectFees. In the following, we examine the specific collectFees() API from the TargetVaultPancake contract. This routine is designed to collect fees and invest the remaining funds back for additional gains. However, it comes to our attention that the collected fee is denominated at the token for investment, not the reward token. The current implementation incorrectly uses the reward token for fee collection (line 148), which needs to be changed back to the target token.
```solidity
function _collectFees() internal virtual {
    uint256 _balance = IERC20(rewardToken).balanceOf(address(this));
    uint256 _fees = _balance.mul(feesBP).div(10000);
    if (_fees > 0) {
        if (autoBuyBack) {
            uint256 buyBackBefore = IERC20(buyBackToken).balanceOf(address(this));
            token.safeIncreaseAllowance(swapRouterAddress, _fees);
            IPancakeRouter02(swapRouterAddress).swapExactTokensForTokensSupportingFeeOnTransferTokens(
                _fees,
                tokenToBuyBackPath,
                address(this),
                block.timestamp + 120
            );
            uint256 buyBackAfter = IERC20(buyBackToken).balanceOf(address(this));
            uint256 buyBackAmount = buyBackAfter.sub(buyBackBefore);
            IERC20(buyBackToken).safeTransfer(feesCollector, buyBackAmount);
            emit FeesCollected(address(feesCollector), address(buyBackToken), _fees);
        } else {
            token.safeTransfer(feesCollector, _fees);
            emit FeesCollected(address(feesCollector), address(token), _fees);
        }
    }
    _deposit();
}
```

## Recommendation
Revive the above _collectFees() routine to use the intended investment token, instead of the reward token, for fee collection.
