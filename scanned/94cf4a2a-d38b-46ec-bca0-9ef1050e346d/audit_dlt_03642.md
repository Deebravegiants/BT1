# [M] Some functions don't check if liquidity > 0 before calling decreaseLiquidity

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-25
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/47
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol#L654-L658


# Vulnerability details

## Impact
- Users cannot just collect UniswapV3 fees alone.
- Users cannot call `leverageDown` with fee alone.

## Proof of concept
One of the most important features of Revert Lend is that it allows user to take loans using UniswapV3 positions as collateral while at the same time able to manage their positions; this includes collecting fees, decrease liquidity, increase liquidity,... as documented [here](https://docs.revert.finance/revert/technical-docs/auto-compounder/manage-positions)

However, the current implementation will not allow user to just collect fees. `V3Vault` contains a function called `decreaseLiquidityAndCollect`:
```solidity
function decreaseLiquidityAndCollect(DecreaseLiquidityAndCollectParams calldata params)
        external
        override
        returns (uint256 amount0, uint256 amount1)
    {
     ...
     (amount0, amount1) = nonfungiblePositionManager.decreaseLiquidity(
            INonfungiblePositionManager.DecreaseLiquidityParams(
                params.tokenId, params.liquidity, params.amount0Min, params.amount1Min, params.deadline
            )
        );
     ...
    }
```
However as you can see in the above code, the function will call `decreaseLiquidity` without checking if `liquidity` to be removed >0; if `liquidity = 0`, then `decreaseLiquidity` will revert. Below is the UniswapV3 NonfungibleTokenManager code for this situation https://github.com/Uniswap/v3-periphery/blob/main/contracts/NonfungiblePositionManager.sol#L265:

```solidity
 function decreaseLiquidity(DecreaseLiquidityParams calldata params)
        external
        payable
        override
        isAuthorizedForToken(params.tokenId)
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/47_
