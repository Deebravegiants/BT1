# [C] No approvals from Helper to TokenizedLP

## Summary
Severity: Critical
Contest weight: 0.2468
Dataset id: 13914
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The money flow goes through LockZap to UniV3PoolHelper.zapETH() or to UniV3PoolHelper.zapTokens(). But later tokens should be deposited to UniV3TokenizedLp.deposit().
```solidity
function zapWETH(uint256 amount) public onlyLockZap returns (uint256 liquidity) {
    IERC20(weth9Addr).safeTransferFrom(msg.sender, address(this), amount);
    uint256 token0Amt = token0 == weth9Addr ? amount : 0;
    uint256 token1Amt = token1 == weth9Addr ? amount : 0;
    liquidity = tokenizedLpToken.deposit(token0Amt, token1Amt, msg.sender);
}
```
UniV3TokenizedLp takes tokens from UniV3PoolHelper.zapETH() via transferFrom() which required approvals given. But UniV3PoolHelper does not approve tokens, so the whole money flow will be reverted.

## Recommendation
Consider giving approvals from UniV3PoolHelper to UniV3TokenizedLp.
