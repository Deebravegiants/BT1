# [?] SKP Token - Owner Backdoor LP Burn + Price Manipulation

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SKP
Published: 2026-05-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/SKP_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~$212K USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : ~$212K USD
// Attacker : 0x83B9e7EDC5B3127E4853A4F4945b92aa88eEF0C8
// Attack Contract : 0xE924853DcDfcB89292335042AB10d68c7315D7C1
// Vulnerable Contract : 0xeCBDc0B76142740Bb564B8aA1BCd061Cb151a666 (SKP Token)
// Attack Tx : 0xbc01ea37bd2ff8f6aa6afcfbe0406114ff27a01e9aa56102bfa4ad8a0c2f25ee
// @Analysis
// Attack date: May 26, 2026
// Chain: BSC, Block: 100582079

// Root Cause:
// The SKP token exposes ownerBurnLiquidityPairTokens(uint256), an owner-only backdoor that
// burns SKP held directly inside the SKP/USDT LP pair. The deployer/owner first burns the
// bulk of the SKP sitting in the pair, then calls sync() on the pair to force the reserves
// to match the now-depleted SKP balance. With SKP reserves slashed but USDT reserves intact,
// the on-chain SKP/USDT price spikes. The attacker (who is the owner) then supplies the
// over-valued SKP as collateral on Venus/Lista DAO to borrow BTCB + USDT.

// Function selectors decoded from bytecode:
// 0x4eb9b26d: ownerBurnLiquidityPairTokens(uint256) -- owner-only burn-from-LP backdoor
// 0xfff6cae9: sync()                                -- pair reserve resync
// burnPercent() = 200 (2% auto-burn on transfer)
// brunFee()     = 500 (5% transfer fee)
// feeWhiteList(address)                             -- bypass fees

interface ISKP is IERC20 {
    function ownerBurnLiquidityPairTokens(
        uint256 amount
    ) external;
    function owner() external view returns (address);
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/SKP_exp.sol_
