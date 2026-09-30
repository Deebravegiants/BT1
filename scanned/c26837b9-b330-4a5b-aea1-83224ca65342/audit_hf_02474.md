# [M] Improved Initial remainingAmount in withdrawToVault()

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 13242
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As described in Section 3.3, when the vault doesn't have enough assets to cover the withdrawal amount and the buffer, it will withdraw the missing part from the splitter. Similarly, if it doesn't have enough available assets in the splitter, it will withdraw the remaining assets from the strategies public one by one starting from the lower APR until the target amount is reached. While reviewing the withdraw logic in the StrategySplitterV2 contract, we notice it may withdraw more assets than expected from the strategies.
To elaborate, we show below the code snippet of the withdrawToVault() routine, which is called from the vault to withdraw assets from the splitter. It takes the target amount from the input parameter amount. Specially, if current available balance in the splitter is smaller than the target amount (line 467), it withdraws the remaining amount from the strategies (lines 476 480). However, it comes to our attention that, the initial remainingAmount is set to the target amount without subtracting current balance of the splitter (line 466). As a result, it will withdraw more assets from the strategies than expected. Our analysis shows that, the initial remainingAmount shall be set to amount - balance.
```solidity
function withdrawToVault(uint256 amount) external override
    _onlyVault();
    address _asset = asset;
    uint balance = IERC20(_asset).balanceOf(address(this));
    uint remainingAmount = amount;
    if (balance < amount)
        uint length = strategies.length;
        for (uint i = length; i > 0; i--) {
            IStrategyV2 strategy = IStrategyV2(strategies[i - 1]);
            uint strategyBalance = strategy.totalAssets();
            uint balanceBefore = strategyBalance + balance;
            // withdraw from strategy
            if (strategyBalance <= remainingAmount)
                strategy.withdrawAllToSplitter();
            else
                strategy.withdrawToSplitter(remainingAmount);
            emit WithdrawFromStrategy(address(strategy));
            uint currentBalance = IERC20(_asset).balanceOf(address(this));
            // assume that we can not decrease splitter balance during withdraw process
            uint withdrew = currentBalance - balance;
            balance = currentBalance;
            remainingAmount = withdrew <= remainingAmount
                ? remainingAmount - withdrew
                : 0;
        }
    public
```

## Recommendation
Set the initial remainingAmount to amount - balance in case there are not enough assets available in the splitter.
