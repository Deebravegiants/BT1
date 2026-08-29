# [?] LQDX - Unauthorized TransferFrom

## Summary
Severity: Unknown
Chain: Ethereum
Component: LQDX_alert
Published: 2024-01-10
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/LQDX_alert_exp.sol
Type: defi-exploit-poc

## Details
Lost: unknown

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";

// @Info
// LQDX LiquidXv2Zap Contract : https://etherscan.io/address/0x364f17a23ae4350319b7491224d10df5796190bc#codeL490

// @NewsTrack
// SlowMist : https://twitter.com/SlowMist_Team/status/1744972012865671452

// Note: the problem lies in the `deposit` function where there is no check that the `account` should be `msg.sender`, thus `account`'s approval on the `zap` can be spent to buy tokens and add liquidity.

interface ILiquidXv2Zap {
    struct swapRouter {
        string platform;
        address tokenIn;
        address tokenOut;
        uint256 amountOutMin;
        uint256 meta; // fee, flag(stable), 0=v2
        uint256 percent;
    }

    struct swapLine {
        swapRouter[] swaps;
    }

    struct swapBlock {
        swapLine[] lines;
    }

    struct swapPath {
        swapBlock[] path;
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2024-01/LQDX_alert_exp.sol_
