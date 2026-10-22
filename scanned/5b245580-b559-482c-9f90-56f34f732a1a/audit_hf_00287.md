# [M] `UniV2ClassDex.sol#uniClassSell

## Summary
Severity: Medium
Contest weight: 0.5967
Dataset id: 1460
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
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

While `uniClassBuy()` correctly checks the actually received amount by comparing the before and after the balance of the receiver, `uniClassSell()` trusted the result given by `getAmountOut()`. This makes `uniClassSell()` can result in an output amount fewer than `minBuyAmount`.

## Recommendation
Change to:
```solidity
    function uniClassSell(DexInfo memory dexInfo,
        address buyToken,
        address sellToken,
        uint sellAmount,
        uint minBuyAmount,
        address payer,
        address payee
    ) internal returns (uint bought){
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
        uint bought = IERC20(buyToken).balanceOf(payee).sub(balanceBefore);
        require(bought >= minBuyAmount, 'buy amount less than min');
    }
```

Agree with this finding! Uniswap token swaps are meant to support all types of tokens. It does seem possible for there to be `payer` to experience increased slippage because the check operates on `getAmountOut()` and not the `bought` output.
 
It’s fair to say that this will lead to value leakage, so I think `medium` severity is justified.
