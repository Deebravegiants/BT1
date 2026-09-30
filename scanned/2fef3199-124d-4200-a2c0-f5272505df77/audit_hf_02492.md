# [M] Improper Corner Case Handling in _swapETHToToken()

## Summary
Severity: Medium
Contest weight: 0.4595
Dataset id: 13334
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Velvet Capital protocol has an Adapter contract that is used for transferring funds from the vault to the contract and vice versa as well as swap tokens to and from native coins. Within the contract, there are a number of swap-related helper routines. Our analysis shows that a specific swap routine _swapETHToToken() needs to be improved to better handle possible corner cases. To elaborate, we show below the implementation of this _swapETHToToken() routine. As the name indicates, this routine is used to swap ETH to a specific token. However, when the token being swapped is equal to getETH() (line 102), the resulting amount of swapResult is improperly calculated. Specifically, there is a missing assignment swapResult = swapAmount right before the lendBNB() call (line 104).
```solidity
function _swapETHToToken(
    address t,
    uint256 swapAmount,
    address to
) public payable onlyIndexManager returns (uint256 swapResult) {
    if (t == getETH()) {
        if (tokenMetadata.vTokens(t) != address(0)) {
            lendBNB(t, tokenMetadata.vTokens(t), swapResult, to);
        } else {
            IWETH(t).deposit{value: swapAmount}();
            swapResult = swapAmount;
            if (to != address(this)) {
                IWETH(t).transfer(to, swapAmount);
            }
        }
    } else {
        if (tokenMetadata.vTokens(t) != address(0)) {
            swapResult = pancakeSwapRouter.swapExactETHForTokens{
                value: swapAmount
            }(
                getPathForETH(t),
                address(this),
                block.timestamp
                // using now for convenience, for mainnet pass deadline from frontend!
            )[1];
            lendToken(t, tokenMetadata.vTokens(t), swapResult, to);
        } else {
            swapResult = pancakeSwapRouter.swapExactETHForTokens{
                value: swapAmount
            }(
                getPathForETH(t),
                to,
                block.timestamp
                // using now for convenience, for mainnet pass deadline from frontend!
            )[1];
        }
    }
}
```

## Recommendation
Properly handle all possible cases in the above _swapETHToToken() routine.
