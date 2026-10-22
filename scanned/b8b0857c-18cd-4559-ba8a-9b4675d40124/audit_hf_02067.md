# [M] Possibly Earlier Pair Creation Before Completion

## Summary
Severity: Medium
Contest weight: 0.4339
Dataset id: 11727
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the BasePump protocol has a core BondingCurveLogic contract that allows for real-time discovery of token price. Moreover, once the bonding process ends, liquidity will be automatically added to the respective pair in UniswapV2. While reviewing the final step of liquidity addition, we notice a possibility that the intended token-weth pair may be created with imbalanced pool before completion. To elaborate, we show below the implementation of the related _deployPool() function. As the name indicates, this routine is invoked when the bonding curve is completed. However, it currently assumes the pair may not be created by others. With that, if a malicious user intentionally creates the pool earlier with an imbalanced state, the added liquidity may result in a loss as it is being added into an imbalanced pool. To fix, there is a need to better protect the liquidity to avoid being manipulated.

```solidity
function _deployPool(
    uint256 poolTokenInput
) internal virtual returns (address pool) {
    IUniswapV2Router02 router = IUniswapV2Router02(FACTORY.UNISWAP_ROUTER());
    TOKEN.approve(address(router), poolTokenInput);
    router.addLiquidityETH{
        value: virtualEthReserve - INITIAL_VIRTUAL_ETH_RESERVE
    }(
        address(TOKEN),
        poolTokenInput,
        0,
        0,
        FACTORY.lpTokenReceiver(),
        block.timestamp
    );
    return IUniswapV2Factory(router.factory()).getPair(address(TOKEN), router.WETH());
}
```

## Recommendation
Revise the above logic to properly complete the bonding curve and protect the liquidity.
