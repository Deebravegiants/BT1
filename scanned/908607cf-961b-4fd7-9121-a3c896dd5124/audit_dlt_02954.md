# [?] ATM Token - Hidden transferFrom Auto-Swap Drain

## Summary
Severity: Unknown
Chain: BNB Chain
Component: ATM
Published: 2026-06-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/ATM_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$243,543 USDT

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~$243,543 USDT (gross drained from the ATM/USDT PancakeSwap pair)
// Attacker EOA    : 0x7e7C1f0D567c0483f85e1d016718E44414CdBAFE
// Attacker Helper : 0xeCe23b485c38110b7a50B5067B7D4B644f897Dc9 (drives the 30 farmer clones)
// Vulnerable      : 0x986058ec93756E57b4e55b406dD0BeE24bcD95e3 (ATM token, custom _transfer)
// Victim pair     : 0x659b44d603052132fd36cf048d9e0ba1e307ae3a (ATM/USDT Cake-LP)
// Setup    Tx     : 0x3738909da7960d72efc2635d73aff5f15ef14a1b18ee0281abaa3d4c94adc69b (block 102070707, buy leg)
// Drain    Tx     : 0x37b90a337075cd2feea93b12780abe9f953dad476e1c1418a02447aaa6dcfd86 (block 102072357, sell leg)
// @Analysis
// Attack date : June 4, 2026
// Chain       : BSC, drain Block 102072357
// SlowMist    : https://hacked.slowmist.io/  (ATM, BSC, $243,500)
//
// ---------------------------------------------------------------------------------------------
// Root cause (verified from Sourcify-verified ATMToken source):
//
// ATMToken._transfer() sell branch (recipient == uniswapV2Pair, not add-liquidity) auto-dumps the
// contract's OWN ATM holdings whenever its balance exceeds swapAtAmount (200e18):
//
//     uint256 contractTokenBalance = balanceOf[address(this)];
//     if (contractTokenBalance > swapAtAmount) {
//         uint256 numTokensSellToFund = (amount * numTokensSellRate) / 100; // numTokensSellRate = 20 -> 20%
//         if (numTokensSellToFund > contractTokenBalance) numTokensSellToFund = contractTokenBalance;
//         _swapTokenForFund(numTokensSellToFund);  // PancakeSwap sell with amountOutMin = 0
//     }
//
// On every sell the token sells an extra 20%-of-the-sell-size of its own reserves into the pair
// at amountOutMin=0, with proceeds going to the marketing/dividend wallets. Combined with weak
// anti-whale controls that key only off the *sender's* fresh state, an attacker farms the pool.
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-06/ATM_exp.sol_
