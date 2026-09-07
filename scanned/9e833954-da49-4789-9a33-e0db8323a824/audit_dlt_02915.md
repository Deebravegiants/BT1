# [?] MONA LisaVault - reward-farming / BurnAddress accounting exploit!

## Summary
Severity: Unknown
Chain: BNB Chain
Component: MONA_LisaVault
Published: 2026-04-14
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/MONA_LisaVault_exp.sol
Type: defi-exploit-poc

## Details
References:
- https://bscscan.com/tx/0x3a60e1b3a4b0736be4f31839bfd7abc8bfc53b93ddbd3702e77fbc64561a7ea4
- https://app.blocksec.com/phalcon/explorer/tx/bsc/0x3a60e1b3a4b0736be4f31839bfd7abc8bfc53b93ddbd3702e77fbc64561a7ea4

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// @title   MONA LisaVault — Exploit PoC (BSC, block 92,429,268)
//
// @description
//   The MONA node-staking vault (LisaVault) on BSC was exploited in two stages:
//
//   STAGE 1 — LP Drain (insider component)
//     The vault deployer (0xDd02...) also controlled the entire MONA/USDT
//     PancakeSwap LP, supplying 9,874,973 MONA + 66,450 USDT as liquidity.
//     In the exploit tx the deployer's LP was redeemed: MONA returned to the
//     deployer while the 66,450 USDT was routed to the exploit contract.
//     In this PoC we replicate this with vm.prank(VAULT_OWNER).
//
//   STAGE 2 — Vault self-referral exploit
//     For each 220 USDT node purchase the vault distributes:
//       80 USDT → vault reserve
//       20 USDT → WBNB conversion (PancakeSwap USDT/WBNB LP)
//       70 USDT → Level-1 referrer (exploit contract)
//       50 USDT → Level-2 referrer (also exploit-controlled)
//     By buying 25 nodes via proxy contracts (bypassing the 1-node-per-address
//     limit) and controlling both referrer tiers, the attacker recovers
//     25 × (70 + 50) = 3,000 USDT. Combined with the 66,450 USDT from

//     Stage 1 and small MONA dividend sales, net profit ≈ 60,950 USDT.
//
// @exploitTx   0x3a60e1b3a4b0736be4f31839bfd7abc8bfc53b93ddbd3702e77fbc64561a7ea4
// @block       92,429,268
// @attacker    0x7eeEC499e501293f6e589d550046375a2ad0b4c3
// @flashSrc    ListaDAO:Moolah (WBNB flash loan used as inflated collateral
//              to borrow USDT — simulated here via PancakeSwap flash swap)
// @profit      60,950.308 USDT
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2026-04/MONA_LisaVault_exp.sol_
