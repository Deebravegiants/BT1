# [M] Accounting will be broken if output token is

## Summary
Severity: Medium
Contest weight: 0.5737
Dataset id: 22797
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Accounting will be broken if output token is one of the lpTokens. When the strategy's balances is calculated, it counts both the funds in the LP positions and the funds within the strategy contract, fetched via regular erc20.balanceOf.
```solidity
function balances() public view returns (uint256 token0Bal, uint256 token1Bal) {
    (uint256 thisBal0, uint256 thisBal1) = balancesOfThis();
    (uint256 poolBal0, uint256 poolBal1,,,,) = balancesOfPool();
    uint256 total0 = thisBal0 + poolBal0;
    uint256 total1 = thisBal1 + poolBal1;
    // For token0 and token1 we return balance of this contract + balance of positions - feesUnharvested.
    return (total0, total1);
}
```
```solidity
function balancesOfThis() public view returns (uint256 token0Bal, uint256 token1Bal) {
    return (IERC20Metadata(lpToken0).balanceOf(address(this)), IERC20Metadata(lpToken1).balanceOf(address(this)));
}
```
The problem is that the output token might be one of the lpTokens too and any accrued fees that are not yet harvested will be included in this number. This would unfairly inflate share value when people are depositing via the Vault. Once rewards are collected though, these same depositors would suffer all the losses. Furthermore, it would lead to insolvency as the accrued fees might be deposited in the LP position, hence it will be hard to harvest them in order to temporarily fix accounting. Broken accounting, loss of funds, insolvency

## Recommendation
If one of the lpTokens is output token, deduct the fees from the token balance
