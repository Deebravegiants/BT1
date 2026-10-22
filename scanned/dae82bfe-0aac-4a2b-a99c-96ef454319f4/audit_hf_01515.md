# [M] Some functions don't have deadline check

## Summary
Severity: Medium
Contest weight: 0.3917
Dataset id: 8020
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The withdraw() function calls _decreaseLiquidity(), and the deposit() function calls _addLiquidity() and _createLiquidityPosition(). These internal functions set the deadline parameter to block.timestamp:  

Farms_audit.md  

```solidity
INonfungiblePositionManager.DecreaseLiquidityParams({
    tokenId: farm.lp.tokenId,
    liquidity: liquidity,
    amount0Min: minAmount0,
    amount1Min: minAmount1,
    deadline: block.timestamp
});
```

Without a deadline, pending transactions could be left open and later executed under conditions that are unfavorable to the user.  
Users have no way to enforce a time limit on their transactions, meaning their swap could be executed at an unexpected time, which may no longer be beneficial.

## Recommendation
Introduce a deadline parameter in these functions.
