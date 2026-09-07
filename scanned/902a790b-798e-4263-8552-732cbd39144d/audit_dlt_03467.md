# [H] Change `require` conditions can prevent fund loss when called with mistaken input data

## Summary
Severity: High
Chain: Smart contract
Component: 2021-10-tally
Published: 2021-10-22
Source: https://github.com/code-423n4/2021-10-tally-findings/issues/33
Type: code-finding

## Details
# Handle

WatchPug


# Vulnerability details

https://github.com/code-423n4/2021-10-tally/blob/c585c214edb58486e0564cb53d87e4831959c08b/contracts/swap/Swap.sol#L106-L123

```solidity
function swapByQuote(
    address zrxSellTokenAddress,
    uint256 amountToSell,
    address zrxBuyTokenAddress,
    uint256 minimumAmountReceived,
    address zrxAllowanceTarget,
    address payable zrxTo,
    bytes calldata zrxData,
    uint256 deadline
) external payable whenNotPaused nonReentrant {
    require(
        block.timestamp <= deadline,
        "Swap::swapByQuote: Deadline exceeded"
    );
    require(
        !signifiesETHOrZero(zrxSellTokenAddress) || msg.value > 0,
        "Swap::swapByQuote: Unwrapped ETH must be swapped via msg.value"
    );
```

There is a potential mistake that can be made on the input data for `swapByQuote()` which uses the address of `WETH` as `zrxSellTokenAddress` and send unwrapped ETH via `msg.value`.

This is how the input data of the Uni v2 Router is formatted. Considering the popularity of Uni v2, it might be possible that some user or contract will call Tally's `Swap.sol` contract using calldata formatted in such a way.

https://github.com/Uniswap/v2-periphery/blob/master/contracts/UniswapV2Router02.sol#L260-L263

```solidity
function swapExactETHForTokens(uint amountOutMin, address[] calldata path, address to, uint deadline)
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2021-10-tally-findings/issues/33_
