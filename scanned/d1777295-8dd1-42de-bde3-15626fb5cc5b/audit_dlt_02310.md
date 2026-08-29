# [?] - BonqDAO - Price Oracle Manipulation

## Summary
Severity: Unknown
Chain: Polygon
Component: BonqDAO
Published: 2023-02-02
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/BonqDAO_exp.sol
Type: defi-exploit-poc

## Details
Lost: BEUR stablecoin and ALBT Token (~88M US$)
References:
- https://polygonscan.com/address/0x8f55d884cad66b79e1a131f6bcb0e66f4fd84d5b#code#F2#L282
- https://explorer.forta.network/alert/0x6338aaa7df91e7136c9f494dfea2c5309dae7c1575815f015f1e9e94be6759d5

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo
// Total Lost : BEUR stablecoin and ALBT token (~88MUS$)
//   |_ 100,514,098.3407 BEUR from BonqDAO protocol
//   |_ 113,813,998.3698 ALBT from BonqDAO's borrowers
// Attacker: 0xcAcf2D28B2A5309e099f0C6e8C60Ec3dDf656642
// Attack Contract: 0xed596991ac5f1aa1858da66c67f7cfa7e54b5f1

// Root cause : Price Oracle manipulation
// The Vulnerability on TellorFlex, Exploit on BonqDAO affecting the AllianceBlock token.
//   The cost of the collateral required by the TellorFlex Oracle to quote is much lower than the profit from the attacker,
//   So the attacker manipulates the wALBT price to extremely high to borrow massive amount of BEUR in Tx1
//   Then, the attacker manipulates the wALBT price to extremely low to liquidates other users wALBT CDP in Tx2.
// Potential mitigations:
//   1. Use VWAP-based Price Oracle or TWAP-based Price Oracle.
//   2. Use `getDataBefore()` to get a wALBT price that passed a sufficient dispute window

// @Info
// Attack Txs:
//   Tx1: 0x31957ecc43774d19f54d9968e95c69c882468b46860f921668f2c55fadd51b19 (for BEUR) 38792978
//   Tx2: 0xa02d0c3d16d6ee0e0b6a42c3cc91997c2b40c87d777136dedebe8ee0f47f32b1 (for ALBT) 38793029
// Vulnerable Contract Code:
//   https://polygonscan.com/address/0x8f55d884cad66b79e1a131f6bcb0e66f4fd84d5b#code#F2#L282
// Malicious Price Reporters:
//   For Tx1: 0xbaf48429b4d30bdfad488508d3b528033331fe8a
//   For Tx2: 0xb5c0ba8ed0f4fb9a31fccf84b9fb3da639a1ede5

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2023-02/BonqDAO_exp.sol_
