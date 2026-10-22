# [M] Potential Front-Running/MEV With Reduced Return

## Summary
Severity: Medium
Contest weight: 0.4608
Dataset id: 12335
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The JUKU platform support two treasuries, i.e., CBI_Treasury and CMultiSigTreasury. Both treasuries have the need of swapping an input token to another. However, our analysis shows the current conversion does not enforce meaningful slippage control.
```solidity
function _swapTokens(
    address inputToken,
    address outputToken,
    uint256 amount,
    address user,
    string memory userId
) internal {
    require(amount > 0, "CBI_Treasury: Zero amount");
    Token storage inputTokenInfo = allowedTokensInfo[inputToken];
    Token storage outputTokenInfo = allowedTokensInfo[outputToken];
    require(
        inputTokenInfo.allowed && outputTokenInfo.allowed,
        "CBI_Treasury: Not allowed token"
    );
    uint balanceInputToken = IERC20(inputToken).balanceOf(address(this));
    require(
        balanceInputToken >= amount,
        "CBI_Treasury: Not enough token balance"
    );
    require(
        balanceInputToken - amount >= inputTokenInfo.swapLimit,
        "CBI_Treasury: Token swap limit exceeded"
    );
    address[] memory path = new address[](2);
    path[0] = inputToken;
    path[1] = outputToken;
    uint256[] memory swapAmounts = swapRouter.swapExactTokensForTokens(
        amount,
        0,
        path,
        address(this),
        block.timestamp
    );
    emit SwapTokens(
        inputToken,
        outputToken,
        amount,
        swapAmounts[1],
        user,
        userId
    );
}
```
To elaborate, we show above one example routine _swapTokens(). We notice the conversion is routed to an external swapRouter in order to swap one asset to another. And the swap operation does not specify any restriction on possible slippage (line 344) and is therefore vulnerable to possible front-running attacks, resulting in a smaller gain for this round of conversion. A similar issue also exists in _swapTokensForExactToken() from both treasury contracts as well as swap-related routines from YieldOptimizer and YieldOptimizerStaking. Note that this is a common issue plaguing current AMM-based DEX solutions. Speciﬁcally, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search eﬀorts for an eﬀective defense.

## Recommendation
Develop an eﬀective mitigation (e.g., slippage control) to the above front-running attack to better protect the interests of farming users.
