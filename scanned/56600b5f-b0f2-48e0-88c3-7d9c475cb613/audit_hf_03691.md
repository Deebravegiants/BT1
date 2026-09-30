# [M] PerpDepository.netAssetDeposits variable

## Summary
Severity: Medium
Contest weight: 0.5821
Dataset id: 19786
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
PerpDepository.netAssetDeposits variable can prevent users to withdraw with underflow error
When user deposits using PerpDepository, then netAssetDeposits variable is increased with the base assets amount, provided by depositor.
erp/PerpDepository.sol#L283-L288
```solidity
function _depositAsset(uint256 amount) private {
    netAssetDeposits += amount;
    IERC20(assetToken).approve(address(vault), amount);
    vault.deposit(assetToken, amount);
}
```
Also when user withdraws, this netAssetDeposits variable is decreased with base amount that user has received for redeeming his UXD tokens.
erp/PerpDepository.sol#L294-L302
```solidity
function _withdrawAsset(uint256 amount, address to) private {
    if (amount > netAssetDeposits) {
        revert InsufficientAssetDeposits(netAssetDeposits, amount);
    }
    netAssetDeposits -= amount;
    vault.withdraw(address(assetToken), amount);
    IERC20(assetToken).transfer(to, amount);
}
```
The problem here is that when user deposits X assets, then he receives Y UXD tokens. And when later he redeems his Y UXD tokens he can receive more or less than X assets. This can lead to situation when netAssetDeposits variable will be set to negative value which will revert tx.
Example. 1. User deposits 1 WETH when it costs 1200$. As result 1200 UXD tokens were minted and netAssetDeposits was set to 1. 2. Price of WETH has decreased and now it costs 1100. 3. User redeems his 1200 UXD tokens and receives from perp protocol 1200/1100=1.09 WETH. But because netAssetDeposits is 1, then transaction will revert inside _withdrawAsset function with underflow error.
User can't redeem all his UXD tokens.

## Recommendation
As you don't use this variable anywhere else, you can remove it. Otherwise you need to have 2 variables instead: totalDeposited and totalWithdrawn.
