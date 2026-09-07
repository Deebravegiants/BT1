# [?] SNK - Reward Calculation Error

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SNK
Published: 2023-05-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/SNK_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$197k
References:
- https://twitter.com/Phalcon_xyz/status/1656176776425644032
- https://explorer.phalcon.xyz/tx/bsc/0xace112925935335d0d7460a2470a612494f910467e263c7ff477221deee90a2c
- https://explorer.phalcon.xyz/tx/bsc/0x7394f2520ff4e913321dd78f67dd84483e396eb7a25cbb02e06fe875fc47013a

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @Analysis
// https://twitter.com/Phalcon_xyz/status/1656176776425644032
// @TX
// https://explorer.phalcon.xyz/tx/bsc/0xace112925935335d0d7460a2470a612494f910467e263c7ff477221deee90a2c
// https://explorer.phalcon.xyz/tx/bsc/0x7394f2520ff4e913321dd78f67dd84483e396eb7a25cbb02e06fe875fc47013a
// @Summary
// parent `rewardPerToken`, but times all children's balance

interface IPancakeRouter01 {
    function factory() external pure returns (address);
    function WETH() external pure returns (address);

    function addLiquidity(
        address tokenA,
        address tokenB,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    ) external returns (uint256 amountA, uint256 amountB, uint256 liquidity);
    function addLiquidityETH(
        address token,
        uint256 amountTokenDesired,
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/SNK_exp.sol_
