# [M] Improper Limit Enforcement in CBI_Treasury

## Summary
Severity: Medium
Contest weight: 0.4599
Dataset id: 12324
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, the JUKU platform support two treasuries - CBI_Treasury and CMultiSigTreasury. While examining the allowed tokens in the ﬁrst treasury, we notice the use of swapLimit and withdrawLimit to ensure certain limits for swap and withdraw operations. However, our analysis shows their enforcement needs to be revisited. If we use the swapLimit as an example, we show below the implementation of the related _swapTokens() function. The swapLimit enforcement is applied to ensure the input token amount for each swap will not exceed the given limit. However, the current implementation require( balanceInputToken - amount >= inputTokenInfo.swapLimit ) basically ensures the remaining amount after the swap will not be smaller than the swap limit! An intended enforcement should be revised as require(amount <= inputTokenInfo.swapLimit);.
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
A similar issue is also applicable to the swapLimit enforcement in _swapTokensForExactToken() and the withdrawLimit enforcement in _withdraw().

## Recommendation
Revisit the above-mentioned routines to properly apply the intended swapLimit and withdrawLimit.
