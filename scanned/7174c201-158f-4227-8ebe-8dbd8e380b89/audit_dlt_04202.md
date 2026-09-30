# [M] externalSwap should refund excess fromToken

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/61
Type: sherlock-finding

## Details
cccz

medium

# externalSwap should refund excess fromToken

## Summary
When using externalSwap, the fromToken spent may be less than the fromTokenAmount, so the excess fromToken should be refunded.
## Vulnerability Detail
According to the documentation, ExternalSwap is for other routers like 0x, 1inch and paraswap.
For example, if the user uses paraswap.buyOnUniswapV2Fork in externalSwap, in the externalSwap function, the fromTokenAmount of the fromToken is sent to the contract for swapping.
Since paraswap.buyOnUniswapV2Fork determines the amountIn based on the amountOut, this may cause the actual number of fromTokens spent to be less than the fromTokenAmount.
```solidity
    function _buy(
        address tokenIn,
        uint256 amountInMax,
        uint256 amountOut,
        address weth,
        uint256[] memory pools
    )
        private
        returns (uint256 tokensSold)
    {
        uint256 pairs = pools.length;

        require(pairs != 0, "At least one pool required");

        uint256[] memory amounts = new uint256[](pairs + 1);

        amounts[pairs] = amountOut;

        for (uint256 i = pairs; i != 0; --i) {
            uint256 p = pools[i - 1];
            amounts[i - 1] = NewUniswapV2Lib.getAmountIn(
                amounts[i],
                address(p),
                p & DIRECTION_FLAG == 0,
                p >> FEE_OFFSET
            );
        }

        tokensSold = amounts[0];
        require(tokensSold <= amountInMax, "UniswapV2Router: INSUFFICIENT_INPUT_AMOUNT");
```
https://developers.paraswap.network/smart-contracts

Since the excess fromTokens are not refunded to the user, when other users swap, they can use these fromTokens in the contract

## Impact
Since the excess fromTokens are not refunded to the user, when other users swap, they can use these fromTokens in the contract
## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L164-L229
## Tool used

Manual Review

## Recommendation
In the externalSwap function, refund the remaining fromToken to the user
