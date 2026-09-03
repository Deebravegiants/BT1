# [?] SKP Token - Deliberately Engineered Drain (Insider Exploit / Rug Pull)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: SKP_exp2
Published: 2026-05-26
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/SKP_exp2.sol
Type: defi-exploit-poc

## Details
References:
- https://bscscan.com/tx/0xadf1b6ff02a917043c816bc8bd1ed67038d64a19d06544b09ceeb872518fda37
- https://bscscan.com/tx/0xedb2b6a35cf9637d11bef3e440a36994fd6eb72e1dcbee3b8343757ab55699b4

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// @title   SKP/USDT BNB — Deliberately Engineered Token Drain (BSC, block 100,582,079)
//
// @description
//   A premeditated insider exploit (exit scam) on BNB Smart Chain targeting the
//   SKP/USDT PancakeSwap V2 pair. The SKP token's _transfer() hook
//   (_runSpecialPairFlow) fires whenever the pair sends SKP to a buyer and
//   redistributes an unbounded amount of treasury SKP to a single whitelisted
//   address (WL_ADDRESS). The trigger (balanceOf(pair) − reserve) is flash-loan
//   inflatable in one transaction; the redistribution source is a treasury with
//   no issuance cap.
//
//   This is NOT a conventional external hack. On-chain evidence proves the operator
//   engineered every precondition:
//
//     1. setFeeWhiteList() is onlyOwner — no outside party could set WL_ADDRESS.
//        The owner changed WL to the exploit contract ~6 days before the drain:
//        https://bscscan.com/tx/0xadf1b6ff02a917043c816bc8bd1ed67038d64a19d06544b09ceeb872518fda37
//        https://bscscan.com/tx/0xedb2b6a35cf9637d11bef3e440a36994fd6eb72e1dcbee3b8343757ab55699b4
//
//     2. WL_ADDRESS was deployed and funded by the same wallet that deployed SKP.
//        (BSCScan: WL creator == SKP deployer 0x041F52BF...)
//
//     3. SKP contract source was intentionally left unverified on BSCScan — opacity
//        designed to conceal the hook from LP buyers.
//
//     4. BlockRazor private mempool + deBridge cross-chain bridge were configured in
//        advance (outsiders do not set up exit infrastructure before an "accident").
//
//     5. SKP deployer simultaneously operated 7+ throwaway tokens (SLT2, ZEST,
//        ZXMOTO, FIFA2026, POPMART…) — a classic disposable launcher pattern.
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-05/SKP_exp2.sol_
