# [M] Potential Sandwich/MEV Attack In HLND

## Summary
Severity: Medium
Contest weight: 0.4310
Dataset id: 12230
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While examining the HLND contract, we notice there are several functions that can be improved with slippage control. In the following, we take the swapTokensForBNB() routine as an example. To elaborate, we show below the related code snippet of the HLND contract. According to the design, the swapTokensForBNB() function is used to swap HLND to BNB. In the function, the swapExactTokensForETHSupportingFeeOnTransferTokens() function of PancakeSwap is called (line 2344) to swap the exact HLND amount to BNB. However, we observe the second input amountOutMin parameter is assigned to 0, which means this transaction does not specify any restriction on possible slippage and is therefore vulnerable to possible front-running attacks.
```solidity
function swapTokensForBNB(uint256 tokenAmount) internal {
    // generate the uniswap pair path of token -> weth
    address[] memory path = new address[](2);
    path[0] = address(this);
    path[1] = addressParameters.router.WETH();
    _approve(address(this), address(addressParameters.router), tokenAmount);
    // make the swap
    addressParameters.router.swapExactTokensForETHSupportingFeeOnTransferTokens(
        tokenAmount,
        0, // accept any amount of ETH
        path,
        address(this),
        block.timestamp
    );
}
```
Note other routines such as addLiquidity(), buyBackAndBurn(), and swapTokensForDividendToken() in the same contract can be similarly improved.

## Recommendation
Improve the above-mentioned functions by adding necessary slippage control.
