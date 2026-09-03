# [?] Lien Finance - Permissionless bond registration / payoff mispricing

## Summary
Severity: Unknown
Chain: Ethereum
Component: LienFinance
Published: 2026-07-24
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/LienFinance_exp.sol
Type: defi-exploit-poc

## Details
Lost: ~542,144 USDC

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";

// Lien Finance — permissionless bond registration + crafted payoff function mispricing.
//
// Incident tx : 0xb96d572b557a12f5ef193e88cca86123a6ae1b6e98b0eeee265870c85848e0e7
//   Ethereum mainnet block 25599302, tx index 4 (the USDC drain). The attack is staged
//   across several txs in that same block, all from EOA 0x0D7d..1808a:
//     idx 0  CREATE  -> deploys the orchestration contract 0xe74d..062e
//     idx 1  0xb67d3eef  -> BondMakerCollateralizedEth.registerNewBond(...) x3 with
//                           attacker-crafted piecewise-linear payoff functions
//     idx 2  0x973de16c  -> further bond registration / bond-group setup
//     idx 3  0x808f4a48  -> further setup
//     idx 4  0xa5514ef8  -> registerNewBondGroup + exchangeEquivalentBonds, then swaps the
//                           freshly-minted bonds through the OTC pools and sweeps the USDC
//   The faithful replay therefore deploys the exact orchestration creation bytecode at the
//   pre-attack block and calls the same four parameterless selectors, in order, as the EOA.
//
// Root cause (contract-logic bug, NOT an oracle manipulation):
//   BondMakerCollateralizedEth.registerNewBond is permissionless — anyone can register a bond
//   whose payoff (fnMap) they fully control. GeneralizedDotc._calcRateBondToErc20 prices such a
//   bond via bondPricer.calcPriceAndLeverage(payoff, oraclePrice, volatility, ...). With a
//   crafted payoff the pricer massively OVER-values a near-worthless bond. The Chainlink feeds
//   are read at their normal on-chain values during the drain tx (ETH latestAnswer 187042764678
//   ~= $1870.42, pricing oracle latestPrice 0x5f5e100 == 1e8) — no price is moved or spoofed.
//   The attacker mints the overvalued bonds for ~free and swaps them, via the OTC pools, against
//   USDC that the LP (0xA961..4d80) had granted as allowance to those pools — draining it.
//
// Verified on-chain USDC (6 dp) deltas across the drain tx:
//   attacker EOA 0x0D7d..1808a   0 -> 542,144,628,604   (+542,144.628604 USDC)
//   LP           0xA961..4d80    allowance to GeneralizedDotc pre-block 532,070,026,484 pulled
//   Final orchestration -> attacker transfer: exactly 542,144,628,604.
//
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-07/LienFinance_exp.sol_
