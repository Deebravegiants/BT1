# [M] First depositor can make subsequent depositor lose all of her or his deposit

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1473
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L226-L250
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L151-L153
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L225-L227
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L591-L593
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L627-L630


# Vulnerability details

## Impact
For calculating the `shares` for the corresponding deposit, the following `calculateDepositShares` function call the `previewDeposit` function below, which further calls the `_convertToShares`, `totalAssets`, and `TVL` functions below. Higher `baseToken.balanceOf(address(this))` causes the values returned by the `TVL` and `totalAssets` functions to be higher and the calculated `shares` to be lower for the same deposit amount. Thus, the first depositor can deposit just 1 wei of `baseToken` and then transfer a huge amount of `baseToken` to the `AccountingManager` contract after the `shares` are calculated for her or his deposit. Afterwards, the `shares` calculated for the subsequent depositor's deposit can round down to 0. In this case, the first depositor can later withdraw all of her or his deposit and transferred amount but the subsequent depositor cannot withdraw any of her or his deposit since she or he owns 0 shares. As a result, the subsequent depositor loses all of her or his deposit.

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L226-L250
```solidity
    function calculateDepositShares(uint256 maxIterations) public onlyManager nonReentrant whenNotPaused {
        uint256 middleTemp = depositQueue.middle;
        uint64 i = 0;

        uint256 oldestUpdateTime = TVLHelper.getLatestUpdateTime(vaultId, registry);

        while (
            depositQueue.last > middleTemp && depositQueue.queue[middleTemp].recordTime <= oldestUpdateTime
                && i < maxIterations
        ) {
            i += 1;
            DepositRequest storage data = depositQueue.queue[middleTemp];

            uint256 shares = previewDeposit(data.amount);
            data.shares = shares;
            data.calculationTime = block.timestamp;
            ...

            middleTemp += 1;
        }

        depositQueue.middle = middleTemp;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1473_
