# [M] `UniV2ClassDex.sol#uniClassSell()` Tokens with fee on transfer are not fully supported

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-openleverage
Published: 2022-02-02
Source: https://github.com/code-423n4/2022-01-openleverage-findings/issues/208
Type: code-finding

## Details
# Handle

WatchPug


# Vulnerability details

https://github.com/code-423n4/2022-01-openleverage/blob/501e8f5c7ebaf1242572712626a77a3d65bdd3ad/openleverage-contracts/contracts/dex/bsc/UniV2ClassDex.sol#L31-L56

```solidity
function uniClassSell(DexInfo memory dexInfo,
    address buyToken,
    address sellToken,
    uint sellAmount,
    uint minBuyAmount,
    address payer,
    address payee
) internal returns (uint buyAmount){
    address pair = getUniClassPair(buyToken, sellToken, dexInfo.factory);
    IUniswapV2Pair(pair).sync();
    (uint256 token0Reserves, uint256 token1Reserves,) = IUniswapV2Pair(pair).getReserves();
    sellAmount = transferOut(IERC20(sellToken), payer, pair, sellAmount);
    uint balanceBefore = IERC20(buyToken).balanceOf(payee);
    dexInfo.fees = getPairFees(dexInfo, pair);
    if (buyToken < sellToken) {
        buyAmount = getAmountOut(sellAmount, token1Reserves, token0Reserves, dexInfo.fees);
        IUniswapV2Pair(pair).swap(buyAmount, 0, payee, "");
    } else {
        buyAmount = getAmountOut(sellAmount, token0Reserves, token1Reserves, dexInfo.fees);
        IUniswapV2Pair(pair).swap(0, buyAmount, payee, "");
    }

    require(buyAmount >= minBuyAmount, 'buy amount less than min');
    uint bought = IERC20(buyToken).balanceOf(payee).sub(balanceBefore);
    return bought;
}
```


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-openleverage-findings/issues/208_
