# [H] Logic Error Of Swaps For Deﬂationary Tokens

## Summary
Severity: High
Contest weight: 0.6384
Dataset id: 12279
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the HecoHurricaneRouterPart contract, we observe both of the swapExactTokensForTokens() and swapExactTokensForTokensSupportingFeeOnTransferTokens() functions are used to swap the exact amount of one token to another specified by the third input path parameter. Compared with the swapExactTokensForTokens() function, the swapExactTokensForTokensSupportingFeeOnTransferTokens() function supports the swap of deﬂationary tokens. While examining the logic of them, we observe an incorrect logic in the swapExactTokensForTokensSupportingFeeOnTransferTokens() function. To elaborate, we show below the related code snippet of the contract. In the swapExactTokensForTokens() function, assume the third input path parameter is [tokenA, tokenB, tokenC], the amounts variable calculated by HecoHurricaneLibrary.getAmountsOut(factory, amountIn, path) (line 56) will save the actual amount of tokenA, tokenB and tokenC. Only when the fifth input realAmounts parameter includes the actual amount of tokenA, tokenB and tokenC, the swapExactTokensForTokens() function will work well. Therefore, the fifth input realAmounts parameter will include the actual amount of all the tokens in the path in the real scenarios. However, in the swapExactTokensForTokensSupportingFeeOnTransferTokens() function, if we assume the third input path parameter is [tokenA, tokenB, tokenC], the amounts variable calculated by _swapSupportingFeeOnTransferTokens(path, to) (line 228) will only save the actual amount of tokenA and tokenB without tokenC. If the fifth input realAmounts parameter includes the actual amount of tokenA, tokenB and tokenC as the swapExactTokensForTokens() function, the swapExactTokensForTokensSupportingFeeOnTransferTokens() function will always be reverted.

```solidity
function swapExactTokensForTokens(
    uint amountIn,
    uint amountOutMin,
    address[] calldata path,
    address to,
    uint[] calldata realAmounts,
    uint deadline
) external ensure(deadline) returns (uint[] memory amounts) {
    require(msg.sender == IHurricaneFactory(factory).getOwner(), "HurricaneRouter: EXPIRED");
    (bool lpSwitch, bool swapSwitch) = IHurricaneFactory(factory).getSwitch();
    require(!lpSwitch && swapSwitch, "Hurricane: not allowed");
    amounts = HecoHurricaneLibrary.getAmountsOut(factory, amountIn, path);
    require(amounts[amounts.length - 1] >= amountOutMin, "HurricaneRouter: INSUFFICIENT_OUTPUT_AMOUNT");
    require(_compareAmounts(realAmounts, amounts), "HurricaneRouter: swap wrong order");
    TransferHelper.safeTransferFrom(
        path[0],
        msg.sender,
        HecoHurricaneLibrary.pairFor(factory, path[0], path[1]),
        amounts[0]
    );
    _swap(amounts, path, to);
    emit SwapPath(amounts, amountIn, amountOutMin, path, to, "swapExactTokensForTokens");
}

function swapExactTokensForTokensSupportingFeeOnTransferTokens(
    uint amountIn,
    uint amountOutMin,
    address[] calldata path,
    address to,
    uint[] calldata realAmounts,
    uint deadline
) external ensure(deadline) {
    require(msg.sender == IHurricaneFactory(factory).getOwner(), "HurricaneRouter: EXPIRED");
    (bool lpSwitch, bool swapSwitch) = IHurricaneFactory(factory).getSwitch();
    require(!lpSwitch && swapSwitch, "Hurricane: liquidity open or swap closed");
    TransferHelper.safeTransferFrom(
        path[0],
        msg.sender,
        HecoHurricaneLibrary.pairFor(factory, path[0], path[1]),
        amountIn
    );
    uint balanceBefore = IERC20(path[path.length - 1]).balanceOf(to);
    uint[] memory amounts = _swapSupportingFeeOnTransferTokens(path, to);
    require(
        IERC20(path[path.length - 1]).balanceOf(to).sub(balanceBefore) >= amountOutMin,
        "HurricaneRouter: INSUFFICIENT_OUTPUT_AMOUNT"
    );
    require(_compareAmounts(realAmounts, amounts), "HurricaneRouter: swap wrong order");
    emit SwapPath(amounts, amountIn, amountOutMin, path, to, "swapExactTokensForTokensSupportingFeeOnTransferTokens");
}
```
Note a number of functions can be similarly improved, including AvaxHurricaneRouterPart::swapExactTokensForTokensSupportingFeeOnTransferTokens() and AvaxHurricaneRouterPart::swapExactAVAXForTokensSupportingFeeOnTransferTokens().

## Recommendation
There is no need to use require(_compareAmounts(realAmounts, amounts), "HurricaneRouter: swap wrong order") (line 58) to keep the swap order. It becomes optional to remove the related codes.
