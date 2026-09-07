# [?] SushiSwap - Unchecked User Input

## Summary
Severity: Unknown
Chain: Ethereum
Component: Sushi_Router
Published: 2023-04-09
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/Sushi_Router_exp.sol
Type: defi-exploit-poc

## Details
Lost: >$3.3M
References:
- https://twitter.com/peckshield/status/1644907207530774530
- https://twitter.com/SlowMist_Team/status/1644936375924584449
- https://twitter.com/AnciliaInc/status/1644925421006520320
- https://library.dedaub.com/ethereum/tx/0x04b166e7b4ab5105a8e9c85f08f6346de1c66368687215b0e0b58d6e5002bc32

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @Analysis
// https://twitter.com/peckshield/status/1644907207530774530
// https://twitter.com/SlowMist_Team/status/1644936375924584449
// https://twitter.com/AnciliaInc/status/1644925421006520320
// @TX
// https://library.dedaub.com/ethereum/tx/0x04b166e7b4ab5105a8e9c85f08f6346de1c66368687215b0e0b58d6e5002bc32
// @Summary
// Sushi RouteProcessor2 does not check user input `route` carefully.

interface IUniswapV3Pool {
    function swap(
        address recipient,
        bool zeroForOne,
        int256 amountSpecified,
        uint160 sqrtPriceLimitX96,
        bytes calldata data
    ) external returns (int256 amount0, int256 amount1);
}

interface IRouteProcessor2 {
    function processRoute(
        address tokenIn,
        uint256 amountIn,
        address tokenOut,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-04/Sushi_Router_exp.sol_
